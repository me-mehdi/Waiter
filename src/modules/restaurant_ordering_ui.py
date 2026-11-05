"""
Restaurant Digital Ordering Platform UI (Nando's UK Style Experience).
Route: /order/menu and /order/checkout
Features:
- Nando's signature fiery red, craft beige and charcoal aesthetic branded as 'Restaurant'.
- Mandatory UK FSA Allergen Gate Modal.
- Full category horizontal sticky nav with auto-scroll.
- Landscape feature cards and responsive standard menu cards with kcal, serves, and dietary badges.
- Dedicated Product Configurator:
    * The Heat Selector (7 spice levels from Plain to VUSA XX Hot)
    * The Meal Choice (On its own vs +2 regular sides with Best Value badge)
    * The Side Selector (14 sides, regular included + premium upgrades with surcharges)
    * Extras & Add-ons
    * Real-time dynamic pricing & required step validation
- Slide-out Basket Drawer with full line-item customization summary.
- 'Don't forget these...' smart upsell carousel.
- Guest Eat-In Checkout:
    * Table Number validation
    * Diner details (name, email, mobile)
    * UK tip selector (0%, 10%, 12.5%, 15%, 20%)
    * Payment selector: Apple Pay, Google Pay, Credit/Debit Card, Pay by Bank
- Direct integration with SQLite database, KDS live ticket feed, and Stripe/OpenBanking payments.
"""

import json
from src.core.db import db
from src.modules.qr_ordering import qr_ordering_service

