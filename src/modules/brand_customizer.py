from typing import Dict, Any
from src.core.db import db

class BrandCustomizerModule:
    """
    White-Label Brand & Theme Customizer Module for 'The Waiter'
    Manages restaurant logo, primary/accent brand colors, typography, guest welcome messages, and table service controls.
    """
    DEFAULT_CONFIG = {
        "brand_name": "The Waiter",
        "store_subheading": "Covent Garden Flagship (UK)",
        "logo_icon": "",
        "logo_image_url": "",
        "primary_color": "#0f1520",
        "header_bg": "#0f1520",
        "accent_color": "#c8a86b",
        "hero_accent": "#c8a86b",
        "font_family": "Fraunces",
        "guest_welcome_message": "Scan, browse and order from your table.",
        "call_waiter_text": "Call waiter",
        "show_allergens": True,
        "default_tip_percentage": 12.5
    }

    def __init__(self):
        if "brand_config" not in db.custom_settings:
            db.custom_settings["brand_config"] = dict(self.DEFAULT_CONFIG)

    def get_config(self) -> Dict[str, Any]:
        return db.custom_settings.get("brand_config", self.DEFAULT_CONFIG)

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        current = self.get_config()
        for key, value in updates.items():
            if key in self.DEFAULT_CONFIG:
                current[key] = value
        db.custom_settings["brand_config"] = current
        return current

brand_customizer_service = BrandCustomizerModule()
