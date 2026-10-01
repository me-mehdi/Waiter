import io
from typing import List, Dict, Optional
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from src.core.db import db
from src.core.config import Config
from src.modules.venue import venue_service

# Tax Jurisdiction Rate Rules
TAX_JURISDICTIONS = {
    "UK": {
        "name": "UK HMRC Value Added Tax (VAT)",
        "currency": "GBP",
        "symbol": "£",
        "standard_vat_rate": 0.20,
        "reduced_vat_rate": 0.05,
        "tax_inclusive": True,
        "authority": "HM Revenue & Customs (HMRC)"
    },
    "EU": {
        "name": "French Taxe sur la Valeur Ajoutée (TVA)",
        "currency": "EUR",
        "symbol": "€",
        "standard_vat_rate": 0.20,
        "food_vat_rate": 0.10,
        "tax_inclusive": True,
        "authority": "Direction Générale des Finances Publiques (DGFiP)"
    },
    "US": {
        "name": "New York State & City Sales Tax",
        "currency": "USD",
        "symbol": "$",
        "sales_tax_rate": 0.08875,
        "tax_inclusive": False,
        "authority": "NYS Dept of Taxation & Finance"
    }
}

class MultiTaxComplianceModule:
    """
    Multi-Tax Regulatory Compliance & HMRC Making Tax Digital (MTD) VAT Module.
    Calculates jurisdiction-specific taxes (UK 20% VAT, EU 10%/20% TVA, US 8.875% Sales Tax),
    generates HMRC MTD digital VAT ledgers, and exports formal ReportLab PDF Tax Audit Reports.
    """

    def calculate_tax_breakdown(self, order_id: str) -> Dict:
        """
        Calculates exact tax breakdown for an order according to venue market jurisdiction.
        """
        order = db.orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found.")

        venue_id = order.get("venue_id", "venue-1")
        venues = venue_service.get_venues()
        active_v = next((v for v in venues if v["id"] == venue_id), venues[0])
        market = active_v.get("market", "UK").upper()

        tax_rule = TAX_JURISDICTIONS.get(market, TAX_JURISDICTIONS["UK"])
        subtotal = float(order["subtotal"])
        discount = float(order["discount"])
        net_subtotal = max(0.0, subtotal - discount)

        if tax_rule["tax_inclusive"]:
            # Tax included in price (UK & EU)
            rate = tax_rule["standard_vat_rate"]
            tax_amount = round(net_subtotal * rate / (1.0 + rate), 2)
            net_sales_before_tax = round(net_subtotal - tax_amount, 2)
            total_charged = round(net_subtotal, 2)
        else:
            # Tax added on top of subtotal (US Sales Tax)
            rate = tax_rule["sales_tax_rate"]
            tax_amount = round(net_subtotal * rate, 2)
            net_sales_before_tax = round(net_subtotal, 2)
            total_charged = round(net_subtotal + tax_amount, 2)

        return {
            "order_id": order_id,
            "market": market,
            "jurisdiction": tax_rule["name"],
            "authority": tax_rule["authority"],
            "currency": tax_rule["currency"],
            "currency_symbol": tax_rule["symbol"],
            "tax_inclusive": tax_rule["tax_inclusive"],
            "net_sales_before_tax": net_sales_before_tax,
            "tax_rate_pct": f"{rate * 100:.2f}%",
            "tax_amount": tax_amount,
            "total_charged": total_charged
        }

    def generate_vat_ledger(self, currency: str = "GBP") -> Dict:
        """
        Generates HMRC Making Tax Digital (MTD) 9-box VAT ledger summary across completed orders.
        """
        completed_orders = [o for o in db.orders.values() if o["status"] != "CANCELLED"]
        
        curr = currency.upper()
        symbol = Config.CURRENCY_SYMBOLS.get(curr, "£")
        tax_rate = Config.TAX_RATES.get(curr, 0.20)

        total_gross_sales_gbp = sum(o["total"] for o in completed_orders)
        total_gross_sales = Config.convert_price(total_gross_sales_gbp, curr)

        vat_due_box1 = round(total_gross_sales * tax_rate / (1.0 + tax_rate), 2)
        total_sales_ex_vat_box6 = round(total_gross_sales - vat_due_box1, 2)

        box_1_vat_due = vat_due_box1
        box_2_vat_acquisitions = 0.0
        box_3_total_vat_due = round(box_1_vat_due + box_2_vat_acquisitions, 2)
        box_4_vat_reclaimed = 0.0
        box_5_net_vat_payable = round(box_3_total_vat_due - box_4_vat_reclaimed, 2)
        box_6_total_sales_ex_vat = total_sales_ex_vat_box6
        box_7_total_purchases_ex_vat = 0.0
        box_8_total_goods_supplied_eu = 0.0
        box_9_total_goods_acquired_eu = 0.0

        return {
            "currency": curr,
            "currency_symbol": symbol,
            "total_completed_orders": len(completed_orders),
            "total_gross_revenue": round(total_gross_sales, 2),
            "vat_rate_applicable": f"{tax_rate * 100:.1f}%",
            "mtd_boxes": {
                "box_1_vat_due": box_1_vat_due,
                "box_2_vat_acquisitions": box_2_vat_acquisitions,
                "box_3_total_vat_due": box_3_total_vat_due,
                "box_4_vat_reclaimed": box_4_vat_reclaimed,
                "box_5_net_vat_payable": box_5_net_vat_payable,
                "box_6_total_sales_ex_vat": box_6_total_sales_ex_vat,
                "box_7_total_purchases_ex_vat": box_7_total_purchases_ex_vat,
                "box_8_total_goods_supplied_eu": box_8_total_goods_supplied_eu,
                "box_9_total_goods_acquired_eu": box_9_total_goods_acquired_eu
            }
        }

    def generate_vat_report_pdf(self, currency: str = "GBP") -> bytes:
        """
        Generates a formal ReportLab PDF HMRC MTD VAT Return Audit Statement.
        """
        ledger = self.generate_vat_ledger(currency)
        curr_sym = ledger["currency_symbol"]

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
            'VATTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'VATSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        bold_style = ParagraphStyle('VATBold', parent=styles['Normal'], fontName='Helvetica-Bold')
        normal_style = styles['Normal']

        elements = []

        # Document Header
        elements.append(Paragraph("HMRC MAKING TAX DIGITAL (MTD) VAT RETURN STATEMENT", title_style))
        elements.append(Paragraph(f"Tax Authority: HM Revenue & Customs (UK) | Period: Current Quarter | Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Executive Tax Summary Cards
        summary_data = [
            [
                Paragraph("<b>Total Gross Revenue</b>", bold_style),
                Paragraph("<b>Net Sales (Ex. VAT)</b>", bold_style),
                Paragraph("<b>Net VAT Payable (Box 5)</b>", bold_style)
            ],
            [
                Paragraph(f"{curr_sym}{ledger['total_gross_revenue']:.2f}", normal_style),
                Paragraph(f"{curr_sym}{ledger['mtd_boxes']['box_6_total_sales_ex_vat']:.2f}", normal_style),
                Paragraph(f"<b>{curr_sym}{ledger['mtd_boxes']['box_5_net_vat_payable']:.2f}</b>", bold_style)
            ]
        ]
        sum_table = Table(summary_data, colWidths=[170, 170, 180])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0F172A')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(sum_table)
        elements.append(Spacer(1, 15))

        # HMRC 9-Box MTD Table Grid
        elements.append(Paragraph("<b>HMRC 9-BOX VAT RETURN LEDGER:</b>", bold_style))
        elements.append(Spacer(1, 5))

        boxes = ledger["mtd_boxes"]
        box_table_data = [
            [Paragraph("<b>MTD Box Description</b>", bold_style), Paragraph("<b>Amount (£)</b>", bold_style)],
            [Paragraph("Box 1: VAT due on sales and outputs", normal_style), f"{curr_sym}{boxes['box_1_vat_due']:.2f}"],
            [Paragraph("Box 2: VAT due on acquisitions from EU member states", normal_style), f"{curr_sym}{boxes['box_2_vat_acquisitions']:.2f}"],
            [Paragraph("Box 3: Total VAT due (Box 1 + Box 2)", bold_style), f"{curr_sym}{boxes['box_3_total_vat_due']:.2f}"],
            [Paragraph("Box 4: VAT reclaimed on purchases and inputs", normal_style), f"{curr_sym}{boxes['box_4_vat_reclaimed']:.2f}"],
            [Paragraph("Box 5: Net VAT to pay to HMRC (Box 3 - Box 4)", bold_style), f"<b>{curr_sym}{boxes['box_5_net_vat_payable']:.2f}</b>"],
            [Paragraph("Box 6: Total value of sales excluding VAT", normal_style), f"{curr_sym}{boxes['box_6_total_sales_ex_vat']:.2f}"],
            [Paragraph("Box 7: Total value of purchases excluding VAT", normal_style), f"{curr_sym}{boxes['box_7_total_purchases_ex_vat']:.2f}"],
            [Paragraph("Box 8: Total value of goods supplied to EU states", normal_style), f"{curr_sym}{boxes['box_8_total_goods_supplied_eu']:.2f}"],
            [Paragraph("Box 9: Total value of goods acquired from EU states", normal_style), f"{curr_sym}{boxes['box_9_total_goods_acquired_eu']:.2f}"]
        ]

        b_table = Table(box_table_data, colWidths=[370, 150])
        b_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(b_table)
        elements.append(Spacer(1, 20))

        # Compliance Footer
        cert_text = "<i>This statement is formatted according to UK HMRC Making Tax Digital (MTD) for VAT compliance standards. Generated by The Waiter POS.</i>"
        elements.append(Paragraph(cert_text, normal_style))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

tax_compliance_service = MultiTaxComplianceModule()
