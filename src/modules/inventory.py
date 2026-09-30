from typing import List, Dict, Optional
from src.core.db import db

class InventoryModule:
    """
    Automated Inventory & Stock Tracking Module
    Tracks stock quantities, triggers low stock alerts, and handles item restocking.
    """
    LOW_STOCK_THRESHOLD = 5

    def get_inventory_status(self) -> List[dict]:
        items = list(db.menu_items.values())
        status_list = []
        for item in items:
            stock = item.get("stock_qty", 0)
            if stock <= 0:
                status = "OUT_OF_STOCK"
            elif stock <= InventoryModule.LOW_STOCK_THRESHOLD:
                status = "LOW_STOCK"
            else:
                status = "IN_STOCK"

            item_copy = dict(item)
            item_copy["stock_status"] = status
            status_list.append(item_copy)
        return status_list

    def restock(self, item_id: str, quantity: int = 20) -> Optional[dict]:
        new_qty = db.restock_item(item_id, quantity)
        if new_qty is not None:
            return {
                "item_id": item_id,
                "new_stock_qty": new_qty,
                "status": "RESTOCKED"
            }
        return None

inventory_service = InventoryModule()
