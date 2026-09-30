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
    Generates professional digital invoices with sequential numbering, PDF exports, and tracks RevPASH metrics.
    """
    def generate_invoice(self, order_id: str) -> Optional[dict]:
        order = db.orders.get(order_id)
        if not order:
            return None

        # Check if invoice already exists
        if order_id in db.invoices:
            return db.invoices[order_id]

        invoice_number = f"INV-UK-{db.invoice_counter}"

        subtotal = order["subtotal"]
        vat_rate = 0.20  # UK VAT 20%
        vat_amount = round(subtotal * vat_rate, 2)
        total_with_vat = round(order["total"] + vat_amount, 2)

        invoice = {
            "invoice_number": invoice_number,
            "order_id": order_id,
            "table_number": order["table_number"],
            "items": order["items"],
            "subtotal": subtotal,
            "discount": order["discount"],
            "vat_rate": "20%",
            "vat_amount": vat_amount,
            "total": total_with_vat,
            "currency": Config.DEFAULT_CURRENCY,
            "currency_symbol": Config.CURRENCY_SYMBOL,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "status": "PAID"
        }
        db.invoices[order_id] = invoice
        return invoice

    def generate_pdf_invoice(self, order_id: str) -> Optional[bytes]:
        invoice = self.generate_invoice(order_id)
        if not invoice:
            return None

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
        story.append(Paragraph(f"<b>Status:</b> <font color='green'>{invoice['status']}</font>", styles['Normal']))
        story.append(Spacer(1, 16))

        # Table data
        data = [["Item Description", "Price (£)"]]
        for item in invoice["items"]:
            data.append([item["name"], f"£{item['price']:.2f}"])

        data.append(["", ""])
        data.append(["Subtotal", f"£{invoice['subtotal']:.2f}"])
        data.append(["Discount", f"-£{invoice['discount']:.2f}"])
        data.append(["UK VAT (20%)", f"£{invoice['vat_amount']:.2f}"])
        data.append(["TOTAL PAID", f"£{invoice['total']:.2f}"])

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

    def calculate_analytics(self, total_seats: int = 50, operating_hours: int = 12) -> dict:
        orders = list(db.orders.values())
        total_revenue = sum(o["total"] for o in orders)
        total_orders = len(orders)
        
        # Calculate RevPASH (Revenue Per Available Seat Hour)
        available_seat_hours = total_seats * operating_hours
        rev_pash = round(total_revenue / available_seat_hours, 2) if available_seat_hours > 0 else 0.0

        # Calculate dish popularity ranking
        dish_counts = {}
        for order in orders:
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
            "currency_symbol": Config.CURRENCY_SYMBOL
        }

finance_service = FinanceModule()
