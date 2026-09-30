import os

class Config:
    PROJECT_NAME = "The Waiter"
    MARKET = "UK"
    DEFAULT_CURRENCY = "GBP"
    CURRENCY_SYMBOL = "£"
    SUPPORTED_LANGUAGES = ["en", "fr", "ar"]
    DEFAULT_LANGUAGE = "en"
    
    # Operational thresholds
    TARGET_UPSELL_RATIO = 0.15  # 15% increase in ATV target
    TARGET_REV_PASH_GROWTH = 0.20  # 20% growth target
    
    SECRET_KEY = os.environ.get("SECRET_KEY", "waiter-secret-key-uk-2026")
