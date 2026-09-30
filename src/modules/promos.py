from typing import Dict, Optional
from src.core.db import db

class PromoModule:
    """
    Targeted Promo Codes & Discounts Module
    Manages promotional campaigns and usage limits for off-peak demand generation.
    """
    def create_promo(self, code: str, discount_pct: float, max_uses: int) -> dict:
        code_upper = code.strip().upper()
        promo = {
            "code": code_upper,
            "discount_pct": discount_pct,
            "max_uses": max_uses,
            "current_uses": 0,
            "active": True
        }
        db.promos[code_upper] = promo
        return promo

    def validate_promo(self, code: str) -> Optional[dict]:
        code_upper = code.strip().upper()
        promo = db.promos.get(code_upper)
        if promo and promo["active"] and promo["current_uses"] < promo["max_uses"]:
            return promo
        return None

promo_service = PromoModule()
