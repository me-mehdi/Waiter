"""
Navy & Brass UK Hospitality UI Suite (Fraunces + Inter, Flat Colour Blocks, Zero Gradients, Zero Emoji, 44px Accessibility Targets).
Loads the unified HTML template from uk_blueprint_suite.html.
"""

import os

_TEMPLATE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "uk_blueprint_suite.html")
)

if os.path.exists(_TEMPLATE_PATH):
    with open(_TEMPLATE_PATH, "r", encoding="utf-8") as _f:
        NAVY_BRASS_SUITE_HTML = _f.read()
else:
    NAVY_BRASS_SUITE_HTML = "<!-- Template not found -->"
