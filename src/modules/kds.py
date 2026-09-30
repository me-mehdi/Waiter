from typing import List, Dict, Optional
from src.core.db import db

class KDSModule:
    """
    Kitchen Display System (KDS) & TV Display Module
    Digitalizes production workflows: New -> Preparing -> Ready -> Served.
    """
    VALID_STATUSES = ["New", "Preparing", "Ready", "Served"]

    def get_active_kitchen_orders(self) -> List[dict]:
        """Returns all orders currently in kitchen (New, Preparing, Ready)."""
        active_orders = [
            order for order in db.orders.values()
            if order["status"] in ["New", "Preparing", "Ready"]
        ]
        # Sort by creation time (FIFO)
        return sorted(active_orders, key=lambda x: x["created_at"])

    def get_tv_display_status(self) -> dict:
        """Returns orders categorized for guest-facing TV screens."""
        preparing = [o["id"] for o in db.orders.values() if o["status"] == "Preparing"]
        ready = [o["id"] for o in db.orders.values() if o["status"] == "Ready"]
        return {
            "preparing": preparing,
            "ready": ready
        }

    def advance_order_status(self, order_id: str) -> Optional[dict]:
        """Advances order status through the KDS lifecycle."""
        order = db.orders.get(order_id)
        if not order:
            return None
            
        current_idx = self.VALID_STATUSES.index(order["status"])
        if current_idx < len(self.VALID_STATUSES) - 1:
            next_status = self.VALID_STATUSES[current_idx + 1]
            return db.update_order_status(order_id, next_status)
        return order

kds_service = KDSModule()