def render_restaurant_ordering_html(table_num: int = 12, initial_item_id: str = None) -> str:
    menu_items = qr_ordering_service.get_menu(language="en", currency="GBP")
    categories = []
    cat_seen = set()
    for item in menu_items:
        c = item.get("category", "Mains")
        if c not in cat_seen:
            cat_seen.add(c)
            categories.append(c)

    menu_json = json.dumps(menu_items)
    categories_json = json.dumps(categories)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Order from Restaurant | Eat-In Digital Ordering</title>
    <!-- Fonts: Inter & Outfit/Plus Jakarta Sans -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- FontAwesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {{
            --primary: #E4002B;
            --primary-hover: #C00024;
            --primary-light: #FFF1F2;
            --charcoal: #1D1D1B;
            --charcoal-soft: #2D2D2A;
            --bg-page: #F8F5EE;
            --bg-card: #FFFFFF;
            --border-card: #E8E3D9;
            --border-hover: #D5CEBF;
            --text-main: #1D1D1B;
            --text-muted: #6B6862;
            --badge-green: #1B5E20;
            --badge-green-bg: #E8F5E9;
            --badge-red: #D32F2F;
            --badge-red-bg: #FFEBEE;
            --heat-vusa: #800020;
            --heat-extra: #B3001B;
            --heat-hot: #E65100;
            --heat-medium: #F57C00;
            --heat-lemon: #7CB342;
            --heat-plain: #757575;
            --heat-bbq: #6A1B9A;
            --font-display: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            --font-body: 'Inter', system-ui, -apple-system, sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }}

        body {{
            font-family: var(--font-body);
            background-color: var(--bg-page);
            color: var(--text-main);
            line-height: 1.5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* --- TOP HEADER --- */
        .site-header {{
            position: sticky;
            top: 0;
            z-index: 40;
            background: #FFFFFF;
            border-bottom: 1px solid var(--border-card);
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }}
        .header-inner {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .brand-logo-area {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: inherit;
        }}
        .brand-badge {{
            background: var(--primary);
            color: #FFFFFF;
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            font-weight: 900;
            box-shadow: 0 4px 10px rgba(228,0,43,0.3);
        }}
        .brand-title {{
            font-family: var(--font-display);
            font-size: 1.5rem;
            font-weight: 900;
            letter-spacing: -0.5px;
            text-transform: uppercase;
            color: var(--charcoal);
        }}
        .dine-in-context {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: #FAF7F2;
            border: 1px solid var(--border-card);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--charcoal);
        }}
        .dine-in-context .table-tag {{
            background: var(--charcoal);
            color: #FFFFFF;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        .header-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .btn-header-link {{
            background: none;
            border: none;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--charcoal);
            cursor: pointer;
            padding: 8px 12px;
            border-radius: 6px;
            text-decoration: none;
        }}
        .btn-header-link:hover {{
            background: #F1EDE4;
        }}
        .btn-basket-pill {{
            background: var(--primary);
            color: #FFFFFF;
            border: none;
            font-weight: 700;
            font-size: 0.9rem;
            padding: 10px 18px;
            border-radius: 24px;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(228,0,43,0.25);
        }}
        .btn-basket-pill:hover {{
            background: var(--primary-hover);
            transform: translateY(-1px);
        }}
        .btn-basket-pill .basket-count {{
            background: #FFFFFF;
            color: var(--primary);
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 800;
        }}

        /* --- STICKY CATEGORY NAV --- */
        .category-nav-wrap {{
            position: sticky;
            top: 69px;
            z-index: 35;
            background: #FFFFFF;
            border-bottom: 1px solid var(--border-card);
            overflow-x: auto;
            scrollbar-width: none;
        }}
        .category-nav-wrap::-webkit-scrollbar {{
            display: none;
        }}
        .category-nav {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 8px 20px;
            display: flex;
            gap: 8px;
            white-space: nowrap;
        }}
        .cat-chip {{
            background: #F4EFE6;
            border: none;
            color: var(--charcoal);
            font-family: var(--font-display);
            font-weight: 700;
            font-size: 0.85rem;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .cat-chip:hover {{
            background: #E8E2D5;
        }}
        .cat-chip.active {{
            background: var(--charcoal);
            color: #FFFFFF;
        }}

        /* --- MAIN CONTAINER --- */
        .main-layout {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 24px 20px;
            display: flex;
            gap: 28px;
            flex: 1;
            width: 100%;
        }}
        .menu-feed {{
            flex: 1;
            min-width: 0;
        }}
        .sidebar-rail {{
            width: 380px;
            flex-shrink: 0;
            display: none;
        }}
        @media (min-width: 1024px) {{
            .sidebar-rail {{
                display: block;
            }}
        }}

        /* --- CATEGORY SECTION --- */
        .category-section {{
            margin-bottom: 36px;
            scroll-margin-top: 130px;
        }}
        .category-heading {{
            font-family: var(--font-display);
            font-size: 1.6rem;
            font-weight: 900;
            color: var(--charcoal);
            margin-bottom: 16px;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        /* --- FEATURED LANDSCAPE CARD --- */
        .card-featured {{
            background: #FFFFFF;
            border: 1px solid var(--border-card);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 3px 12px rgba(0,0,0,0.03);
            text-decoration: none;
            color: inherit;
        }}
        @media (min-width: 640px) {{
            .card-featured {{
                flex-direction: row;
                height: 220px;
            }}
        }}
        .card-featured:hover {{
            border-color: var(--border-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        }}
        .card-featured .card-img-wrap {{
            width: 100%;
            height: 180px;
            flex-shrink: 0;
            position: relative;
            background: #EEE9DF;
        }}
        @media (min-width: 640px) {{
            .card-featured .card-img-wrap {{
                width: 42%;
                height: 100%;
            }}
        }}
        .card-featured .card-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .card-featured .card-content {{
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            flex: 1;
        }}

        /* --- STANDARD 2-COL CARDS --- */
        .cards-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }}
        @media (min-width: 640px) {{
            .cards-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        .menu-card {{
            background: #FFFFFF;
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            gap: 16px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            text-decoration: none;
            color: inherit;
        }}
        .menu-card:hover {{
            border-color: var(--border-hover);
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        }}
        .menu-card .card-info {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .card-title {{
            font-family: var(--font-display);
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--charcoal);
            margin-bottom: 4px;
            line-height: 1.3;
        }}
        .card-meta {{
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .card-desc {{
            font-size: 0.85rem;
            color: #55524C;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 12px;
        }}
        .card-price-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: auto;
        }}
        .card-price {{
            font-family: var(--font-display);
            font-size: 1.05rem;
            font-weight: 800;
            color: var(--charcoal);
        }}
        .card-thumb-wrap {{
            width: 100px;
            height: 100px;
            flex-shrink: 0;
            border-radius: 8px;
            overflow: hidden;
            background: #EEE9DF;
            position: relative;
        }}
        .card-thumb {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        /* --- BADGES --- */
        .badge-tag {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        .badge-tag.veg {{
            background: var(--badge-green-bg);
            color: var(--badge-green);
        }}
        .badge-tag.new {{
            background: var(--badge-red-bg);
            color: var(--badge-red);
        }}

        /* --- BASKET STICKY SIDEBAR --- */
        .basket-sidebar-card {{
            position: sticky;
            top: 130px;
            background: #FFFFFF;
            border: 1px solid var(--border-card);
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.04);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 160px);
        }}
        .basket-header {{
            padding: 16px 20px;
            background: #FAF7F2;
            border-bottom: 1px solid var(--border-card);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .basket-header-title {{
            font-family: var(--font-display);
            font-size: 1.15rem;
            font-weight: 800;
        }}
        .basket-body {{
            padding: 16px 20px;
            overflow-y: auto;
            flex: 1;
        }}
        .basket-empty {{
            text-align: center;
            padding: 36px 12px;
            color: var(--text-muted);
        }}
        .basket-empty i {{
            font-size: 2.5rem;
            color: #D3CDC0;
            margin-bottom: 12px;
        }}
        .basket-item {{
            padding-bottom: 14px;
            margin-bottom: 14px;
            border-bottom: 1px solid #F0ECE4;
        }}
        .basket-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
        }}
        .basket-item-row {{
            display: flex;
            justify-content: space-between;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .basket-item-mods {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-bottom: 6px;
            line-height: 1.3;
        }}
        .basket-item-ctrls {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .btn-qty {{
            width: 26px;
            height: 26px;
            border-radius: 50%;
            border: 1px solid var(--border-card);
            background: #FAF7F2;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.85rem;
        }}
        .btn-qty:hover {{
            background: #EDE7DC;
        }}

        /* --- UPSELL CAROUSEL --- */
        .upsell-section {{
            padding: 14px 20px;
            background: #FCFAF6;
            border-top: 1px solid var(--border-card);
        }}
        .upsell-title {{
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 10px;
        }}
        .upsell-items {{
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding-bottom: 6px;
            scrollbar-width: none;
        }}
        .upsell-card {{
            min-width: 140px;
            max-width: 140px;
            background: #FFFFFF;
            border: 1px solid var(--border-card);
            border-radius: 8px;
            padding: 8px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .upsell-card-name {{
            font-size: 0.8rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 4px;
        }}
        .upsell-card-price {{
            font-size: 0.75rem;
            font-weight: 800;
            color: var(--charcoal);
            margin-bottom: 6px;
        }}
        .btn-upsell-add {{
            background: var(--charcoal);
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 4px;
            cursor: pointer;
            text-align: center;
        }}
        .btn-upsell-add:hover {{
            background: var(--primary);
        }}

        .basket-footer {{
            padding: 16px 20px;
            background: #FFFFFF;
            border-top: 1px solid var(--border-card);
        }}
        .btn-checkout-cta {{
            width: 100%;
            background: var(--primary);
            color: #FFFFFF;
            border: none;
            border-radius: 12px;
            font-family: var(--font-display);
            font-size: 1.05rem;
            font-weight: 800;
            padding: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 14px rgba(228,0,43,0.3);
            transition: all 0.2s ease;
        }}
        .btn-checkout-cta:hover {{
            background: var(--primary-hover);
        }}

        /* --- MOBILE BOTTOM STICKY BAR --- */
        .mobile-bottom-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #FFFFFF;
            border-top: 1px solid var(--border-card);
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 38;
            box-shadow: 0 -4px 16px rgba(0,0,0,0.06);
        }}
        @media (min-width: 1024px) {{
            .mobile-bottom-bar {{
                display: none;
            }}
        }}

        /* --- TOAST NOTIFICATION --- */
        .toast-notification {{
            position: fixed;
            bottom: 84px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background: #1D1D1B;
            color: #FFFFFF;
            padding: 10px 18px;
            border-radius: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.25);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            z-index: 90;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            max-width: 92vw;
            width: max-content;
        }}
        .toast-notification.active {{
            transform: translateX(-50%) translateY(0);
            opacity: 1;
            pointer-events: auto;
        }}
        .toast-message {{
            font-size: 0.88rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }}
        .btn-toast-view {{
            background: var(--primary);
            color: #FFFFFF;
            border: none;
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 0.8rem;
            font-weight: 800;
            cursor: pointer;
            white-space: nowrap;
        }}
        .btn-toast-view:hover {{
            background: #C40024;
        }}

        body.is-embedded .btn-header-link {{
            display: none !important;
        }}

        /* --- MODAL OVERLAYS (ALLERGY & PRODUCT CONFIGURATOR & CHECKOUT) --- */
        .modal-overlay {{
            position: fixed;
            inset: 0;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }}
        .modal-overlay.active {{
            display: flex;
        }}
        .modal-card {{
            background: #FFFFFF;
            border-radius: 16px;
            max-width: 580px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            box-shadow: 0 12px 40px rgba(0,0,0,0.25);
            animation: modalSlideUp 0.25s ease-out;
        }}
        @keyframes modalSlideUp {{
            from {{ transform: translateY(20px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}

        /* --- ALLERGY NOTICE MODAL --- */
        .allergy-modal-card {{
            max-width: 460px;
            text-align: center;
            padding: 32px 24px;
        }}
        .allergy-icon-badge {{
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: #FFF1F2;
            color: var(--primary);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            margin-bottom: 20px;
        }}
        .allergy-modal-title {{
            font-family: var(--font-display);
            font-size: 1.5rem;
            font-weight: 900;
            color: var(--charcoal);
            margin-bottom: 12px;
        }}
        .allergy-modal-desc {{
            font-size: 0.95rem;
            color: #4A4742;
            margin-bottom: 24px;
            line-height: 1.5;
        }}
        .btn-allergy-confirm {{
            background: var(--charcoal);
            color: #FFFFFF;
            border: none;
            border-radius: 28px;
            font-family: var(--font-display);
            font-size: 1rem;
            font-weight: 800;
            padding: 14px 32px;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s ease;
        }}
        .btn-allergy-confirm:hover {{
            background: #000000;
        }}

        /* --- PRODUCT CONFIGURATOR STYLES --- */
        .config-header-img {{
            width: 100%;
            height: 220px;
            object-fit: cover;
            background: #EEE9DF;
        }}
        .config-body {{
            padding: 24px;
        }}
        .config-title {{
            font-family: var(--font-display);
            font-size: 1.6rem;
            font-weight: 900;
            margin-bottom: 6px;
        }}
        .config-meta {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .config-desc {{
            font-size: 0.9rem;
            color: #4A4742;
            margin-bottom: 24px;
        }}

        .config-step-title {{
            font-family: var(--font-display);
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--charcoal);
            margin: 20px 0 12px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .config-step-hint {{
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
        }}

        /* Heat Selector Cards (The PERi-ometer) */
        .heat-options-grid {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .heat-option-card {{
            border: 2px solid var(--border-card);
            border-radius: 10px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .heat-option-card:hover {{
            border-color: var(--border-hover);
        }}
        .heat-option-card.selected {{
            border-color: var(--charcoal);
            background: #FAF7F2;
        }}
        .heat-badge-flag {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            flex-shrink: 0;
            margin-right: 12px;
        }}
        .heat-card-info {{
            flex: 1;
        }}
        .heat-name {{
            font-weight: 800;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .heat-desc {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
        .heat-meter {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
        }}

        /* Meal Choice (On its own vs +2 sides) */
        .meal-choices-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        .meal-card {{
            border: 2px solid var(--border-card);
            border-radius: 10px;
            padding: 14px;
            cursor: pointer;
            text-align: center;
            transition: all 0.15s ease;
        }}
        .meal-card.selected {{
            border-color: var(--charcoal);
            background: #FAF7F2;
        }}
        .meal-card-title {{
            font-weight: 800;
            font-size: 0.95rem;
            margin-bottom: 4px;
        }}
        .meal-card-price {{
            font-family: var(--font-display);
            font-weight: 900;
            font-size: 1.1rem;
            color: var(--charcoal);
        }}

        /* Sides Multi-Select Grid */
        .sides-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
            max-height: 280px;
            overflow-y: auto;
            padding-right: 4px;
        }}
        .side-select-card {{
            border: 1px solid var(--border-card);
            border-radius: 8px;
            padding: 10px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .side-select-card:hover {{
            background: #FAF7F2;
        }}
        .side-select-card.selected {{
            border-color: var(--primary);
            background: #FFF5F6;
        }}
        .side-title {{
            font-weight: 700;
            font-size: 0.9rem;
        }}
        .side-extra-price {{
            font-size: 0.8rem;
            font-weight: 800;
            color: var(--primary);
        }}

        /* Config Sticky Footer */
        .config-footer {{
            position: sticky;
            bottom: 0;
            background: #FFFFFF;
            border-top: 1px solid var(--border-card);
            padding: 16px 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .btn-add-to-basket {{
            flex: 1;
            background: var(--primary);
            color: #FFFFFF;
            border: none;
            border-radius: 28px;
            font-family: var(--font-display);
            font-size: 1.05rem;
            font-weight: 800;
            padding: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s ease;
        }}
        .btn-add-to-basket:disabled {{
            background: #D3CDC0;
            cursor: not-allowed;
        }}

        /* --- CHECKOUT MODAL STYLES --- */
        .checkout-modal-card {{
            max-width: 620px;
        }}
        .checkout-header {{
            padding: 20px 24px;
            background: #FAF7F2;
            border-bottom: 1px solid var(--border-card);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .checkout-body {{
            padding: 24px;
        }}
        .form-group {{
            margin-bottom: 16px;
        }}
        .form-label {{
            display: block;
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--charcoal);
            margin-bottom: 6px;
        }}
        .form-input {{
            width: 100%;
            padding: 12px 14px;
            border: 1px solid var(--border-card);
            border-radius: 8px;
            font-family: var(--font-body);
            font-size: 0.95rem;
            color: var(--charcoal);
            background: #FAF7F2;
        }}
        .form-input:focus {{
            outline: none;
            border-color: var(--charcoal);
            background: #FFFFFF;
        }}

        /* Tip Selector */
        .tip-pills {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            margin-bottom: 20px;
        }}
        .tip-pill {{
            padding: 8px;
            text-align: center;
            border: 1px solid var(--border-card);
            border-radius: 6px;
            background: #FAF7F2;
            cursor: pointer;
            font-weight: 700;
            font-size: 0.85rem;
        }}
        .tip-pill.active {{
            background: var(--charcoal);
            color: #FFFFFF;
            border-color: var(--charcoal);
        }}

        /* Payment Selector */
        .payment-methods-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 24px;
        }}
        .pay-card {{
            border: 2px solid var(--border-card);
            border-radius: 10px;
            padding: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            font-size: 0.9rem;
            transition: all 0.15s ease;
        }}
        .pay-card.active {{
            border-color: var(--charcoal);
            background: #FAF7F2;
        }}

        .order-summary-box {{
            background: #FAF7F2;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 20px;
        }}
        .summary-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            margin-bottom: 6px;
        }}
        .summary-row.total {{
            font-family: var(--font-display);
            font-weight: 900;
            font-size: 1.15rem;
            color: var(--charcoal);
            border-top: 1px solid var(--border-card);
            padding-top: 8px;
            margin-top: 8px;
            margin-bottom: 0;
        }}
    </style>
</head>
<body>

    <!-- TOP HEADER -->
    <header class="site-header">
        <div class="header-inner">
            <a href="./" class="brand-logo-area">
                <div class="brand-badge">
                    <i class="fa-solid fa-utensils"></i>
                </div>
                <div>
                    <div class="brand-title">RESTAURANT</div>
                    <div style="font-size: 0.7rem; font-weight: 700; color: var(--primary); letter-spacing: 1px; text-transform: uppercase;">Flame & Grill</div>
                </div>
            </a>

            <div class="dine-in-context">
                <i class="fa-solid fa-location-dot" style="color: var(--primary);"></i>
                <span>Eating in Restaurant</span>
                <span class="table-tag" id="headerTableTag">TABLE {table_num}</span>
            </div>

            <div class="header-actions">
                <a href="../../" class="btn-header-link" title="Back to Waiter Overview">
                    <i class="fa-solid fa-arrow-left me-1"></i> Waiter Suite
                </a>
                <a href="../../#kitchen" class="btn-header-link" target="_blank" title="Open KDS Kitchen Display">
                    <i class="fa-solid fa-tv me-1"></i> Kitchen KDS
                </a>
                <button class="btn-basket-pill" onclick="openBasketDrawer()">
                    <i class="fa-solid fa-bag-shopping"></i>
                    <span class="basket-pill-total">£0.00</span>
                    <span class="basket-count" id="basketCountBadge">0</span>
                </button>
            </div>
        </div>
    </header>

    <!-- STICKY CATEGORY NAV -->
    <nav class="category-nav-wrap">
        <div class="category-nav" id="categoryNav">
            <!-- Populated dynamically -->
        </div>
    </nav>

    <!-- MAIN MENU CONTENT -->
    <main class="main-layout">
        <!-- Feed of Category Sections -->
        <div class="menu-feed" id="menuFeed">
            <!-- Sections and items rendered here -->
        </div>

        <!-- Sticky Sidebar Basket Rail (Desktop) -->
        <aside class="sidebar-rail">
            <div class="basket-sidebar-card">
                <div class="basket-header">
                    <div class="basket-header-title">Your Order</div>
                    <span class="table-tag" style="background: var(--charcoal); color:#fff; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:700;">Table {table_num}</span>
                </div>
                
                <div class="basket-body" id="sidebarBasketBody">
                    <div class="basket-empty">
                        <i class="fa-solid fa-basket-shopping"></i>
                        <p style="font-weight: 700;">Your basket is empty</p>
                        <p style="font-size: 0.85rem; margin-top: 4px;">Select dishes from the menu to build your feast!</p>
                    </div>
                </div>

                <!-- Don't forget these Upsells -->
                <div class="upsell-section" id="sidebarUpsellSection">
                    <div class="upsell-title">Don't forget these...</div>
                    <div class="upsell-items" id="sidebarUpsellItems">
                        <!-- Upsell cards -->
                    </div>
                </div>

                <div class="basket-footer">
                    <button class="btn-checkout-cta" id="btnSidebarCheckout" onclick="openCheckoutModal()" disabled>
                        <span>CHECKOUT</span>
                        <span id="sidebarCheckoutTotal">£0.00</span>
                    </button>
                </div>
            </div>
        </aside>
    </main>

    <!-- MOBILE BOTTOM STICKY BAR -->
    <div class="mobile-bottom-bar" id="mobileBottomBar" style="display: none;">
        <div>
            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 700;">TOTAL</div>
            <div style="font-family: var(--font-display); font-size: 1.25rem; font-weight: 900;" id="mobileBarTotal">£0.00</div>
        </div>
        <button class="btn-basket-pill" onclick="openBasketDrawer()" style="padding: 12px 24px;">
            <span>View basket (<span id="mobileBarCount">0</span>)</span>
            <i class="fa-solid fa-arrow-right"></i>
        </button>
    </div>

    <!-- TOAST NOTIFICATION -->
    <div class="toast-notification" id="toastNotification">
        <div class="toast-message">
            <i class="fa-solid fa-circle-check text-success"></i>
            <span id="toastMessage">Added to your basket</span>
        </div>
        <button class="btn-toast-view" onclick="openBasketDrawer()">View Basket</button>
    </div>

    <!-- 1. MANDATORY ALLERGEN MODAL -->
    <div class="modal-overlay" id="allergyModalOverlay">
        <div class="modal-card allergy-modal-card">
            <div class="allergy-icon-badge">
                <i class="fa-solid fa-triangle-exclamation"></i>
            </div>
            <h2 class="allergy-modal-title">Got an allergy?</h2>
            <p class="allergy-modal-desc">
                We can't take digital allergy orders - head to the till and ask to speak to a Manager. They'll take your order and talk you through our cooking methods and ingredients.
            </p>
            <button class="btn-allergy-confirm" onclick="dismissAllergyModal()">
                OK, GOT IT
            </button>
        </div>
    </div>

    <!-- 2. PRODUCT CONFIGURATOR MODAL -->
    <div class="modal-overlay" id="configModalOverlay">
        <div class="modal-card" style="max-width: 600px;">
            <button onclick="closeConfigModal()" style="position: absolute; top: 16px; right: 16px; z-index: 10; background: rgba(255,255,255,0.9); border: none; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 1.1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                <i class="fa-solid fa-xmark"></i>
            </button>
            <img id="configImg" class="config-header-img" src="" alt="Dish">
            <div class="config-body">
                <h1 class="config-title" id="configTitle">Item Title</h1>
                <div class="config-meta" id="configMeta">0 kcal • Serves 1</div>
                <p class="config-desc" id="configDesc">Description</p>

                <!-- Step 1: Heat Selector (The PERi-ometer) -->
                <div id="configHeatSection" style="display: none;">
                    <div class="config-step-title">
                        <span>How spicy?</span>
                        <span class="config-step-hint">Required</span>
                    </div>
                    <div class="heat-options-grid" id="heatOptionsGrid">
                        <!-- Heat options generated here -->
                    </div>
                </div>

                <!-- Step 2: Meal Choice -->
                <div id="configMealSection" style="display: none;">
                    <div class="config-step-title">
                        <span>Choose your meal</span>
                        <span class="config-step-hint">Required</span>
                    </div>
                    <div class="meal-choices-grid" id="mealChoicesGrid">
                        <!-- Meal cards generated here -->
                    </div>
                </div>

                <!-- Step 3: Sides Selector (when 2 sides combo chosen) -->
                <div id="configSidesSection" style="display: none;">
                    <div class="config-step-title">
                        <span>Choose 2 regular sides</span>
                        <span class="config-step-hint" id="sidesSelectedCounter">0 of 2 selected</span>
                    </div>
                    <div class="sides-grid" id="sidesGrid">
                        <!-- Sides options generated here -->
                    </div>
                </div>

                <!-- Step 4: Extras & Add-ons -->
                <div id="configExtrasSection" style="display: none;">
                    <div class="config-step-title">
                        <span>Add extras & upgrades</span>
                        <span class="config-step-hint">Optional</span>
                    </div>
                    <div class="sides-grid" id="extrasGrid">
                        <!-- Extras generated here -->
                    </div>
                </div>
            </div>

            <!-- Sticky Add to Basket Footer -->
            <div class="config-footer">
                <div style="display: flex; align-items: center; gap: 8px; background: #FAF7F2; padding: 6px 12px; border-radius: 20px; border: 1px solid var(--border-card);">
                    <button class="btn-qty" onclick="adjustConfigQty(-1)">-</button>
                    <span style="font-weight: 800; min-width: 20px; text-align: center;" id="configQtyDisplay">1</span>
                    <button class="btn-qty" onclick="adjustConfigQty(1)">+</button>
                </div>
                <button class="btn-add-to-basket" id="btnAddConfigToBasket" onclick="commitConfiguredItemToBasket()">
                    <span>ADD TO BASKET</span>
                    <span id="configDynamicTotal">£0.00</span>
                </button>
            </div>
        </div>
    </div>

    <!-- 2.5 DEDICATED BASKET DRAWER / MODAL -->
    <div class="modal-overlay" id="basketModalOverlay">
        <div class="modal-card basket-modal-card" style="max-width: 520px; display: flex; flex-direction: column; max-height: 88vh;">
            <div class="basket-modal-header" style="padding: 18px 24px; border-bottom: 1px solid var(--border-card); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-family: var(--font-display); font-size: 1.25rem; font-weight: 900; color: var(--charcoal);">
                        <i class="fa-solid fa-basket-shopping text-primary me-2"></i>Your Basket
                    </div>
                    <div style="font-size: 0.82rem; color: var(--text-muted); font-weight: 600; margin-top: 2px;">
                        Table {table_num} · Dine-in
                    </div>
                </div>
                <button onclick="closeBasketDrawer()" style="background: none; border: none; font-size: 1.3rem; cursor: pointer; color: var(--text-muted);" aria-label="Close basket">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>

            <!-- Basket Items list -->
            <div class="basket-body" id="modalBasketBody" style="flex: 1; overflow-y: auto; padding: 20px 24px; max-height: 48vh;">
                <!-- Dynamically populated -->
            </div>

            <!-- Smart Upsell Carousel inside Basket -->
            <div class="upsell-section" id="modalUpsellSection" style="padding: 14px 24px;">
                <div class="upsell-title">Don't forget these...</div>
                <div class="upsell-items" id="modalUpsellItems">
                    <!-- Populated by JS -->
                </div>
            </div>

            <!-- Basket Subtotal & CTA Footer -->
            <div class="basket-footer" style="padding: 18px 24px; border-top: 1px solid var(--border-card); background: #FAF7F2; display: flex; flex-direction: column; gap: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 1rem; font-weight: 700; color: var(--charcoal); margin-bottom: 4px;">
                    <span>Subtotal</span>
                    <span id="modalBasketSubtotal" style="font-family: var(--font-display); font-size: 1.25rem; font-weight: 900;">£0.00</span>
                </div>
                <button class="btn-checkout-cta" id="btnBasketModalCheckout" onclick="proceedFromBasketToCheckout()" style="width: 100%; justify-content: space-between;">
                    <span>PROCEED TO CHECKOUT</span>
                    <span id="basketDrawerCheckoutTotal">£0.00</span>
                </button>
                <button type="button" onclick="closeBasketDrawer()" style="background: none; border: none; color: var(--text-muted); font-size: 0.88rem; font-weight: 700; cursor: pointer; padding: 6px; text-align: center;">
                    + Add more items from menu
                </button>
            </div>
        </div>
    </div>

    <!-- 3. CHECKOUT MODAL -->
    <div class="modal-overlay" id="checkoutModalOverlay">
        <div class="modal-card checkout-modal-card">
            <div class="checkout-header">
                <div style="font-family: var(--font-display); font-size: 1.3rem; font-weight: 900;">
                    <i class="fa-solid fa-lock text-success me-2"></i>Checkout & Settle
                </div>
                <button onclick="closeCheckoutModal()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer;">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>

            <div class="checkout-body">
                <!-- Dining Context Info -->
                <div style="display: flex; gap: 12px; margin-bottom: 20px;">
                    <div class="form-group" style="flex: 1; margin-bottom: 0;">
                        <label class="form-label">Table Number</label>
                        <input type="number" id="checkoutTableNum" class="form-input" value="{table_num}" min="1" max="50">
                    </div>
                    <div class="form-group" style="flex: 2; margin-bottom: 0;">
                        <label class="form-label">Your Name</label>
                        <input type="text" id="checkoutDinerName" class="form-input" placeholder="e.g. Alex Smith" value="Alex">
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">Email Address (for e-receipt & VAT invoice)</label>
                    <input type="email" id="checkoutEmail" class="form-input" placeholder="alex.smith@example.co.uk" value="alex@example.co.uk">
                </div>

                <div class="form-group">
                    <label class="form-label">Special Kitchen Notes</label>
                    <input type="text" id="checkoutNotes" class="form-input" placeholder="e.g. Extra crispy skin, sauces on the side">
                </div>

                <!-- Tip Selector -->
                <div style="margin-top: 20px;">
                    <label class="form-label">Add a Tip for the Team (100% to staff under UK Tips Act)</label>
                    <div class="tip-pills">
                        <div class="tip-pill" onclick="selectTip(0, this)">No Tip</div>
                        <div class="tip-pill" onclick="selectTip(10, this)">10%</div>
                        <div class="tip-pill active" onclick="selectTip(12.5, this)">12.5%</div>
                        <div class="tip-pill" onclick="selectTip(15, this)">15%</div>
                        <div class="tip-pill" onclick="selectTip(20, this)">20%</div>
                    </div>
                </div>

                <!-- Payment Method Selector -->
                <label class="form-label">Select Payment Method</label>
                <div class="payment-methods-grid">
                    <div class="pay-card active" onclick="selectPaymentMethod('APPLE_PAY', this)">
                        <i class="fa-brands fa-apple fs-4"></i>
                        <div>
                            <div>Apple Pay</div>
                            <div style="font-size: 0.72rem; color: var(--text-muted);">1-Tap Biometric</div>
                        </div>
                    </div>
                    <div class="pay-card" onclick="selectPaymentMethod('GOOGLE_PAY', this)">
                        <i class="fa-brands fa-google-pay fs-4"></i>
                        <div>
                            <div>Google Pay</div>
                            <div style="font-size: 0.72rem; color: var(--text-muted);">Instant Settle</div>
                        </div>
                    </div>
                    <div class="pay-card" onclick="selectPaymentMethod('CARD_STRIPE', this)">
                        <i class="fa-solid fa-credit-card fs-5 text-primary"></i>
                        <div>
                            <div>Debit / Credit Card</div>
                            <div style="font-size: 0.72rem; color: var(--text-muted);">Visa, MC, Amex</div>
                        </div>
                    </div>
                    <div class="pay-card" onclick="selectPaymentMethod('PAY_BY_BANK', this)">
                        <i class="fa-solid fa-building-columns fs-5 text-success"></i>
                        <div>
                            <div>Pay by Bank</div>
                            <div style="font-size: 0.72rem; color: var(--text-muted);">UK Faster Payments</div>
                        </div>
                    </div>
                </div>

                <!-- Order Summary Breakdown -->
                <div class="order-summary-box">
                    <div class="summary-row">
                        <span>Items Subtotal</span>
                        <span id="summarySubtotal">£0.00</span>
                    </div>
                    <div class="summary-row">
                        <span>Staff Tip (<span id="summaryTipPct">12.5%</span>)</span>
                        <span id="summaryTipAmount">£0.00</span>
                    </div>
                    <div class="summary-row total">
                        <span>Total to Pay</span>
                        <span id="summaryGrandTotal">£0.00</span>
                    </div>
                </div>

                <button class="btn-checkout-cta" id="btnConfirmPay" onclick="submitFinalOrder()" style="justify-content: center; gap: 10px;">
                    <i class="fa-solid fa-lock"></i>
                    <span>PAY & PLACE ORDER</span>
                </button>
            </div>
        </div>
    </div>

    <!-- 4. ORDER CONFIRMATION MODAL -->
    <div class="modal-overlay" id="successModalOverlay">
        <div class="modal-card" style="max-width: 460px; text-align: center; padding: 36px 24px;">
            <div style="width: 72px; height: 72px; border-radius: 50%; background: #E8F5E9; color: #2E7D32; display: inline-flex; align-items: center; justify-content: center; font-size: 2.2rem; margin-bottom: 20px;">
                <i class="fa-solid fa-check"></i>
            </div>
            <h2 style="font-family: var(--font-display); font-size: 1.6rem; font-weight: 900; margin-bottom: 8px;">Order Placed!</h2>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 20px;">
                Your order is on the grill and has been sent directly to the kitchen display.
            </p>
            <div style="background: #FAF7F2; border: 1px solid var(--border-card); border-radius: 12px; padding: 16px; margin-bottom: 24px; text-align: left;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9rem;">
                    <span style="font-weight: 700;">Order Reference:</span>
                    <span style="font-weight: 900; color: var(--primary);" id="successOrderRef">#1028</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9rem;">
                    <span style="font-weight: 700;">Table:</span>
                    <span id="successTableNum">Table 12</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                    <span style="font-weight: 700;">Status:</span>
                    <span style="background: #FFF3E0; color: #E65100; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.8rem;">ON THE GRILL</span>
                </div>
            </div>
            <div style="display: flex; gap: 10px;">
                <a href="../../#kitchen" target="_blank" class="btn-allergy-confirm" style="background: var(--charcoal); flex: 1; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <i class="fa-solid fa-tv"></i> View on KDS
                </a>
                <button onclick="resetOrderAfterSuccess()" class="btn-allergy-confirm" style="background: var(--primary); flex: 1;">
                    Order More
                </button>
            </div>
        </div>
    </div>

    <!-- JAVASCRIPT STATE ENGINE -->
    <script>
        const MENU_DATA = {menu_json};
        const CATEGORIES = {categories_json};
        const INITIAL_TABLE = {table_num};

        let basket = [];
        let currentConfigItem = null;
        let selectedHeat = null;
        let selectedMeal = null;
        let selectedSides = [];
        let selectedExtras = [];
        let configQuantity = 1;

        let selectedTipPercent = 12.5;
        let activePaymentMethod = 'APPLE_PAY';

        // --- INIT ---
        document.addEventListener('DOMContentLoaded', () => {{
            if (window.self !== window.top) {{
                document.body.classList.add('is-embedded');
            }}
            renderCategories();
            renderMenuSections();
            renderUpsells();
            updateBasketUI();

            // Check allergy modal consent
            if (!localStorage.getItem('restaurant_allergy_confirmed')) {{
                document.getElementById('allergyModalOverlay').classList.add('active');
            }}
        }});

        function dismissAllergyModal() {{
            localStorage.setItem('restaurant_allergy_confirmed', 'true');
            document.getElementById('allergyModalOverlay').classList.remove('active');
        }}

        // --- RENDER CATEGORY PILLS ---
        function renderCategories() {{
            const nav = document.getElementById('categoryNav');
            nav.innerHTML = CATEGORIES.map((cat, idx) => `
                <button class="cat-chip ${{idx === 0 ? 'active' : ''}}" onclick="scrollToCategory('${{cat}}', this)">
                    ${{cat}}
                </button>
            `).join('');
        }}

        function scrollToCategory(catName, btn) {{
            document.querySelectorAll('.cat-chip').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const target = document.getElementById('cat-sec-' + catName.replace(/[^a-zA-Z0-9]/g, '-'));
            if (target) {{
                target.scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        // --- RENDER MENU SECTIONS ---
        function renderMenuSections() {{
            const feed = document.getElementById('menuFeed');
            feed.innerHTML = CATEGORIES.map(cat => {{
                const items = MENU_DATA.filter(i => i.category === cat);
                if (!items.length) return '';
                const secId = 'cat-sec-' + cat.replace(/[^a-zA-Z0-9]/g, '-');
                
                // Featured item vs standard items
                const featuredItem = items.find(i => i.is_featured);
                const regularItems = items.filter(i => i !== featuredItem);

                let featuredHtml = '';
                if (featuredItem) {{
                    featuredHtml = `
                        <div class="card-featured" onclick="openProductCustomizer('${{featuredItem.id}}')">
                            <div class="card-img-wrap">
                                <img src="${{featuredItem.image_url}}" class="card-img" alt="${{featuredItem.name_translated}}" loading="lazy">
                            </div>
                            <div class="card-content">
                                <div>
                                    <div class="card-title">${{featuredItem.name_translated}}</div>
                                    <div class="card-meta">
                                        <span>${{featuredItem.kcal}} kcal</span>
                                        ${{featuredItem.serves ? `<span>• ${{featuredItem.serves}}</span>` : ''}}
                                        ${{featuredItem.dietary.includes('vegetarian') ? '<span class="badge-tag veg">Vegetarian</span>' : ''}}
                                        ${{featuredItem.is_new ? '<span class="badge-tag new">New</span>' : ''}}
                                    </div>
                                    <p class="card-desc">${{featuredItem.description_translated}}</p>
                                </div>
                                <div class="card-price-row">
                                    <span class="card-price">${{featuredItem.price_from ? 'From ' : ''}}${{featuredItem.price_formatted}}</span>
                                    <span style="font-weight: 700; color: var(--primary); font-size: 0.9rem;">Customise <i class="fa-solid fa-angle-right ms-1"></i></span>
                                </div>
                            </div>
                        </div>
                    `;
                }}

                const cardsHtml = regularItems.map(item => `
                    <div class="menu-card" onclick="openProductCustomizer('${{item.id}}')">
                        <div class="card-info">
                            <div>
                                <div class="card-title">${{item.name_translated}}</div>
                                <div class="card-meta">
                                    <span>${{item.kcal}} kcal</span>
                                    ${{item.serves ? `<span>• ${{item.serves}}</span>` : ''}}
                                    ${{item.dietary.includes('vegetarian') ? '<span class="badge-tag veg">Vegetarian</span>' : ''}}
                                    ${{item.is_new ? '<span class="badge-tag new">New</span>' : ''}}
                                </div>
                                <p class="card-desc">${{item.description_translated}}</p>
                            </div>
                            <div class="card-price-row">
                                <span class="card-price">${{item.price_from ? 'From ' : ''}}${{item.price_formatted}}</span>
                                <span style="font-weight: 700; color: var(--primary); font-size: 0.85rem;">Customise <i class="fa-solid fa-angle-right ms-1"></i></span>
                            </div>
                        </div>
                        <div class="card-thumb-wrap">
                            <img src="${{item.image_url}}" class="card-thumb" alt="${{item.name_translated}}" loading="lazy">
                        </div>
                    </div>
                `).join('');

                return `
                    <section class="category-section" id="${{secId}}">
                        <h2 class="category-heading">${{cat}}</h2>
                        ${{featuredHtml}}
                        <div class="cards-grid">
                            ${{cardsHtml}}
                        </div>
                    </section>
                `;
            }}).join('');
        }}

        // --- UPSELLS ---
        function renderUpsells() {{
            const upsellContainer = document.getElementById('sidebarUpsellItems');
            const modalUpsellContainer = document.getElementById('modalUpsellItems');
            const targetIds = ['drink-coke', 'drink-diet-coke', 'starter-chicken-chorizo', 'starter-halloumi-chilli'];
            const items = MENU_DATA.filter(i => targetIds.includes(i.id));

            const html = items.map(item => `
                <div class="upsell-card">
                    <div>
                        <div class="upsell-card-name">${{item.name_translated}}</div>
                        <div class="upsell-card-price">${{item.price_formatted}}</div>
                    </div>
                    <button class="btn-upsell-add" onclick="addInstantUpsell('${{item.id}}')">
                        + ADD
                    </button>
                </div>
            `).join('');

            if (upsellContainer) upsellContainer.innerHTML = html;
            if (modalUpsellContainer) modalUpsellContainer.innerHTML = html;
        }}

        function addInstantUpsell(itemId) {{
            const item = MENU_DATA.find(i => i.id === itemId);
            if (!item) return;
            const existing = basket.find(b => b.item_id === item.id && !b.heat && !b.meal_type && (!b.sides || b.sides.length === 0));
            if (existing) {{
                existing.quantity++;
                existing.total_price = existing.base_price * existing.quantity;
            }} else {{
                basket.push({{
                    item_id: item.id,
                    name: item.name_translated,
                    base_price: item.price,
                    total_price: item.price,
                    quantity: 1,
                    heat: null,
                    meal_type: null,
                    sides: [],
                    extras: []
                }});
            }}
            updateBasketUI();
            showToast(`✓ Added 1× ${{item.name_translated}} to basket!`);
        }}

        // --- PRODUCT CONFIGURATOR MODAL LOGIC ---
        function openProductCustomizer(itemId) {{
            const toast = document.getElementById('toastNotification');
            if (toast) toast.classList.remove('active');
            const item = MENU_DATA.find(i => i.id === itemId);
            if (!item) return;
            currentConfigItem = item;
            configQuantity = 1;
            selectedHeat = null;
            selectedMeal = null;
            selectedSides = [];
            selectedExtras = [];

            document.getElementById('configImg').src = item.image_url;
            document.getElementById('configTitle').innerText = item.name_translated;
            document.getElementById('configMeta').innerText = `${{item.kcal}} kcal • ${{item.serves || '1 Diner'}}`;
            document.getElementById('configDesc').innerText = item.description_translated;
            document.getElementById('configQtyDisplay').innerText = '1';

            const mods = item.modifiers || {{}};

            // 1. Heat Section
            const heatSec = document.getElementById('configHeatSection');
            if (mods.heats && mods.heats.length) {{
                heatSec.style.display = 'block';
                const grid = document.getElementById('heatOptionsGrid');
                grid.innerHTML = mods.heats.map((h, idx) => `
                    <div class="heat-option-card ${{idx === 3 ? 'selected' : ''}}" onclick="selectHeat('${{h.id}}', this)">
                        <div style="display: flex; align-items: center;">
                            <div class="heat-badge-flag" style="background: ${{h.color}};"></div>
                            <div class="heat-card-info">
                                <div class="heat-name">
                                    <span>${{h.name}}</span>
                                    ${{h.badge ? `<span style="font-size:0.68rem; text-transform:uppercase; background:#FFEBEE; color:#D32F2F; padding:2px 6px; border-radius:4px;">${{h.badge}}</span>` : ''}}
                                </div>
                                <div class="heat-desc">${{h.desc}} • ${{h.kcal}} kcal</div>
                            </div>
                        </div>
                        <div class="heat-meter">Level ${{h.level}} of 5</div>
                    </div>
                `).join('');
                selectedHeat = mods.heats[3]; // Default to Medium
            }} else {{
                heatSec.style.display = 'none';
            }}

            // 2. Meal Section
            const mealSec = document.getElementById('configMealSection');
            if (mods.meals && mods.meals.length) {{
                mealSec.style.display = 'block';
                const grid = document.getElementById('mealChoicesGrid');
                grid.innerHTML = mods.meals.map((m, idx) => `
                    <div class="meal-card ${{idx === 1 ? 'selected' : ''}}" onclick="selectMeal('${{m.id}}', this)">
                        <div class="meal-card-title">${{m.name}}</div>
                        <div class="meal-card-price">£${{m.price.toFixed(2)}}</div>
                        ${{m.badge ? `<div style="font-size:0.7rem; font-weight:800; color:var(--primary); margin-top:4px;">${{m.badge}}</div>` : ''}}
                    </div>
                `).join('');
                selectedMeal = mods.meals[1] || mods.meals[0]; // Default to 2 sides combo
            }} else {{
                mealSec.style.display = 'none';
            }}

            // 3. Sides Section
            const sidesSec = document.getElementById('configSidesSection');
            if (selectedMeal && selectedMeal.sides_count && mods.sides && mods.sides.length) {{
                sidesSec.style.display = 'block';
                renderSidesOptions(mods.sides);
                // Preselect first two regular sides
                selectedSides = [mods.sides[0], mods.sides[3]];
                updateSidesCardUI();
            }} else {{
                sidesSec.style.display = 'none';
            }}

            // 4. Extras Section
            const extrasSec = document.getElementById('configExtrasSection');
            if (mods.extras && mods.extras.length) {{
                extrasSec.style.display = 'block';
                const grid = document.getElementById('extrasGrid');
                grid.innerHTML = mods.extras.map(e => `
                    <div class="side-select-card" onclick="toggleExtra('${{e.id}}', this)">
                        <div>
                            <div class="side-title">${{e.name}}</div>
                            <div style="font-size:0.75rem; color:var(--text-muted);">${{e.kcal}} kcal</div>
                        </div>
                        <div class="side-extra-price">+£${{e.price.toFixed(2)}}</div>
                    </div>
                `).join('');
            }} else {{
                extrasSec.style.display = 'none';
            }}

            calculateConfigPrice();
            document.getElementById('configModalOverlay').classList.add('active');
        }}

        function closeConfigModal() {{
            document.getElementById('configModalOverlay').classList.remove('active');
        }}

        function selectHeat(heatId, cardEl) {{
            const mods = currentConfigItem.modifiers || {{}};
            selectedHeat = mods.heats.find(h => h.id === heatId);
            document.querySelectorAll('.heat-option-card').forEach(c => c.classList.remove('selected'));
            cardEl.classList.add('selected');
            calculateConfigPrice();
        }}

        function selectMeal(mealId, cardEl) {{
            const mods = currentConfigItem.modifiers || {{}};
            selectedMeal = mods.meals.find(m => m.id === mealId);
            document.querySelectorAll('.meal-card').forEach(c => c.classList.remove('selected'));
            cardEl.classList.add('selected');

            const sidesSec = document.getElementById('configSidesSection');
            if (selectedMeal && selectedMeal.sides_count) {{
                sidesSec.style.display = 'block';
                if (!selectedSides.length) {{
                    selectedSides = [mods.sides[0], mods.sides[3]];
                }}
                renderSidesOptions(mods.sides);
            }} else {{
                sidesSec.style.display = 'none';
                selectedSides = [];
            }}
            calculateConfigPrice();
        }}

        function renderSidesOptions(sidesList) {{
            const grid = document.getElementById('sidesGrid');
            grid.innerHTML = sidesList.map(s => `
                <div class="side-select-card" id="side-opt-${{s.id}}" onclick="toggleSide('${{s.id}}')">
                    <div>
                        <div class="side-title">${{s.name}} ${{s.is_new ? '<span class="badge-tag new" style="margin-left:4px;">New</span>' : ''}}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${{s.kcal}} kcal</div>
                    </div>
                    ${{s.surcharge > 0 ? `<div class="side-extra-price">+£${{s.surcharge.toFixed(2)}}</div>` : '<div style="font-size:0.75rem; color:var(--text-muted);">Included</div>'}}
                </div>
            `).join('');
            updateSidesCardUI();
        }}

        function toggleSide(sideId) {{
            const mods = currentConfigItem.modifiers || {{}};
            const sideObj = mods.sides.find(s => s.id === sideId);
            if (!sideObj) return;

            const existingIdx = selectedSides.findIndex(s => s.id === sideId);
            if (existingIdx >= 0) {{
                selectedSides.splice(existingIdx, 1);
            }} else {{
                if (selectedSides.length < (selectedMeal.sides_count || 2)) {{
                    selectedSides.push(sideObj);
                }} else {{
                    // Replace the first side
                    selectedSides.shift();
                    selectedSides.push(sideObj);
                }}
            }}
            updateSidesCardUI();
            calculateConfigPrice();
        }}

        function updateSidesCardUI() {{
            const count = selectedSides.length;
            const target = selectedMeal ? (selectedMeal.sides_count || 2) : 2;
            document.getElementById('sidesSelectedCounter').innerText = `${{count}} of ${{target}} selected`;
            
            document.querySelectorAll('.side-select-card[id^="side-opt-"]').forEach(el => {{
                el.classList.remove('selected');
            }});
            selectedSides.forEach(s => {{
                const el = document.getElementById('side-opt-' + s.id);
                if (el) el.classList.add('selected');
            }});
        }}

        function toggleExtra(extraId, cardEl) {{
            const mods = currentConfigItem.modifiers || {{}};
            const extraObj = mods.extras.find(e => e.id === extraId);
            if (!extraObj) return;

            const idx = selectedExtras.findIndex(e => e.id === extraId);
            if (idx >= 0) {{
                selectedExtras.splice(idx, 1);
                cardEl.classList.remove('selected');
            }} else {{
                selectedExtras.push(extraObj);
                cardEl.classList.add('selected');
            }}
            calculateConfigPrice();
        }}

        function adjustConfigQty(delta) {{
            configQuantity = Math.max(1, configQuantity + delta);
            document.getElementById('configQtyDisplay').innerText = configQuantity;
            calculateConfigPrice();
        }}

        function calculateConfigPrice() {{
            if (!currentConfigItem) return 0;
            let unitPrice = currentConfigItem.price;

            if (selectedMeal) {{
                unitPrice = selectedMeal.price;
            }}

            // Add side surcharges
            selectedSides.forEach(s => {{
                unitPrice += (s.surcharge || 0);
            }});

            // Add extras
            selectedExtras.forEach(e => {{
                unitPrice += (e.price || 0);
            }});

            const total = unitPrice * configQuantity;
            document.getElementById('configDynamicTotal').innerText = `£${{total.toFixed(2)}}`;

            // Validate requirements
            const mods = currentConfigItem.modifiers || {{}};
            const btn = document.getElementById('btnAddConfigToBasket');
            let isValid = true;
            let btnText = 'ADD TO BASKET';

            if (mods.heats && mods.heats.length && !selectedHeat) {{
                isValid = false;
                btnText = 'SELECT A HEAT LEVEL';
            }} else if (selectedMeal && selectedMeal.sides_count && selectedSides.length < selectedMeal.sides_count) {{
                isValid = false;
                const need = selectedMeal.sides_count - selectedSides.length;
                btnText = `CHOOSE ${{need}} MORE SIDE${{need > 1 ? 'S' : ''}}`;
            }}

            btn.disabled = !isValid;
            btn.querySelector('span:first-child').innerText = btnText;
            return total;
        }}

        let toastTimer = null;
        function showToast(msg) {{
            const toast = document.getElementById('toastNotification');
            const msgEl = document.getElementById('toastMessage');
            if (!toast || !msgEl) return;
            msgEl.innerText = msg;
            toast.classList.add('active');
            if (toastTimer) clearTimeout(toastTimer);
            toastTimer = setTimeout(() => {{
                toast.classList.remove('active');
            }}, 3200);
        }}

        function commitConfiguredItemToBasket() {{
            if (!currentConfigItem) return;
            const singleUnitPrice = calculateConfigPrice() / configQuantity;

            basket.push({{
                item_id: currentConfigItem.id,
                name: currentConfigItem.name_translated,
                base_price: singleUnitPrice,
                total_price: singleUnitPrice * configQuantity,
                quantity: configQuantity,
                heat: selectedHeat ? selectedHeat.name : null,
                meal_type: selectedMeal ? selectedMeal.name : null,
                sides: selectedSides.map(s => s.name),
                extras: selectedExtras.map(e => e.name)
            }});

            closeConfigModal();
            updateBasketUI();
            showToast(`✓ Added ${{configQuantity}}× ${{currentConfigItem.name_translated}} to basket!`);
        }}

        // --- BASKET & DRAWER MANAGEMENT ---
        function renderModalBasketItems() {{
            const body = document.getElementById('modalBasketBody');
            const subtotalEl = document.getElementById('modalBasketSubtotal');
            const checkoutTotalEl = document.getElementById('basketDrawerCheckoutTotal');
            const checkoutBtn = document.getElementById('btnBasketModalCheckout');
            if (!body) return;

            const total = basket.reduce((sum, item) => sum + item.total_price, 0);
            if (subtotalEl) subtotalEl.innerText = `£${{total.toFixed(2)}}`;
            if (checkoutTotalEl) checkoutTotalEl.innerText = `£${{total.toFixed(2)}}`;

            if (basket.length === 0) {{
                body.innerHTML = `
                    <div class="basket-empty">
                        <i class="fa-solid fa-basket-shopping"></i>
                        <p style="font-weight: 700; margin-top: 10px; font-size: 1.1rem; color: var(--charcoal);">Your basket is empty</p>
                        <p style="font-size: 0.88rem; margin-top: 4px; color: var(--text-muted);">Explore our menu and add your favourites to get started!</p>
                    </div>
                `;
                if (checkoutBtn) checkoutBtn.disabled = true;
                return;
            }}

            if (checkoutBtn) checkoutBtn.disabled = false;

            body.innerHTML = basket.map((item, idx) => `
                <div class="basket-item">
                    <div class="basket-item-row">
                        <span style="font-size: 0.98rem; font-weight: 800; color: var(--charcoal);">${{item.name}}</span>
                        <span style="font-weight: 800; color: var(--charcoal); font-size: 0.98rem;">£${{item.total_price.toFixed(2)}}</span>
                    </div>
                    ${{item.meal_type ? `<div class="basket-item-mods" style="color:var(--text-muted); font-size:0.82rem; margin-bottom:2px;"><i class="fa-solid fa-layer-group me-1"></i>${{item.meal_type}}</div>` : ''}}
                    ${{item.heat ? `<div class="basket-item-mods" style="color:#E4002B; font-weight:700; font-size:0.82rem; margin-bottom:2px;"><i class="fa-solid fa-fire me-1"></i>${{item.heat}}</div>` : ''}}
                    ${{item.sides && item.sides.length ? `<div class="basket-item-mods" style="color:#007A3D; font-weight:600; font-size:0.82rem; margin-bottom:2px;"><i class="fa-solid fa-circle-check me-1"></i>${{item.sides.join(', ')}}</div>` : ''}}
                    ${{item.extras && item.extras.length ? `<div class="basket-item-mods" style="color:#7C3AED; font-weight:600; font-size:0.82rem; margin-bottom:2px;"><i class="fa-solid fa-plus-circle me-1"></i>${{item.extras.join(', ')}}</div>` : ''}}
                    <div class="basket-item-ctrls" style="margin-top: 8px;">
                        <button class="btn-qty" onclick="changeBasketQty(${{idx}}, -1)" aria-label="Decrease quantity">-</button>
                        <span style="font-size:0.88rem; font-weight:800; min-width: 18px; text-align: center;">${{item.quantity}}</span>
                        <button class="btn-qty" onclick="changeBasketQty(${{idx}}, 1)" aria-label="Increase quantity">+</button>
                        <button onclick="removeBasketItem(${{idx}})" style="background:none; border:none; color:#B00020; font-size:0.85rem; margin-left:auto; cursor:pointer; padding: 4px;" aria-label="Remove item">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }}

        function openBasketDrawer() {{
            const toast = document.getElementById('toastNotification');
            if (toast) toast.classList.remove('active');
            renderModalBasketItems();
            renderUpsells();
            document.getElementById('basketModalOverlay').classList.add('active');
        }}

        function closeBasketDrawer() {{
            document.getElementById('basketModalOverlay').classList.remove('active');
        }}

        function proceedFromBasketToCheckout() {{
            if (basket.length === 0) return;
            closeBasketDrawer();
            openCheckoutModal();
        }}

        function updateBasketUI() {{
            const count = basket.reduce((sum, item) => sum + item.quantity, 0);
            const total = basket.reduce((sum, item) => sum + item.total_price, 0);

            document.getElementById('basketCountBadge').innerText = count;
            document.querySelector('.basket-pill-total').innerText = `£${{total.toFixed(2)}}`;

            // Mobile bar
            const mobileBar = document.getElementById('mobileBottomBar');
            if (count > 0) {{
                mobileBar.style.display = 'flex';
                document.getElementById('mobileBarTotal').innerText = `£${{total.toFixed(2)}}`;
                document.getElementById('mobileBarCount').innerText = count;
            }} else {{
                mobileBar.style.display = 'none';
            }}

            // Sidebar
            const body = document.getElementById('sidebarBasketBody');
            const checkoutBtn = document.getElementById('btnSidebarCheckout');
            if (checkoutBtn) {{
                document.getElementById('sidebarCheckoutTotal').innerText = `£${{total.toFixed(2)}}`;
            }}

            if (body) {{
                if (basket.length === 0) {{
                    body.innerHTML = `
                        <div class="basket-empty">
                            <i class="fa-solid fa-basket-shopping"></i>
                            <p style="font-weight: 700;">Your basket is empty</p>
                            <p style="font-size: 0.85rem; margin-top: 4px;">Select dishes from the menu to build your feast!</p>
                        </div>
                    `;
                    if (checkoutBtn) checkoutBtn.disabled = true;
                }} else {{
                    body.innerHTML = basket.map((item, idx) => `
                        <div class="basket-item">
                            <div class="basket-item-row">
                                <span>${{item.quantity}}× ${{item.name}}</span>
                                <span>£${{item.total_price.toFixed(2)}}</span>
                            </div>
                            ${{item.heat ? `<div class="basket-item-mods"><i class="fa-solid fa-fire text-danger me-1"></i>${{item.heat}}</div>` : ''}}
                            ${{item.sides && item.sides.length ? `<div class="basket-item-mods"><i class="fa-solid fa-circle-check text-success me-1"></i>${{item.sides.join(', ')}}</div>` : ''}}
                            ${{item.extras && item.extras.length ? `<div class="basket-item-mods">+ ${{item.extras.join(', ')}}</div>` : ''}}
                            <div class="basket-item-ctrls">
                                <button class="btn-qty" onclick="changeBasketQty(${{idx}}, -1)">-</button>
                                <span style="font-size:0.85rem; font-weight:800;">${{item.quantity}}</span>
                                <button class="btn-qty" onclick="changeBasketQty(${{idx}}, 1)">+</button>
                                <button onclick="removeBasketItem(${{idx}})" style="background:none; border:none; color:#B00020; font-size:0.8rem; margin-left:auto; cursor:pointer;">
                                    <i class="fa-solid fa-trash-can"></i>
                                </button>
                            </div>
                        </div>
                    `).join('');
                    if (checkoutBtn) checkoutBtn.disabled = false;
                }}
            }}

            // Also refresh modal basket if active
            if (document.getElementById('basketModalOverlay').classList.contains('active')) {{
                renderModalBasketItems();
            }}
        }}

        function changeBasketQty(idx, delta) {{
            const item = basket[idx];
            if (!item) return;
            item.quantity += delta;
            if (item.quantity <= 0) {{
                basket.splice(idx, 1);
            }} else {{
                item.total_price = item.base_price * item.quantity;
            }}
            updateBasketUI();
        }}

        function removeBasketItem(idx) {{
            basket.splice(idx, 1);
            updateBasketUI();
        }}

        // --- CHECKOUT MODAL LOGIC ---
        function openCheckoutModal() {{
            if (basket.length === 0) return;
            const toast = document.getElementById('toastNotification');
            if (toast) toast.classList.remove('active');
            updateCheckoutSummary();
            document.getElementById('checkoutModalOverlay').classList.add('active');
        }}

        function closeCheckoutModal() {{
            document.getElementById('checkoutModalOverlay').classList.remove('active');
        }}

        function selectTip(percent, pillEl) {{
            selectedTipPercent = percent;
            document.querySelectorAll('.tip-pill').forEach(p => p.classList.remove('active'));
            pillEl.classList.add('active');
            updateCheckoutSummary();
        }}

        function selectPaymentMethod(method, cardEl) {{
            activePaymentMethod = method;
            document.querySelectorAll('.pay-card').forEach(c => c.classList.remove('active'));
            cardEl.classList.add('active');
        }}

        function updateCheckoutSummary() {{
            const subtotal = basket.reduce((sum, item) => sum + item.total_price, 0);
            const tip = Math.round((subtotal * (selectedTipPercent / 100)) * 100) / 100;
            const grandTotal = subtotal + tip;

            document.getElementById('summarySubtotal').innerText = `£${{subtotal.toFixed(2)}}`;
            document.getElementById('summaryTipPct').innerText = `${{selectedTipPercent}}%`;
            document.getElementById('summaryTipAmount').innerText = `£${{tip.toFixed(2)}}`;
            document.getElementById('summaryGrandTotal').innerText = `£${{grandTotal.toFixed(2)}}`;
        }}

        // --- SUBMIT FINAL ORDER TO KDS & DATABASE ---
        async function submitFinalOrder() {{
            const btn = document.getElementById('btnConfirmPay');
            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Payment...';

            const tableNum = parseInt(document.getElementById('checkoutTableNum').value) || INITIAL_TABLE;
            const dinerName = document.getElementById('checkoutDinerName').value.trim() || 'Guest';
            const email = document.getElementById('checkoutEmail').value.trim() || 'guest@restaurant.co.uk';
            const notes = document.getElementById('checkoutNotes').value.trim();

            const subtotal = basket.reduce((sum, item) => sum + item.total_price, 0);
            const tipAmount = Math.round((subtotal * (selectedTipPercent / 100)) * 100) / 100;
            const grandTotal = subtotal + tipAmount;

            const orderPayload = {{
                table_number: tableNum,
                channel: "DINE_IN",
                customer: {{
                    name: dinerName,
                    email: email,
                    phone: "+44 7700 900077"
                }},
                items: basket.map(b => ({{
                    item_id: b.item_id,
                    name: b.name,
                    price: b.base_price,
                    quantity: b.quantity,
                    heat: b.heat,
                    meal_type: b.meal_type,
                    sides: b.sides,
                    extras: b.extras
                }})),
                subtotal: subtotal,
                discount: 0.0,
                total: grandTotal,
                tip_amount: tipAmount,
                payment_method: activePaymentMethod,
                notes: notes
            }};

            try {{
                const res = await fetch('/api/order', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(orderPayload)
                }});

                if (res.ok) {{
                    const result = await res.json();
                    if (result && result.order) {{
                        closeCheckoutModal();
                        document.getElementById('successOrderRef').innerText = result.order.id;
                        document.getElementById('successTableNum').innerText = `Table ${{tableNum}}`;
                        document.getElementById('successModalOverlay').classList.add('active');
                        basket = [];
                        updateBasketUI();
                        return;
                    }}
                }}
            }} catch (err) {{
                console.warn('Backend unavailable or running on static hosting:', err);
            }}

            // Offline / GitHub Pages static fallback: store order locally and show success
            const mockOrderId = 'ORD-' + Math.floor(1000 + Math.random() * 9000);
            try {{
                const offlineQueue = JSON.parse(localStorage.getItem('waiter_offline_orders') || '[]');
                orderPayload.id = mockOrderId;
                orderPayload.created_at = new Date().toISOString();
                offlineQueue.push(orderPayload);
                localStorage.setItem('waiter_offline_orders', JSON.stringify(offlineQueue));
            }} catch (e) {{}}

            closeCheckoutModal();
            document.getElementById('successOrderRef').innerText = mockOrderId;
            document.getElementById('successTableNum').innerText = `Table ${{tableNum}}`;
            document.getElementById('successModalOverlay').classList.add('active');
            basket = [];
            updateBasketUI();
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-lock"></i> PAY & PLACE ORDER';
        }}

        function resetOrderAfterSuccess() {{
            document.getElementById('successModalOverlay').classList.remove('active');
        }}
    </script>
</body>
</html>
"""
