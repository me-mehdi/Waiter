import io
from typing import List, Dict, Optional
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from src.core.db import db
from src.core.config import Config
from src.modules.inventory import inventory_service

DEFAULT_SUPPLIERS = {
    "SEAFOOD": {
        "name": "Brixham Seafood Direct Ltd",
        "email": "orders@brixhamseafood.co.uk",
        "contact": "Dave Miller",
        "address": "Brixham Fish Market, Devon TQ5 8AW"
    },
    "MEAT": {
        "name": "Smithfield Quality Meats Ltd",
        "email": "orders@smithfieldmeats.co.uk",
        "contact": "John Smith",
        "address": "Charterhouse St, Smithfield, London EC1M 6HJ"
    },
    "BEVERAGE": {
        "name": "Bermondsey Craft Brewery Ltd",
        "email": "trade@bermondseybrewery.co.uk",
        "contact": "Sarah Craft",
        "address": "100 Druid St, Bermondsey, London SE1 2HQ"
    },
    "PRODUCE": {
        "name": "Covent Garden Wholesale Produce",
        "email": "orders@coventgardenproduce.co.uk",
        "contact": "Mary Garden",
        "address": "New Covent Garden Market, Nine Elms, London SW8 5NX"
    }
}

ITEM_SUPPLIER_MAP = {
    "item-1": "SEAFOOD",     # Fish & Chips
    "item-2": "MEAT",        # Full English Breakfast
    "item-3": "BEVERAGE",    # Craft IPA Pint
    "item-4": "PRODUCE",     # Tartare Sauce & Peas
    "item-5": "PRODUCE",     # Fresh Orange Juice
}

