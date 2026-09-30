import os
from typing import Dict

class Config:
    PROJECT_NAME = "The Waiter"
    MARKET = "UK"
    
    DEFAULT_CURRENCY = "GBP"
    SUPPORTED_CURRENCIES = ["GBP", "EUR", "USD"]
    CURRENCY_SYMBOLS = {
        "GBP": "£",
        "EUR": "€",
        "USD": "$"
    }
    EXCHANGE_RATES = {
        "GBP": 1.00,
        "EUR": 1.18,
        "USD": 1.28
    }
    TAX_RATES = {
        "GBP": 0.20,
        "EUR": 0.19,
        "USD": 0.08875
    }
    TAX_LABELS = {
        "GBP": "UK VAT (20%)",
        "EUR": "EU VAT (19%)",
        "USD": "US Sales Tax (8.875%)"
    }

    SUPPORTED_LANGUAGES = ["en", "fr", "ar"]
    DEFAULT_LANGUAGE = "en"
    
    TARGET_UPSELL_RATIO = 0.15
    TARGET_REV_PASH_GROWTH = 0.20
    
    SECRET_KEY = os.environ.get("SECRET_KEY", "waiter-secret-key-uk-2026")

    @classmethod
    def convert_price(cls, amount_gbp: float, target_currency: str) -> float:
        rate = cls.EXCHANGE_RATES.get(target_currency.upper(), 1.0)
        return round(amount_gbp * rate, 2)

    @classmethod
    def format_price(cls, amount_gbp: float, target_currency: str = "GBP") -> str:
        curr = target_currency.upper()
        symbol = cls.CURRENCY_SYMBOLS.get(curr, "£")
        converted = cls.convert_price(amount_gbp, curr)
        return f"{symbol}{converted:.2f}"
