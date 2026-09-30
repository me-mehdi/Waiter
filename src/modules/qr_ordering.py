from typing import List, Dict
from src.core.db import db
from src.core.translation import translator

class QROrderingModule:
    """
    QR Code Ordering & Digital Menu Module
    Renders dynamic, multi-language menus and triggers smart upsell recommendations.
    """
    def get_menu(self, language: str = "en") -> List[dict]:
        menu_items = list(db.menu_items.values())
        formatted_menu = []
        for item in menu_items:
            translated = translator.translate_item(item, language)
            formatted_menu.append(translated)
        return formatted_menu

    def get_upsells_for_cart(self, item_ids: List[str], language: str = "en") -> List[dict]:
        upsell_ids = set()
        for item_id in item_ids:
            item = db.menu_items.get(item_id)
            if item:
                upsell_ids.update(item.get("upsell_ids", []))
        
        # Remove items already in cart
        upsell_ids = [uid for uid in upsell_ids if uid not in item_ids]
        
        upsell_items = []
        for uid in upsell_ids:
            item = db.menu_items.get(uid)
            if item:
                upsell_items.append(translator.translate_item(item, language))
        return upsell_items

    def submit_order(self, table_number: int, item_ids: List[str], promo_code: str = None) -> dict:
        subtotal = 0.0
        order_items = []
        
        for item_id in item_ids:
            item = db.menu_items.get(item_id)
            if item:
                subtotal += item["price"]
                order_items.append({
                    "item_id": item["id"],
                    "name": item["name"]["en"],
                    "price": item["price"]
                })
        
        discount = 0.0
        if promo_code and promo_code in db.promos:
            promo = db.promos[promo_code]
            if promo["active"] and promo["current_uses"] < promo["max_uses"]:
                discount = subtotal * (promo["discount_pct"] / 100.0)
                promo["current_uses"] += 1
                
        total = max(0.0, subtotal - discount)
        
        order_payload = {
            "table_number": table_number,
            "items": order_items,
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "total": round(total, 2)
        }
        
        return db.add_order(order_payload)

qr_ordering_service = QROrderingModule()