class PurchaseOrderModule:
    """
    Automated Purchase Order (PO) Generator for Low-Stock Inventory.
    Auto-detects low stock items, groups by supplier, calculates reorder costs,
    and generates formal supplier emails & ReportLab PDF Purchase Orders.
    """
    DEFAULT_LOW_STOCK_THRESHOLD = 10
    DEFAULT_REORDER_QTY = 50

    def get_low_stock_items(self, threshold: int = DEFAULT_LOW_STOCK_THRESHOLD) -> List[Dict]:
        items = list(db.menu_items.values())
        low_stock = []
        for item in items:
            stock = item.get("stock_qty", 0)
            if stock <= threshold:
                item_copy = dict(item)
                item_copy["supplier_category"] = ITEM_SUPPLIER_MAP.get(item["id"], "PRODUCE")
                item_copy["reorder_suggested_qty"] = max(10, self.DEFAULT_REORDER_QTY - stock)
                low_stock.append(item_copy)
        return low_stock

    def generate_purchase_orders(self, threshold: int = DEFAULT_LOW_STOCK_THRESHOLD, reorder_qty: int = DEFAULT_REORDER_QTY) -> List[Dict]:
        """
        Generates purchase orders grouped by supplier for all low-stock items.
        """
        low_stock_items = self.get_low_stock_items(threshold)
        if not low_stock_items:
            return []

        # Group items by supplier
        supplier_groups: Dict[str, List[Dict]] = {}
        for item in low_stock_items:
            sup_cat = item["supplier_category"]
            if sup_cat not in supplier_groups:
                supplier_groups[sup_cat] = []
            supplier_groups[sup_cat].append(item)

        purchase_orders = []
        po_counter = 1001
        now_iso = datetime.now(timezone.utc).isoformat()

        for sup_cat, items in supplier_groups.items():
            supplier_info = DEFAULT_SUPPLIERS.get(sup_cat, DEFAULT_SUPPLIERS["PRODUCE"])
            po_number = f"PO-UK-{po_counter}"
            po_counter += 1

            po_items = []
            total_est_cost = 0.0

            for item in items:
                qty_to_order = max(10, reorder_qty - item["stock_qty"])
                # Wholesale estimated cost ~ 40% of menu retail price
                unit_cost = round(item["price"] * 0.40, 2)
                item_total = round(unit_cost * qty_to_order, 2)
                total_est_cost += item_total

                po_items.append({
                    "item_id": item["id"],
                    "name": item["name"]["en"],
                    "current_stock": item["stock_qty"],
                    "order_qty": qty_to_order,
                    "unit_cost": unit_cost,
                    "total_cost": item_total
                })

            po_record = {
                "po_number": po_number,
                "supplier_category": sup_cat,
                "supplier_name": supplier_info["name"],
                "supplier_email": supplier_info["email"],
                "supplier_contact": supplier_info["contact"],
                "supplier_address": supplier_info["address"],
                "created_at": now_iso,
                "delivery_destination": "The Waiter Central Kitchen, 12 Floral St, London WC2E 9DH",
                "items": po_items,
                "total_estimated_cost": round(total_est_cost, 2),
                "currency": "GBP",
                "currency_symbol": "£",
                "status": "DRAFT"
            }
            purchase_orders.append(po_record)

        return purchase_orders

    def generate_po_email_text(self, po: Dict) -> str:
        """
        Formats automated plain-text supplier purchase order email body.
        """
        lines = []
        lines.append(f"SUBJECT: Purchase Order {po['po_number']} - The Waiter UK")
        lines.append("")
        lines.append(f"Dear {po['supplier_contact']} ({po['supplier_name']}),")
        lines.append("")
        lines.append(f"Please accept this Purchase Order ({po['po_number']}) for immediate restocking delivery to:")
        lines.append(f"Delivery Address: {po['delivery_destination']}")
        lines.append("")
        lines.append("ORDERED ITEMS:")
        lines.append("-" * 60)
        lines.append(f"{'ITEM NAME':<30} | {'QTY':<8} | {'UNIT EST (£)':<12} | {'TOTAL (£)'}")
        lines.append("-" * 60)

        for item in po["items"]:
            lines.append(f"{item['name'][:30]:<30} | {item['order_qty']:<8} | £{item['unit_cost']:<11.2f} | £{item['total_cost']:.2f}")

        lines.append("-" * 60)
        lines.append(f"ESTIMATED TOTAL ORDER COST: £{po['total_estimated_cost']:.2f}")
        lines.append("")
        lines.append("Please confirm receipt and dispatch estimated arrival time.")
        lines.append("")
        lines.append("Best regards,")
        lines.append("Inventory & Procurement Manager")
        lines.append("The Waiter UK Ltd (London)")

        return "\n".join(lines)

    def generate_po_pdf(self, po: Dict) -> bytes:
        """
        Generates a formal ReportLab PDF document for a Purchase Order.
        """
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
            'POTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'POSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        normal_style = styles['Normal']
        bold_style = ParagraphStyle('POBold', parent=normal_style, fontName='Helvetica-Bold')

        elements = []

        # Document Header
        elements.append(Paragraph(f"PURCHASE ORDER: {po['po_number']}", title_style))
        elements.append(Paragraph(f"Issued by: The Waiter UK Ltd | Date: {po['created_at'][:10]}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Supplier & Delivery Metadata Table
        meta_data = [
            [
                Paragraph("<b>SUPPLIER DETAILS:</b>", bold_style),
                Paragraph("<b>DELIVERY LOCATION:</b>", bold_style)
            ],
            [
                Paragraph(f"{po['supplier_name']}<br/>Attn: {po['supplier_contact']}<br/>{po['supplier_address']}<br/>Email: {po['supplier_email']}", normal_style),
                Paragraph(f"{po['delivery_destination']}<br/>Tel: +44 20 7946 0912<br/>Ref: Urgent Stock Replenishment", normal_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[260, 260])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 15))

        # Items Grid
        table_data = [
            [
                Paragraph("<b>Item Name</b>", bold_style),
                Paragraph("<b>Cur. Stock</b>", bold_style),
                Paragraph("<b>Order Qty</b>", bold_style),
                Paragraph("<b>Est Unit (£)</b>", bold_style),
                Paragraph("<b>Total Cost (£)</b>", bold_style)
            ]
        ]

        for item in po["items"]:
            table_data.append([
                Paragraph(item["name"], normal_style),
                str(item["current_stock"]),
                str(item["order_qty"]),
                f"£{item['unit_cost']:.2f}",
                f"£{item['total_cost']:.2f}"
            ])

        # Summary Row
        table_data.append([
            Paragraph("<b>TOTAL ESTIMATED PO VALUE</b>", bold_style),
            "", "", "",
            Paragraph(f"<b>£{po['total_estimated_cost']:.2f}</b>", bold_style)
        ])

        po_table = Table(table_data, colWidths=[200, 70, 70, 90, 90])
        po_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F1F5F9')]),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E2E8F0')),
            ('SPAN', (0,-1), (3,-1)),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))

        elements.append(po_table)
        elements.append(Spacer(1, 25))

        # Terms & Signatures
        terms_text = (
            "<b>Payment Terms:</b> Net 30 Days from delivery invoice date.<br/>"
            "<b>Quality Standard:</b> Fresh produce must comply with UK Food Standards Agency (FSA) guidelines."
        )
        elements.append(Paragraph(terms_text, normal_style))
        elements.append(Spacer(1, 30))

        sig_data = [
            [Paragraph("<b>Authorized By:</b> ___________________________", normal_style), Paragraph("<b>Supplier Confirmation:</b> ___________________________", normal_style)]
        ]
        sig_table = Table(sig_data, colWidths=[260, 260])
        elements.append(sig_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

purchase_order_service = PurchaseOrderModule()
