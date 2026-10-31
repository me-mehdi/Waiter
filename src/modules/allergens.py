from typing import List, Dict, Optional
from src.core.db import db
from src.core.translation import translator
from src.core.config import Config

class AllergenModule:
    """
    Allergen & Dietary Filter Module
    Provides dynamic menu filtering by dietary requirements (Vegan, Vegetarian, Halal, Gluten-Free) and allergen exclusions (Gluten, Dairy, Eggs, Nuts, Fish).
    """
    ALLERGEN_CATALOG = ["gluten", "dairy", "eggs", "nuts", "fish", "pork"]
    DIETARY_CATALOG = ["vegan", "vegetarian", "halal", "gluten-free"]

    def get_filtered_menu(
        self,
        language: str = "en",
        currency: str = "GBP",
        dietary_filter: Optional[str] = None,
        exclude_allergens: Optional[List[str]] = None
    ) -> List[dict]:
        all_items = list(db.menu_items.values())
        filtered = []

        if exclude_allergens:
            exclude_set = {a.lower().strip() for a in exclude_allergens if a.strip()}
        else:
            exclude_set = set()

        for item in all_items:
            item_allergens = set(item.get("allergens", []))
            item_dietary = set(item.get("dietary", []))

            # Exclusion check
            if exclude_set and (item_allergens & exclude_set):
                continue

            # Dietary requirement check
            if dietary_filter and dietary_filter.lower() != "all":
                target_diet = dietary_filter.lower().strip()
                if target_diet not in item_dietary:
                    continue

            translated = translator.translate_item(item, language)
            base_price = item["price"]
            converted_price = Config.convert_price(base_price, currency)
            symbol = Config.CURRENCY_SYMBOLS.get(currency.upper(), "£")

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
            translated["allergens"] = item.get("allergens", [])
            translated["dietary"] = item.get("dietary", [])
            translated["alcohol"] = item["id"] in Config.ALCOHOL_ITEM_IDS

            filtered.append(translated)

        return filtered

allergen_service = AllergenModule()
