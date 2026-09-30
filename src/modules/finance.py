from typing import Dict, List, Optional
from datetime import datetime, timezone
from src.core.db import db
from src.core.config import Config

class FinanceModule:
    """
    Automated Finance & Analytics Module
    Generates professional digital invoices with sequential numbering and tracks RevPASH metrics.
    """
    def generate_invoice(self, order_id: str) -> Optional[dict]:
        order = db.orders.get(order_id)
        if not order:
            return None

        # Check if invoice already exists
        if order_id in db.invoices:
            return db.invoices[order_id]

        invoice_number = f"INV-UK-{db.invoice_counter}"
        db.invoice_counter += 1

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
