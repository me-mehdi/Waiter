from typing import Dict, List, Optional
from datetime import datetime, timezone
import io

from src.core.db import db
from src.core.config import Config

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class FinanceModule:
    """
    Automated Finance & Analytics Module
    Generates digital invoices with sequential numbering, multi-currency PDF exports, and RevPASH analytics.
    Excludes cancelled/refunded orders from net financial metrics.
    """
    def generate_invoice(self, order_id: str, currency: str = "GBP") -> Optional[dict]:
        order = db.orders.get(order_id)
        if not order:
            return None

        if order_id in db.invoices:
            return db.invoices[order_id]

        invoice_number = f"INV-UK-{db.invoice_counter}"
        curr = currency.upper()
        symbol = Config.CURRENCY_SYMBOLS.get(curr, "£")
        tax_rate = Config.TAX_RATES.get(curr, 0.20)
        tax_label = Config.TAX_LABELS.get(curr, "UK VAT (20%)")

        subtotal_gbp = order["subtotal"]
        subtotal = Config.convert_price(subtotal_gbp, curr)
        discount = Config.convert_price(order["discount"], curr)
        
        vat_amount = round(subtotal * tax_rate, 2)
        total_with_vat = round((subtotal - discount) + vat_amount, 2)

        items_converted = []
        for item in order["items"]:
            item_copy = dict(item)
            item_copy["price"] = Config.convert_price(item["price"], curr)
            items_converted.append(item_copy)

        invoice_status = "REFUNDED" if order["status"] == "CANCELLED" else "PAID"

        invoice = {
            "invoice_number": invoice_number,
            "order_id": order_id,
            "table_number": order["table_number"],
            "items": items_converted,
            "subtotal": subtotal,
            "discount": discount,
            "vat_rate": f"{int(tax_rate*100)}%",
            "vat_label": tax_label,
            "vat_amount": vat_amount,
            "total": total_with_vat,
            "currency": curr,
            "currency_symbol": symbol,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "status": invoice_status
        }
        db.invoices[order_id] = invoice
        return invoice

    def generate_pdf_invoice(self, order_id: str, currency: str = "GBP") -> Optional[bytes]:
        invoice = self.generate_invoice(order_id, currency)
        if not invoice:
            return None

        symbol = invoice.get("currency_symbol", "£")
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#1e3c72"),
            spaceAfter=12
        )
        
        story.append(Paragraph("THE WAITER - OFFICIAL INVOICE", title_style))
        story.append(Paragraph(f"<b>Invoice No:</b> {invoice['invoice_number']} | <b>Table:</b> #{invoice['table_number']}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {invoice['issued_at'][:19].replace('T', ' ')} UTC", styles['Normal']))
        story.append(Paragraph(f"<b>Currency:</b> {invoice['currency']} ({symbol})", styles['Normal']))
        
        status_color = "red" if invoice['status'] == "REFUNDED" else "green"
        story.append(Paragraph(f"<b>Status:</b> <font color='{status_color}'>{invoice['status']}</font>", styles['Normal']))
        story.append(Spacer(1, 16))

        # Table data
        data = [[f"Item Description", f"Price ({symbol})"]]
        for item in invoice["items"]:
            data.append([item["name"], f"{symbol}{item['price']:.2f}"])

        data.append(["", ""])
        data.append(["Subtotal", f"{symbol}{invoice['subtotal']:.2f}"])
        data.append(["Discount", f"-{symbol}{invoice['discount']:.2f}"])
        data.append([invoice.get('vat_label', 'Tax'), f"{symbol}{invoice['vat_amount']:.2f}"])
        data.append(["TOTAL PAID", f"{symbol}{invoice['total']:.2f}"])

        table = Table(data, colWidths=[350, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3c72")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
            ('GRID', (0, 0), (-1, -6), 0.5, colors.lightgrey),
            ('LINEABOVE', (0, -4), (-1, -4), 1, colors.HexColor("#1e3c72")),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))

        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            alignment=1
        )
        story.append(Paragraph("Thank you for dining with us! Powered by The Waiter (waiter.com)", footer_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def calculate_analytics(self, total_seats: int = 50, operating_hours: int = 12, currency: str = "GBP") -> dict:
        # Exclude CANCELLED orders from net financial metrics
        active_orders = [o for o in db.orders.values() if o["status"] != "CANCELLED"]
        curr = currency.upper()
        symbol = Config.CURRENCY_SYMBOLS.get(curr, "£")

        total_revenue_gbp = sum(o["total"] for o in active_orders)
        total_revenue = Config.convert_price(total_revenue_gbp, curr)
        total_orders = len(active_orders)
        
        available_seat_hours = total_seats * operating_hours
        rev_pash = round(total_revenue / available_seat_hours, 2) if available_seat_hours > 0 else 0.0

        dish_counts = {}
        for order in active_orders:
            for item in order["items"]:
                name = item["name"]
                dish_counts[name] = dish_counts.get(name, 0) + 1

        popular_dishes = sorted(dish_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "average_transaction_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0,
            "rev_pash": rev_pash,
            "popular_dishes": popular_dishes,
            "currency": curr,
            "currency_symbol": symbol
        }

    def generate_z_report(self, date_str: Optional[str] = None, currency: str = "GBP") -> dict:
        """
        Calculates End-of-Day Z-Report metrics for a given date.
        """
        if not date_str:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        curr = currency.upper()
        symbol = Config.CURRENCY_SYMBOLS.get(curr, "£")
        tax_rate = Config.TAX_RATES.get(curr, 0.20)
        tax_label = Config.TAX_LABELS.get(curr, "UK VAT (20%)")

        all_orders = db.orders.values()
        day_orders = [o for o in all_orders if o.get("created_at", "").startswith(date_str)]

        completed_orders = [o for o in day_orders if o["status"] != "CANCELLED"]
        cancelled_orders = [o for o in day_orders if o["status"] == "CANCELLED"]

        gross_sales = sum(o["subtotal"] for o in completed_orders)
        discounts = sum(o["discount"] for o in completed_orders)
        net_sales = gross_sales - discounts
        vat_amount = round(net_sales * tax_rate, 2)
        total_revenue = round(net_sales + vat_amount, 2)

        gross_sales = Config.convert_price(gross_sales, curr)
        discounts = Config.convert_price(discounts, curr)
        net_sales = Config.convert_price(net_sales, curr)
        vat_amount = Config.convert_price(vat_amount, curr)
        total_revenue = Config.convert_price(total_revenue, curr)

        voided_value = sum(o["total"] for o in cancelled_orders)
        voided_value = Config.convert_price(voided_value, curr)

        total_tickets = len(day_orders)
        completed_count = len(completed_orders)
        cancelled_count = len(cancelled_orders)

        atv = round(total_revenue / completed_count, 2) if completed_count > 0 else 0.0

        dish_counts = {}
        for order in completed_orders:
            for item in order["items"]:
                name = item["name"]
                dish_counts[name] = dish_counts.get(name, 0) + 1

        top_dishes = sorted(dish_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "report_date": date_str,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "currency": curr,
            "currency_symbol": symbol,
            "vat_label": tax_label,
            "gross_sales": round(gross_sales, 2),
            "discounts": round(discounts, 2),
            "net_sales": round(net_sales, 2),
            "vat_amount": round(vat_amount, 2),
            "total_revenue": round(total_revenue, 2),
            "voided_value": round(voided_value, 2),
            "total_tickets": total_tickets,
            "completed_tickets": completed_count,
            "cancelled_tickets": cancelled_count,
            "atv": atv,
            "top_dishes": top_dishes
        }

    def generate_pdf_z_report(self, date_str: Optional[str] = None, currency: str = "GBP") -> bytes:
        """
        Generates a formal End-of-Day Z-Report PDF document.
        """
        report = self.generate_z_report(date_str, currency)
        symbol = report["currency_symbol"]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ZReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor("#0b0c10"),
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'ZReportSubTitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#4a5568"),
            spaceAfter=15
        )

        section_style = ParagraphStyle(
            'ZReportSection',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor("#1e3c72"),
            spaceBefore=12,
            spaceAfter=8
        )

        story.append(Paragraph("THE WAITER — DAILY FINANCIAL Z-REPORT", title_style))
        story.append(Paragraph(f"<b>Venue:</b> UK Flagship | <b>Report Date:</b> {report['report_date']} | <b>Generated:</b> {report['generated_at'][:19].replace('T', ' ')} UTC", subtitle_style))
        story.append(Spacer(1, 10))

        # Financial Performance Summary
        story.append(Paragraph("1. Financial Summary", section_style))
        fin_data = [
            ["Metric", f"Amount ({symbol})"],
            ["Gross Sales (excl. Tax)", f"{symbol}{report['gross_sales']:.2f}"],
            ["Discounts & Promos", f"-{symbol}{report['discounts']:.2f}"],
            ["Net Taxable Sales", f"{symbol}{report['net_sales']:.2f}"],
            [report['vat_label'], f"{symbol}{report['vat_amount']:.2f}"],
            ["TOTAL NET REVENUE COLLECTED", f"{symbol}{report['total_revenue']:.2f}"],
            ["Voided / Cancelled Value (Lost Revenue)", f"{symbol}{report['voided_value']:.2f}"]
        ]
        t1 = Table(fin_data, colWidths=[350, 150])
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3c72")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor("#e2e8f0")),
            ('TEXTCOLOR', (0, 6), (-1, 6), colors.red),
        ]))
        story.append(t1)
        story.append(Spacer(1, 15))

        # Operational Ticket Summary
        story.append(Paragraph("2. Operational Statistics", section_style))
        ops_data = [
            ["Metric", "Value"],
            ["Total Tickets Issued", str(report['total_tickets'])],
            ["Completed / Served Tickets", str(report['completed_tickets'])],
            ["Cancelled / Voided Tickets", str(report['cancelled_tickets'])],
            ["Average Ticket Value (ATV)", f"{symbol}{report['atv']:.2f}"]
        ]
        t2 = Table(ops_data, colWidths=[350, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2d3748")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ffffff")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))

        # Top Selling Items
        story.append(Paragraph("3. Top 5 Best-Selling Dishes", section_style))
        top_data = [["Item Description", "Qty Sold"]]
        if report['top_dishes']:
            for name, qty in report['top_dishes']:
                top_data.append([name, str(qty)])
        else:
            top_data.append(["No items sold for this date", "0"])

        t3 = Table(top_data, colWidths=[350, 150])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4a5568")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        story.append(t3)
        story.append(Spacer(1, 30))

        # Duty Manager Sign-Off
        story.append(Paragraph("<b>Duty Manager Verification & Sign-Off</b>", styles['Normal']))
        story.append(Spacer(1, 10))
        sign_data = [
            ["Manager Name: _______________________", "Signature: _______________________"],
            ["Shift: [  ] Morning   [  ] Evening   [  ] Full Day", "Date Signed: ____ / ____ / ________"]
        ]
        t_sign = Table(sign_data, colWidths=[250, 250])
        t_sign.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#2d3748")),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(t_sign)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

finance_service = FinanceModule()

