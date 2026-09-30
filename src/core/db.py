from datetime import datetime, timezone
from typing import List, Dict, Optional
import threading

class DatabaseStore:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.menu_items: Dict[str, dict] = {
                "item-1": {
                    "id": "item-1",
                    "name": {"en": "Fish & Chips", "fr": "Poisson & Frites", "ar": "سمك وبطاطس"},
                    "description": {"en": "Fresh Atlantic cod with crispy chips", "fr": "Cabillaud frais et frites croustillantes", "ar": "قد أطلسي طازج مع بطاطس مقرمشة"},
                    "price": 14.50,
                    "category": "Mains",
                    "upsell_ids": ["item-4"]
                },
                "item-2": {
                    "id": "item-2",
                    "name": {"en": "Full English Breakfast", "fr": "Petit déjeuner anglais", "ar": "إفطار إنجليزي كامل"},
                    "description": {"en": "Sausages, bacon, eggs, beans, toast", "fr": "Saucisses, bacon, œufs, haricots, pain grillé", "ar": "نقانق، لحم قديد، بيض، فاصوليا، نخب"},
                    "price": 11.00,
                    "category": "Mains",
                    "upsell_ids": ["item-5"]
                },
                "item-3": {
                    "id": "item-3",
                    "name": {"en": "Craft IPA Pint", "fr": "Pinte de Bière Artisanale", "ar": "بيل ايل حرفية"},
                    "description": {"en": "Local UK craft brewery IPA", "fr": "Bière IPA artisanale britannique", "ar": "بيرة بريطانية حرفية"},
                    "price": 6.20,
                    "category": "Drinks",
                    "upsell_ids": []
                },
                "item-4": {
                    "id": "item-4",
                    "name": {"en": "Tartare Sauce & Peas", "fr": "Sauce Tartare & Petits Pois", "ar": "صلصة التارتار والبسلة"},
                    "description": {"en": "Homemade tartare sauce & crushed mint peas", "fr": "Sauce tartare maison et petits pois écrasés", "ar": "صلصة تارتار منزلية وبسلة بالنيداد"},
                    "price": 2.50,
                    "category": "Sides",
                    "upsell_ids": []
                },
                "item-5": {
                    "id": "item-5",
                    "name": {"en": "Fresh Orange Juice", "fr": "Jus d'Orange Frais", "ar": "عصير برتقال طازج"},
                    "description": {"en": "Freshly squeezed juice", "fr": "Jus fraîchement pressé", "ar": "عصير برتقال طازج مكرر"},
                    "price": 3.80,
                    "category": "Drinks",
                    "upsell_ids": []
                }
            }
            self.orders: Dict[str, dict] = {}
            self.promos: Dict[str, dict] = {
                "WELCOME10": {"code": "WELCOME10", "discount_pct": 10.0, "max_uses": 100, "current_uses": 0, "active": True},
                "OFFPEAK20": {"code": "OFFPEAK20", "discount_pct": 20.0, "max_uses": 50, "current_uses": 0, "active": True}
            }
            self.reviews: List[dict] = []
            self.invoices: Dict[str, dict] = {}
            self.invoice_counter = 1001

    def add_order(self, order_data: dict) -> dict:
        with self._lock:
            order_id = f"ORD-{len(self.orders) + 1:04d}"
            order = {
                "id": order_id,
                "table_number": order_data.get("table_number", 1),
                "items": order_data.get("items", []),
                "status": "New",  # New, Preparing, Ready, Served
                "subtotal": order_data.get("subtotal", 0.0),
                "discount": order_data.get("discount", 0.0),
                "total": order_data.get("total", 0.0),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            self.orders[order_id] = order
            return order

    def update_order_status(self, order_id: str, new_status: str) -> Optional[dict]:
        with self._lock:
            if order_id in self.orders:
                self.orders[order_id]["status"] = new_status
                self.orders[order_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
                return self.orders[order_id]
            return None

    def add_review(self, review_data: dict) -> dict:
        with self._lock:
            review = {
                "id": f"REV-{len(self.reviews) + 1:04d}",
                "table_number": review_data.get("table_number"),
                "rating": review_data.get("rating", 5),
                "comment": review_data.get("comment", ""),
                "private": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.reviews.append(review)
            return review

db = DatabaseStore()
