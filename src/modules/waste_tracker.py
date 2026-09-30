import io
import json
from typing import List, Dict, Optional
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from src.core.db import db
from src.core.config import Config
from src.modules.venue import venue_service

VALID_WASTE_REASONS = [
    "EXPIRED",
    "SPOILED",
    "PREP_ERROR",
    "CUSTOMER_RETURN",
    "SPILLAGE"
]

class WasteTrackerModule:
    """
    Kitchen Waste & Food Loss Tracking Module for The Waiter.
    Tracks ingredient/dishes loss, updates stock levels, categorizes loss reasons,
    calculates financial loss metrics, and exports ReportLab PDF Waste Loss Audit Reports.
    """

    def log_waste(self, item_id: str, quantity: int, reason: str, staff_name: str = "Head Chef") -> Dict:
        """
        Logs a new kitchen food waste / loss entry and updates stock.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        reason_clean = reason.upper()
        if reason_clean not in VALID_WASTE_REASONS:
            raise ValueError(f"Invalid waste reason '{reason}'. Valid reasons: {', '.join(VALID_WASTE_REASONS)}")

        item = db.menu_items.get(item_id)
        if not item:
            raise ValueError(f"Item ID {item_id} not found.")

        # Estimate wholesale unit cost (~40% of retail price)
        unit_cost = round(item["price"] * 0.40, 2)
        total_loss = round(unit_cost * quantity, 2)

        # Deduct stock quantity from inventory
        current_stock = item.get("stock_qty", 0)
        new_stock = max(0, current_stock - quantity)
        db.update_stock_qty(item_id, new_stock)

        now_iso = datetime.now(timezone.utc).isoformat()
        venue_id = venue_service.get_active_venue()["id"]

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM food_waste")
            w_count = cursor.fetchone()[0] + 1
            waste_id = f"WST-{w_count:04d}"

            cursor.execute("""
                INSERT INTO food_waste (id, item_id, item_name, quantity, unit_cost, total_loss, reason, staff_name, logged_at, venue_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                waste_id,
                item_id,
                item["name"]["en"],
                quantity,
                unit_cost,
                total_loss,
                reason_clean,
                staff_name,
                now_iso,
                venue_id
            ))
            conn.commit()

        return {
            "id": waste_id,
            "item_id": item_id,
            "item_name": item["name"]["en"],
            "quantity": quantity,
            "unit_cost": unit_cost,
            "total_loss": total_loss,
            "reason": reason_clean,
            "staff_name": staff_name,
            "remaining_stock": new_stock,
            "logged_at": now_iso,
            "venue_id": venue_id
        }

    def get_waste_logs(self, reason: str = None) -> List[Dict]:
        """
        Retrieves recorded kitchen waste logs.
        """
        with db._get_connection() as conn:
            cursor = conn.cursor()
            if reason:
                cursor.execute("SELECT * FROM food_waste WHERE reason = ? ORDER BY logged_at DESC", (reason.upper(),))
            else:
                cursor.execute("SELECT * FROM food_waste ORDER BY logged_at DESC")

            rows = cursor.fetchall()

        logs = []
        for r in rows:
            logs.append({
                "id": r["id"],
                "item_id": r["item_id"],
                "item_name": r["item_name"],
                "quantity": r["quantity"],
                "unit_cost": float(r["unit_cost"]),
                "total_loss": float(r["total_loss"]),
                "reason": r["reason"],
                "staff_name": r["staff_name"],
                "logged_at": r["logged_at"],
                "venue_id": r["venue_id"]
            })
        return logs

    def get_waste_analytics(self, currency: str = "GBP") -> Dict:
        """
        Calculates financial loss analytics, breakdown by reason, and top wasted items.
        """
        logs = self.get_waste_logs()
        curr = currency.upper()
        symbol = Config.CURRENCY_SYMBOLS.get(curr, "£")

        total_waste_items = sum(l["quantity"] for l in logs)
        total_loss_gbp = sum(l["total_loss"] for l in logs)
        total_loss_converted = Config.convert_price(total_loss_gbp, curr)

        reason_breakdown: Dict[str, Dict] = {}
        for r_name in VALID_WASTE_REASONS:
            reason_breakdown[r_name] = {"count": 0, "quantity": 0, "loss_amount": 0.0}

        item_totals: Dict[str, Dict] = {}

        for l in logs:
            r = l["reason"]
            if r not in reason_breakdown:
                reason_breakdown[r] = {"count": 0, "quantity": 0, "loss_amount": 0.0}

            reason_breakdown[r]["count"] += 1
            reason_breakdown[r]["quantity"] += l["quantity"]
            reason_breakdown[r]["loss_amount"] += Config.convert_price(l["total_loss"], curr)

            iname = l["item_name"]
            if iname not in item_totals:
                item_totals[iname] = {"quantity": 0, "loss_amount": 0.0}
            item_totals[iname]["quantity"] += l["quantity"]
            item_totals[iname]["loss_amount"] += Config.convert_price(l["total_loss"], curr)

        for k in reason_breakdown:
            reason_breakdown[k]["loss_amount"] = round(reason_breakdown[k]["loss_amount"], 2)

        top_wasted = sorted(
            [{"item_name": k, "quantity": v["quantity"], "loss_amount": round(v["loss_amount"], 2)} for k, v in item_totals.items()],
            key=lambda x: x["loss_amount"],
            reverse=True
        )

        return {
            "total_waste_logs": len(logs),
            "total_items_wasted": total_waste_items,
            "total_financial_loss": round(total_loss_converted, 2),
            "currency": curr,
            "currency_symbol": symbol,
            "reason_breakdown": reason_breakdown,
            "top_wasted_items": top_wasted[:5]
        }

    def generate_waste_pdf_report(self, currency: str = "GBP") -> bytes:
        """
        Generates a formal ReportLab PDF Waste Audit & Loss Summary report.
        """
        analytics = self.get_waste_analytics(currency)
        logs = self.get_waste_logs()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'WasteTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#DC2626'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'WasteSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        bold_style = ParagraphStyle('WasteBold', parent=styles['Normal'], fontName='Helvetica-Bold')
        normal_style = styles['Normal']

        elements = []

        # Document Header
        elements.append(Paragraph("KITCHEN WASTE & FOOD LOSS AUDIT REPORT", title_style))
        elements.append(Paragraph(f"Venue: {venue_service.get_active_venue()['name']} | Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Financial Executive Summary Cards
        curr_sym = analytics["currency_symbol"]
        summary_data = [
            [
                Paragraph("<b>Total Waste Incidents</b>", bold_style),
                Paragraph("<b>Total Units Lost</b>", bold_style),
                Paragraph("<b>Total Financial Cost Loss</b>", bold_style)
            ],
            [
                Paragraph(str(analytics["total_waste_logs"]), normal_style),
                Paragraph(str(analytics["total_items_wasted"]), normal_style),
                Paragraph(f"{curr_sym}{analytics['total_financial_loss']:.2f}", bold_style)
            ]
        ]
        sum_table = Table(summary_data, colWidths=[170, 170, 180])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#FCA5A5')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FECACA')),
        ]))
        elements.append(sum_table)
        elements.append(Spacer(1, 15))

        # Loss Reason Breakdown Grid
        elements.append(Paragraph("<b>LOSS BREAKDOWN BY REASON:</b>", bold_style))
        elements.append(Spacer(1, 5))

        reason_table_data = [
            [
                Paragraph("<b>Waste Category Reason</b>", bold_style),
                Paragraph("<b>Incident Count</b>", bold_style),
                Paragraph("<b>Units Wasted</b>", bold_style),
                Paragraph("<b>Financial Loss</b>", bold_style)
            ]
        ]

        for r_name, r_info in analytics["reason_breakdown"].items():
            reason_table_data.append([
                Paragraph(r_name, normal_style),
                str(r_info["count"]),
                str(r_info["quantity"]),
                f"{curr_sym}{r_info['loss_amount']:.2f}"
            ])

        r_table = Table(reason_table_data, colWidths=[180, 110, 110, 120])
        r_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#791E1E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#FFF1F1')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FCA5A5')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(r_table)
        elements.append(Spacer(1, 15))

        # Recent Log Entries Table
        elements.append(Paragraph("<b>RECENT WASTE AUDIT LOGS:</b>", bold_style))
        elements.append(Spacer(1, 5))

        log_table_data = [
            [
                Paragraph("<b>ID</b>", bold_style),
                Paragraph("<b>Item Dish Name</b>", bold_style),
                Paragraph("<b>Qty</b>", bold_style),
                Paragraph("<b>Reason</b>", bold_style),
                Paragraph("<b>Staff</b>", bold_style),
                Paragraph("<b>Total Loss</b>", bold_style)
            ]
        ]

        for l in logs[:10]:
            loss_converted = Config.convert_price(l["total_loss"], currency)
            log_table_data.append([
                l["id"],
                Paragraph(l["item_name"], normal_style),
                str(l["quantity"]),
                l["reason"],
                Paragraph(l["staff_name"], normal_style),
                f"{curr_sym}{loss_converted:.2f}"
            ])

        if len(logs) == 0:
            log_table_data.append(["-", "No waste logged", "0", "-", "-", f"{curr_sym}0.00"])

        l_table = Table(log_table_data, colWidths=[65, 145, 45, 105, 95, 65])
        l_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (2,0), (2,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(l_table)
        elements.append(Spacer(1, 20))

        # Certification Footer
        cert_text = "<i>This audit report is generated automatically by The Waiter Kitchen Inventory System. Verified for UK Food Safety Compliance.</i>"
        elements.append(Paragraph(cert_text, normal_style))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

waste_tracker_service = WasteTrackerModule()
