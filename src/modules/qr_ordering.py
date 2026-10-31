from typing import List, Dict
from src.core.db import db
from src.core.translation import translator
from src.core.config import Config

from src.modules.venue import venue_service
from src.modules.kds import kds_service

class QROrderingModule:
    """
    QR Code Ordering & Digital Menu Module
    Renders dynamic multi-language menus, multi-currency conversion, stock status, and smart upsell recommendations.
    """
    def get_menu(self, language: str = "en", currency: str = "GBP") -> List[dict]:
        menu_items = list(db.menu_items.values())
        formatted_menu = []
        for item in menu_items:
            translated = translator.translate_item(item, language)
            
            # Currency conversion
            base_price = item["price"]
            converted_price = Config.convert_price(base_price, currency)
            symbol = Config.CURRENCY_SYMBOLS.get(currency.upper(), "£")
            
            # Stock Status calculation
            stock = item.get("stock_qty", 0)
            if stock <= 0:
                stock_status = "OUT_OF_STOCK"
            elif stock <= 5:
                stock_status = "LOW_STOCK"
            else:
                stock_status = "IN_STOCK"

            translated["price"] = converted_price
            translated["price_formatted"] = f"{symbol}{converted_price:.2f}"
            translated["currency"] = currency.upper()
            translated["stock_qty"] = stock
            translated["stock_status"] = stock_status
            translated["alcohol"] = item["id"] in Config.ALCOHOL_ITEM_IDS
            
            formatted_menu.append(translated)
        return formatted_menu

    def get_upsells_for_cart(self, item_ids: List[str], language: str = "en", currency: str = "GBP") -> List[dict]:
        upsell_ids = set()
        for item_id in item_ids:
            item = db.menu_items.get(item_id)
            if item:
                upsell_ids.update(item.get("upsell_ids", []))
        
        upsell_ids = [uid for uid in upsell_ids if uid not in item_ids]
        
        upsell_items = []
        for uid in upsell_ids:
            item = db.menu_items.get(uid)
            if item and item.get("stock_qty", 0) > 0:
                translated = translator.translate_item(item, language)
                converted_price = Config.convert_price(item["price"], currency)
                symbol = Config.CURRENCY_SYMBOLS.get(currency.upper(), "£")
                translated["price"] = converted_price
                translated["price_formatted"] = f"{symbol}{converted_price:.2f}"
                translated["currency"] = currency.upper()
                translated["stock_qty"] = item.get("stock_qty", 0)
                upsell_items.append(translated)
        return upsell_items

    def submit_order(self, table_number: int, item_ids: List[str], promo_code: str = None, venue_id: str = None, notes: str = None) -> dict:
        if not venue_id:
            venue_id = venue_service.get_active_venue()["id"]

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
        promo_key = (promo_code or "").strip().upper()
        promos = db.promos
        if promo_key and promo_key in promos:
            promo = promos[promo_key]
            if promo["active"] and promo["current_uses"] < promo["max_uses"]:
                discount = subtotal * (promo["discount_pct"] / 100.0)
                db.increment_promo_use(promo_key)
                
        total = max(0.0, subtotal - discount)
        
        order_payload = {
            "table_number": table_number,
            "items": order_items,
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "total": round(total, 2),
            "venue_id": venue_id,
            "notes": notes or ""
        }
        
        order = db.add_order(order_payload)
        kds_service.publish_event("kds_update", {
            "action": "ORDER_CREATED",
            "order_id": order["id"],
            "tv": kds_service.get_tv_display_status()
        })
        return order



qr_ordering_service = QROrderingModule()
