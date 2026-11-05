"""
Navy & Brass UK Hospitality UI Suite (Fraunces + Inter, Flat Colour Blocks, Zero Gradients, Zero Emoji, 44px Accessibility Targets).
Loads the unified HTML template from uk_blueprint_suite.html and renders dedicated pages for each route.
"""

import os
import re

_TEMPLATE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "uk_blueprint_suite.html")
)

def _load_template() -> str:
    if os.path.exists(_TEMPLATE_PATH):
        with open(_TEMPLATE_PATH, "r", encoding="utf-8") as _f:
            return _f.read()
    return "<!-- Template not found -->"

NAVY_BRASS_SUITE_HTML = _load_template()

def render_navy_brass_page(page_name: str = "all") -> str:
    """
    Renders dedicated standalone page or full suite with appropriate active navigation state.
    Supported page_name:
      'landing', 'menu', 'kitchen', 'today', 'till', 'reservations', 'stock', 'staff', 'settings', 'all'
    """
    html = _load_template()
    alias_map = {
        "guest": "menu",
        "order": "menu",
        "kds": "kitchen",
        "tv": "kitchen",
        "owner": "today",
        "dashboard": "today",
        "pos": "till",
        "terminal": "till",
        "bookings": "reservations",
        "cellar": "stock",
        "rota": "staff",
        "printers": "settings",
        "reliability": "settings"
    }
    canonical = alias_map.get(page_name.lower(), page_name.lower())
    
    target_data_page = canonical
    if target_data_page == "all":
        target_data_page = "landing"
    elif target_data_page == "menu":
        target_data_page = "guest"
    elif target_data_page == "today":
        target_data_page = "owner"
        
    # Safely activate matching nav button in HTML if present without corrupting scripts
    html = re.sub(r'(<button[^>]*class="[^"]*)\bactive\b([^"]*"[^>]*>)', r'\1\2', html)
    html = re.sub(rf'(<button[^>]*data-page="{target_data_page}"[^>]*class="[^"]*)(")', r'\1 active\2', html)
    
    if canonical != "all":
        section_id_map = {
            "landing": "nb-screen-landing",
            "menu": "nb-screen-guest",
            "kitchen": "nb-screen-kitchen",
            "today": "nb-screen-owner",
            "till": "nb-screen-till",
            "reservations": "nb-screen-reservations",
            "stock": "nb-screen-stock",
            "staff": "nb-screen-staff",
            "settings": "nb-screen-settings",
        }
        active_id = section_id_map.get(canonical)
        if active_id:
            hide_css = f"<style>#navyBrassShowcaseRoot .nb-screen-section {{ display: none !important; }} #navyBrassShowcaseRoot #{active_id} {{ display: block !important; }}</style>"
            html = html.replace("</head>", f"{hide_css}\n</head>")
            
    return html
