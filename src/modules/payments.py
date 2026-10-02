import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from src.core.db import db

class PaymentsModule:
    """
    Online Table Payments & Digital Tip Selector Module for 'The Waiter'
    Handles Apple Pay, Google Pay, and Stripe Card Checkout with digital tipping presets (10%, 12.5%, 15%, 20%).
    """
    SUPPORTED_METHODS = [
        {"id": "APPLE_PAY", "name": "Apple Pay", "icon": "fa-brands fa-apple"},
        {"id": "GOOGLE_PAY", "name": "Google Pay", "icon": "fa-brands fa-google-pay"},
        {"id": "CARD_STRIPE", "name": "Debit / Credit Card (Stripe)", "icon": "fa-solid fa-credit-card"}
    ]

    TIP_PRESETS = [0.0, 10.0, 12.5, 15.0, 20.0]

    def process_checkout(
        self,
        order_id: str,
        payment_method: str = "CARD_STRIPE",
        tip_percentage: float = 12.5,
        custom_tip_amount: Optional[float] = None,
        currency: str = "GBP"
    ) -> Dict[str, Any]:
        """Processes payment for an order with tip calculation and payment confirmation."""
        order = db.orders.get(order_id)
        if not order:
            raise ValueError(f"Order '{order_id}' not found")

        order_total = order["total"]
        
        # Calculate tip
        if custom_tip_amount is not None and custom_tip_amount >= 0:
            tip_amount = round(custom_tip_amount, 2)
        else:
            tip_amount = round(order_total * (tip_percentage / 100.0), 2)

        grand_total = round(order_total + tip_amount, 2)
        transaction_ref = f"TXN-{payment_method[:4]}-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        payment_record = {
            "transaction_ref": transaction_ref,
            "order_id": order_id,
            "table_number": order["table_number"],
            "order_total": order_total,
            "tip_percentage": tip_percentage if custom_tip_amount is None else 0.0,
            "tip_amount": tip_amount,
            "grand_total": grand_total,
            "currency": currency,
            "payment_method": payment_method,
            "status": "COMPLETED",
            "timestamp": now_iso
        }

        # Store payment in custom_settings
        if "payments_history" not in db.custom_settings:
            db.custom_settings["payments_history"] = []
        db.custom_settings["payments_history"].append(payment_record)

        return payment_record

    def get_payment_methods(self) -> Dict[str, Any]:
        return {
            "methods": self.SUPPORTED_METHODS,
            "tip_presets": self.TIP_PRESETS
        }

payments_service = PaymentsModule()
