from flask import Flask, jsonify, request, render_template_string, Response
import os
import sys
import json
import queue
from datetime import datetime, timezone


# Ensure src path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.config import Config
from src.core.db import db
from src.core.auth import auth_service
from src.modules.qr_ordering import qr_ordering_service
from src.modules.kds import kds_service
from src.modules.promos import promo_service
from src.modules.reviews import review_service
from src.modules.finance import finance_service
from src.modules.thermal_print import thermal_printer_service
from src.modules.qr_generator import qr_generator_service
from src.modules.inventory import inventory_service
from src.modules.exporter import exporter_service
from src.modules.venue import venue_service
from src.modules.staff import staff_service
from src.modules.floor_plan import floor_plan_service
from src.modules.loyalty import loyalty_service
from src.modules.allergens import allergen_service
from src.modules.prep_routing import prep_routing_service
from src.modules.tips_tronc import tips_tronc_service
from src.modules.bill_splitting import bill_splitting_service
from src.modules.purchase_orders import purchase_order_service
from src.modules.waste_tracker import waste_tracker_service
from src.modules.feedback_analytics import feedback_analytics_service
from src.modules.table_booking import table_booking_service
from src.modules.store_transfers import store_transfers_service
from src.modules.tax_compliance import tax_compliance_service
from src.modules.integrations import integrations_service
from src.modules.ai_forecasting import ai_forecasting_service
from src.modules.brand_customizer import brand_customizer_service
from src.modules.payments import payments_service
from src.modules.uk_compliance import uk_compliance_service
from src.modules.money_margins import money_margins_service

app = Flask(__name__)







app.config['SECRET_KEY'] = Config.SECRET_KEY

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>The Waiter | Online Payments & Hospitality OS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0f172a">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;600;700&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style id="dynamicBrandTheme">
        :root {
            --primary-bg: #0f172a;
            --header-bg: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            --accent-blue: #0284c7;
            --accent-green: #10b981;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
        }
        body {
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            background-color: #f8fafc;
            color: var(--text-main);
            padding-bottom: 80px;
        }

        .app-header {
            background: var(--header-bg);
            color: white;
            padding: 14px 20px;
            border-bottom: 3px solid #38bdf8;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .table-badge {
            background: #38bdf8;
            color: #0f172a;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.95rem;
        }

        .mode-switch-btn {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.25);
            color: white;
            font-weight: 600;
            font-size: 0.8rem;
            padding: 6px 12px;
            border-radius: 20px;
            transition: all 0.2s;
        }
        .mode-switch-btn:hover, .mode-switch-btn.active {
            background: white;
            color: #0f172a;
        }

        .card-custom {
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            background: var(--card-bg);
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        @media(min-width: 768px) {
            .card-custom:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
        }

        .dish-card {
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            background: white;
            padding: 16px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .dish-price {
            font-weight: 800;
            font-size: 1.1rem;
            color: var(--accent-blue);
        }
        .add-btn {
            border-radius: 12px;
            font-weight: 700;
            padding: 8px 16px;
        }

        .mobile-cart-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 1040;
            background: #0f172a;
            color: white;
            padding: 14px 20px;
            border-top: 2px solid #38bdf8;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.2);
        }

        .nav-pills .nav-link {
            color: #475569;
            font-weight: 600;
            padding: 10px 18px;
            border-radius: 12px;
            font-size: 0.88rem;
            white-space: nowrap;
        }
        .nav-pills .nav-link.active {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
        }

        .order-step {
            flex: 1;
            text-align: center;
            position: relative;
            font-size: 0.75rem;
            font-weight: 700;
            color: #94a3b8;
        }
        .order-step.active {
            color: #0284c7;
        }
        .order-step-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 6px;
        }
        .order-step.active .order-step-icon {
            background: #0284c7;
            color: white;
        }

        .station-badge-GRILL { background-color: #f59e0b; color: #000; }
        .station-badge-FRYER { background-color: #ef4444; color: #fff; }
        .station-badge-BAR { background-color: #0284c7; color: #fff; }
        .station-badge-LARDER { background-color: #8b5cf6; color: #fff; }
        .station-badge-HOT_LINE { background-color: #64748b; color: #fff; }

        .pay-method-card {
            border: 2px solid #cbd5e1;
            border-radius: 12px;
            padding: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .pay-method-card.selected {
            border-color: #0284c7;
            background-color: #f0f9ff;
        }
    </style>
</head>
<body>

    <!-- Unified Cross-Platform App Header -->
    <header class="app-header">
        <div class="container-fluid px-md-4">
            <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center gap-3">
                    <div class="lh-1">
                        <h4 class="fw-bold mb-0 text-white"><i class="fa-solid fa-utensils me-2 text-info" id="brandLogoIcon"></i><span id="brandNameLabel">The Waiter</span></h4>
                        <small class="text-light opacity-75 d-none d-sm-inline" id="activeStoreLabel">Covent Garden Flagship</small>
                    </div>
                    <div class="table-badge d-flex align-items-center gap-2">
                        <i class="fa-solid fa-qrcode"></i>
                        <span>Table #<span id="activeTableBadgeNum">1</span></span>
                    </div>
                    <span id="pwaNetworkBadge" class="badge bg-success rounded-pill px-3 py-2 ms-2 me-2"><i class="fa-solid fa-wifi me-1"></i> Online</span>
                    <!-- AI Language Toggle Matrix (Page 6 Blueprint) -->
                    <div class="btn-group btn-group-sm rounded-pill overflow-hidden border border-light" role="group" aria-label="AI Language Matrix">
                        <button type="button" class="btn btn-dark text-white fw-bold px-2" onclick="setAppLanguage('en')" id="langBtn-en" title="English">🇬🇧 EN</button>
                        <button type="button" class="btn btn-outline-light text-white fw-bold px-2" onclick="setAppLanguage('fr')" id="langBtn-fr" title="Français">🇫🇷 FR</button>
                        <button type="button" class="btn btn-outline-light text-white fw-bold px-2" onclick="setAppLanguage('ar')" id="langBtn-ar" title="العربية">🇸🇦 AR</button>
                    </div>
                </div>

                <div class="d-flex align-items-center gap-2">
                    <button class="btn btn-sm btn-outline-info text-white fw-bold rounded-pill px-3 me-1" id="btnVoiceCommand" onclick="toggleVoiceCommand()"><i class="fa-solid fa-microphone text-info me-1" id="voiceMicIcon"></i> <span id="voiceBtnText">Voice AI</span></button>
                    <button class="btn btn-sm btn-outline-warning text-white fw-bold rounded-pill px-3 me-1" onclick="showLoyaltyModal()"><i class="fa-solid fa-crown me-1 text-warning"></i> VIP Rewards</button>
                    <button class="btn btn-sm btn-warning text-dark font-weight-bold rounded-pill px-3" onclick="callWaiter()"><i class="fa-solid fa-bell me-1"></i> <span id="callWaiterBtnText">Call Waiter</span></button>
                    <button class="mode-switch-btn active" id="btnGuestView" onclick="setAppMode('guest')"><i class="fa-solid fa-mobile-screen me-1"></i> Table View</button>
                    <button class="mode-switch-btn" id="btnStaffView" onclick="setAppMode('staff')"><i class="fa-solid fa-user-shield me-1"></i> Staff Workspace</button>
                </div>
            </div>
        </div>
    </header>

    <!-- GUEST TABLE VIEW CONTAINER -->
    <main id="guestViewSection" class="container my-4">
        <!-- Floating AI Sommelier Companion Button (Page 6 Blueprint) -->
        <button class="btn btn-dark text-warning rounded-circle shadow-lg position-fixed bottom-0 end-0 m-4 z-3 d-flex align-items-center justify-content-center border border-warning" style="width: 58px; height: 58px;" onclick="showAiSommelierModal()" title="AI Sommelier & Culinary Assistant">
            <i class="fa-solid fa-wine-glass-empty fs-3"></i>
        </button>
        <div class="p-3 bg-white rounded-3 border shadow-sm mb-2 d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-2">
                <i class="fa-solid fa-heart text-danger fs-5"></i>
                <span class="fw-semibold text-dark" id="guestWelcomeMsgText">Welcome! Tap dishes below to order directly from Table #1</span>
            </div>
            <span class="badge bg-success bg-opacity-25 text-success border border-success"><i class="fa-solid fa-bolt me-1"></i> Fast Digital Service</span>
        </div>

        <!-- Dynamic Happy Hour & Active Promo Flash Banner -->
        <div id="guestPromoFlashBanner" class="p-2 px-3 rounded-3 mb-2 d-flex flex-wrap align-items-center justify-content-between text-white shadow-sm" style="background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%);">
            <div class="d-flex align-items-center gap-2 small">
                <span class="badge bg-warning text-dark fw-bold"><i class="fa-solid fa-bolt me-1"></i>ACTIVE PROMOS</span>
                <span id="guestPromoListText" class="fw-semibold">Tap a promo badge to apply instant discount to your table cart:</span>
            </div>
            <div id="guestPromoBadgesContainer" class="d-flex flex-wrap gap-1 mt-1 mt-sm-0">
                <!-- Populated dynamically by loadGuestActivePromos() -->
            </div>
        </div>

        <!-- 1-Tap Table Concierge & Service Call Bell Bar -->
        <div class="p-2 px-3 bg-white rounded-3 border shadow-sm mb-3 d-flex flex-wrap align-items-center justify-content-between gap-2">
            <span class="small fw-bold text-muted"><i class="fa-solid fa-bell-concierge text-warning me-1"></i>Table Concierge:</span>
            <div class="d-flex flex-wrap gap-1">
                <button class="btn btn-xs btn-outline-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('WATER', '💧 Free Tap Water')">💧 Tap Water</button>
                <button class="btn btn-xs btn-outline-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('CUTLERY', '🍴 Extra Napkins & Cutlery')">🍴 Cutlery/Napkins</button>
                <button class="btn btn-xs btn-outline-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('CONDIMENTS', '🌶️ Condiments & Sauces')">🌶️ Sauces</button>
                <button class="btn btn-xs btn-outline-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('BILL', '🧾 Request Physical Bill')">🧾 Physical Bill</button>
                <button class="btn btn-xs btn-warning text-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('SERVER', '🙋 Call Server to Table')">🙋 Call Server</button>
            </div>
        </div>

        <div id="voiceFeedbackToast" class="alert alert-info border-info shadow-lg rounded-3 d-none position-fixed bottom-0 end-0 m-4 z-3" style="max-width: 360px;">
            <div class="d-flex align-items-center gap-3">
                <i class="fa-solid fa-waveform text-info fs-3"></i>
                <div>
                    <strong class="d-block text-dark small">Voice AI Recognized</strong>
                    <div id="voiceRecognizedText" class="fw-bold text-primary small">"..."</div>
                </div>
            </div>
        </div>
        <div id="offlineSyncBanner" class="alert alert-warning border-warning shadow-sm rounded-3 d-none mb-3" role="alert">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <i class="fa-solid fa-wifi-slash text-danger me-2 fs-5"></i>
                    <strong>Offline Dining Mode (Dead-Zone Protection)</strong>
                    <div class="small text-dark">You are offline. Orders are saved securely on device and will auto-sync when connection resumes.</div>
                </div>
                <span class="badge bg-dark text-warning fs-6 px-3 py-2 rounded-pill" id="offlinePendingCountBadge">0 Pending</span>
            </div>
        </div>
        <div id="waiterAlertBanner" class="alert alert-success alert-dismissible fade show d-none shadow-sm rounded-3" role="alert">
            <i class="fa-solid fa-circle-check me-2"></i><strong>Server Notified!</strong> A staff member is on their way to Table #<span id="alertTableNum">1</span>.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>

        <div id="tableLiveOrderCard" class="card card-custom p-3 bg-white shadow-sm mb-4 d-none">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-clock-rotate-left text-primary me-2"></i>Live Order Status (Table #<span id="liveTableNum">1</span>)</h6>
                <span class="badge bg-primary" id="liveOrderRef">ORD-1001</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div class="order-step active" id="stepReceived">
                    <div class="order-step-icon"><i class="fa-solid fa-check"></i></div>
                    Received
                </div>
                <div class="order-step" id="stepPreparing">
                    <div class="order-step-icon"><i class="fa-solid fa-fire-burner"></i></div>
                    Preparing
                </div>
                <div class="order-step" id="stepReady">
                    <div class="order-step-icon"><i class="fa-solid fa-bell"></i></div>
                    Ready
                </div>
            </div>
            <div id="liveOrderStationEtaBox" class="p-2 bg-light rounded-3 border mb-3 small">
                <!-- Populated dynamically by loadTableLiveOrderStatus() via GET /api/kds/eta/<order_id> -->
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-sm btn-dark flex-grow-1 fw-bold" onclick="showOnlinePaymentModal()"><i class="fa-solid fa-credit-card text-success me-1"></i> Pay Bill at Table Now</button>
                <button class="btn btn-sm btn-outline-danger fw-bold d-none" id="btnCancelGuestOrder" onclick="cancelActiveGuestOrder()"><i class="fa-solid fa-ban me-1"></i> Cancel Order</button>
            </div>
        </div>

        <div class="row g-4">
            <div class="col-lg-8">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                    <h4 class="fw-bold mb-0 text-dark">Digital Menu</h4>
                    <div class="d-flex align-items-center gap-2">
                        <div class="btn-group btn-group-sm" id="langGroup">
                            <button class="btn btn-outline-dark active fw-bold" onclick="setLanguage('en', this)">EN</button>
                            <button class="btn btn-outline-dark fw-bold" onclick="setLanguage('fr', this)">FR</button>
                            <button class="btn btn-outline-dark fw-bold" onclick="setLanguage('ar', this)">AR</button>
                        </div>
                        <div class="btn-group btn-group-sm" id="currGroup">
                            <button class="btn btn-dark active fw-bold" onclick="setCurrency('GBP', this)">£ GBP</button>
                            <button class="btn btn-outline-dark fw-bold" onclick="setCurrency('EUR', this)">€ EUR</button>
                            <button class="btn btn-outline-dark fw-bold" onclick="setCurrency('USD', this)">$ USD</button>
                        </div>
                    </div>
                </div>

                <div class="d-flex flex-wrap align-items-center gap-2 mb-3 p-3 bg-white rounded-3 border shadow-sm">
                    <span class="small fw-bold text-muted me-1"><i class="fa-solid fa-filter me-1 text-primary"></i>Dietary Filters:</span>
                    <button class="btn btn-sm btn-outline-success active rounded-pill px-3 py-1 fw-bold" onclick="filterMenuDiet('all', this)">All Dishes</button>
                    <button class="btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold" onclick="filterMenuDiet('vegan', this)">🌱 Vegan</button>
                    <button class="btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold" onclick="filterMenuDiet('vegetarian', this)">🥬 Vegetarian</button>
                    <button class="btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold" onclick="filterMenuDiet('halal', this)">🕌 Halal</button>
                    <button class="btn btn-sm btn-outline-danger rounded-pill px-3 py-1 fw-bold ms-auto" onclick="toggleExclusion('gluten', this)">🌾 Exclude Gluten</button>
                </div>

                <div id="menuContainer" class="row g-3">
                    <!-- Dynamically populated -->
                </div>
            </div>

            <div class="col-lg-4 d-none d-lg-block">
                <div class="card card-custom p-4 bg-white sticky-top" style="top: 20px;">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold mb-0"><i class="fa-solid fa-cart-shopping text-primary me-2"></i>Table Cart</h5>
                        <span class="badge bg-secondary">Table #<span id="desktopTableNum">1</span></span>
                    </div>
                    <hr class="my-2">
                    <div id="cartItems" class="mb-3 text-muted small py-2">Cart is empty. Select dishes from menu.</div>
                    
                    <div id="upsellBox" class="upsell-box mb-3 d-none">
                        <strong class="small text-dark"><i class="fa-solid fa-lightbulb text-warning me-1"></i>Recommended Add-on:</strong>
                        <div id="upsellContent" class="mt-1"></div>
                    </div>

                    <!-- UK Challenge 25 Alcohol Age Verification Alert (Licensing Act 2003) -->
                    <div id="challenge25CartBanner" class="p-2 mb-3 rounded-3 bg-danger bg-opacity-10 border border-danger small d-none">
                        <strong class="text-danger d-block"><i class="fa-solid fa-id-card me-1"></i>🔞 UK Challenge 25 Policy</strong>
                        <span class="text-dark">Alcohol item detected. Staff will verify photographic ID (Passport / UK Driving Licence / PASS 18+) at your table before serving.</span>
                    </div>

                    <!-- HMRC VAT Notice 709/1 Dining Mode Selector (Eat-In vs Hot vs Cold Takeaway) -->
                    <div class="mb-3 p-2 bg-light rounded-3 border">
                        <label class="small fw-bold text-muted d-block mb-1"><i class="fa-solid fa-scale-balanced text-primary me-1"></i>UK VAT Mode (HMRC 709/1):</label>
                        <select id="guestVatDiningMode" class="form-select form-select-sm fw-bold mb-1" onchange="renderCart()">
                            <option value="EAT_IN">🍽️ Eat-In (20% Standard UK VAT)</option>
                            <option value="HOT_TAKEAWAY">🔥 Hot Takeaway (20% Standard UK VAT)</option>
                            <option value="COLD_TAKEAWAY">❄️ Cold Takeaway Grab & Go (0% Zero-Rated Food)</option>
                        </select>
                        <div id="guestVatBreakdownLine" class="small text-muted d-flex justify-content-between">
                            <span>Net: £0.00</span>
                            <span>UK VAT: £0.00</span>
                        </div>
                    </div>

                    <div class="mb-3">
                        <input type="text" id="promoInput" class="form-control form-control-sm" placeholder="Promo code (e.g. WELCOME10)">
                    </div>

                    <div class="d-flex justify-content-between fw-bold mb-3 fs-5">
                        <span>Total:</span>
                        <span id="cartTotal" class="text-success">£0.00</span>
                    </div>

                    <button class="btn btn-primary w-100 fw-bold mb-2 py-2" onclick="placeOrder()"><i class="fa-solid fa-check-circle me-1"></i> Submit Order</button>
                    <button class="btn btn-dark w-100 fw-bold py-2 mb-2" onclick="showOnlinePaymentModal()"><i class="fa-solid fa-credit-card text-success me-1"></i> Pay at Table Now</button>
                    <button class="btn btn-outline-success text-dark w-100 btn-sm fw-bold mb-2" onclick="showSplitBillModal()"><i class="fa-solid fa-calculator me-1"></i> Split Table Bill</button>
                    <button class="btn btn-outline-warning text-dark w-100 btn-sm fw-bold" data-bs-toggle="modal" data-bs-target="#reviewModal"><i class="fa-solid fa-comment-dots me-1"></i> Leave Private Feedback</button>
                </div>
            </div>
        </div>
    </main>

    <!-- FLOATING STICKY MOBILE BOTTOM CART BAR -->
    <div class="mobile-cart-bar d-lg-none" id="mobileCartBar">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <small class="text-light opacity-75 d-block">Table #<span id="mobileTableNum">1</span> Order Total</small>
                <strong class="fs-5 text-info" id="mobileCartTotal">£0.00</strong>
            </div>
            <button class="btn btn-info text-dark font-weight-bold px-4 py-2 rounded-pill shadow-sm" data-bs-toggle="modal" data-bs-target="#mobileCartModal">
                <i class="fa-solid fa-bag-shopping me-1"></i> View Cart (<span id="mobileCartCount">0</span>)
            </button>
        </div>
    </div>

    <!-- MOBILE CART MODAL -->
    <div class="modal fade" id="mobileCartModal" tabindex="-1" aria-labelledby="mobileCartModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="mobileCartModalLabel"><i class="fa-solid fa-cart-shopping text-primary me-2"></i>Table Cart</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div id="mobileCartItems" class="mb-3 text-muted small">Cart is empty.</div>
                    <div class="mb-3">
                        <input type="text" id="mobilePromoInput" class="form-control form-control-sm" placeholder="Promo code (e.g. WELCOME10)">
                    </div>
                    <div class="d-flex justify-content-between fw-bold mb-3 fs-5">
                        <span>Total:</span>
                        <span id="mobileModalCartTotal" class="text-success">£0.00</span>
                    </div>
                    <button class="btn btn-primary w-100 fw-bold mb-2 py-2" onclick="placeOrder(); bootstrap.Modal.getInstance(document.getElementById('mobileCartModal')).hide();"><i class="fa-solid fa-check-circle me-1"></i> Submit Order</button>
                    <button class="btn btn-dark w-100 fw-bold py-2 mb-2" onclick="bootstrap.Modal.getInstance(document.getElementById('mobileCartModal')).hide(); showOnlinePaymentModal();"><i class="fa-solid fa-credit-card text-success me-1"></i> Pay at Table Now</button>
                    <button class="btn btn-outline-success w-100 btn-sm fw-bold mb-2" onclick="showSplitBillModal()"><i class="fa-solid fa-calculator me-1"></i> Split Bill</button>
                    <button class="btn btn-outline-warning text-dark w-100 btn-sm fw-bold" data-bs-toggle="modal" data-bs-target="#reviewModal"><i class="fa-solid fa-comment-dots me-1"></i> Leave Private Feedback</button>
                </div>
            </div>
        </div>
    </div>

    <!-- ONLINE TABLE PAYMENTS & DIGITAL TIP MODAL -->
    <div class="modal fade" id="paymentModal" tabindex="-1" aria-labelledby="paymentModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="paymentModalLabel"><i class="fa-solid fa-credit-card text-success me-2"></i>Pay at Table (Table #<span id="payModalTableNum">1</span>)</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <!-- Tip Selection Pills -->
                    <label class="form-label small fw-bold text-muted mb-2"><i class="fa-solid fa-hand-holding-dollar me-1 text-warning"></i>Select Service Tip:</label>
                    <div class="d-flex flex-wrap gap-2 mb-3" id="tipPresetGroup">
                        <button class="btn btn-sm btn-outline-dark rounded-pill fw-bold" onclick="selectTipPreset(0, this)">No Tip (0%)</button>
                        <button class="btn btn-sm btn-outline-dark rounded-pill fw-bold" onclick="selectTipPreset(10, this)">10%</button>
                        <button class="btn btn-sm btn-dark active rounded-pill fw-bold" onclick="selectTipPreset(12.5, this)">12.5% (UK Std)</button>
                        <button class="btn btn-sm btn-outline-dark rounded-pill fw-bold" onclick="selectTipPreset(15, this)">15%</button>
                        <button class="btn btn-sm btn-outline-dark rounded-pill fw-bold" onclick="selectTipPreset(20, this)">20%</button>
                    </div>

                    <!-- Payment Method Selection Cards -->
                    <label class="form-label small fw-bold text-muted mb-2"><i class="fa-solid fa-wallet me-1 text-primary"></i>Choose Payment Method:</label>
                    <div class="row g-2 mb-3">
                        <div class="col-6 col-sm-3">
                            <div class="pay-method-card text-center selected" id="pmPayByBank" onclick="selectPaymentMethod('PAY_BY_BANK', this)">
                                <i class="fa-solid fa-building-columns fs-4 text-info mb-1"></i>
                                <span class="d-block small fw-bold">Pay by Bank</span>
                                <span class="badge bg-success" style="font-size: 0.65rem;">0.2% Fee • Fast</span>
                            </div>
                        </div>
                        <div class="col-6 col-sm-3">
                            <div class="pay-method-card text-center" id="pmApplePay" onclick="selectPaymentMethod('APPLE_PAY', this)">
                                <i class="fa-brands fa-apple fs-4 text-dark mb-1"></i>
                                <span class="d-block small fw-bold">Apple Pay</span>
                                <span class="badge bg-light text-muted border" style="font-size: 0.65rem;">1-Tap Wallet</span>
                            </div>
                        </div>
                        <div class="col-6 col-sm-3">
                            <div class="pay-method-card text-center" id="pmGooglePay" onclick="selectPaymentMethod('GOOGLE_PAY', this)">
                                <i class="fa-brands fa-google-pay fs-4 text-primary mb-1"></i>
                                <span class="d-block small fw-bold">Google Pay</span>
                                <span class="badge bg-light text-muted border" style="font-size: 0.65rem;">1-Tap Wallet</span>
                            </div>
                        </div>
                        <div class="col-6 col-sm-3">
                            <div class="pay-method-card text-center" id="pmCardStripe" onclick="selectPaymentMethod('CARD_STRIPE', this)">
                                <i class="fa-solid fa-credit-card fs-4 text-success mb-1"></i>
                                <span class="d-block small fw-bold">Card Stripe</span>
                                <span class="badge bg-light text-muted border" style="font-size: 0.65rem;">Chip / Contactless</span>
                            </div>
                        </div>
                    </div>

                    <!-- Total Breakdown Card -->
                    <div class="p-3 bg-light rounded-3 border mb-3">
                        <div class="d-flex justify-content-between small text-muted mb-1">
                            <span>Order Subtotal:</span>
                            <span id="paySubtotalVal">£0.00</span>
                        </div>
                        <div class="d-flex justify-content-between small text-muted mb-1">
                            <span>Selected Tip Amount:</span>
                            <span id="payTipVal" class="text-warning fw-bold">+£0.00</span>
                        </div>
                        <hr class="my-2">
                        <div class="d-flex justify-content-between fs-5 fw-bold text-dark">
                            <span>Grand Total Paid:</span>
                            <span id="payGrandTotalVal" class="text-success">£0.00</span>
                        </div>
                    </div>

                    <button class="btn btn-success w-100 fw-bold py-2 fs-6" onclick="processTableCheckout()"><i class="fa-solid fa-lock me-1"></i> Pay Now & Issue Receipt</button>
                </div>
            </div>
        </div>
    </div>

    <!-- STAFF & MANAGER WORKSPACE CONTAINER -->
    <main id="staffViewSection" class="container my-4 d-none">
        <div class="d-flex justify-content-between align-items-center mb-4 p-3 bg-white border rounded-3 shadow-sm">
            <div class="d-flex align-items-center gap-3">
                <div class="p-2 bg-primary bg-opacity-10 text-primary rounded-3 fs-4"><i class="fa-solid fa-store"></i></div>
                <div>
                    <span class="small fw-bold text-muted text-uppercase d-block">Active Store Location</span>
                    <strong id="activeVenueName" class="fs-6 text-dark">Covent Garden Flagship (UK)</strong>
                </div>
            </div>
            <div class="d-flex align-items-center gap-2">
                <label for="venueSelect" class="small fw-bold text-muted mb-0"><i class="fa-solid fa-location-dot me-1"></i>Venue Switcher:</label>
                <select id="venueSelect" class="form-select form-select-sm w-auto fw-bold text-dark border-primary" onchange="switchVenue(this.value)">
                    <!-- Dynamically populated -->
                </select>
            </div>
        </div>

        <div class="row g-3 mb-4">
            <div class="col-6 col-md-3">
                <div class="card card-custom p-3 shadow-sm">
                    <small class="text-muted text-uppercase fw-bold">Gross Revenue</small>
                    <div class="fs-3 fw-bold text-success" id="kpiGrossRev">£0.00</div>
                    <span class="small text-muted" id="kpiTotalOrdersCount">0 orders today</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card card-custom p-3 shadow-sm">
                    <small class="text-muted text-uppercase fw-bold">Active KDS Tickets</small>
                    <div class="fs-3 fw-bold text-primary" id="kpiActiveKds">0</div>
                    <span class="small text-muted">Real-time KDS stream</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card card-custom p-3 shadow-sm">
                    <small class="text-muted text-uppercase fw-bold">Active Staff & Labor</small>
                    <div class="fs-3 fw-bold text-info" id="kpiActiveStaff">0 Staff</div>
                    <span class="small text-muted" id="kpiLaborCost">£0.00 (0% labor)</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card card-custom p-3 shadow-sm">
                    <small class="text-muted text-uppercase fw-bold">NPS Guest Score</small>
                    <div class="fs-3 fw-bold text-warning" id="kpiNpsScore">0.0</div>
                    <span class="small text-muted" id="kpiNpsLabel">0 Reviews</span>
                </div>
            </div>
        </div>

        <div class="d-flex flex-wrap gap-2 mb-4 p-2 bg-white rounded-3 border shadow-sm">
            <span class="small fw-bold text-muted me-2 align-self-center"><i class="fa-solid fa-file-pdf text-danger me-1"></i>Quick PDF Exports:</span>
            <a href="/api/qr/cards/pdf" target="_blank" class="badge bg-danger text-white text-decoration-none p-2"><i class="fa-solid fa-qrcode me-1"></i> Table QR Tents</a>
            <a href="/api/finance/z-report/pdf" target="_blank" class="badge bg-dark text-warning text-decoration-none p-2"><i class="fa-solid fa-chart-line me-1"></i> Daily Z-Report</a>
            <a href="/api/waste/report/pdf" target="_blank" class="badge bg-danger text-white text-decoration-none p-2"><i class="fa-solid fa-trash-can me-1"></i> Waste Audit</a>
            <a href="/api/tax/report/pdf" target="_blank" class="badge bg-success text-white text-decoration-none p-2"><i class="fa-solid fa-file-invoice-dollar me-1"></i> HMRC MTD VAT</a>
            <a href="/api/feedback/report/pdf" target="_blank" class="badge bg-primary text-white text-decoration-none p-2"><i class="fa-solid fa-star me-1"></i> NPS Feedback</a>
            <a href="/api/inventory/purchase-orders/SEAFOOD/pdf" target="_blank" class="badge bg-info text-dark text-decoration-none p-2"><i class="fa-solid fa-truck-ramp-box me-1"></i> Supplier PO</a>
            <a href="/api/forecasting/report/pdf" target="_blank" class="badge bg-secondary text-white text-decoration-none p-2"><i class="fa-solid fa-brain me-1"></i> AI Forecast</a>
        </div>

        <ul class="nav nav-pills mb-4 justify-content-start justify-content-md-center flex-nowrap overflow-auto py-1" id="staffTabs" role="tablist">
            <li class="nav-item">
                <button class="nav-link active" id="floorplan-tab" data-bs-toggle="tab" data-bs-target="#floorplan" type="button" onclick="loadVisualFloorplan()"><i class="fa-solid fa-map-location-dot me-1"></i> Visual Floor Plan</button>
            <li class="nav-item">
                <button class="nav-link" id="kds-tab" data-bs-toggle="tab" data-bs-target="#kds" type="button" onclick="loadKDS()"><i class="fa-solid fa-fire-burner me-1"></i> Kitchen KDS</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="delivery-tab" data-bs-toggle="tab" data-bs-target="#delivery" type="button" onclick="loadDeliveryHub()"><i class="fa-solid fa-motorcycle me-1"></i> Delivery Hub</button>
            </li>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="qrstudio-tab" data-bs-toggle="tab" data-bs-target="#qrstudio" type="button" onclick="loadQrStudio()"><i class="fa-solid fa-qrcode me-1"></i> Table QR Studio</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="branding-tab" data-bs-toggle="tab" data-bs-target="#branding" type="button" onclick="loadBrandConfig()"><i class="fa-solid fa-palette me-1"></i> Brand & Theme</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="bookings-tab" data-bs-toggle="tab" data-bs-target="#bookings" type="button" onclick="loadBookings()"><i class="fa-solid fa-calendar-check me-1"></i> Reservations</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="inventory-tab" data-bs-toggle="tab" data-bs-target="#inventory" type="button" onclick="loadInventory()"><i class="fa-solid fa-boxes-stacked me-1"></i> Stock & POs</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="waste-tab" data-bs-toggle="tab" data-bs-target="#waste" type="button" onclick="loadWaste()"><i class="fa-solid fa-trash-can me-1"></i> Kitchen Waste</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="tax-tab" data-bs-toggle="tab" data-bs-target="#tax" type="button" onclick="loadTax()"><i class="fa-solid fa-file-invoice-dollar me-1"></i> MTD VAT & Transfers</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="feedback-tab" data-bs-toggle="tab" data-bs-target="#feedback" type="button" onclick="loadFeedback()"><i class="fa-solid fa-comments me-1"></i> Guest NPS</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="forecasting-tab" data-bs-toggle="tab" data-bs-target="#forecasting" type="button" onclick="loadForecasting()"><i class="fa-solid fa-brain me-1"></i> AI Forecast</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="staff-tab" data-bs-toggle="tab" data-bs-target="#staff" type="button" onclick="loadStaff()"><i class="fa-solid fa-user-clock me-1"></i> Staff & Tronc</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="reports-tab" data-bs-toggle="tab" data-bs-target="#reports" type="button" onclick="loadZReportAndPromos()"><i class="fa-solid fa-chart-pie me-1"></i> Z-Report & Promos</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="margins-tab" data-bs-toggle="tab" data-bs-target="#margins" type="button" onclick="loadMoneyAndMarginsHub()"><i class="fa-solid fa-sterling-sign me-1 text-success"></i> 💷 Money & Margins</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="ukcompliance-tab" data-bs-toggle="tab" data-bs-target="#ukcompliance" type="button" onclick="loadUkComplianceHub()"><i class="fa-solid fa-shield-halved me-1 text-danger"></i> 🇬🇧 UK Compliance & EHO</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" type="button"><i class="fa-solid fa-file-contract me-1"></i> Strategy</button>
            </li>
        </ul>

        <div class="tab-content" id="staffTabContent">

            <!-- TAB 0: Visual Blueprint Floor Plan Layout (Page 1 Blueprint) -->
            <div class="tab-pane fade show active" id="floorplan" role="tabpanel">
                <!-- Live Table Service Calls Dispatch Queue -->
                <div id="staffServiceCallsCard" class="card card-custom p-3 bg-warning bg-opacity-10 border border-warning mb-3 d-none">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="fw-bold text-dark mb-0"><i class="fa-solid fa-bell-concierge text-danger me-2"></i>Active Table Concierge & Server Calls</h6>
                        <span class="badge bg-danger" id="activeServiceCallsCountBadge">0 Pending</span>
                    </div>
                    <div id="staffServiceCallsList" class="d-flex flex-wrap gap-2">
                        <!-- Populated dynamically by loadServiceCallsQueue() -->
                    </div>
                </div>
                <div class="card card-custom p-4 bg-dark text-white border-0 shadow-lg mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <span class="badge bg-info text-dark fw-bold mb-1"><i class="fa-solid fa-layer-group me-1"></i> BLUEPRINT ENGINE</span>
                            <h4 class="fw-bold mb-0 text-white"><i class="fa-solid fa-map-location-dot me-2 text-warning"></i>Live Interactive Floor Plan Map</h4>
                            <small class="text-light opacity-75">Real-time table turnover speed, occupancy status, and capacity tracking</small>
                        </div>
                        <div class="d-flex flex-wrap gap-3 text-end">
                            <div class="px-2 border-end border-secondary">
                                <small class="text-light opacity-75 d-block">REVENUE YTD</small>
                                <h5 class="fw-bold text-success mb-0" id="bpRevenueYtd">£1.2M ↑</h5>
                            </div>
                            <div class="px-2 border-end border-secondary">
                                <small class="text-light opacity-75 d-block">STAFF ACTIVE</small>
                                <h5 class="fw-bold text-info mb-0" id="bpStaffActive">18</h5>
                            </div>
                            <div class="px-2 border-end border-secondary">
                                <small class="text-light opacity-75 d-block">AVG TABLE TURN</small>
                                <h5 class="fw-bold text-warning mb-0" id="bpAvgTurn"><i class="fa-solid fa-rotate me-1"></i> 55 MIN</h5>
                            </div>
                            <div class="ps-2">
                                <small class="text-light opacity-75 d-block">RESERVATIONS</small>
                                <h5 class="fw-bold text-white mb-0" id="bpReservationsToday">120 <small class="fs-6 text-warning">(TODAY)</small></h5>
                            </div>
                        </div>
                    </div>

                    <!-- Floorplan Graphic Canvas / Table Grid + Page 1 Architectural Bar Stools & Kitchen Pass -->
                    <div class="p-4 bg-secondary bg-opacity-25 rounded-3 border border-secondary mb-3">
                        <div class="row g-3">
                            <div class="col-lg-9">
                                <div class="row g-3" id="visualFloorplanGrid">
                                    <!-- Dynamically generated visual table map -->
                                </div>
                            </div>
                            <div class="col-lg-3 d-flex flex-column gap-3">
                                <!-- Architectural Draft Bar Counter & 5 Bar Stools (Page 1 Blueprint) -->
                                <div class="p-3 rounded-3 border border-warning bg-dark bg-opacity-75 text-center h-100 d-flex flex-column justify-content-between">
                                    <div>
                                        <span class="badge bg-warning text-dark fw-bold mb-1"><i class="fa-solid fa-beer-mug-empty me-1"></i> DRAFT BAR COUNTER</span>
                                        <small class="text-light opacity-75 d-block">5 Bar Stools • Live Tap Line</small>
                                    </div>
                                    <div class="d-flex justify-content-center gap-2 my-3" id="barStoolsBlueprintRow">
                                        <span class="badge rounded-circle bg-success p-2 border border-light" title="Bar Stool #1 (Available)">S1</span>
                                        <span class="badge rounded-circle bg-danger p-2 border border-light" title="Bar Stool #2 (Occupied)">S2</span>
                                        <span class="badge rounded-circle bg-danger p-2 border border-light" title="Bar Stool #3 (Occupied)">S3</span>
                                        <span class="badge rounded-circle bg-success p-2 border border-light" title="Bar Stool #4 (Available)">S4</span>
                                        <span class="badge rounded-circle bg-warning text-dark p-2 border border-light" title="Bar Stool #5 (Reserved)">S5</span>
                                    </div>
                                    <div class="p-2 rounded bg-secondary bg-opacity-25 border border-secondary small">
                                        <i class="fa-solid fa-fire-burner text-warning me-1"></i> <strong>KITCHEN STOVE PASS</strong>
                                        <div class="text-info small mt-1">● ● ● ● Hot Line Active</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="d-flex justify-content-between align-items-center small text-light opacity-75">
                        <div class="d-flex gap-3">
                            <span><i class="fa-solid fa-circle text-success me-1"></i> Available</span>
                            <span><i class="fa-solid fa-circle text-danger me-1"></i> Occupied</span>
                            <span><i class="fa-solid fa-circle text-warning me-1"></i> Reserved</span>
                        </div>
                        <span><i class="fa-solid fa-bolt text-info me-1"></i> Zero Hardware Lock-In Engine</span>
                    </div>
                </div>

                <!-- MODULE 1: Executive Peak-Hour Sales Heatmap & Table Turnover Analytics -->
                <div class="row g-4">
                    <div class="col-lg-7">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-fire text-danger me-2"></i>Executive Peak-Hour Revenue Heatmap</h5>
                                    <small class="text-muted">Hourly sales velocity, rush intensity & AI staffing recommendations</small>
                                </div>
                                <span class="badge bg-danger bg-opacity-10 text-danger border border-danger fw-bold" id="peakWindowBadge">Peak Rush: 19:00 - 21:00</span>
                            </div>
                            <div id="salesHeatmapGrid" class="vstack gap-2">
                                <!-- Populated dynamically by loadSalesHeatmap() -->
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-5">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-1 text-dark"><i class="fa-solid fa-stopwatch text-primary me-2"></i>Dining Zone Turnover & Dwell Time</h5>
                            <small class="text-muted d-block mb-3">Average table turn speed vs target benchmark per zone</small>
                            <div id="zoneTurnoverContainer" class="vstack gap-3">
                                <!-- Populated dynamically by loadSalesHeatmap() -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- PAGE 8 & PAGE 9 BLUEPRINT: Auto-Generated Live Invoice Card, KPI Horizon Switcher & 6-Device Cloud Sync Hub -->
                <div class="row g-4 mt-1">
                    <!-- Page 8: Zero-Touch Administration & Auto-Numbered Live Invoice Preview -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-primary">
                            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                                <div>
                                    <span class="badge bg-primary bg-opacity-10 text-primary fw-bold mb-1">PAGE 8 BLUEPRINT • ZERO-TOUCH ADMIN</span>
                                    <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-file-invoice-dollar text-primary me-2"></i>Automated Instant Invoice Preview</h5>
                                </div>
                                <div class="btn-group btn-group-sm" role="group" aria-label="KPI Horizon Switcher">
                                    <button type="button" class="btn btn-dark fw-bold active" id="kpiHorizon-daily" onclick="switchBlueprintKpiHorizon('daily')">Daily</button>
                                    <button type="button" class="btn btn-outline-dark fw-bold" id="kpiHorizon-monthly" onclick="switchBlueprintKpiHorizon('monthly')">Monthly</button>
                                    <button type="button" class="btn btn-outline-dark fw-bold" id="kpiHorizon-annual" onclick="switchBlueprintKpiHorizon('annual')">Annual</button>
                                </div>
                            </div>
                            <div id="blueprintHorizonSummaryStrip" class="p-2 px-3 bg-light rounded border mb-3 d-flex justify-content-between align-items-center small">
                                <span><strong class="text-dark">Horizon KPIs (<span id="bpHorizonLabel">DAILY</span>):</strong></span>
                                <span class="fw-bold text-success" id="bpHorizonRev">£3,735.50 Sales</span>
                                <span class="fw-bold text-primary" id="bpHorizonOrders">152 Tickets</span>
                                <span class="fw-bold text-warning text-dark" id="bpHorizonTopItem">Top: Classic Pub Burger</span>
                            </div>
                            <!-- Crisp Visual Invoice Card matching Page 8 Slide -->
                            <div class="p-3 bg-light rounded-3 border font-monospace small" id="liveBlueprintInvoiceCard">
                                <div class="d-flex justify-content-between align-items-start border-bottom pb-2 mb-2">
                                    <div>
                                        <strong class="fs-6 text-dark d-block">THE WAITER UK FLAGSHIP</strong>
                                        <span class="text-muted">Auto-Generated Tax Invoice • VAT Reg #GB-9482104</span>
                                    </div>
                                    <div class="text-end">
                                        <span class="badge bg-dark text-warning fw-bold" id="bpInvoiceNumber">INVOICE #001024</span>
                                        <small class="text-muted d-block">Table #4 • Paid via Apple Pay</small>
                                    </div>
                                </div>
                                <table class="table table-sm table-borderless mb-2 small">
                                    <thead class="border-bottom text-muted">
                                        <tr><th>Item</th><th class="text-center">Qty</th><th class="text-end">Price</th><th class="text-end">Total</th></tr>
                                    </thead>
                                    <tbody id="bpInvoiceLinesBody">
                                        <tr><td>Classic Pub Burger (Wagyu)</td><td class="text-center">2</td><td class="text-end">£15.50</td><td class="text-end fw-bold">£31.00</td></tr>
                                        <tr><td>Pint of Craft Ale / IPA</td><td class="text-center">3</td><td class="text-end">£6.50</td><td class="text-end fw-bold">£19.50</td></tr>
                                    </tbody>
                                    <tfoot class="border-top">
                                        <tr><td colspan="3" class="text-end text-muted">Subtotal (Net):</td><td class="text-end fw-bold">£50.50</td></tr>
                                        <tr><td colspan="3" class="text-end text-muted">UK VAT (20%):</td><td class="text-end fw-bold text-danger">£10.10</td></tr>
                                        <tr class="fs-6"><td colspan="3" class="text-end fw-bold text-dark">Total Due (Cleared):</td><td class="text-end fw-bold text-success">£60.60</td></tr>
                                    </tfoot>
                                </table>
                                <div class="d-flex justify-content-end gap-2">
                                    <a href="/api/finance/z-report/pdf" target="_blank" class="btn btn-xs btn-outline-dark fw-bold"><i class="fa-solid fa-file-pdf text-danger me-1"></i>Export KPI PDF</a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Page 9: Zero Hardware Lock-In — The Waiter Cloud Sync 6-Device Ecosystem Hub -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-dark text-white shadow-sm h-100 border-top border-4 border-info">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <span class="badge bg-info text-dark fw-bold mb-1">PAGE 9 BLUEPRINT • ZERO HARDWARE LOCK-IN</span>
                                    <h5 class="fw-bold mb-0 text-white"><i class="fa-solid fa-cloud-bolt text-info me-2"></i>The Waiter Cloud Sync — 6-Device Hub</h5>
                                    <small class="text-light opacity-75">Run on hardware you already own — no £5,000 proprietary till contracts</small>
                                </div>
                                <span class="badge bg-success"><i class="fa-solid fa-circle-check me-1"></i>6/6 Nodes Synced</span>
                            </div>
                            <div class="row g-2">
                                <div class="col-sm-6">
                                    <div class="p-2 rounded border border-secondary bg-secondary bg-opacity-25 d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fa-solid fa-mobile-screen-button text-info me-2"></i>
                                            <strong class="small">1. Smartphone QR Menu</strong>
                                            <small class="d-block text-light opacity-75">Guest BYOD Ordering</small>
                                        </div>
                                        <a href="/?table=1" class="btn btn-xs btn-info text-dark fw-bold py-0 px-2">Open</a>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="p-2 rounded border border-secondary bg-secondary bg-opacity-25 d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fa-solid fa-tablet-screen-button text-warning me-2"></i>
                                            <strong class="small">2. Waiter Floor Tablet</strong>
                                            <small class="d-block text-light opacity-75">2D Map & Concierge</small>
                                        </div>
                                        <span class="badge bg-success">Active</span>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="p-2 rounded border border-secondary bg-secondary bg-opacity-25 d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fa-solid fa-tv text-success me-2"></i>
                                            <strong class="small">3. Any Existing Smart TV</strong>
                                            <small class="d-block text-light opacity-75">Live KDS Pickup Screen</small>
                                        </div>
                                        <a href="/tv" target="_blank" class="btn btn-xs btn-outline-light fw-bold py-0 px-2">Launch TV</a>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="p-2 rounded border border-secondary bg-secondary bg-opacity-25 d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fa-solid fa-barcode text-info me-2"></i>
                                            <strong class="small">4. Counter POS & Scanner</strong>
                                            <small class="d-block text-light opacity-75">USB Barcode & Till Kiosk</small>
                                        </div>
                                        <a href="/terminal" target="_blank" class="btn btn-xs btn-outline-info fw-bold py-0 px-2">Launch POS</a>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="p-2 rounded border border-secondary bg-secondary bg-opacity-25 d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fa-solid fa-print text-warning me-2"></i>
                                            <strong class="small">5. Thermal Receipt Printer</strong>
                                            <small class="d-block text-light opacity-75">80mm / 58mm ESC/POS</small>
                                        </div>
                                        <button onclick="openThermalPrinterEmulator()" class="btn btn-xs btn-warning text-dark fw-bold py-0 px-2">Test Print</button>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="p-2 rounded border border-secondary bg-secondary bg-opacity-25 d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fa-solid fa-laptop text-primary me-2"></i>
                                            <strong class="small">6. Back-Office PC / Mac</strong>
                                            <small class="d-block text-light opacity-75">Cloud Accounting & VAT</small>
                                        </div>
                                        <span class="badge bg-info text-dark">Cloud Sync</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 1: KDS with Station Routing & Sound Generator -->
            <div class="tab-pane fade" id="kds" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-fire-burner text-warning me-2"></i>Kitchen Display System (KDS)</h4>
                    <button class="btn btn-sm btn-outline-primary fw-bold" onclick="loadKDS()"><i class="fa-solid fa-rotate me-1"></i> Refresh Orders</button>
                </div>

                <div class="d-flex flex-wrap align-items-center gap-2 mb-3 p-3 bg-white rounded-3 border shadow-sm" id="kdsStationFilterGroup">
                    <span class="small fw-bold text-muted me-1"><i class="fa-solid fa-filter text-primary me-1"></i>Station Filter:</span>
                    <button class="btn btn-sm btn-dark active rounded-pill px-3 py-1 fw-bold" onclick="filterKdsStation('ALL', this)">All Stations <span class="badge bg-secondary ms-1" id="stBadgeALL">0</span></button>
                    <button class="btn btn-sm btn-outline-dark rounded-pill px-3 py-1 fw-bold" onclick="filterKdsStation('GRILL', this)">🔥 Grill <span class="badge bg-secondary ms-1" id="stBadgeGRILL">0</span></button>
                    <button class="btn btn-sm btn-outline-dark rounded-pill px-3 py-1 fw-bold" onclick="filterKdsStation('FRYER', this)">🍟 Fryer & Sides <span class="badge bg-secondary ms-1" id="stBadgeFRYER">0</span></button>
                    <button class="btn btn-sm btn-outline-dark rounded-pill px-3 py-1 fw-bold" onclick="filterKdsStation('BAR', this)">🍺 Bar & Drinks <span class="badge bg-secondary ms-1" id="stBadgeBAR">0</span></button>
                    <button class="btn btn-sm btn-outline-dark rounded-pill px-3 py-1 fw-bold" onclick="filterKdsStation('LARDER', this)">🍰 Dessert & Pantry <span class="badge bg-secondary ms-1" id="stBadgeLARDER">0</span></button>
                    <button class="btn btn-sm btn-outline-dark rounded-pill px-3 py-1 fw-bold" onclick="filterKdsStation('HOT_LINE', this)">HOT Line Pass <span class="badge bg-secondary ms-1" id="stBadgeHOT_LINE">0</span></button>
                    
                    <button class="btn btn-sm btn-outline-dark rounded-pill px-3 py-1 fw-bold me-1" onclick="openThermalPrinterEmulator()"><i class="fa-solid fa-print me-1 text-primary"></i> Thermal Docket</button>
                    <button class="btn btn-sm btn-warning text-dark rounded-pill px-3 py-1 fw-bold me-2" onclick="openChefRecipeModal()"><i class="fa-solid fa-book-open-reader me-1"></i> Chef Recipes & Natasha's Law Allergens</button>
                    <button class="btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold ms-auto" id="chimeToggleBtn" onclick="toggleOrderChime()"><i class="fa-solid fa-volume-high me-1"></i> Audio Chime On</button>
                </div>

                <div id="kdsContainer" class="row g-3">
                    <!-- Loaded dynamically -->
                </div>
            </div>

            <!-- TAB 1B: Interactive Delivery Aggregator Command Center (Deliveroo / UberEats / Deliverect / Toast) -->
            <div class="tab-pane fade" id="delivery" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-motorcycle text-info me-2"></i>Delivery Aggregator & POS Command Center</h4>
                        <small class="text-muted">Synchronize live menus & stock to Deliveroo, UberEats, Deliverect, and Toast POS or simulate inbound delivery orders.</small>
                    </div>
                    <button class="btn btn-sm btn-outline-primary fw-bold" onclick="loadDeliveryHub()"><i class="fa-solid fa-rotate me-1"></i> Refresh Channels</button>
                </div>

                <!-- Live Aggregator Channel Status Cards -->
                <div class="row g-3 mb-4" id="deliveryChannelsGrid">
                    <!-- Dynamically populated -->
                </div>

                <!-- Simulate Live Inbound Delivery Webhook & Menu Sync -->
                <div class="row g-4">
                    <div class="col-md-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-2 text-dark"><i class="fa-solid fa-bolt text-warning me-2"></i>Simulate Inbound Delivery Webhook</h5>
                            <p class="small text-muted mb-3">Test zero-touch order injection from third-party delivery apps straight into your Kitchen KDS.</p>
                            <form onsubmit="triggerSimulatedDeliveryWebhook(event)">
                                <div class="row g-2 mb-3">
                                    <div class="col-6">
                                        <label class="form-label small fw-bold text-muted">Aggregator Platform</label>
                                        <select id="simDeliveryPlatform" class="form-select form-select-sm fw-bold">
                                            <option value="DELIVEROO">🦘 Deliveroo UK</option>
                                            <option value="UBEREATS">🥡 UberEats UK</option>
                                            <option value="DELIVERECT">🔗 Deliverect Hub</option>
                                            <option value="TOAST">🍞 Toast POS</option>
                                        </select>
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label small fw-bold text-muted">Customer Name</label>
                                        <input type="text" id="simDeliveryCustomer" class="form-control form-control-sm" value="Emma Watson (VIP Delivery)" required>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Delivery Drop-off Address / Rider Note</label>
                                    <input type="text" id="simDeliveryAddress" class="form-control form-control-sm" value="14 Covent Garden Piazza, London WC2E 8HD" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Select Combo Items</label>
                                    <select id="simDeliveryItems" class="form-select form-select-sm">
                                        <option value="item-1,item-3">Fish & Chips + Craft IPA Pint (£20.70)</option>
                                        <option value="item-2,item-4">Wagyu Beef Burger + Truffle Fries (£22.00)</option>
                                        <option value="item-1,item-2,item-5">Family Feast: Cod + Wagyu Burger + Sticky Toffee Pudding (£38.00)</option>
                                    </select>
                                </div>
                                <button type="submit" class="btn btn-info text-dark fw-bold w-100"><i class="fa-solid fa-paper-plane me-1"></i> Inject Live Delivery Order to KDS</button>
                            </form>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-2 text-dark"><i class="fa-solid fa-cloud-arrow-up text-success me-2"></i>Last Aggregator Menu Sync Payload</h5>
                            <p class="small text-muted mb-2">Click "Sync Menu" on any channel card above to push live pricing, stock quantities, and Natasha's Law allergen tags.</p>
                            <pre id="deliverySyncResultBox" class="p-3 bg-dark text-info rounded-3 small mb-0" style="max-height: 230px; overflow-y: auto; font-size: 0.78rem;">// Click "Sync Menu" on Deliveroo or UberEats above to inspect live JSON catalog payload...</pre>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: Interactive Table QR Generator Studio -->
            <div class="tab-pane fade" id="qrstudio" role="tabpanel">
                <div class="card card-custom p-4 bg-white shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-qrcode text-primary me-2"></i>Interactive Table QR Studio</h4>
                            <p class="text-muted small mb-0">Generate, preview, and download custom table QR cards for instant guest scanning.</p>
                        </div>
                        <a href="/api/qr/cards/pdf?tables=12" target="_blank" class="btn btn-sm btn-danger fw-bold"><i class="fa-solid fa-file-pdf me-1"></i> Download PDF Table Tents (1-12)</a>
                    </div>

                    <div class="row g-4">
                        <div class="col-md-5">
                            <div class="p-3 border rounded-3 bg-light">
                                <label class="form-label fw-bold text-dark mb-1">Select Table Number</label>
                                <div class="input-group mb-3">
                                    <span class="input-group-text fw-bold">Table #</span>
                                    <input type="number" id="qrStudioTableNum" class="form-control form-control-lg fw-bold" value="1" min="1" max="100" oninput="updateQrStudioPreview()">
                                </div>

                                <label class="form-label small fw-bold text-muted mb-1">Quick Select Slider (1 to 50)</label>
                                <input type="range" class="form-range mb-4" id="qrStudioSlider" min="1" max="50" value="1" oninput="document.getElementById('qrStudioTableNum').value=this.value; updateQrStudioPreview();">

                                <div class="d-grid gap-2">
                                    <a id="btnDownloadPng" href="/api/qr/table/1" target="_blank" class="btn btn-primary fw-bold py-2"><i class="fa-solid fa-download me-1"></i> Download High-Res PNG</a>
                                    <a id="btnOpenTableUrl" href="/?table=1" target="_blank" class="btn btn-outline-dark fw-bold"><i class="fa-solid fa-arrow-up-right-from-square me-1"></i> Test Table Ordering Page</a>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-7">
                            <div class="qr-tent-mockup">
                                <h3 class="fw-extrabold text-dark mb-1" id="qrTentBrandTitle">THE WAITER UK</h3>
                                <h1 class="fw-black text-primary display-4 mb-2" id="qrTentTableLabel">TABLE #1</h1>
                                <div class="my-3">
                                    <img id="qrStudioPreviewImg" src="" alt="Table QR Code Preview" style="width: 200px; height: 200px;" class="border p-2 bg-white rounded">
                                </div>
                                <h5 class="fw-bold text-dark mb-1"><i class="fa-solid fa-camera me-1"></i> SCAN TO VIEW MENU & ORDER</h5>
                                <p class="small text-muted mb-2">Point your smartphone camera at the QR code above.<br>No app download required.</p>
                                <span class="badge bg-light text-dark border small"><i class="fa-solid fa-link me-1"></i> <span id="qrStudioTargetUrl">http://127.0.0.1:5050/?table=1</span></span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h5 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-grip me-2 text-info"></i>Quick Table QR Cards (Tables 1 to 12)</h5>
                    <div id="batchQrGridContainer" class="row g-3">
                        <!-- Loaded dynamically -->
                    </div>
                </div>
            </div>

            <!-- TAB 3: White-Label Brand & Theme Customizer -->
            <div class="tab-pane fade" id="branding" role="tabpanel">
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-palette text-primary me-2"></i>White-Label Brand & Theme Customizer</h4>
                            <p class="text-muted small mb-0">Customize restaurant name, brand colors, typography, and guest welcome messaging in real-time.</p>
                        </div>
                        <button class="btn btn-sm btn-success fw-bold px-3 py-2" onclick="saveBrandConfig()"><i class="fa-solid fa-floppy-disk me-1"></i> Save & Publish Brand Theme</button>
                    </div>

                    <div class="row g-4">
                        <div class="col-md-6">
                            <form id="brandForm">
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Restaurant / Brand Name</label>
                                    <input type="text" id="cfgBrandName" class="form-control" value="The Waiter" oninput="previewBrandTheme()">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Store Subheading</label>
                                    <input type="text" id="cfgStoreSubheading" class="form-control" value="Covent Garden Flagship (UK)" oninput="previewBrandTheme()">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Guest Welcome Message</label>
                                    <input type="text" id="cfgGuestWelcomeMsg" class="form-control" value="Welcome! Tap dishes below to order directly from Table #" oninput="previewBrandTheme()">
                                </div>
                                <div class="row g-2 mb-3">
                                    <div class="col-6">
                                        <label class="form-label small fw-bold text-muted">Primary Brand Color</label>
                                        <input type="color" id="cfgPrimaryColor" class="form-control form-control-color w-100" value="#0f172a" oninput="previewBrandTheme()">
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label small fw-bold text-muted">Accent Color</label>
                                        <input type="color" id="cfgAccentColor" class="form-control form-control-color w-100" value="#0284c7" oninput="previewBrandTheme()">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Typography Font Family</label>
                                    <select id="cfgFontFamily" class="form-select" onchange="previewBrandTheme()">
                                        <option value="Plus Jakarta Sans">Plus Jakarta Sans (Modern Clean)</option>
                                        <option value="Inter">Inter (Enterprise Slate)</option>
                                        <option value="Outfit">Outfit (High Luxury)</option>
                                    </select>
                                </div>
                            </form>
                        </div>

                        <div class="col-md-6">
                            <div class="p-3 border rounded-3 bg-light h-100">
                                <h6 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-eye text-info me-2"></i>Live Theme Preview</h6>
                                <div class="p-3 rounded-3 text-white mb-3" id="prevHeader" style="background: #0f172a;">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <h5 class="fw-bold mb-0" id="prevBrandName">The Waiter</h5>
                                        <span class="badge bg-info text-dark fw-bold">Table #5</span>
                                    </div>
                                    <small class="opacity-75" id="prevSubheading">Covent Garden Flagship (UK)</small>
                                </div>
                                <div class="p-3 bg-white rounded-3 border mb-3">
                                    <small class="text-muted d-block mb-1">Guest Welcome Subtitle:</small>
                                    <strong class="text-dark" id="prevWelcomeMsg">Welcome! Tap dishes below to order directly from Table #5</strong>
                                </div>
                                <button class="btn btn-sm w-100 text-white fw-bold py-2" id="prevBtn" style="background-color: #0284c7;">Sample Add-to-Cart Button</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 4: Bookings -->
            <div class="tab-pane fade" id="bookings" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-calendar-check text-success me-2"></i>Guest Reservations</h4>
                    <button class="btn btn-sm btn-success fw-bold" data-bs-toggle="modal" data-bs-target="#bookingModal"><i class="fa-solid fa-plus me-1"></i> New Reservation</button>
                </div>
                <div class="card card-custom p-3 bg-white shadow-sm">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Ref</th>
                                    <th>Guest Name</th>
                                    <th>Party</th>
                                    <th>Date & Time</th>
                                    <th>Special Requests</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="bookingsTableBody">
                                <!-- Loaded dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB 5: Inventory Stock & Automated POs -->
            <div class="tab-pane fade" id="inventory" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-boxes-stacked text-primary me-2"></i>Stock & Purchase Orders</h4>
                    <button class="btn btn-sm btn-outline-primary fw-bold" onclick="loadInventory()"><i class="fa-solid fa-rotate me-1"></i> Refresh</button>
                </div>
                <div id="inventoryContainer" class="row g-3 mb-4">
                    <!-- Loaded dynamically -->
                </div>
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h5 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-truck-ramp-box text-info me-2"></i>Supplier Purchase Orders</h5>
                    <div id="purchaseOrdersContainer" class="row g-3">
                        <!-- Loaded dynamically -->
                    </div>
                </div>
            </div>

            <!-- TAB 6: Kitchen Waste Tracker -->
            <div class="tab-pane fade" id="waste" role="tabpanel">
                <div class="row g-4">
                    <div class="col-md-5">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h5 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-trash-can text-danger me-2"></i>Log Kitchen Waste</h5>
                            <form id="wasteLogForm" onsubmit="submitWasteLog(event)">
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Item Wasted</label>
                                    <select id="wasteItemId" class="form-select form-select-sm" required>
                                        <option value="item-1">Fresh Atlantic Cod (Fillet)</option>
                                        <option value="item-2">Wagyu Beef Burger (200g Patty)</option>
                                        <option value="item-3">Truffle Parmesan Fries</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Quantity</label>
                                    <input type="number" id="wasteQty" class="form-control form-control-sm" value="1" min="1" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Reason</label>
                                    <select id="wasteReason" class="form-select form-select-sm">
                                        <option value="SPOILAGE">Spoilage / Expired</option>
                                        <option value="PREP_TRIM">Preparation Trim</option>
                                        <option value="OVER_PREP">Over-Prepared Unsold</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Staff Name</label>
                                    <input type="text" id="wasteStaffName" class="form-control form-control-sm" value="Head Chef" required>
                                </div>
                                <button type="submit" class="btn btn-danger w-100 fw-bold"><i class="fa-solid fa-floppy-disk me-1"></i> Record Waste</button>
                            </form>
                        </div>
                    </div>

                    <div class="col-md-7">
                        <div class="card card-custom p-4 bg-white shadow-sm mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-chart-pie text-warning me-2"></i>Waste Financial Analytics</h5>
                                <a href="/api/waste/report/pdf" target="_blank" class="btn btn-sm btn-outline-danger"><i class="fa-solid fa-file-pdf me-1"></i> Waste Audit PDF</a>
                            </div>
                            <div id="wasteAnalyticsContent" class="row text-center">
                                <!-- Loaded dynamically -->
                            </div>
                        </div>
                        <div class="card card-custom p-3 bg-white shadow-sm">
                            <h6 class="fw-bold mb-2">Recent Kitchen Waste Log</h6>
                            <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
                                <table class="table table-sm table-hover align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th>Time</th>
                                            <th>Item</th>
                                            <th>Qty</th>
                                            <th>Reason</th>
                                            <th>Staff</th>
                                            <th>Cost</th>
                                        </tr>
                                    </thead>
                                    <tbody id="wasteLogsTableBody">
                                        <!-- Loaded dynamically -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 7: MTD VAT & Transfers -->
            <div class="tab-pane fade" id="tax" role="tabpanel">
                <div class="row g-4">
                    <div class="col-md-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-building-columns text-success me-2"></i>HMRC MTD VAT Ledger (UK)</h5>
                                <a href="/api/tax/report/pdf" target="_blank" class="btn btn-sm btn-success fw-bold"><i class="fa-solid fa-file-pdf me-1"></i> HMRC PDF</a>
                            </div>
                            <div id="vatLedgerContainer">
                                <!-- Loaded dynamically -->
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-truck-arrow-right text-primary me-2"></i>Inter-Venue Stock Transfer</h5>
                            <form id="transferForm" onsubmit="submitStoreTransfer(event)">
                                <div class="row g-2 mb-2">
                                    <div class="col-6">
                                        <label class="form-label small fw-bold text-muted">Source Venue</label>
                                        <select id="transferSourceVenue" class="form-select form-select-sm">
                                            <option value="venue-1">Covent Garden Flagship</option>
                                            <option value="venue-2">Soho Bistro</option>
                                        </select>
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label small fw-bold text-muted">Target Venue</label>
                                        <select id="transferTargetVenue" class="form-select form-select-sm">
                                            <option value="venue-2" selected>Soho Bistro</option>
                                            <option value="venue-1">Covent Garden Flagship</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mb-2">
                                    <label class="form-label small fw-bold text-muted">Stock Item & Qty</label>
                                    <div class="input-group input-group-sm">
                                        <select id="transferItemId" class="form-select">
                                            <option value="item-1">Fresh Atlantic Cod (Fillet)</option>
                                            <option value="item-2">Wagyu Beef Burger (200g Patty)</option>
                                        </select>
                                        <input type="number" id="transferQty" class="form-control" value="10" min="1" style="max-width: 90px;">
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary btn-sm w-100 fw-bold mb-3"><i class="fa-solid fa-paper-plane me-1"></i> Dispatch Transfer Waybill</button>
                            </form>
                            <div id="transfersListContainer" style="max-height: 180px; overflow-y: auto;">
                                <!-- Loaded dynamically -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 8: Guest NPS & Private Feedback -->
            <div class="tab-pane fade" id="feedback" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-star text-warning me-2"></i>Guest Sentiment & NPS</h4>
                    <a href="/api/feedback/report/pdf" target="_blank" class="btn btn-sm btn-outline-primary fw-bold"><i class="fa-solid fa-file-pdf me-1"></i> NPS Report PDF</a>
                </div>
                <div class="row g-3 mb-4">
                    <div class="col-md-4">
                        <div class="card card-custom p-4 bg-white text-center shadow-sm">
                            <span class="small fw-bold text-muted text-uppercase mb-2">Net Promoter Score</span>
                            <div class="fs-1 fw-bold text-primary" id="npsScoreVal">+0</div>
                            <small class="text-muted" id="npsBreakdownText">0 Promoters | 0 Passives | 0 Detractors</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <span class="small fw-bold text-muted text-uppercase mb-2">Sentiment Distribution</span>
                            <div id="sentimentDistributionContent" class="py-2"></div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <span class="small fw-bold text-muted text-uppercase mb-2">Manager Action Alerts</span>
                            <div id="managerAlertsContent" class="py-1"></div>
                        </div>
                    </div>
                </div>
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h5 class="fw-bold mb-3 text-dark">Recent Reviews</h5>
                    <div id="reviewsContainer" class="row g-3"></div>
                </div>
            </div>

            <!-- TAB 9: AI Demand Forecasting -->
            <div class="tab-pane fade" id="forecasting" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-brain text-info me-2"></i>AI Demand Forecasting</h4>
                    <a href="/api/forecasting/report/pdf" target="_blank" class="btn btn-sm btn-info text-dark fw-bold"><i class="fa-solid fa-file-pdf me-1"></i> AI Report PDF</a>
                </div>
                <div class="row g-4">
                    <div class="col-md-7">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h5 class="fw-bold mb-3 text-dark">Predicted Kitchen Prep Demand</h5>
                            <div class="table-responsive">
                                <table class="table table-sm table-hover align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th>Dish</th>
                                            <th>Avg Sales</th>
                                            <th>Predicted Prep</th>
                                            <th>Confidence</th>
                                        </tr>
                                    </thead>
                                    <tbody id="aiForecastTableBody"></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-5">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h5 class="fw-bold mb-3 text-dark">Menu Engineering Matrix</h5>
                            <div id="menuMatrixContainer"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 10: Staff Clock & Tronc -->
            <div class="tab-pane fade" id="staff" role="tabpanel">
                <div class="row g-4">
                    <div class="col-md-5">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h4 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-clock text-primary me-2"></i>Staff Shift Clock</h4>
                            <p class="text-muted small">Enter staff PIN (Manager: <code>1234</code>, Chef: <code>5555</code>, Server: <code>7777</code>)</p>
                            <input type="password" id="staffPinInput" class="form-control text-center fs-3 fw-bold mb-3" maxlength="4" placeholder="••••">
                            <div class="row g-2">
                                <div class="col-6">
                                    <button class="btn btn-success w-100 fw-bold py-2" onclick="staffClockIn()"><i class="fa-solid fa-right-to-bracket me-1"></i> Clock In</button>
                                </div>
                                <div class="col-6">
                                    <button class="btn btn-danger w-100 fw-bold py-2" onclick="staffClockOut()"><i class="fa-solid fa-right-from-bracket me-1"></i> Clock Out</button>
                                </div>
                            </div>
                        </div>
                        <div class="card card-custom p-4 bg-white shadow-sm mt-4">
                            <h5 class="fw-bold mb-2 text-dark"><i class="fa-solid fa-hand-holding-dollar text-warning me-2"></i>12.5% Tronc Pool</h5>
                            <div id="troncSummaryContainer"></div>
                        </div>
                    </div>
                    <div class="col-md-7">
                        <div class="card card-custom p-4 bg-white shadow-sm mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold mb-0 text-dark">Active Roster & Labor Analytics</h5>
                                <span class="badge bg-primary fs-6" id="activeStaffBadge">0 Active</span>
                            </div>
                            <div id="laborSummaryContent" class="row text-center mb-1"></div>
                        </div>
                        <div class="card card-custom p-3 bg-white shadow-sm">
                            <h6 class="fw-bold mb-2">Shift History Log</h6>
                            <div id="shiftHistoryContainer" style="max-height: 250px; overflow-y: auto;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 11: Interactive Z-Report Financial Reconciliation, Promo Studio & CSV Hub -->
            <div class="tab-pane fade" id="reports" role="tabpanel">
                <div class="row g-4 mb-4">
                    <!-- Left Column: End-of-Day Z-Report Financial Reconciliation -->
                    <div class="col-lg-7">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-cash-register text-primary me-2"></i>End-of-Day Z-Report Financial Reconciliation</h5>
                                    <small class="text-muted">Live shift settlement, net taxable revenue, VAT & ticket velocity</small>
                                </div>
                                <a href="/api/finance/z-report/pdf" target="_blank" class="btn btn-sm btn-danger fw-bold"><i class="fa-solid fa-file-pdf me-1"></i> Official Z-Report PDF</a>
                            </div>
                            <div id="zReportInteractiveContainer">
                                <!-- Populated dynamically by loadZReportAndPromos() -->
                            </div>
                        </div>
                    </div>

                    <!-- Right Column: Dynamic Happy Hour & Promo Code Campaign Studio -->
                    <div class="col-lg-5">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-1 text-dark"><i class="fa-solid fa-tags text-warning me-2"></i>Happy Hour & Promo Campaign Studio</h5>
                            <small class="text-muted d-block mb-3">Create instant discount codes broadcasted live to all Guest QR Menus</small>
                            <form onsubmit="createPromoCampaign(event)" class="row g-2 mb-3">
                                <div class="col-7">
                                    <input type="text" id="newPromoCodeInput" class="form-control form-control-sm text-uppercase fw-bold" placeholder="CODE (e.g. HAPPYHOUR25)" required>
                                </div>
                                <div class="col-5">
                                    <div class="input-group input-group-sm">
                                        <input type="number" id="newPromoDiscountInput" class="form-control fw-bold" placeholder="25" min="5" max="90" value="25" required>
                                        <span class="input-group-text">% OFF</span>
                                    </div>
                                </div>
                                <div class="col-12">
                                    <button type="submit" class="btn btn-sm btn-dark text-warning w-100 fw-bold"><i class="fa-solid fa-bullhorn me-1"></i> Launch Live Promo Campaign</button>
                                </div>
                            </form>
                            <h6 class="fw-bold small text-uppercase text-muted mb-2">Active Promo Codes on Guest Menu</h6>
                            <div id="staffPromosListContainer" class="vstack gap-2">
                                <!-- Populated dynamically by loadZReportAndPromos() -->
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h5 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-file-csv text-success me-2"></i>Accounting & Audit CSV Data Exports</h5>
                    <div class="row g-3">
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-receipt fs-2 text-primary mb-2"></i>
                                <h6 class="fw-bold">Orders CSV</h6>
                                <a href="/api/export/orders/csv" target="_blank" class="btn btn-primary btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-boxes-stacked fs-2 text-success mb-2"></i>
                                <h6 class="fw-bold">Inventory CSV</h6>
                                <a href="/api/export/inventory/csv" target="_blank" class="btn btn-success btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-comments fs-2 text-warning mb-2"></i>
                                <h6 class="fw-bold">Reviews CSV</h6>
                                <a href="/api/export/reviews/csv" target="_blank" class="btn btn-warning text-dark btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-file-pdf fs-2 text-danger mb-2"></i>
                                <h6 class="fw-bold">Daily Z-Report PDF</h6>
                                <a href="/api/finance/z-report/pdf" target="_blank" class="btn btn-danger btn-sm mt-auto"><i class="fa-solid fa-file-pdf me-1"></i> Download</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 11A: 💷 Money & Margins Hub (Xero/QuickBooks/Sage/FreeAgent, Recipe Costing & GP%, Booker/Bidfood/Brakes & Invoice OCR, Rota Labour % & Holiday Accrual) -->
            <div class="tab-pane fade" id="margins" role="tabpanel">
                <!-- Top Summary Banner -->
                <div class="card card-custom p-4 bg-dark text-white shadow-sm mb-4 border-start border-5 border-success">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                        <div>
                            <div class="d-flex flex-wrap gap-2 mb-2">
                                <span class="badge bg-success fw-bold"><i class="fa-solid fa-building-columns me-1"></i>PAY-BY-BANK (0.2% FEE)</span>
                                <span class="badge bg-info text-dark fw-bold"><i class="fa-solid fa-rotate me-1"></i>XERO • QUICKBOOKS • SAGE • FREEAGENT</span>
                                <span class="badge bg-warning text-dark fw-bold"><i class="fa-solid fa-chart-pie me-1"></i>LIVE DISH GP% ENGINE</span>
                                <span class="badge bg-primary fw-bold"><i class="fa-solid fa-truck-field me-1"></i>BOOKER • BIDFOOD • BRAKES OCR</span>
                            </div>
                            <h4 class="fw-bold mb-1 text-white">💷 Money, Gross Profit (GP%) & Margin Protection Command Center</h4>
                            <small class="text-light opacity-75">MTD Accounting Sync • Dish Recipe Costing & GP% • Wholesaler EDI & Invoice Scanning • Rota Labour % & 12.07% UK Holiday Accrual</small>
                        </div>
                        <a href="/api/margins/payroll/export/csv" target="_blank" class="btn btn-success fw-bold px-3 py-2 shadow">
                            <i class="fa-solid fa-file-csv me-1"></i> Export UK Payroll & Holiday Accrual CSV
                        </a>
                    </div>
                </div>

                <!-- Row 1: UK Accounting Integrations (Xero, QuickBooks, Sage, FreeAgent) -->
                <div class="card card-custom p-4 bg-white shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-book-journal-whills text-primary me-2"></i>1. UK Making Tax Digital (MTD) Accounting Integrations</h5>
                            <small class="text-muted">1-Click automated daily sales, VAT control & COGS journal posting to Xero, QuickBooks, Sage, and FreeAgent</small>
                        </div>
                        <span class="badge bg-success">HMRC MTD Bridged</span>
                    </div>
                    <div class="row g-3" id="accountingProvidersGrid">
                        <!-- Populated dynamically by loadMoneyAndMarginsHub() -->
                    </div>
                </div>

                <!-- Row 2: Live Recipe Costing & GP% Matrix + UK Wholesalers (Booker, Bidfood, Brakes) & Invoice Scanner -->
                <div class="row g-4 mb-4">
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-success">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-scale-unbalanced-flip text-success me-2"></i>2. Live Recipe Costing & Dish GP%</h5>
                                <span class="badge bg-dark text-warning" id="avgMenuGpBadge">Avg Menu GP: 72.8%</span>
                            </div>
                            <small class="text-muted d-block mb-3">Live Cost of Goods Sold (COGS), Net Price (excl. 20% VAT), Gross Profit %, wastage loss & low-stock alerts.</small>
                            <div id="recipeGpMatrixContainer" class="vstack gap-2">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-warning">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-truck-ramp-box text-warning me-2"></i>3. UK Wholesaler Reordering & Invoice OCR Scanner</h5>
                                <span class="badge bg-primary">Booker • Bidfood • Brakes</span>
                            </div>
                            <small class="text-muted d-block mb-3">Transmit 1-click EDI reorders or scan supplier delivery invoices to auto-detect ingredient price hikes and update live GP%.</small>

                            <div id="ukWholesalersContainer" class="vstack gap-2 mb-3">
                                <!-- Populated dynamically -->
                            </div>

                            <!-- AI Supplier Invoice OCR Scanner -->
                            <div class="p-3 bg-light rounded-3 border">
                                <h6 class="fw-bold small text-uppercase text-dark mb-2"><i class="fa-solid fa-file-invoice text-danger me-1"></i>AI Supplier Delivery Invoice Scanner (Price-Hike Detector)</h6>
                                <form onsubmit="scanSupplierInvoice(event)" class="row g-2 mb-2">
                                    <div class="col-sm-4">
                                        <select id="scanSupplierSelect" class="form-select form-select-sm fw-bold">
                                            <option value="BRAKES">Brakes (Sysco UK)</option>
                                            <option value="BIDFOOD">Bidfood UK</option>
                                            <option value="BOOKER">Booker Wholesale</option>
                                        </select>
                                    </div>
                                    <div class="col-sm-4">
                                        <div class="input-group input-group-sm">
                                            <span class="input-group-text">Cod £</span>
                                            <input type="number" step="0.05" id="scanCodCostInput" class="form-control fw-bold" value="2.75" required>
                                        </div>
                                    </div>
                                    <div class="col-sm-4">
                                        <button type="submit" class="btn btn-sm btn-dark text-warning w-100 fw-bold"><i class="fa-solid fa-camera me-1"></i> Scan Invoice</button>
                                    </div>
                                </form>
                                <div id="scannedInvoicesAlertBox" class="small"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Row 3: Live Labour Cost % vs Sales (Slide 2 Labour Crisis), 12.07% UK Holiday Accrual & Payroll -->
                <div class="card card-custom p-4 bg-white shadow-sm border-top border-4 border-info">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                        <div>
                            <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-users-gear text-info me-2"></i>4. Live Labour Cost % vs. Sales, Rota & UK Holiday Accrual (12.07%)</h5>
                            <small class="text-muted">Tied directly to weekly staff rotas, Employer NIC (15%), and UK Working Time Regulations 5.6-week (12.07%) holiday accrual</small>
                        </div>
                        <div class="d-flex gap-2 align-items-center">
                            <span class="badge bg-success fs-6 px-3 py-2" id="liveLabourRatioBadge">Labour vs Sales: 24.1% (Target ≤28%)</span>
                            <a href="/api/margins/payroll/export/csv" target="_blank" class="btn btn-sm btn-outline-dark fw-bold"><i class="fa-solid fa-download me-1"></i> Payroll CSV</a>
                        </div>
                    </div>
                    <div id="rotaLabourPayrollContainer" class="table-responsive">
                        <!-- Populated dynamically -->
                    </div>
                </div>
            </div>

            <!-- TAB 11B: 🇬🇧 UK Statutory Compliance, Natasha's Law, Tips Act 2024, Challenge 25, EHO Food Safety & GDPR Hub -->
            <div class="tab-pane fade" id="ukcompliance" role="tabpanel">
                <!-- Top UK Sovereign Cloud, GDPR & Cyber Essentials Banner -->
                <div class="card card-custom p-4 bg-dark text-white shadow-sm mb-4 border-start border-5 border-info">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                        <div>
                            <div class="d-flex flex-wrap gap-2 mb-2">
                                <span class="badge bg-info text-dark fw-bold"><i class="fa-solid fa-server me-1"></i>UK LONDON REGION (eu-west-2)</span>
                                <span class="badge bg-success fw-bold"><i class="fa-solid fa-lock me-1"></i>NCSC CYBER ESSENTIALS</span>
                                <span class="badge bg-warning text-dark fw-bold"><i class="fa-solid fa-user-Halved me-1"></i>UK GDPR & DPA 2018</span>
                                <span class="badge bg-primary fw-bold"><i class="fa-solid fa-star me-1"></i>FSA 5-STAR EHO READY</span>
                            </div>
                            <h4 class="fw-bold mb-1 text-white">🇬🇧 UK Statutory Hospitality Compliance & Environmental Health (EHO) Hub</h4>
                            <small class="text-light opacity-75">Natasha's Law (PPDS) • Employment (Allocation of Tips) Act Oct 2024 • Challenge 25 • FSA SFBB / HACCP • HMRC VAT 709/1</small>
                        </div>
                        <a href="/api/uk-compliance/eho-report/pdf" target="_blank" class="btn btn-warning text-dark fw-bold px-3 py-2 shadow">
                            <i class="fa-solid fa-file-shield me-1"></i> Export EHO & Compliance Audit PDF
                        </a>
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <!-- Pillar 1: Natasha's Law (PPDS) Ingredient-to-14-Allergen Builder & Label Printer -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-warning">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-tag text-warning me-2"></i>1. Natasha's Law (PPDS) Label Engine</h5>
                                <span class="badge bg-dark text-warning">14 UK FSA Allergens</span>
                            </div>
                            <small class="text-muted d-block mb-3">Build dishes from raw ingredients, auto-tag the 14 UK allergens in <strong>BOLD CAPITALS</strong>, and print PPDS grab-and-go labels.</small>

                            <div class="row g-2 mb-3">
                                <div class="col-sm-5">
                                    <select id="ppdsDishSelect" class="form-select form-select-sm fw-bold" onchange="previewNatashasLawLabel()">
                                        <option value="item-1">Brixham Cod Fish & Chips</option>
                                        <option value="item-2">British Wagyu Beef Burger</option>
                                        <option value="item-4">Truffle & Parmesan Fries</option>
                                        <option value="item-5">Sticky Toffee Pudding Pot</option>
                                    </select>
                                </div>
                                <div class="col-sm-7">
                                    <div class="input-group input-group-sm">
                                        <input type="text" id="ppdsCustomIngInput" class="form-control" placeholder="Or custom ingredients (e.g. Wheat Flour, Milk, Egg, Mustard)">
                                        <button class="btn btn-dark fw-bold" onclick="buildCustomPpdsLabel()">Auto-Tag</button>
                                    </div>
                                </div>
                            </div>

                            <!-- Printable PPDS Grab-and-Go Sticker Preview -->
                            <div id="ppdsLabelPreviewBox" class="p-3 rounded-3 border border-2 border-dark bg-light small mb-3" style="font-family: 'Segoe UI', sans-serif;">
                                <!-- Populated dynamically -->
                            </div>
                            <button class="btn btn-sm btn-outline-dark fw-bold w-100" onclick="printPpdsGrabAndGoLabel()">
                                <i class="fa-solid fa-print me-1"></i> Print Compliant PPDS Grab-and-Go Label
                            </button>
                        </div>
                    </div>

                    <!-- Pillar 2: Employment (Allocation of Tips) Act 2023 (Effective Oct 2024) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-success">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-hand-holding-dollar text-success me-2"></i>2. Employment (Allocation of Tips) Act 2024</h5>
                                <span class="badge bg-success">100% Pass-Through (0% Ded.)</span>
                            </div>
                            <div id="tipsActPolicyBox" class="p-2 px-3 bg-success bg-opacity-10 border border-success rounded-3 small mb-3">
                                <!-- Written policy summary -->
                            </div>
                            <form onsubmit="recordUkTipPayout(event)" class="row g-2 mb-3">
                                <div class="col-sm-4">
                                    <input type="text" id="tipStaffName" class="form-control form-control-sm" placeholder="Staff Name" required>
                                </div>
                                <div class="col-sm-3">
                                    <input type="text" id="tipStaffRole" class="form-control form-control-sm" placeholder="Role (e.g. FOH)" required>
                                </div>
                                <div class="col-sm-2">
                                    <input type="number" id="tipStaffHours" class="form-control form-control-sm" placeholder="Hrs" value="38" required>
                                </div>
                                <div class="col-sm-3">
                                    <button type="submit" class="btn btn-sm btn-success w-100 fw-bold">+ Log Payout</button>
                                </div>
                            </form>
                            <div id="tipsActPayoutLogsContainer" class="table-responsive" style="max-height: 175px; overflow-y: auto;">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <!-- Pillar 3: Challenge 25 Age Verification & Refusal Register (Licensing Act 2003) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-danger">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-id-card-clip text-danger me-2"></i>3. Challenge 25 Alcohol Age Verification</h5>
                                <span class="badge bg-danger">Licensing Act 2003</span>
                            </div>
                            <small class="text-muted d-block mb-3">Confirm photographic ID (Passport, Driving Licence, PASS) before serving alcohol orders to protect the Premises Licence.</small>

                            <form onsubmit="submitChallenge25Check(event)" class="row g-2 mb-3">
                                <div class="col-sm-3">
                                    <input type="number" id="ch25TableNum" class="form-control form-control-sm" placeholder="Table #" value="4" min="1" required>
                                </div>
                                <div class="col-sm-4">
                                    <select id="ch25IdType" class="form-select form-select-sm">
                                        <option value="UK Photocard Driving Licence">UK Driving Licence</option>
                                        <option value="UK / Biometric Passport">Passport</option>
                                        <option value="PASS Hologram Card">PASS Card (18+)</option>
                                        <option value="NO VALID ID — SALE REFUSED">No ID (Refuse Sale)</option>
                                    </select>
                                </div>
                                <div class="col-sm-5 d-flex gap-1">
                                    <button type="submit" class="btn btn-sm btn-success flex-grow-1 fw-bold" onclick="document.getElementById('ch25Decision').value='APPROVED'">✓ Confirm 18+</button>
                                    <button type="submit" class="btn btn-sm btn-danger fw-bold" onclick="document.getElementById('ch25Decision').value='REFUSED'">✕ Refuse</button>
                                    <input type="hidden" id="ch25Decision" value="APPROVED">
                                </div>
                            </form>
                            <div id="challenge25LogsContainer" class="vstack gap-2" style="max-height: 180px; overflow-y: auto;">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>

                    <!-- Pillar 4: FSA Food Safety Logs (Digital Fridge Temps, Cleaning & HACCP Checklists) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-primary">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-temperature-low text-primary me-2"></i>4. FSA Food Safety, Fridge Temps & HACCP</h5>
                                <span class="badge bg-primary" id="ehoReadyStatusBadge">EHO Inspection Ready</span>
                            </div>
                            <form onsubmit="submitFridgeTempLog(event)" class="row g-2 mb-3">
                                <div class="col-sm-5">
                                    <select id="safetyUnitName" class="form-select form-select-sm">
                                        <option value="Walk-In Cold Room #1|CHILLER">Walk-In Chiller #1 (0-5°C)</option>
                                        <option value="Grab & Go Display Fridge #2|CHILLER">Display Fridge #2 (0-5°C)</option>
                                        <option value="Deep Freeze Chest #1|FREEZER">Freezer Chest #1 (≤-18°C)</option>
                                        <option value="Kitchen Hot Pass Hold|HOT_HOLD">Hot Hold Pass (≥63°C)</option>
                                    </select>
                                </div>
                                <div class="col-sm-3">
                                    <div class="input-group input-group-sm">
                                        <input type="number" step="0.1" id="safetyTempVal" class="form-control fw-bold" value="3.1" required>
                                        <span class="input-group-text">°C</span>
                                    </div>
                                </div>
                                <div class="col-sm-4">
                                    <button type="submit" class="btn btn-sm btn-primary w-100 fw-bold">+ Log Probe Temp</button>
                                </div>
                            </form>
                            <div id="fridgeTempLogsContainer" class="mb-2" style="max-height: 110px; overflow-y: auto;"></div>
                            <h6 class="small fw-bold text-uppercase text-muted mb-1">Daily SFBB Opening / Closing & CCP Checklist:</h6>
                            <div id="haccpChecklistContainer" class="vstack gap-1"></div>
                        </div>
                    </div>
                </div>

                <!-- Pillar 5 & Pillar 6: HMRC VAT Notice 709/1 Matrix & UK GDPR / Cyber Essentials Security -->
                <div class="row g-4">
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-1 text-dark"><i class="fa-solid fa-percent text-info me-2"></i>5. HMRC VAT Notice 709/1 (Eat-In vs Hot vs Cold Takeaway)</h5>
                            <small class="text-muted d-block mb-3">Simulate UK split-rate VAT liability across Eat-In (20%), Hot Takeaway (20%), and Cold Takeaway Grab-and-Go (0% Zero-Rated Food).</small>
                            <div class="btn-group btn-group-sm mb-3" role="group">
                                <button type="button" class="btn btn-dark fw-bold" onclick="simulateHmrcVatMode('EAT_IN')">🍽️ Eat-In (20%)</button>
                                <button type="button" class="btn btn-outline-dark fw-bold" onclick="simulateHmrcVatMode('HOT_TAKEAWAY')">🔥 Hot Takeaway (20%)</button>
                                <button type="button" class="btn btn-outline-dark fw-bold" onclick="simulateHmrcVatMode('COLD_TAKEAWAY')">❄️ Cold Takeaway (0% Food)</button>
                            </div>
                            <div id="hmrcVat709ResultBox" class="p-3 bg-light rounded-3 border small"></div>
                        </div>
                    </div>

                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-1 text-dark"><i class="fa-solid fa-lock text-success me-2"></i>6. UK GDPR, London Cloud Residency & Cyber Essentials</h5>
                            <small class="text-muted d-block mb-3">Sovereign UK data residency, ICO Data Protection Act 2018 compliance, and NCSC Cyber Essentials posture.</small>
                            <div id="ukGdprSecurityBox" class="p-3 bg-light rounded-3 border small"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 12: The Waiter Business Blueprint (Pages 2, 3, 10 & 11) -->
            <div class="tab-pane fade" id="strategy" role="tabpanel">
                <div class="row g-4 mb-4">
                    <!-- Pages 2, 3 & 10: The Operational Shift Comparison Table & Margin Reclaim ROI Calculator -->
                    <div class="col-lg-7">
                        <div class="card card-custom p-4 bg-dark text-white shadow-sm h-100">
                            <span class="badge bg-warning text-dark fw-bold w-auto align-self-start mb-2">PAGES 2, 3 & 10 BLUEPRINT • THE OPERATIONAL SHIFT</span>
                            <h4 class="fw-bold mb-1 text-white">The Old Way vs. The Waiter Blueprint</h4>
                            <p class="small text-light opacity-75 mb-3">Eliminate the UK Hospitality Squeeze: The Labour Crisis, The Tech Bloat (5 separate SaaS bills), and The £5,000 Hardware Trap.</p>

                            <div class="table-responsive mb-3">
                                <table class="table table-dark table-bordered align-middle small mb-0">
                                    <thead>
                                        <tr class="text-warning text-uppercase">
                                            <th>Operational Pillar</th>
                                            <th class="text-danger"><i class="fa-solid fa-xmark me-1"></i>The Old Way</th>
                                            <th class="text-success"><i class="fa-solid fa-check me-1"></i>The Waiter Blueprint</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td class="fw-bold">Software Subscriptions</td>
                                            <td class="text-light opacity-75">Up to 5 different SaaS bills (QR, POS, KDS, Accounting, Loyalty)</td>
                                            <td class="text-info fw-bold">1 Unified Platform</td>
                                        </tr>
                                        <tr>
                                            <td class="fw-bold">Hardware Requirements</td>
                                            <td class="text-light opacity-75">Expensive £5,000 locked-in proprietary tills</td>
                                            <td class="text-info fw-bold">Any existing phone, tablet, PC, or printer</td>
                                        </tr>
                                        <tr>
                                            <td class="fw-bold">Kitchen Workflow</td>
                                            <td class="text-light opacity-75">Manual paper dockets, kitchen shouting, high error rate</td>
                                            <td class="text-info fw-bold">100% synchronised KDS traffic light system</td>
                                        </tr>
                                        <tr>
                                            <td class="fw-bold">Data & Analytics</td>
                                            <td class="text-light opacity-75">Fragmented, impossible to cross-reference</td>
                                            <td class="text-info fw-bold">Real-time, centralised business dashboard</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>

                            <!-- Interactive SaaS & Hardware Trap ROI Calculator -->
                            <div class="p-3 rounded-3 bg-secondary bg-opacity-25 border border-secondary">
                                <h6 class="fw-bold text-warning mb-2"><i class="fa-solid fa-calculator me-2"></i>UK Pub & Restaurant Annual Margin Reclaim Calculator</h6>
                                <div class="row g-2 align-items-end">
                                    <div class="col-sm-4">
                                        <label class="small text-light opacity-75">Legacy SaaS Tools (1-5)</label>
                                        <input type="number" id="roiSaasCount" class="form-control form-control-sm bg-dark text-white border-secondary fw-bold" value="5" min="1" max="10" onchange="calculateBlueprintRoi()">
                                    </div>
                                    <div class="col-sm-4">
                                        <label class="small text-light opacity-75">Tables in Venue</label>
                                        <input type="number" id="roiTablesCount" class="form-control form-control-sm bg-dark text-white border-secondary fw-bold" value="15" min="1" max="100" onchange="calculateBlueprintRoi()">
                                    </div>
                                    <div class="col-sm-4">
                                        <div class="p-2 rounded bg-success bg-opacity-25 border border-success text-center">
                                            <small class="d-block text-light">Est. Annual Savings</small>
                                            <strong class="fs-5 text-warning" id="roiAnnualSavingsLabel">£11,400 / yr</strong>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Page 11: Construct Your Modern Service — UK Consultation & 7-Day Free Trial -->
                    <div class="col-lg-5">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-warning">
                            <span class="badge bg-dark text-warning fw-bold w-auto align-self-start mb-2">PAGE 11 BLUEPRINT • ONBOARDING</span>
                            <h4 class="fw-bold text-dark mb-1">Construct Your Modern Service.</h4>
                            <p class="small text-muted mb-3">Stop paying for software bloat. Start running a unified, highly profitable venue. Book a bespoke consultation and live demonstration with our UK team today.</p>

                            <div class="p-3 bg-light rounded-3 border mb-3 small">
                                <div class="d-flex justify-content-between py-1 border-bottom">
                                    <span class="text-muted fw-bold"><i class="fa-solid fa-globe text-primary me-2"></i>Website:</span>
                                    <a href="https://waiter.com" target="_blank" class="fw-bold text-dark text-decoration-none">waiter.com</a>
                                </div>
                                <div class="d-flex justify-content-between py-1 border-bottom">
                                    <span class="text-muted fw-bold"><i class="fa-solid fa-phone text-success me-2"></i>Direct Phone:</span>
                                    <a href="tel:+447594560831" class="fw-bold text-dark text-decoration-none">+44 7594 560831</a>
                                </div>
                                <div class="d-flex justify-content-between py-1">
                                    <span class="text-muted fw-bold"><i class="fa-solid fa-envelope text-danger me-2"></i>Email:</span>
                                    <a href="mailto:nidaazzielmehdi@gmail.com" class="fw-bold text-dark text-decoration-none">nidaazzielmehdi@gmail.com</a>
                                </div>
                            </div>

                            <form onsubmit="submitBlueprintConsultation(event)" class="vstack gap-2 mb-3">
                                <input type="text" id="consultVenueName" class="form-control form-control-sm" placeholder="Your Pub, Cafe or Restaurant Name" required>
                                <input type="email" id="consultEmail" class="form-control form-control-sm" placeholder="Manager Email or Phone (+44...)" required>
                                <button type="submit" class="btn btn-dark text-warning fw-bold py-2"><i class="fa-solid fa-rocket me-1"></i> Start 7-Day Free Trial (3-Min Setup)</button>
                            </form>
                            <div class="p-2 text-center rounded border border-warning bg-warning bg-opacity-10 small fw-bold text-dark">
                                <i class="fa-solid fa-bolt text-warning me-1"></i> Set up in under 3 minutes. Try it for 7 days, absolutely free.
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h5 class="fw-bold mb-3 text-dark">Full UK Market Strategy Document</h5>
                    <iframe src="/docs/strategy" style="width: 100%; height: 450px; border: 1px solid #cbd5e1; border-radius: 8px;"></iframe>
                </div>
            </div>

        </div>
    </main>

    <!-- Manager PIN Auth Modal -->
    <div class="modal fade" id="pinModal" tabindex="-1" aria-labelledby="pinModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-sm modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="pinModalLabel"><i class="fa-solid fa-user-shield text-warning me-2"></i>Staff Workspace Lock</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center">
                    <p class="text-muted small">Enter Manager PIN to access Staff Workspace (Default: <code>1234</code>)</p>
                    <input type="password" id="pinInput" class="form-control text-center fs-2 fw-bold mb-3" maxlength="4" placeholder="••••">
                    <button type="button" class="btn btn-primary w-100 fw-bold" onclick="authenticatePIN()"><i class="fa-solid fa-unlock me-1"></i> Unlock Staff Workspace</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Review Modal for Guests -->
    <div class="modal fade" id="reviewModal" tabindex="-1" aria-labelledby="reviewModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="reviewModalLabel"><i class="fa-solid fa-heart text-danger me-2"></i>How was your experience?</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center">
                    <p class="text-muted small">Your feedback is sent directly to restaurant management.</p>
                    <div class="fs-2 text-warning mb-3" id="modalStars">
                        <i class="fa-solid fa-star" onclick="setRating(1)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(2)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(3)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(4)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(5)"></i>
                    </div>
                    <input type="hidden" id="selectedRating" value="5">
                    <textarea id="reviewComment" class="form-control mb-3" rows="3" placeholder="Tell us about the food quality or service..."></textarea>
                    <button type="button" class="btn btn-primary w-100 fw-bold" onclick="submitGuestReview()">Submit Private Review</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Split Bill Modal & Shared Table Balances -->
    <div class="modal fade" id="splitModal" tabindex="-1" aria-labelledby="splitModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header bg-dark text-white">
                    <h5 class="modal-title fw-bold" id="splitModalLabel"><i class="fa-solid fa-scissors text-warning me-2"></i>Split Table Bill & Shared Cart Balance</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-4">
                    <!-- Live Table Balance Header -->
                    <div id="splitTableBalanceHeader" class="p-3 bg-light rounded-3 border mb-4">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div>
                                <small class="text-muted fw-semibold">Table #<span id="splitModalTableNum">1</span> Order Total</small>
                                <h4 class="fw-bold mb-0 text-dark" id="splitOrderTotalLabel">£0.00</h4>
                            </div>
                            <span class="badge bg-warning text-dark px-3 py-2 fs-6 rounded-pill" id="splitSettleStatusBadge"><i class="fa-solid fa-clock me-1"></i> Open Balance</span>
                        </div>
                        <div class="progress mb-2" style="height: 10px;">
                            <div class="progress-bar bg-success" role="progressbar" id="splitProgressBar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <div class="d-flex justify-content-between small text-muted">
                            <span>Paid So Far: <strong class="text-success" id="splitTotalPaidLabel">£0.00</strong></span>
                            <span>Remaining: <strong class="text-danger" id="splitRemainingLabel">£0.00</strong></span>
                        </div>
                    </div>

                    <!-- Split Mode Tabs -->
                    <ul class="nav nav-pills nav-fill mb-3" id="splitTab" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active fw-bold" id="tab-even-tab" data-bs-toggle="tab" data-bs-target="#tab-even" type="button" role="tab"><i class="fa-solid fa-users me-1"></i> Split Evenly</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link fw-bold" id="tab-itemized-tab" data-bs-toggle="tab" data-bs-target="#tab-itemized" type="button" role="tab" onclick="loadItemizedSplitOptions()"><i class="fa-solid fa-list-check me-1"></i> Split by Item</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link fw-bold" id="tab-pct-tab" data-bs-toggle="tab" data-bs-target="#tab-pct" type="button" role="tab"><i class="fa-solid fa-percent me-1"></i> Split by Percentage</button>
                        </li>
                    </ul>

                    <div class="tab-content" id="splitTabContent">
                        <!-- Tab 1: Split Evenly -->
                        <div class="tab-pane fade show active" id="tab-even" role="tabpanel">
                            <div class="row g-2 align-items-center mb-3">
                                <div class="col-sm-8">
                                    <label class="form-label small fw-bold text-muted mb-1">Number of Guests Sharing Bill</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fa-solid fa-user-group"></i></span>
                                        <input type="number" id="guestSplitNum" class="form-control" value="2" min="2" max="10">
                                    </div>
                                </div>
                                <div class="col-sm-4">
                                    <label class="form-label d-none d-sm-block mb-1">&nbsp;</label>
                                    <button class="btn btn-success w-100 fw-bold" onclick="calculateTableSplit()"><i class="fa-solid fa-calculator me-1"></i> Calculate</button>
                                </div>
                            </div>
                            <div id="tableSplitResult"></div>
                        </div>

                        <!-- Tab 2: Itemized Split -->
                        <div class="tab-pane fade" id="tab-itemized" role="tabpanel">
                            <p class="small text-muted mb-3"><i class="fa-solid fa-info-circle me-1"></i> Assign specific ordered dishes to Guest 1, Guest 2, etc. Unassigned items default to shared table balance.</p>
                            <div id="itemizedSplitContainer" class="mb-3"></div>
                            <button class="btn btn-primary w-100 fw-bold" onclick="submitItemizedSplit()"><i class="fa-solid fa-check-circle me-1"></i> Apply Itemized Split</button>
                        </div>

                        <!-- Tab 3: Split by Percentage (%) -->
                        <div class="tab-pane fade" id="tab-pct" role="tabpanel">
                            <p class="small text-muted mb-2"><i class="fa-solid fa-percent me-1 text-primary"></i> Enter percentage shares totaling 100% (e.g. <code>50, 25, 25</code> or <code>60, 40</code>):</p>
                            <div class="row g-2 mb-3">
                                <div class="col-sm-8">
                                    <input type="text" id="pctSplitInput" class="form-control fw-bold" value="50, 25, 25" placeholder="e.g. 50, 25, 25">
                                </div>
                                <div class="col-sm-4">
                                    <button class="btn btn-dark text-warning w-100 fw-bold" onclick="calculatePercentageSplit()"><i class="fa-solid fa-calculator me-1"></i> Split by %</button>
                                </div>
                            </div>
                            <div id="pctSplitResultContainer"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Digital Loyalty & Rewards Studio Modal -->
    <div class="modal fade" id="loyaltyModal" tabindex="-1" aria-labelledby="loyaltyModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header text-white" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
                    <h5 class="modal-title fw-bold" id="loyaltyModalLabel"><i class="fa-solid fa-crown text-warning me-2"></i>VIP Loyalty & Digital Rewards Studio</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-4">
                    <!-- Login / Account Lookup Form -->
                    <div id="loyaltyAccountForm" class="p-4 bg-light rounded-3 border mb-4">
                        <h6 class="fw-bold text-dark mb-2"><i class="fa-solid fa-user-check me-2 text-primary"></i>Check Points or Quick Sign-Up</h6>
                        <p class="small text-muted mb-3">Earn 10 points per £1 spent + 50 points instant welcome bonus on sign-up!</p>
                        <div class="row g-2">
                            <div class="col-sm-5">
                                <input type="text" id="loyaltyIdentifierInput" class="form-control" placeholder="Phone or Email (e.g. alex@example.com)">
                            </div>
                            <div class="col-sm-4">
                                <input type="text" id="loyaltyGuestNameInput" class="form-control" placeholder="Guest Name (e.g. Alex M.)">
                            </div>
                            <div class="col-sm-3">
                                <button class="btn btn-primary w-100 fw-bold" onclick="loginOrRegisterLoyalty()"><i class="fa-solid fa-arrow-right me-1"></i> Access Rewards</button>
                            </div>
                        </div>
                    </div>

                    <!-- Active VIP Profile Card -->
                    <div id="loyaltyProfileCard" class="d-none">
                        <div class="card bg-dark text-white border-0 rounded-3 p-4 mb-4 shadow-sm position-relative overflow-hidden">
                            <div class="d-flex justify-content-between align-items-start position-relative z-1 mb-3">
                                <div>
                                    <span class="badge bg-warning text-dark fw-bold mb-2 px-3 py-1" id="loyaltyTierBadge">BRONZE VIP</span>
                                    <h4 class="fw-bold mb-0 text-white" id="loyaltyGuestNameLabel">Guest Member</h4>
                                    <small class="text-light opacity-75" id="loyaltyIdentifierLabel">guest@example.com</small>
                                </div>
                                <div class="text-end">
                                    <small class="text-light opacity-75 d-block">Points Balance</small>
                                    <h2 class="fw-bold text-warning mb-0" id="loyaltyPointsBalanceLabel">50 pts</h2>
                                </div>
                            </div>
                            <div class="position-relative z-1">
                                <div class="d-flex justify-content-between small text-light opacity-75 mb-1">
                                    <span>Total Lifetime Spent: <strong class="text-white" id="loyaltyTotalSpentLabel">£0.00</strong></span>
                                    <span id="loyaltyNextTierLabel">450 pts to SILVER</span>
                                </div>
                                <div class="progress bg-secondary" style="height: 8px;">
                                    <div class="progress-bar bg-warning" role="progressbar" id="loyaltyTierProgressBar" style="width: 10%;"></div>
                                </div>
                            </div>
                        </div>

                        <!-- Available Vouchers & Rewards Store -->
                        <h6 class="fw-bold text-dark mb-3"><i class="fa-solid fa-gift me-2 text-danger"></i>Redeem Reward Vouchers</h6>
                        <div class="row g-3 mb-4" id="loyaltyRewardCatalogGrid"></div>

                        <!-- Active Voucher Wallet -->
                        <h6 class="fw-bold text-dark mb-3"><i class="fa-solid fa-wallet me-2 text-success"></i>My Active Voucher Wallet</h6>
                        <div id="loyaltyVoucherWalletList"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Thermal ESC/POS Printer Emulator Modal -->
    <div class="modal fade" id="thermalEmulatorModal" tabindex="-1" aria-labelledby="thermalEmulatorModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header bg-dark text-white">
                    <h5 class="modal-title fw-bold" id="thermalEmulatorModalLabel"><i class="fa-solid fa-print text-warning me-2"></i>Epson/Star ESC/POS Thermal Docket Emulator</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-4 bg-secondary bg-opacity-10">
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label small fw-bold text-muted">Select Target Ticket</label>
                            <select id="thermalTargetOrderSelect" class="form-select form-select-sm" onchange="renderThermalRollPreview()">
                                <option value="ORD-0001">Ticket #ORD-0001 (Table #5)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small fw-bold text-muted">Thermal Paper Width</label>
                            <div class="btn-group btn-group-sm w-100" role="group">
                                <input type="radio" class="btn-check" name="thermalWidth" id="width32" value="32" checked onchange="renderThermalRollPreview()">
                                <label class="btn btn-outline-dark" for="width32">58mm (32 Cols)</label>
                                <input type="radio" class="btn-check" name="thermalWidth" id="width42" value="42" onchange="renderThermalRollPreview()">
                                <label class="btn btn-outline-dark" for="width42">80mm (42 Cols)</label>
                            </div>
                        </div>
                    </div>

                    <!-- Realistic Thermal Paper Roll Screen -->
                    <div class="d-flex justify-content-center my-3">
                        <div class="thermal-roll-paper p-4 rounded-top border shadow-lg" style="background-color: #fffef0; color: #111; font-family: 'Courier New', Courier, monospace; font-size: 0.85rem; max-width: 380px; width: 100%; border-bottom: 12px dashed #cbd5e1 !important;">
                            <div class="text-center fw-bold mb-2">*** KITCHEN CHEF DOCKET ***</div>
                            <pre id="thermalPaperContent" class="mb-0" style="white-space: pre-wrap; font-family: inherit; font-size: inherit;"></pre>
                        </div>
                    </div>

                    <div class="d-flex gap-2 justify-content-center mt-4">
                        <button class="btn btn-success fw-bold px-4" onclick="simulateEscposPrintCut()"><i class="fa-solid fa-scissors me-1"></i> Print & Cut Docket (ESC/POS)</button>
                        <button class="btn btn-outline-dark fw-bold px-3" onclick="downloadThermalTxt()"><i class="fa-solid fa-download me-1"></i> Download Raw TXT</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- AI Sommelier & Culinary Companion Modal -->
    <div class="modal fade" id="aiSommelierModal" tabindex="-1" aria-labelledby="aiSommelierModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header text-white" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
                    <h5 class="modal-title fw-bold" id="aiSommelierModalLabel"><i class="fa-solid fa-wine-bottle text-warning me-2"></i>AI Sommelier & Culinary Assistant</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-4">
                    <div class="p-3 bg-light rounded-3 border mb-3">
                        <small class="text-muted fw-bold d-block mb-2"><i class="fa-solid fa-lightbulb text-warning me-1"></i> Quick Sommelier Prompts:</small>
                        <div class="d-flex flex-wrap gap-2">
                            <button class="btn btn-sm btn-outline-dark rounded-pill" onclick="askAiSommelier('What wine pairs best with Fish & Chips?')">🍷 Wine for Fish & Chips</button>
                            <button class="btn btn-sm btn-outline-dark rounded-pill" onclick="askAiSommelier('What beer goes with Wagyu Burger?')">🍺 Beer for Wagyu Burger</button>
                            <button class="btn btn-sm btn-outline-dark rounded-pill" onclick="askAiSommelier('Show gluten-free and vegan options')">🌱 Gluten-Free Options</button>
                        </div>
                    </div>

                    <div id="sommelierChatBox" class="p-3 bg-white border rounded-3 mb-3" style="min-height: 220px; max-height: 320px; overflow-y: auto;">
                        <div class="d-flex align-items-start gap-2 mb-3">
                            <div class="bg-dark text-warning rounded-circle p-2 fs-5"><i class="fa-solid fa-robot"></i></div>
                            <div class="p-3 bg-light rounded-3 text-dark border">
                                Hello! I am your AI Sommelier. Ask me for food & wine pairings, dietary options, or dish recommendations!
                            </div>
                        </div>
                    </div>

                    <div class="input-group">
                        <input type="text" id="sommelierInputPrompt" class="form-control" placeholder="Ask AI Sommelier (e.g., 'Best wine for steak?')..." onkeypress="if(event.key==='Enter') sendSommelierPrompt()">
                        <button class="btn btn-warning text-dark fw-bold px-4" onclick="sendSommelierPrompt()"><i class="fa-solid fa-paper-plane me-1"></i> Ask AI</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Google & TripAdvisor Review Booster Modal -->
    <div class="modal fade" id="reviewBoosterModal" tabindex="-1" aria-labelledby="reviewBoosterModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title fw-bold" id="reviewBoosterModalLabel"><i class="fa-solid fa-star text-warning me-2"></i>Thank You for 5 Stars! 🎉</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-4 text-center">
                    <h6 class="fw-bold text-dark mb-2">Help others discover The Waiter!</h6>
                    <p class="small text-muted mb-4">Would you mind sharing your 5-star experience on Google Reviews or TripAdvisor? It takes less than 30 seconds!</p>
                    <div class="d-grid gap-2 mb-3">
                        <a href="https://maps.google.com" target="_blank" class="btn btn-outline-danger fw-bold py-2"><i class="fa-brands fa-google me-2"></i> Post on Google Reviews</a>
                        <a href="https://tripadvisor.com" target="_blank" class="btn btn-outline-success fw-bold py-2"><i class="fa-solid fa-owl me-2"></i> Post on TripAdvisor</a>
                    </div>
                    <button type="button" class="btn btn-sm btn-link text-muted" data-bs-dismiss="modal">Done / Skip</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Digital Kitchen Recipe & Natasha's Law Allergen Matrix Modal -->
    <div class="modal fade" id="chefRecipeModal" tabindex="-1" aria-labelledby="chefRecipeModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-xl">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header bg-dark text-white">
                    <div>
                        <h5 class="modal-title fw-bold mb-0" id="chefRecipeModalLabel"><i class="fa-solid fa-book-open-reader text-warning me-2"></i>Digital Kitchen Recipe & Natasha's Law Allergen Matrix</h5>
                        <small class="text-light opacity-75">Standardized culinary prep specs, exact weights, core temperatures & mandatory UK allergen hazard controls</small>
                    </div>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-4 bg-light">
                    <div class="row g-3" id="chefRecipesContainer">
                        <!-- Populated dynamically by openChefRecipeModal() -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS & Interactivity Script -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentCart = [];
        let currentLang = 'en';
        let currentCurr = 'GBP';
        let activeTable = 1;
        let isAdminUnlocked = false;
        let currSymbols = { 'GBP': '£', 'EUR': '€', 'USD': '$' };
        let activeOrderForTable = null;
        let currentKdsStation = 'ALL';
        let isChimeEnabled = true;
        let prevOrderCount = 0;
        let selectedTipPercentage = 12.5;
        let selectedPaymentMethod = 'APPLE_PAY';

        const urlParams = new URLSearchParams(window.location.search);
        if(urlParams.has('table')) {
            activeTable = parseInt(urlParams.get('table')) || 1;
        }

        function updateTableDisplays() {
            document.getElementById('activeTableBadgeNum').innerText = activeTable;
            document.getElementById('desktopTableNum').innerText = activeTable;
            document.getElementById('mobileTableNum').innerText = activeTable;
            document.getElementById('alertTableNum').innerText = activeTable;
            document.getElementById('payModalTableNum').innerText = activeTable;
            loadTableLiveOrderStatus();
        }

        function setAppMode(mode) {
            if(mode === 'staff') {
                if(!isAdminUnlocked) {
                    const modal = new bootstrap.Modal(document.getElementById('pinModal'));
                    modal.show();
                    return;
                }
                document.getElementById('guestViewSection').classList.add('d-none');
                document.getElementById('mobileCartBar').classList.add('d-none');
                document.getElementById('staffViewSection').classList.remove('d-none');
                document.getElementById('btnGuestView').classList.remove('active');
                document.getElementById('btnStaffView').classList.add('active');
                loadExecutiveKPIs();
                loadKDS();
            } else {
                document.getElementById('staffViewSection').classList.add('d-none');
                document.getElementById('guestViewSection').classList.remove('d-none');
                document.getElementById('mobileCartBar').classList.remove('d-none');
                document.getElementById('btnStaffView').classList.remove('active');
                document.getElementById('btnGuestView').classList.add('active');
            }
        }

        async function authenticatePIN() {
            const pin = document.getElementById('pinInput').value.trim();
            const res = await fetch('/api/auth/pin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: pin })
            });
            const data = await res.json();
            if(data.success) {
                isAdminUnlocked = true;
                const modalEl = document.getElementById('pinModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
                setAppMode('staff');
            } else {
                alert('Invalid Manager PIN. Try 1234');
            }
        }

        async function callWaiter() {
            await requestTableService('SERVER', '🙋 Call Server to Table');
        }

        async function requestTableService(reqType, label) {
            try {
                await fetch('/api/service-calls', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        table_number: activeTable,
                        request_type: reqType,
                        label: label
                    })
                });
            } catch(e) { console.error(e); }
            const banner = document.getElementById('waiterAlertBanner');
            if(banner) {
                banner.innerHTML = `<i class="fa-solid fa-circle-check me-2"></i><strong>Concierge Dispatched (${label})!</strong> Our team is heading to Table #${activeTable}.`;
                banner.classList.remove('d-none');
                setTimeout(() => banner.classList.add('d-none'), 6000);
            }
            loadServiceCallsQueue();
        }

        function setLanguage(lang, btn) {
            currentLang = lang;
            document.querySelectorAll('#langGroup .btn').forEach(b => b.classList.remove('active', 'btn-dark'));
            document.querySelectorAll('#langGroup .btn').forEach(b => b.classList.add('btn-outline-dark'));
            btn.classList.add('active', 'btn-dark');
            loadMenu();
        }

        function setCurrency(curr, btn) {
            currentCurr = curr;
            document.querySelectorAll('#currGroup .btn').forEach(b => b.classList.remove('active', 'btn-dark'));
            document.querySelectorAll('#currGroup .btn').forEach(b => b.classList.add('btn-outline-dark'));
            btn.classList.add('active', 'btn-dark');
            currentCart = [];
            loadMenu();
        }

        let currentDietary = 'all';
        let excludedAllergens = [];

        function filterMenuDiet(diet, btn) {
            currentDietary = diet;
            document.querySelectorAll('[onclick^="filterMenuDiet"]').forEach(b => {
                b.classList.remove('active', 'btn-success');
                b.classList.add('btn-outline-success');
            });
            btn.classList.remove('btn-outline-success');
            btn.classList.add('active', 'btn-success');
            loadMenu();
        }

        function toggleExclusion(allergen, btn) {
            if(excludedAllergens.includes(allergen)) {
                excludedAllergens = excludedAllergens.filter(a => a !== allergen);
                btn.classList.remove('btn-danger');
                btn.classList.add('btn-outline-danger');
            } else {
                excludedAllergens.push(allergen);
                btn.classList.remove('btn-outline-danger');
                btn.classList.add('btn-danger');
            }
            loadMenu();
        }

        async function loadMenu() {
            let url = `/api/menu/filtered?lang=${currentLang}&currency=${currentCurr}`;
            if(currentDietary && currentDietary !== 'all') {
                url += `&dietary=${currentDietary}`;
            }
            if(excludedAllergens.length > 0) {
                url += `&exclude=${excludedAllergens.join(',')}`;
            }
            const res = await fetch(url);
            const data = await res.json();
            
            const container = document.getElementById('menuContainer');
            if(data.length === 0) {
                container.innerHTML = '<div class="text-muted text-center my-4 fs-6"><i class="fa-solid fa-filter-circle-xmark me-2 text-warning"></i>No dishes match your selected filters.</div>';
                return;
            }

            const dishPhotos = {
                'item-1': 'https://images.unsplash.com/photo-1579208030886-b937da0925dc?auto=format&fit=crop&w=600&q=80',
                'item-2': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80',
                'item-3': 'https://images.unsplash.com/photo-1535958636474-b021ee887b13?auto=format&fit=crop&w=600&q=80',
                'item-4': 'https://images.unsplash.com/photo-1576107232684-1279f3908594?auto=format&fit=crop&w=600&q=80',
                'item-5': 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=600&q=80'
            };
            const allergenIcons = {
                'gluten': '🌾 Gluten',
                'fish': '🐟 Fish',
                'dairy': '🥛 Dairy',
                'eggs': '🥚 Eggs',
                'nuts': '🥜 Nuts'
            };

            container.innerHTML = data.map(item => {
                let stockBadge = '';
                let btnDisabled = '';
                if(item.stock_status === 'OUT_OF_STOCK') {
                    stockBadge = '<span class="badge bg-danger ms-2">Out of Stock</span>';
                    btnDisabled = 'disabled';
                } else if(item.stock_status === 'LOW_STOCK') {
                    stockBadge = `<span class="badge bg-warning text-dark ms-2">Only ${item.stock_qty} left!</span>`;
                }

                const photoUrl = dishPhotos[item.id] || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80';
                const allergenBadges = (item.allergens || []).map(a =>
                    `<span class="badge bg-warning bg-opacity-25 text-dark border border-warning me-1" title="Allergen Alert: ${a}">${allergenIcons[a] || a}</span>`
                ).join('');
                const dietaryBadges = (item.dietary || []).map(d =>
                    `<span class="badge bg-success bg-opacity-10 text-success border border-success me-1 text-capitalize">${d}</span>`
                ).join('');

                return `
                    <div class="col-md-6">
                        <div class="dish-card overflow-hidden p-0">
                            <div class="position-relative" style="height: 155px; background: #0f172a;">
                                <img src="${photoUrl}" alt="${item.name_translated}" class="w-100 h-100" style="object-fit: cover; opacity: 0.92;" loading="lazy">
                                <span class="position-absolute top-0 end-0 m-2 badge bg-dark text-warning fs-6 shadow">${item.price_formatted}</span>
                                <div class="position-absolute bottom-0 start-0 m-2 d-flex flex-wrap gap-1">
                                    ${allergenBadges}
                                </div>
                            </div>
                            <div class="p-3 d-flex flex-column justify-content-between flex-grow-1">
                                <div>
                                    <div class="d-flex justify-content-between align-items-start mb-1">
                                        <h6 class="fw-bold mb-0 text-dark">${item.name_translated} ${stockBadge}</h6>
                                    </div>
                                    <div class="mb-2">${dietaryBadges}</div>
                                    <p class="text-muted small mb-3">${item.description_translated}</p>
                                </div>
                                <button class="btn btn-sm btn-warning text-dark fw-bold w-100 add-btn" ${btnDisabled} onclick="addToCart('${item.id}', '${item.name_translated}', ${item.price}, '${item.price_formatted}')">
                                    <i class="fa-solid fa-plus me-1"></i> Add to Order
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            renderCart();
        }

        function addToCart(id, name, price, priceFormatted) {
            currentCart.push({ id, name, price, priceFormatted });
            renderCart();
            checkUpsells();
        }

        function renderCart() {
            const sym = currSymbols[currentCurr] || '£';
            const desktopItems = document.getElementById('cartItems');
            const mobileItems = document.getElementById('mobileCartItems');
            
            if(currentCart.length === 0) {
                const emptyMsg = 'Cart is empty. Select dishes from menu.';
                if(desktopItems) desktopItems.innerHTML = emptyMsg;
                if(mobileItems) mobileItems.innerHTML = emptyMsg;
                document.getElementById('cartTotal').innerText = sym + '0.00';
                document.getElementById('mobileCartTotal').innerText = sym + '0.00';
                document.getElementById('mobileModalCartTotal').innerText = sym + '0.00';
                document.getElementById('mobileCartCount').innerText = '0';
                return;
            }

            let subtotal = 0;
            const html = currentCart.map((item, idx) => {
                subtotal += item.price;
                return `<div class="d-flex justify-content-between align-items-center mb-2 text-dark font-weight-500">
                    <span>${item.name}</span>
                    <div>
                        <span class="me-2 text-primary fw-bold">${item.priceFormatted || sym + item.price.toFixed(2)}</span>
                        <button class="btn btn-link btn-sm text-danger p-0 fw-bold" onclick="removeFromCart(${idx})">&times;</button>
                    </div>
                </div>`;
            }).join('');

            if(desktopItems) desktopItems.innerHTML = html;
            if(mobileItems) mobileItems.innerHTML = html;

            const totalFormatted = sym + subtotal.toFixed(2);
            document.getElementById('cartTotal').innerText = totalFormatted;
            document.getElementById('mobileCartTotal').innerText = totalFormatted;
            document.getElementById('mobileModalCartTotal').innerText = totalFormatted;
            document.getElementById('mobileCartCount').innerText = currentCart.length;
        }

        function removeFromCart(idx) {
            currentCart.splice(idx, 1);
            renderCart();
            checkUpsells();
        }

        async function checkUpsells() {
            const itemIds = currentCart.map(i => i.id);
            if(itemIds.length === 0) {
                document.getElementById('upsellBox').classList.add('d-none');
                return;
            }
            const res = await fetch(`/api/menu?lang=${currentLang}&currency=${currentCurr}`);
            const menu = await res.json();
            
            const hasCod = itemIds.includes('item-1');
            const hasSide = itemIds.includes('item-4');
            const upsellContainer = document.getElementById('upsellContent');

            if(hasCod && !hasSide) {
                const side = menu.find(m => m.id === 'item-4');
                if(side && side.stock_status !== 'OUT_OF_STOCK') {
                    upsellContainer.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="small fw-bold text-dark">${side.name_translated} (+${side.price_formatted})</span>
                            <button class="btn btn-xs btn-warning text-dark py-0 px-2 fw-bold" onclick="addToCart('item-4', '${side.name_translated}', ${side.price}, '${side.price_formatted}')">+ Add</button>
                        </div>
                    `;
                    document.getElementById('upsellBox').classList.remove('d-none');
                    return;
                }
            }
            document.getElementById('upsellBox').classList.add('d-none');
        }

        async function placeOrder() {
            if(currentCart.length === 0) return alert('Please add items to cart first.');
            const promo = document.getElementById('promoInput').value.trim() || document.getElementById('mobilePromoInput').value.trim();
            const res = await fetch('/api/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table_number: activeTable,
                    items: currentCart.map(i => i.id),
                    promo_code: promo
                })
            });
            const order = await res.json();
            const sym = currSymbols[currentCurr] || '£';
            alert(`Order ${order.id} submitted for Table #${activeTable}! Total: ${sym}${order.total.toFixed(2)}`);
            activeOrderForTable = order;
            currentCart = [];
            renderCart();
            document.getElementById('upsellBox').classList.add('d-none');
            loadMenu();
            loadTableLiveOrderStatus();
            playOrderChime();
            
            const reviewModal = new bootstrap.Modal(document.getElementById('reviewModal'));
            reviewModal.show();
        }

        async function loadTableLiveOrderStatus() {
            try {
                const res = await fetch('/api/kds/active');
                const data = await res.json();
                const orders = Array.isArray(data) ? data : (data.orders || []);
                const tableOrders = orders.filter(o => o.table_number === activeTable);
                const liveCard = document.getElementById('tableLiveOrderCard');

                if(tableOrders.length === 0) {
                    liveCard.classList.add('d-none');
                    return;
                }

                const latestOrder = tableOrders[tableOrders.length - 1];
                activeOrderForTable = latestOrder;
                document.getElementById('liveTableNum').innerText = activeTable;
                document.getElementById('liveOrderRef').innerText = latestOrder.id;
                liveCard.classList.remove('d-none');

                const sRec = document.getElementById('stepReceived');
                const sPrep = document.getElementById('stepPreparing');
                const sReady = document.getElementById('stepReady');

                sRec.className = 'order-step active';
                sPrep.className = 'order-step' + (latestOrder.status === 'PREPARING' || latestOrder.status === 'READY' || latestOrder.status === 'Preparing' || latestOrder.status === 'Ready' ? ' active' : '');
                sReady.className = 'order-step' + (latestOrder.status === 'READY' || latestOrder.status === 'Ready' ? ' active' : '');

                // Show/hide cancel button (available when order is New)
                const cancelBtn = document.getElementById('btnCancelGuestOrder');
                if(cancelBtn) {
                    if(latestOrder.status === 'New' || latestOrder.status === 'NEW') {
                        cancelBtn.classList.remove('d-none');
                    } else {
                        cancelBtn.classList.add('d-none');
                    }
                }

                // Fetch real-time Kitchen Station routing & ETA
                const etaBox = document.getElementById('liveOrderStationEtaBox');
                if(etaBox) {
                    const etaRes = await fetch(`/api/kds/eta/${latestOrder.id}`);
                    if(etaRes.ok) {
                        const etaData = await etaRes.json();
                        const stationBadges = (etaData.items || []).map(it =>
                            `<span class="badge station-badge-${it.station} me-1">${it.station}: ${it.name} (${it.prep_mins}m)</span>`
                        ).join('');
                        etaBox.innerHTML = `
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <span class="fw-bold text-dark"><i class="fa-solid fa-fire-burner text-danger me-1"></i>Kitchen Station Routing</span>
                                <span class="badge bg-dark text-warning"><i class="fa-solid fa-hourglass-half me-1"></i>Est. ${etaData.remaining_mins} mins remaining</span>
                            </div>
                            <div class="d-flex flex-wrap gap-1 mt-1">${stationBadges}</div>
                        `;
                    }
                }
            } catch(e) { console.error(e); }
        }

        async function cancelActiveGuestOrder() {
            if(!activeOrderForTable) return;
            const res = await fetch(`/api/order/cancel/${activeOrderForTable.id}`, { method: 'POST' });
            if(res.ok) {
                alert(`Order ${activeOrderForTable.id} has been cancelled and stock restored.`);
                activeOrderForTable = null;
                loadTableLiveOrderStatus();
                loadMenu();
            }
        }

        // --- Online Table Payments & Tip Calculator ---
        function showOnlinePaymentModal() {
            if (!activeOrderForTable && currentCart.length === 0) {
                return alert('Please select dishes and place an order first.');
            }
            updatePaymentModalTotals();
            const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
            modal.show();
        }

        function selectTipPreset(pct, btn) {
            selectedTipPercentage = pct;
            document.querySelectorAll('#tipPresetGroup .btn').forEach(b => {
                b.classList.remove('active', 'btn-dark');
                b.classList.add('btn-outline-dark');
            });
            btn.classList.remove('btn-outline-dark');
            btn.classList.add('active', 'btn-dark');
            updatePaymentModalTotals();
        }

        function selectPaymentMethod(pm, el) {
            selectedPaymentMethod = pm;
            document.querySelectorAll('.pay-method-card').forEach(c => c.classList.remove('selected'));
            el.classList.add('selected');
        }

        function updatePaymentModalTotals() {
            const sym = currSymbols[currentCurr] || '£';
            let subtotal = 0;
            if (activeOrderForTable) {
                subtotal = activeOrderForTable.total;
            } else {
                subtotal = currentCart.reduce((sum, i) => sum + i.price, 0);
            }

            const tipVal = subtotal * (selectedTipPercentage / 100.0);
            const grandTotal = subtotal + tipVal;

            document.getElementById('paySubtotalVal').innerText = sym + subtotal.toFixed(2);
            document.getElementById('payTipVal').innerText = '+' + sym + tipVal.toFixed(2) + ` (${selectedTipPercentage}%)`;
            document.getElementById('payGrandTotalVal').innerText = sym + grandTotal.toFixed(2);
        }

        async function processTableCheckout() {
            let orderId = activeOrderForTable ? activeOrderForTable.id : null;
            if (!orderId && currentCart.length > 0) {
                const resOrder = await fetch('/api/order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        table_number: activeTable,
                        items: currentCart.map(i => i.id)
                    })
                });
                const newOrder = await resOrder.json();
                orderId = newOrder.id;
                activeOrderForTable = newOrder;
                currentCart = [];
                renderCart();
            }

            if (!orderId) return alert('No order selected for payment.');

            const res = await fetch('/api/payments/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    order_id: orderId,
                    payment_method: selectedPaymentMethod,
                    tip_percentage: selectedTipPercentage,
                    currency: currentCurr
                })
            });

            const data = await res.json();
            if (data.status === 'COMPLETED') {
                const sym = currSymbols[currentCurr] || '£';
                alert(`Payment Successful via ${data.payment_method}!
Transaction Ref: ${data.transaction_ref}
Total Paid: ${sym}${data.grand_total.toFixed(2)} (includes ${sym}${data.tip_amount.toFixed(2)} tip)`);
                const modalEl = document.getElementById('paymentModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
                loadTableLiveOrderStatus();
            } else {
                alert(data.error || 'Payment failed.');
            }
        }

        let activeSplitStatusData = null;

        async function showSplitBillModal() {
            if(!activeOrderForTable) return alert('No active submitted order to split for Table #' + activeTable);
            document.getElementById('splitModalTableNum').innerText = activeTable;
            await refreshSplitStatus();
            const modal = new bootstrap.Modal(document.getElementById('splitModal'));
            modal.show();
            calculateTableSplit();
        }

        async function refreshSplitStatus() {
            if(!activeOrderForTable) return;
            try {
                const res = await fetch(`/api/orders/${activeOrderForTable.id}/split/status`);
                if(res.ok) {
                    const data = await res.json();
                    activeSplitStatusData = data;
                    const orderTotal = data.order_total || 0;
                    const totalPaid = data.total_paid || 0;
                    const remaining = data.remaining_balance || 0;
                    const pctPaid = orderTotal > 0 ? Math.min(100, Math.round((totalPaid / orderTotal) * 100)) : 0;

                    document.getElementById('splitOrderTotalLabel').innerText = '£' + orderTotal.toFixed(2);
                    document.getElementById('splitTotalPaidLabel').innerText = '£' + totalPaid.toFixed(2);
                    document.getElementById('splitRemainingLabel').innerText = '£' + remaining.toFixed(2);

                    const pBar = document.getElementById('splitProgressBar');
                    pBar.style.width = pctPaid + '%';
                    pBar.setAttribute('aria-valuenow', pctPaid);

                    const badge = document.getElementById('splitSettleStatusBadge');
                    if(data.is_settled || remaining <= 0) {
                        badge.className = 'badge bg-success text-white px-3 py-2 fs-6 rounded-pill';
                        badge.innerHTML = '<i class="fa-solid fa-check-circle me-1"></i> Fully Settled';
                    } else {
                        badge.className = 'badge bg-warning text-dark px-3 py-2 fs-6 rounded-pill';
                        badge.innerHTML = '<i class="fa-solid fa-clock me-1"></i> Open Balance';
                    }
                }
            } catch(e) {
                console.error('Failed to fetch split status', e);
            }
        }

        async function calculateTableSplit() {
            if(!activeOrderForTable) return;
            const nGuests = parseInt(document.getElementById('guestSplitNum').value) || 2;
            const res = await fetch(`/api/orders/${activeOrderForTable.id}/split/even`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ num_guests: nGuests, include_service_charge: true })
            });
            const data = await res.json();
            const container = document.getElementById('tableSplitResult');

            if(data.splits) {
                container.innerHTML = `
                    <div class="p-3 bg-light rounded-3 border mb-3">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong class="text-dark d-block">Grand Total: £${data.grand_total.toFixed(2)}</strong>
                                <span class="small text-muted">Divided evenly across ${data.splits.length} guests (£${(data.grand_total/data.splits.length).toFixed(2)} per guest)</span>
                            </div>
                            <span class="badge bg-primary rounded-pill px-3 py-2"><i class="fa-solid fa-users me-1"></i> ${data.splits.length} Shares</span>
                        </div>
                    </div>
                    <div class="vstack gap-2">
                        ${data.splits.map((s, idx) => {
                            const isPaid = s.status === 'PAID';
                            return `
                                <div class="p-3 border rounded-3 d-flex align-items-center justify-content-between ${isPaid ? 'bg-success bg-opacity-10 border-success' : 'bg-white'}">
                                    <div>
                                        <div class="d-flex align-items-center gap-2">
                                            <strong class="text-dark">Guest ${idx + 1} Share</strong>
                                            <span class="badge ${isPaid ? 'bg-success' : 'bg-secondary'}">${isPaid ? 'PAID' : 'UNPAID'}</span>
                                        </div>
                                        <small class="text-muted">Total share: <span class="fw-bold text-dark">£${s.amount.toFixed(2)}</span></small>
                                    </div>
                                    <div class="d-flex gap-2">
                                        <a href="/api/orders/${data.order_id}/split/sub-receipt/${idx + 1}" target="_blank" class="btn btn-sm btn-outline-dark"><i class="fa-solid fa-receipt me-1"></i> Sub-Receipt</a>
                                        ${!isPaid ? `<button class="btn btn-sm btn-success fw-bold" onclick="payShareAmount('${data.order_id}', '${s.id || (idx+1)}', ${s.amount})"><i class="fa-solid fa-credit-card me-1"></i> Pay £${s.amount.toFixed(2)}</button>` : ''}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
            } else {
                container.innerHTML = `<div class="text-danger small">${data.error || 'Failed to split order.'}</div>`;
            }
        }

        async function loadItemizedSplitOptions() {
            if(!activeOrderForTable) return;
            const container = document.getElementById('itemizedSplitContainer');
            const items = activeOrderForTable.items || [];
            if(items.length === 0) {
                container.innerHTML = '<div class="text-muted small">No items in active order.</div>';
                return;
            }

            let html = '<div class="table-responsive"><table class="table table-sm table-borderless align-middle"><thead class="table-light"><tr><th>Item</th><th>Price</th><th style="width: 140px;">Assign To</th></tr></thead><tbody>';
            items.forEach((item, i) => {
                html += `
                    <tr>
                        <td><strong>${item.name || 'Dish'}</strong></td>
                        <td>£${(item.price || 0).toFixed(2)}</td>
                        <td>
                            <select class="form-select form-select-sm item-guest-assign" data-item-id="${item.item_id || item.id}" data-item-name="${item.name}" data-item-price="${item.price}">
                                <option value="1">Guest 1</option>
                                <option value="2">Guest 2</option>
                                <option value="3">Guest 3</option>
                                <option value="4">Guest 4</option>
                            </select>
                        </td>
                    </tr>
                `;
            });
            html += '</tbody></table></div>';
            container.innerHTML = html;
        }

        async function submitItemizedSplit() {
            if(!activeOrderForTable) return;
            const selects = document.querySelectorAll('.item-guest-assign');
            const guestMap = {};
            selects.forEach(sel => {
                const gIdx = parseInt(sel.value) || 1;
                if(!guestMap[gIdx]) guestMap[gIdx] = [];
                guestMap[gIdx].push({
                    item_id: sel.getAttribute('data-item-id'),
                    name: sel.getAttribute('data-item-name'),
                    price: parseFloat(sel.getAttribute('data-item-price')) || 0
                });
            });

            const assignments = Object.keys(guestMap).map(gIdx => ({
                guest_index: parseInt(gIdx),
                guest_name: `Guest ${gIdx}`,
                items: guestMap[gIdx]
            }));

            const res = await fetch(`/api/orders/${activeOrderForTable.id}/split/itemized`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ guest_assignments: assignments, include_service_charge: true })
            });
            const data = await res.json();
            const container = document.getElementById('tableSplitResult');

            if(data.splits) {
                // Switch back to tab 1 to display result
                const evenTabBtn = document.getElementById('tab-even-tab');
                const tab = new bootstrap.Tab(evenTabBtn);
                tab.show();

                container.innerHTML = `
                    <div class="p-3 bg-light rounded-3 border mb-3">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong class="text-dark d-block">Itemized Split Total: £${data.grand_total.toFixed(2)}</strong>
                                <span class="small text-muted">${data.splits.length} Guest Allocations</span>
                            </div>
                        </div>
                    </div>
                    <div class="vstack gap-2">
                        ${data.splits.map((s, idx) => `
                            <div class="p-3 border rounded-3 d-flex align-items-center justify-content-between bg-white">
                                <div>
                                    <strong class="text-dark">Guest ${s.guest_index} (${s.guest_name})</strong>
                                    <div class="small text-muted">${(s.items || []).map(i => i.name).join(', ')}</div>
                                    <small class="text-muted">Total Share (inc. service): <span class="fw-bold text-dark">£${s.total.toFixed(2)}</span></small>
                                </div>
                                <div class="d-flex gap-2">
                                    <a href="/api/orders/${data.order_id}/split/sub-receipt/${s.guest_index}" target="_blank" class="btn btn-sm btn-outline-dark"><i class="fa-solid fa-receipt me-1"></i> Sub-Receipt</a>
                                    <button class="btn btn-sm btn-success fw-bold" onclick="payShareAmount('${data.order_id}', '${s.id}', ${s.total})"><i class="fa-solid fa-credit-card me-1"></i> Pay £${s.total.toFixed(2)}</button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                alert(data.error || 'Failed to apply itemized split.');
            }
        }

        async function payShareAmount(orderId, splitTarget, amount) {
            const res = await fetch(`/api/orders/${orderId}/pay-share`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ split_id_or_index: splitTarget, payment_method: selectedPaymentMethod || 'APPLE_PAY' })
            });
            const data = await res.json();
            if(res.ok) {
                alert(`✅ Guest Share Paid (£${amount.toFixed(2)}) via ${selectedPaymentMethod || 'APPLE_PAY'}! Remaining table balance: £${(data.remaining_balance || 0).toFixed(2)}`);
                await refreshSplitStatus();
                await calculateTableSplit();
            } else {
                alert(data.error || 'Failed to pay guest share.');
            }
        }

        // --- Table QR Studio Generator ---
        async function loadQrStudio() {
            updateQrStudioPreview();
            loadBatchQrGrid();
        }

        async function updateQrStudioPreview() {
            const tNum = parseInt(document.getElementById('qrStudioTableNum').value) || 1;
            const res = await fetch(`/api/qr/table/${tNum}/preview`);
            const data = await res.json();

            document.getElementById('qrTentTableLabel').innerText = 'TABLE #' + data.table_number;
            document.getElementById('qrStudioPreviewImg').src = data.qr_base64;
            document.getElementById('qrStudioTargetUrl').innerText = data.table_url;
            document.getElementById('btnDownloadPng').href = `/api/qr/table/${data.table_number}`;
            document.getElementById('btnOpenTableUrl').href = data.table_url;
        }

        async function loadBatchQrGrid() {
            const container = document.getElementById('batchQrGridContainer');
            let html = '';
            for(let i=1; i<=12; i++) {
                html += `
                    <div class="col-6 col-sm-4 col-md-3">
                        <div class="card p-3 text-center border shadow-sm">
                            <strong class="text-primary mb-1">Table #${i}</strong>
                            <img src="/api/qr/table/${i}" alt="Table ${i}" class="img-fluid mx-auto mb-2 border rounded p-1" style="max-width: 120px;">
                            <a href="/api/qr/table/${i}" target="_blank" class="btn btn-xs btn-outline-dark fw-bold"><i class="fa-solid fa-download me-1"></i> PNG</a>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }

        // --- White-Label Brand & Live Theme Customizer ---
        async function loadBrandConfig() {
            try {
                const res = await fetch('/api/brand/config');
                const cfg = await res.json();
                
                document.getElementById('cfgBrandName').value = cfg.brand_name || 'The Waiter';
                document.getElementById('cfgStoreSubheading').value = cfg.store_subheading || 'Covent Garden Flagship (UK)';
                document.getElementById('cfgGuestWelcomeMsg').value = cfg.guest_welcome_message || 'Welcome! Tap dishes below to order directly from Table #';
                document.getElementById('cfgPrimaryColor').value = cfg.primary_color || '#0f172a';
                document.getElementById('cfgAccentColor').value = cfg.accent_color || '#0284c7';
                document.getElementById('cfgFontFamily').value = cfg.font_family || 'Plus Jakarta Sans';

                applyBrandTheme(cfg);
            } catch(e) { console.error(e); }
        }

        function previewBrandTheme() {
            const cfg = {
                brand_name: document.getElementById('cfgBrandName').value.trim() || 'The Waiter',
                store_subheading: document.getElementById('cfgStoreSubheading').value.trim() || 'Covent Garden Flagship (UK)',
                guest_welcome_message: document.getElementById('cfgGuestWelcomeMsg').value.trim() || 'Welcome! Tap dishes below to order directly from Table #',
                primary_color: document.getElementById('cfgPrimaryColor').value,
                accent_color: document.getElementById('cfgAccentColor').value,
                font_family: document.getElementById('cfgFontFamily').value
            };

            document.getElementById('prevBrandName').innerText = cfg.brand_name;
            document.getElementById('prevSubheading').innerText = cfg.store_subheading;
            document.getElementById('prevWelcomeMsg').innerText = cfg.guest_welcome_message + '5';
            document.getElementById('prevHeader').style.background = cfg.primary_color;
            document.getElementById('prevBtn').style.backgroundColor = cfg.accent_color;

            applyBrandTheme(cfg);
        }

        function applyBrandTheme(cfg) {
            document.getElementById('brandNameLabel').innerText = cfg.brand_name || 'The Waiter';
            document.getElementById('activeStoreLabel').innerText = cfg.store_subheading || 'Covent Garden Flagship';
            document.getElementById('guestWelcomeMsgText').innerText = (cfg.guest_welcome_message || 'Welcome! Tap dishes below to order directly from Table #') + activeTable;
            
            document.body.style.fontFamily = `'${cfg.font_family || 'Plus Jakarta Sans'}', system-ui, sans-serif`;

            const styleEl = document.getElementById('dynamicBrandTheme');
            if(styleEl) {
                styleEl.innerHTML = `
                    :root {
                        --primary-bg: ${cfg.primary_color || '#0f172a'};
                        --header-bg: ${cfg.primary_color || '#0f172a'};
                        --accent-blue: ${cfg.accent_color || '#0284c7'};
                        --accent-green: #10b981;
                        --card-bg: #ffffff;
                        --text-main: #0f172a;
                        --text-muted: #64748b;
                    }
                    body { font-family: '${cfg.font_family || 'Plus Jakarta Sans'}', system-ui, sans-serif; background-color: #f8fafc; color: #0f172a; padding-bottom: 80px; }
                    .app-header { background: ${cfg.primary_color || '#0f172a'}; }
                    .dish-price { color: ${cfg.accent_color || '#0284c7'}; }
                    .btn-primary { background-color: ${cfg.accent_color || '#0284c7'}; border-color: ${cfg.accent_color || '#0284c7'}; }
                `;
            }
        }

        async function saveBrandConfig() {
            const cfg = {
                brand_name: document.getElementById('cfgBrandName').value.trim(),
                store_subheading: document.getElementById('cfgStoreSubheading').value.trim(),
                guest_welcome_message: document.getElementById('cfgGuestWelcomeMsg').value.trim(),
                primary_color: document.getElementById('cfgPrimaryColor').value,
                accent_color: document.getElementById('cfgAccentColor').value,
                font_family: document.getElementById('cfgFontFamily').value
            };

            const res = await fetch('/api/brand/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cfg)
            });
            const data = await res.json();
            alert(`Brand theme published! Restaurant Name: "${data.brand_name}"`);
            applyBrandTheme(data);
        }

        // --- Station KDS & Audio Chime System ---
        function filterKdsStation(station, btn) {
            currentKdsStation = station;
            document.querySelectorAll('#kdsStationFilterGroup .btn').forEach(b => {
                b.classList.remove('active', 'btn-dark');
                b.classList.add('btn-outline-dark');
            });
            btn.classList.remove('btn-outline-dark');
            btn.classList.add('active', 'btn-dark');
            loadKDS();
        }

        function toggleOrderChime() {
            isChimeEnabled = !isChimeEnabled;
            const btn = document.getElementById('chimeToggleBtn');
            if(isChimeEnabled) {
                btn.className = 'btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold ms-auto';
                btn.innerHTML = '<i class="fa-solid fa-volume-high me-1"></i> Audio Chime On';
                playOrderChime();
            } else {
                btn.className = 'btn btn-sm btn-outline-secondary rounded-pill px-3 py-1 fw-bold ms-auto';
                btn.innerHTML = '<i class="fa-solid fa-volume-xmark me-1"></i> Audio Muted';
            }
        }

        function playOrderChime() {
            if (!isChimeEnabled) return;
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                
                // Note 1: High "Ding" (E5 = 659.25Hz)
                const osc1 = audioCtx.createOscillator();
                const gain1 = audioCtx.createGain();
                osc1.type = 'sine';
                osc1.frequency.setValueAtTime(659.25, audioCtx.currentTime);
                gain1.gain.setValueAtTime(0.3, audioCtx.currentTime);
                gain1.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
                osc1.connect(gain1);
                gain1.connect(audioCtx.destination);
                osc1.start(audioCtx.currentTime);
                osc1.stop(audioCtx.currentTime + 0.4);
                
                // Note 2: Lower "Dong" (C5 = 523.25Hz)
                setTimeout(() => {
                    const osc2 = audioCtx.createOscillator();
                    const gain2 = audioCtx.createGain();
                    osc2.type = 'sine';
                    osc2.frequency.setValueAtTime(523.25, audioCtx.currentTime);
                    gain2.gain.setValueAtTime(0.3, audioCtx.currentTime);
                    gain2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.6);
                    osc2.connect(gain2);
                    gain2.connect(audioCtx.destination);
                    osc2.start(audioCtx.currentTime);
                    osc2.stop(audioCtx.currentTime + 0.6);
                }, 150);
            } catch(e) { console.error(e); }
        }

        async function loadKDS() {
            const res = await fetch('/api/kds/active?station=' + currentKdsStation);
            const data = await res.json();
            const orders = data.orders || (Array.isArray(data) ? data : []);
            const counts = data.station_counts || {};

            ['ALL', 'GRILL', 'FRYER', 'BAR', 'LARDER', 'HOT_LINE'].forEach(st => {
                const el = document.getElementById('stBadge' + st);
                if(el && counts[st] !== undefined) el.innerText = counts[st];
            });

            if (counts.ALL !== undefined && counts.ALL > prevOrderCount) {
                if(prevOrderCount > 0) playOrderChime();
            }
            prevOrderCount = counts.ALL || orders.length;

            const container = document.getElementById('kdsContainer');

            if(orders.length === 0) {
                container.innerHTML = `<div class="col-12 text-muted text-center py-4"><i class="fa-solid fa-circle-check text-success me-2 fs-5"></i>No active orders for station: <strong>${currentKdsStation}</strong></div>`;
                return;
            }

            container.innerHTML = orders.map(order => `
                <div class="col-md-4">
                    <div class="card card-custom p-3 bg-white shadow-sm border-top border-4 border-primary">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0 text-dark">${order.id} (Table #${order.table_number})</h6>
                            <span class="badge bg-secondary">${order.status}</span>
                        </div>
                        <ul class="small text-dark mb-3 ps-3">
                            ${order.items.map(i => {
                                const stBadge = i.station ? `<span class="badge station-badge-${i.station} ms-1">${i.station}</span>` : '';
                                return `<li><strong>${i.name}</strong> ${stBadge}</li>`;
                            }).join('')}
                        </ul>
                        <div class="d-flex flex-wrap gap-1 align-items-center">
                            <button class="btn btn-sm btn-success fw-bold" onclick="advanceKDS('${order.id}')">Advance Status</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="cancelOrder('${order.id}')">Refund</button>
                            <a href="/api/invoice/${order.id}/pdf?currency=${currentCurr}" target="_blank" class="btn btn-sm btn-outline-dark"><i class="fa-solid fa-file-pdf text-danger"></i> PDF</a>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        async function advanceKDS(id) {
            await fetch('/api/kds/advance/' + id, { method: 'POST' });
            loadKDS();
            loadTableLiveOrderStatus();
        }

        async function cancelOrder(id) {
            if(!isAdminUnlocked) return alert('Manager PIN required');
            if(!confirm(`Cancel & refund order ${id}?`)) return;
            await fetch('/api/order/cancel/' + id, { method: 'POST' });
            loadKDS();
            loadMenu();
            loadTableLiveOrderStatus();
        }

        function setRating(stars) {
            document.getElementById('selectedRating').value = stars;
            const starElements = document.querySelectorAll('#modalStars i');
            starElements.forEach((s, idx) => {
                s.className = idx < stars ? 'fa-solid fa-star' : 'fa-regular fa-star';
            });
        }

        async function submitGuestReview() {
            const rating = parseInt(document.getElementById('selectedRating').value) || 5;
            const comment = document.getElementById('reviewComment').value.trim();

            await fetch('/api/reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table_number: activeTable,
                    rating: rating,
                    comment: comment
                })
            });

            const modalEl = document.getElementById('reviewModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            document.getElementById('reviewComment').value = '';

            if (rating >= 4) {
                const boosterModal = new bootstrap.Modal(document.getElementById('reviewBoosterModal'));
                boosterModal.show();
            } else {
                alert('Thank you! Your feedback has been sent directly to our General Manager.');
            }
        }

        async function loadExecutiveKPIs() {
            try {
                const res = await fetch('/api/analytics?currency=' + currentCurr);
                const data = await res.json();
                const sym = data.currency_symbol || '£';
                document.getElementById('kpiGrossRev').innerText = sym + data.total_revenue.toFixed(2);
                document.getElementById('kpiTotalOrdersCount').innerText = `${data.total_orders} orders today`;

                const resKds = await fetch('/api/kds/active');
                const kdsData = await resKds.json();
                const kdsOrders = Array.isArray(kdsData) ? kdsData : (kdsData.orders || []);
                document.getElementById('kpiActiveKds').innerText = kdsOrders.length;

                const resLabor = await fetch('/api/staff/labor-summary?currency=' + currentCurr);
                const labor = await resLabor.json();
                document.getElementById('kpiActiveStaff').innerText = `${labor.active_staff_count} Staff`;
                document.getElementById('kpiLaborCost').innerText = `${sym}${labor.total_labor_cost.toFixed(2)} (${labor.labor_cost_percentage}% labor)`;

                const resNps = await fetch('/api/feedback/nps');
                const nps = await resNps.json();
                document.getElementById('kpiNpsScore').innerText = (nps.nps_score > 0 ? '+' : '') + nps.nps_score.toFixed(0);
                document.getElementById('kpiNpsLabel').innerText = `${nps.total_responses} Guest Feedback`;
            } catch(e) { console.error(e); }
        }

        async function loadVenues() {
            try {
                const res = await fetch('/api/venues');
                const data = await res.json();
                const select = document.getElementById('venueSelect');
                select.innerHTML = data.venues.map(v => `
                    <option value="${v.id}" ${v.id === data.active_venue.id ? 'selected' : ''}>
                        ${v.name} (${v.market} - ${v.currency})
                    </option>
                `).join('');
                document.getElementById('activeVenueName').innerText = `${data.active_venue.name} (${data.active_venue.market})`;
            } catch(e) { console.error(e); }
        }

        async function switchVenue(venueId) {
            try {
                const res = await fetch('/api/venues/switch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ venue_id: venueId })
                });
                const data = await res.json();
                if(data.success) {
                    document.getElementById('activeVenueName').innerText = `${data.active_venue.name} (${data.active_venue.market})`;
                    alert(`Switched active venue to: ${data.active_venue.name}`);
                }
            } catch(e) { console.error(e); }
        }

        // Initial Load
        updateTableDisplays();
        loadVenues();
        loadMenu();
        loadBrandConfig();
        loadVisualFloorplan();
        loadSalesHeatmap();
        loadGuestActivePromos();
        loadServiceCallsQueue();
        loadTransfers();

        // SSE Real-Time Listener
        if ('EventSource' in window) {
            const evtSource = new EventSource('/api/kds/events');
            evtSource.addEventListener('kds_update', function(e) {
                loadTableLiveOrderStatus();
                if(isAdminUnlocked) {
                    loadKDS();
                    loadExecutiveKPIs();
                }
            });
        }

        let activeLoyaltyAccount = null;

        function showLoyaltyModal() {
            const modal = new bootstrap.Modal(document.getElementById('loyaltyModal'));
            modal.show();
        }

        async function loginOrRegisterLoyalty() {
            const identifier = document.getElementById('loyaltyIdentifierInput').value.trim();
            const guestName = document.getElementById('loyaltyGuestNameInput').value.trim();
            if(!identifier) return alert('Please enter phone number or email address.');

            let res = await fetch(`/api/loyalty/account?identifier=${encodeURIComponent(identifier)}`);
            let data = await res.json();

            if(!data.account) {
                if(!guestName) return alert('Account not found. Please enter Guest Name to create your VIP account!');
                res = await fetch('/api/loyalty/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ identifier: identifier, guest_name: guestName })
                });
                data = await res.json();
            }

            if(data.account) {
                activeLoyaltyAccount = data.account;
                renderLoyaltyProfile(data.account);
            } else {
                alert(data.error || 'Failed to access loyalty account.');
            }
        }

        function renderLoyaltyProfile(acc) {
            document.getElementById('loyaltyProfileCard').classList.remove('d-none');
            document.getElementById('loyaltyGuestNameLabel').innerText = acc.guest_name || 'VIP Member';
            document.getElementById('loyaltyIdentifierLabel').innerText = acc.phone_or_email;
            document.getElementById('loyaltyPointsBalanceLabel').innerText = acc.points_balance + ' pts';
            document.getElementById('loyaltyTotalSpentLabel').innerText = '£' + (acc.total_spent || 0).toFixed(2);
            document.getElementById('loyaltyTierBadge').innerText = acc.tier + ' VIP';

            let nextTierText = 'MAX VIP TIER REACHED';
            let pct = 100;
            if(acc.tier === 'BRONZE') {
                const diff = 500 - acc.points_balance;
                nextTierText = (diff > 0 ? diff : 0) + ' pts to SILVER';
                pct = Math.min(100, Math.round((acc.points_balance / 500) * 100));
            } else if(acc.tier === 'SILVER') {
                const diff = 1000 - acc.points_balance;
                nextTierText = (diff > 0 ? diff : 0) + ' pts to GOLD';
                pct = Math.min(100, Math.round((acc.points_balance / 1000) * 100));
            }
            document.getElementById('loyaltyNextTierLabel').innerText = nextTierText;
            document.getElementById('loyaltyTierProgressBar').style.width = pct + '%';

            renderRewardCatalog(acc);
            renderVoucherWallet(acc.vouchers || []);
        }

        function renderRewardCatalog(acc) {
            const grid = document.getElementById('loyaltyRewardCatalogGrid');
            const rewards = [
                { key: 'REWARD5', title: '£5 Off Voucher', cost: 100, desc: '15% Off Total Order', icon: 'fa-ticket text-info' },
                { key: 'REWARD15', title: '£15 Off Voucher', cost: 250, desc: '30% Off Total Order', icon: 'fa-tags text-warning' },
                { key: 'FREEMAIN', title: 'Free Main Dish', cost: 500, desc: '50% Off Gourmet Dish', icon: 'fa-utensils text-success' }
            ];

            grid.innerHTML = rewards.map(r => {
                const canAfford = acc.points_balance >= r.cost;
                return `
                    <div class="col-md-4">
                        <div class="card h-100 border p-3 rounded-3 shadow-sm ${canAfford ? 'border-primary' : 'bg-light'}">
                            <div class="d-flex align-items-center gap-2 mb-2">
                                <i class="fa-solid ${r.icon} fs-4"></i>
                                <h6 class="fw-bold mb-0 text-dark">${r.title}</h6>
                            </div>
                            <small class="text-muted mb-2 d-block">${r.desc}</small>
                            <div class="d-flex justify-content-between align-items-center mt-auto">
                                <span class="badge bg-secondary">${r.cost} pts</span>
                                <button class="btn btn-sm ${canAfford ? 'btn-primary' : 'btn-outline-secondary disabled'} fw-bold" onclick="redeemLoyaltyReward('${r.key}')">Redeem</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function redeemLoyaltyReward(rewardKey) {
            if(!activeLoyaltyAccount) return;
            const res = await fetch('/api/loyalty/redeem', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier: activeLoyaltyAccount.phone_or_email, reward_key: rewardKey })
            });
            const data = await res.json();

            if(data.success) {
                activeLoyaltyAccount = data.account;
                renderLoyaltyProfile(data.account);
                alert(`Voucher ${data.voucher_code} issued! Voucher code copied and applied.`);
                applyPromoCodeDirect(data.voucher_code);
            } else {
                alert(data.error || 'Failed to redeem reward.');
            }
        }

        function renderVoucherWallet(vouchers) {
            const list = document.getElementById('loyaltyVoucherWalletList');
            if(vouchers.length === 0) {
                list.innerHTML = '<div class="text-muted small p-3 bg-light rounded text-center">No active vouchers in wallet yet. Redeem rewards above!</div>';
                return;
            }
            list.innerHTML = vouchers.map(v => `
                <div class="p-3 border rounded-3 bg-white d-flex justify-content-between align-items-center mb-2 shadow-sm">
                    <div>
                        <strong class="text-dark d-block"><i class="fa-solid fa-barcode text-success me-1"></i> ${v.code}</strong>
                        <small class="text-muted">${v.description} (${v.discount_pct}% Off)</small>
                    </div>
                    <button class="btn btn-sm btn-outline-success fw-bold" onclick="applyPromoCodeDirect('${v.code}')"><i class="fa-solid fa-check me-1"></i> Apply to Cart</button>
                </div>
            `).join('');
        }

        function applyPromoCodeDirect(code) {
            const pDesktop = document.getElementById('promoInput');
            const pMobile = document.getElementById('mobilePromoInput');
            if(pDesktop) pDesktop.value = code;
            if(pMobile) pMobile.value = code;
            const modalEl = document.getElementById('loyaltyModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if(modal) modal.hide();
        }


        // --- PWA Service Worker & Offline Sync Queue ---
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(reg => console.log('PWA Service Worker registered:', reg.scope))
                    .catch(err => console.error('PWA Service Worker registration failed:', err));
            });
        }

        function updateNetworkStatus() {
            const badge = document.getElementById('pwaNetworkBadge');
            const banner = document.getElementById('offlineSyncBanner');
            const isOnline = navigator.onLine;

            if (badge) {
                if (isOnline) {
                    badge.className = 'badge bg-success rounded-pill px-3 py-2 ms-2';
                    badge.innerHTML = '<i class="fa-solid fa-wifi me-1"></i> Online';
                } else {
                    badge.className = 'badge bg-danger rounded-pill px-3 py-2 ms-2';
                    badge.innerHTML = '<i class="fa-solid fa-wifi-slash me-1"></i> Offline';
                }
            }

            if (banner) {
                if (!isOnline) {
                    banner.classList.remove('d-none');
                } else {
                    banner.classList.add('d-none');
                    syncOfflineQueue();
                }
            }
            updateOfflinePendingBadge();
        }

        function getOfflineQueue() {
            try {
                return JSON.parse(localStorage.getItem('waiter_offline_orders') || '[]');
            } catch(e) {
                return [];
            }
        }

        function saveOfflineQueue(queue) {
            localStorage.setItem('waiter_offline_orders', JSON.stringify(queue));
            updateOfflinePendingBadge();
        }

        function updateOfflinePendingBadge() {
            const queue = getOfflineQueue();
            const badge = document.getElementById('offlinePendingCountBadge');
            if(badge) {
                badge.innerText = queue.length + ' Pending';
            }
        }

        async function saveOrderOffline(orderPayload) {
            const queue = getOfflineQueue();
            queue.push({
                payload: orderPayload,
                timestamp: new Date().toISOString()
            });
            saveOfflineQueue(queue);
            alert('📱 [Offline PWA] Order saved locally on device! It will auto-submit as soon as Wi-Fi reconnects.');
        }

        async function syncOfflineQueue() {
            const queue = getOfflineQueue();
            if (queue.length === 0) return;

            console.log(`Syncing ${queue.length} offline orders...`);
            let syncedCount = 0;
            const remainingQueue = [];

            for (const item of queue) {
                try {
                    const res = await fetch('/api/order', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(item.payload)
                    });
                    if (res.ok) {
                        syncedCount++;
                    } else {
                        remainingQueue.push(item);
                    }
                } catch(e) {
                    remainingQueue.push(item);
                }
            }

            saveOfflineQueue(remainingQueue);

            if (syncedCount > 0) {
                alert(`🚀 [PWA Auto-Sync] Successfully synced ${syncedCount} offline order(s) to the kitchen!`);
                loadTableLiveOrderStatus();
            }
        }

        window.addEventListener('online', updateNetworkStatus);
        window.addEventListener('offline', updateNetworkStatus);


        // --- Hands-Free Voice AI Command System ---
        let recognition = null;
        let isVoiceListening = false;

        function initVoiceRecognition() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                console.warn('Web Speech API is not supported in this browser.');
                return null;
            }

            const rec = new SpeechRecognition();
            rec.continuous = true;
            rec.interimResults = false;
            rec.lang = 'en-US';

            rec.onstart = function() {
                isVoiceListening = true;
                updateVoiceUi(true);
                speakVoiceFeedback("Voice AI active. Listening for commands.");
            };

            rec.onend = function() {
                if (isVoiceListening) {
                    try { rec.start(); } catch(e) {}
                } else {
                    updateVoiceUi(false);
                }
            };

            rec.onresult = function(event) {
                const lastIdx = event.results.length - 1;
                const transcript = event.results[lastIdx][0].transcript.trim().toLowerCase();
                console.log('Voice Command Received:', transcript);
                showVoiceFeedback(transcript);
                processVoiceCommand(transcript);
            };

            rec.onerror = function(event) {
                console.error('Voice Recognition Error:', event.error);
            };

            return rec;
        }

        function toggleVoiceCommand() {
            if (!recognition) {
                recognition = initVoiceRecognition();
            }

            if (!recognition) {
                return alert('Speech Recognition is not supported in your browser. Try Google Chrome or Safari!');
            }

            if (isVoiceListening) {
                isVoiceListening = false;
                recognition.stop();
                updateVoiceUi(false);
                speakVoiceFeedback("Voice AI stopped.");
            } else {
                try {
                    recognition.start();
                } catch(e) {
                    isVoiceListening = true;
                    updateVoiceUi(true);
                }
            }
        }

        function updateVoiceUi(listening) {
            const btn = document.getElementById('btnVoiceCommand');
            const icon = document.getElementById('voiceMicIcon');
            const text = document.getElementById('voiceBtnText');

            if (listening) {
                btn.className = 'btn btn-sm btn-danger text-white fw-bold rounded-pill px-3 me-1 shadow';
                icon.className = 'fa-solid fa-microphone-slash me-1';
                text.innerText = 'Listening...';
            } else {
                btn.className = 'btn btn-sm btn-outline-info text-white fw-bold rounded-pill px-3 me-1';
                icon.className = 'fa-solid fa-microphone text-info me-1';
                text.innerText = 'Voice AI';
            }
        }

        function showVoiceFeedback(text) {
            const toast = document.getElementById('voiceFeedbackToast');
            const label = document.getElementById('voiceRecognizedText');
            if (toast && label) {
                label.innerText = `"${text}"`;
                toast.classList.remove('d-none');
                setTimeout(() => toast.classList.add('d-none'), 4000);
            }
        }

        function speakVoiceFeedback(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        }

        function processVoiceCommand(cmd) {
            if (cmd.includes('call waiter') || cmd.includes('waiter')) {
                callWaiter();
                speakVoiceFeedback("Calling waiter to table number " + activeTable);
            } else if (cmd.includes('pay') || cmd.includes('checkout')) {
                showPaymentModal();
                speakVoiceFeedback("Opening online table payments modal");
            } else if (cmd.includes('split')) {
                showSplitBillModal();
                speakVoiceFeedback("Opening table split bill modal");
            } else if (cmd.includes('rewards') || cmd.includes('points') || cmd.includes('vip')) {
                showLoyaltyModal();
                speakVoiceFeedback("Opening VIP loyalty rewards studio");
            } else if (cmd.includes('grill')) {
                setKdsFilter('GRILL');
                speakVoiceFeedback("Filtering KDS by Grill station");
            } else if (cmd.includes('fryer')) {
                setKdsFilter('FRYER');
                speakVoiceFeedback("Filtering KDS by Fryer station");
            } else if (cmd.includes('bar')) {
                setKdsFilter('BAR');
                speakVoiceFeedback("Filtering KDS by Bar station");
            } else if (cmd.includes('all stations') || cmd.includes('show all')) {
                setKdsFilter('ALL');
                speakVoiceFeedback("Showing all kitchen stations");
            } else if (cmd.includes('bump order') || cmd.includes('ready order') || cmd.includes('order ready')) {
                const match = cmd.match(/\\d+/);
                if (match) {
                    const orderNum = match[0];
                    const targetId = 'ORD-' + orderNum.padStart(4, '0');
                    advanceOrderStatus(targetId);
                    speakVoiceFeedback(`Order ${orderNum} marked ready`);
                }
            } else if (cmd.startsWith('search ')) {
                const query = cmd.replace('search ', '').trim();
                const searchInput = document.getElementById('menuSearchInput');
                if (searchInput) {
                    searchInput.value = query;
                    filterMenu();
                    speakVoiceFeedback(`Filtered menu for ${query}`);
                }
            }
        }


        // --- Multi-Store HQ & Inter-Venue Stock Transfer Engine ---
        async function loadTransfers() {
            const container = document.getElementById('transfersListContainer');
            if(!container) return;

            const res = await fetch('/api/transfers');
            const data = await res.json();
            const transfers = data.transfers || [];

            if(transfers.length === 0) {
                container.innerHTML = '<div class="text-muted small p-2 text-center">No inter-venue stock transfers logged yet.</div>';
                return;
            }

            container.innerHTML = transfers.map(t => {
                let badgeClass = 'bg-secondary';
                if(t.status === 'DISPATCHED') badgeClass = 'bg-warning text-dark';
                if(t.status === 'RECEIVED') badgeClass = 'bg-success';
                return `
                    <div class="p-2 border rounded mb-2 bg-white d-flex justify-content-between align-items-center shadow-sm">
                        <div>
                            <strong class="d-block text-dark small">${t.id} <span class="badge ${badgeClass}">${t.status}</span></strong>
                            <small class="text-muted">${t.source_venue_id} ➔ ${t.target_venue_id} (${(t.items||[]).length} items)</small>
                        </div>
                        <div class="d-flex gap-1">
                            <a href="/api/transfers/${t.id}/pdf" target="_blank" class="btn btn-xs btn-outline-dark py-0 px-2" title="Download Manifest"><i class="fa-solid fa-file-pdf"></i> Manifest</a>
                            ${t.status === 'REQUESTED' ? `<button class="btn btn-xs btn-warning text-dark fw-bold py-0 px-2" onclick="updateTransferStatus('${t.id}', 'DISPATCHED')">Dispatch</button>` : ''}
                            ${t.status === 'DISPATCHED' ? `<button class="btn btn-xs btn-success fw-bold py-0 px-2" onclick="updateTransferStatus('${t.id}', 'RECEIVED')">Receive</button>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function submitStoreTransfer(e) {
            if(e) e.preventDefault();
            const srcVenue = document.getElementById('transferSourceVenue').value;
            const tgtVenue = document.getElementById('transferTargetVenue').value;
            const itemId = document.getElementById('transferItemId').value;
            const qty = parseInt(document.getElementById('transferQty').value) || 10;

            if(srcVenue === tgtVenue) return alert('Source and target venues must be different.');

            const res = await fetch('/api/transfers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_venue_id: srcVenue,
                    target_venue_id: tgtVenue,
                    items: [{ item_id: itemId, quantity: qty }],
                    requested_by: "Central Kitchen HQ",
                    notes: "Routine Stock Replenishment"
                })
            });
            const data = await res.json();
            if(data.id) {
                alert(`Stock Transfer ${data.id} Dispatched successfully!`);
                loadTransfers();
            } else {
                alert(data.error || 'Failed to dispatch stock transfer.');
            }
        }

        async function updateTransferStatus(transferId, newStatus) {
            const res = await fetch(`/api/transfers/${transferId}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_status: newStatus })
            });
            const data = await res.json();
            if(data.id) {
                alert(`Transfer ${transferId} status updated to ${newStatus}!`);
                loadTransfers();
                if(typeof loadInventory === 'function') loadInventory();
            } else {
                alert(data.error || 'Failed to update transfer status.');
            }
        }


        // --- Blueprint Features: AI Language Toggle Matrix & Visual Floor Plan Map ---
        function setAppLanguage(lang) {
            currentLang = lang;
            ['en', 'fr', 'ar'].forEach(l => {
                const btn = document.getElementById(`langBtn-${l}`);
                if(btn) {
                    if(l === lang) {
                        btn.className = 'btn btn-dark text-white fw-bold px-2';
                    } else {
                        btn.className = 'btn btn-outline-light text-white fw-bold px-2';
                    }
                }
            });

            // Adjust document direction for Arabic
            if(lang === 'ar') {
                document.body.setAttribute('dir', 'rtl');
            } else {
                document.body.removeAttribute('dir');
            }

            loadMenu();
        }

        async function loadVisualFloorplan() {
            const container = document.getElementById('visualFloorplanGrid');
            if(!container) return;

            const res = await fetch('/api/floorplan/tables');
            const data = await res.json();
            const tables = Array.isArray(data) ? data : (data.tables || []);

            let html = '';
            tables.forEach(t => {
                const tNum = t.table_number || t.number;
                const st = (t.status || 'AVAILABLE').toUpperCase();
                let statusColor = 'border-success bg-success bg-opacity-10';
                let badgeBg = 'bg-success';
                if(st === 'OCCUPIED') {
                    statusColor = 'border-danger bg-danger bg-opacity-10';
                    badgeBg = 'bg-danger';
                } else if(st === 'RESERVED') {
                    statusColor = 'border-warning bg-warning bg-opacity-10';
                    badgeBg = 'bg-warning text-dark';
                }

                html += `
                    <div class="col-6 col-sm-4 col-md-3">
                        <div class="card p-3 text-white border-2 ${statusColor} rounded-3 shadow-sm text-center position-relative">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <strong class="fs-5 text-white">Table #${tNum}</strong>
                                <span class="badge ${badgeBg} rounded-pill">${st}</span>
                            </div>
                            <div class="my-2">
                                <i class="fa-solid fa-chair fs-3 opacity-75"></i>
                                <div class="small text-light opacity-75 mt-1">${t.capacity} Seats (${t.shape || 'Booth'} - ${t.zone || 'Main'})</div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top border-secondary">
                                <small class="text-warning fw-bold"><i class="fa-solid fa-clock me-1"></i> ${st === 'OCCUPIED' ? 'Turn: 35m' : 'Ready'}</small>
                                ${st === 'AVAILABLE'
                                    ? `<button class="btn btn-xs btn-outline-warning py-0 px-2" onclick="quickToggleTableStatus(${tNum}, 'reserve')">Reserve</button>`
                                    : `<button class="btn btn-xs btn-outline-success py-0 px-2" onclick="quickToggleTableStatus(${tNum}, 'release')">Release</button>`
                                }
                            </div>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        async function quickToggleTableStatus(tableNum, action) {
            const url = action === 'reserve' ? '/api/floorplan/reserve' : '/api/floorplan/release';
            await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ table_number: tableNum, guest_name: 'Walk-In VIP', party_size: 2 })
            });
            loadVisualFloorplan();
        }

        // --- Automated Smart Upsell Recommendation Engine (Page 6 Blueprint) ---
        function triggerSmartUpsell(itemId, itemName) {
            const upsellItem = { id: 'item-3', name: 'Craft IPA Pint', price: 6.20 };
            const modalHtml = `
                <div class="modal fade" id="smartUpsellModal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content border-0 shadow-lg">
                            <div class="modal-header bg-gradient text-white" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);">
                                <h5 class="modal-title fw-bold"><i class="fa-solid fa-bolt text-warning me-2"></i>Automated Smart Upsell</h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body p-4 text-center">
                                <h6 class="fw-bold text-dark mb-2">Great choice with ${itemName}!</h6>
                                <p class="small text-muted mb-3">Guests who ordered this also paired it with our fresh Craft IPA Pint!</p>
                                <div class="p-3 bg-light rounded-3 border d-flex align-items-center justify-content-between mb-3">
                                    <div class="d-flex align-items-center gap-2">
                                        <i class="fa-solid fa-beer-mug-empty text-warning fs-3"></i>
                                        <div class="text-start">
                                            <strong class="d-block text-dark">${upsellItem.name}</strong>
                                            <small class="text-muted">Perfect pairing drink</small>
                                        </div>
                                    </div>
                                    <strong class="text-success fs-5">+£${upsellItem.price.toFixed(2)}</strong>
                                </div>
                                <button class="btn btn-success w-100 fw-bold py-2 mb-2" onclick="addUpsellToCart('${upsellItem.id}', '${upsellItem.name}', ${upsellItem.price})"><i class="fa-solid fa-plus me-1"></i> Add Pair to Order</button>
                                <button class="btn btn-link text-muted btn-sm text-decoration-none" data-bs-dismiss="modal">No thanks, continue</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            let existing = document.getElementById('smartUpsellModal');
            if(existing) existing.remove();

            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('smartUpsellModal'));
            modal.show();
        }

        function addUpsellToCart(id, name, price) {
            addToCart(id);
            const modalEl = document.getElementById('smartUpsellModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if(modal) modal.hide();
        }


        // --- ESC/POS Thermal Docket Printer Emulator ---
        async function openThermalPrinterEmulator(orderId) {
            const select = document.getElementById('thermalTargetOrderSelect');
            if(select) {
                // Populate active orders
                try {
                    const res = await fetch('/api/kds/active');
                    const data = await res.json();
                    const orders = data.orders || [];
                    if(orders.length > 0) {
                        select.innerHTML = orders.map(o => `<option value="${o.id}">Ticket #${o.id} (Table #${o.table_number})</option>`).join('');
                        if(orderId) select.value = orderId;
                    }
                } catch(e) {}
            }

            renderThermalRollPreview();
            const modal = new bootstrap.Modal(document.getElementById('thermalEmulatorModal'));
            modal.show();
        }

        async function renderThermalRollPreview() {
            const select = document.getElementById('thermalTargetOrderSelect');
            const orderId = select ? select.value : 'ORD-0001';
            const widthRadio = document.querySelector('input[name="thermalWidth"]:checked');
            const width = widthRadio ? parseInt(widthRadio.value) : 32;

            const res = await fetch(`/api/receipt/${orderId}/txt?width=${width}`);
            if(res.ok) {
                const text = await res.text();
                document.getElementById('thermalPaperContent').innerText = text;
            } else {
                document.getElementById('thermalPaperContent').innerText = `THE WAITER UK
ORDER: ${orderId}
================================
Fish & Chips          £14.50
Craft IPA Pint         £6.20
================================
TOTAL:                £20.70`;
            }
        }

        function simulateEscposPrintCut() {
            try {
                // Audio paper tear / cut simulation sound using Web Audio API
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(800, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime + 0.15);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.15);
            } catch(e) {}

            alert('✂️ [ESC/POS Hardware Emulator] Received GS V 65 0 (Paper Cut) command! Thermal Docket Printed to Network Spooler.');
        }

        function downloadThermalTxt() {
            const text = document.getElementById('thermalPaperContent').innerText;
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Kitchen_Docket_${Date.now()}.txt`;
            a.click();
            URL.revokeObjectURL(url);
        }


        // --- AI Sommelier & Culinary Companion Engine ---
        function showAiSommelierModal() {
            const modal = new bootstrap.Modal(document.getElementById('aiSommelierModal'));
            modal.show();
        }

        async function askAiSommelier(promptText) {
            document.getElementById('sommelierInputPrompt').value = promptText;
            await sendSommelierPrompt();
        }

        async function sendSommelierPrompt() {
            const input = document.getElementById('sommelierInputPrompt');
            const prompt = input.value.trim();
            if (!prompt) return;

            const chatBox = document.getElementById('sommelierChatBox');

            // Append User Message
            chatBox.innerHTML += `
                <div class="d-flex align-items-start gap-2 mb-3 justify-content-end">
                    <div class="p-3 bg-primary text-white rounded-3 shadow-sm" style="max-width: 80%;">
                        ${prompt}
                    </div>
                    <div class="bg-primary text-white rounded-circle p-2 fs-5"><i class="fa-solid fa-user"></i></div>
                </div>
            `;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/api/ai/sommelier', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, lang: currentLang })
                });
                const data = await res.json();

                let recsHtml = '';
                if (data.recommendations && data.recommendations.length > 0) {
                    recsHtml = `
                        <div class="mt-2 pt-2 border-top">
                            <small class="fw-bold text-dark d-block mb-1"><i class="fa-solid fa-star text-warning me-1"></i> Suggested Menu Pairings:</small>
                            <div class="vstack gap-2">
                                ${data.recommendations.map(r => `
                                    <div class="p-2 border rounded bg-white d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong class="text-dark small">${r.name}</strong>
                                            <small class="text-muted d-block">£${r.price.toFixed(2)}</small>
                                        </div>
                                        <button class="btn btn-xs btn-success fw-bold py-1 px-2" onclick="addToCart('${r.item_id}')"><i class="fa-solid fa-cart-plus me-1"></i> Add £${r.price.toFixed(2)}</button>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }

                // Append AI Response
                chatBox.innerHTML += `
                    <div class="d-flex align-items-start gap-2 mb-3">
                        <div class="bg-dark text-warning rounded-circle p-2 fs-5"><i class="fa-solid fa-robot"></i></div>
                        <div class="p-3 bg-light rounded-3 text-dark border shadow-sm" style="max-width: 85%;">
                            ${data.response_text}
                            ${recsHtml}
                        </div>
                    </div>
                `;
                chatBox.scrollTop = chatBox.scrollHeight;

            } catch(e) {
                console.error('Sommelier AI error', e);
            }
        }


        // --- AI Customer Review Auto-Responder Engine ---
        async function generateAiReviewResponse(rating, comment, tableNum) {
            try {
                const res = await fetch('/api/reviews/auto-respond', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rating: rating, comment: comment, table_number: tableNum })
                });
                const data = await res.json();
                if (data.response_draft) {
                    prompt('AI Generated Staff Response Draft (Copy & Send):', data.response_draft);
                }
            } catch(e) {
                console.error('AI Auto-responder error', e);
            }
        }


        // --- Complete Staff Workspace Tab Loaders & AI Review Auto-Responder ---
        async function loadBookings() {
            const tbody = document.getElementById('bookingsTableBody');
            if(!tbody) return;
            const res = await fetch('/api/bookings');
            const data = await res.json();
            const list = data.bookings || [];
            if(list.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">No active reservations found.</td></tr>';
                return;
            }
            tbody.innerHTML = list.map(b => `
                <tr>
                    <td><strong class="text-primary">${b.id}</strong></td>
                    <td>${b.guest_name}<br><small class="text-muted">${b.guest_phone}</small></td>
                    <td><span class="badge bg-dark">${b.party_size} Guests</span> (Table #${b.table_number})</td>
                    <td>${b.booking_date} @ <strong>${b.time_slot}</strong></td>
                    <td><small>${b.special_requests || 'None'}</small></td>
                    <td><span class="badge ${b.status === 'CONFIRMED' || b.status === 'SEATED' ? 'bg-success' : 'bg-secondary'}">${b.status}</span></td>
                    <td>
                        <div class="d-flex gap-1">
                            <a href="/api/bookings/${b.id}/pdf" target="_blank" class="btn btn-xs btn-outline-danger py-0 px-2"><i class="fa-solid fa-file-pdf"></i> PDF</a>
                            ${b.status === 'CONFIRMED' ? `<button class="btn btn-xs btn-success py-0 px-2" onclick="updateBookingStatus('${b.id}', 'SEATED')">Seat</button>` : ''}
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        async function updateBookingStatus(id, status) {
            await fetch(`/api/bookings/${id}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: status })
            });
            loadBookings();
            loadVisualFloorplan();
        }

        async function loadInventory() {
            const invContainer = document.getElementById('inventoryContainer');
            const poContainer = document.getElementById('purchaseOrdersContainer');
            if(!invContainer) return;

            const res = await fetch('/api/inventory');
            const items = await res.json();
            invContainer.innerHTML = items.map(it => {
                const isLow = it.stock_qty <= 10;
                const itemName = typeof it.name === 'object' ? (it.name[currentLang] || it.name.en) : it.name;
                return `
                    <div class="col-md-4">
                        <div class="card p-3 border ${isLow ? 'border-danger bg-danger bg-opacity-10' : 'bg-white'} shadow-sm">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <strong class="text-dark">${itemName}</strong>
                                <span class="badge ${isLow ? 'bg-danger' : 'bg-success'}">${it.stock_qty} in stock</span>
                            </div>
                            <button class="btn btn-xs btn-outline-primary fw-bold mt-1" onclick="restockInventoryItem('${it.id}', 25)">
                                <i class="fa-solid fa-plus me-1"></i> Quick Restock (+25)
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            const resPo = await fetch('/api/inventory/purchase-orders');
            const poData = await resPo.json();
            const pos = poData.purchase_orders || [];
            if(pos.length === 0) {
                poContainer.innerHTML = '<div class="col-12 text-muted small">All stock levels healthy. No automated supplier POs required.</div>';
            } else {
                poContainer.innerHTML = pos.map(po => `
                    <div class="col-md-6">
                        <div class="p-3 border rounded-3 bg-light d-flex justify-content-between align-items-center">
                            <div>
                                <strong class="text-dark d-block">${po.po_number} (${po.supplier_category})</strong>
                                <small class="text-muted">${po.supplier_name} • Est. Total: £${(po.total_estimated_cost || po.estimated_total_cost || 0).toFixed(2)}</small>
                            </div>
                            <div class="d-flex gap-1">
                                <a href="/api/inventory/purchase-orders/${po.supplier_category}/pdf" target="_blank" class="btn btn-sm btn-danger"><i class="fa-solid fa-file-pdf me-1"></i> PO PDF</a>
                                <a href="/api/inventory/purchase-orders/${po.supplier_category}/email" target="_blank" class="btn btn-sm btn-outline-dark">Email Draft</a>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        }

        async function restockInventoryItem(itemId, qty) {
            await fetch(`/api/inventory/restock/${itemId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ quantity: qty })
            });
            loadInventory();
            loadMenu();
        }

        async function loadWaste() {
            const analyticsEl = document.getElementById('wasteAnalyticsContent');
            const logsBody = document.getElementById('wasteLogsTableBody');
            if(!analyticsEl) return;

            const resAn = await fetch('/api/waste/analytics?currency=' + currentCurr);
            const an = await resAn.json();
            const sym = an.currency_symbol || '£';
            analyticsEl.innerHTML = `
                <div class="col-4">
                    <small class="text-muted d-block">Total Waste Cost</small>
                    <h4 class="fw-bold text-danger mb-0">${sym}${(an.total_financial_loss || an.total_waste_cost || 0).toFixed(2)}</h4>
                </div>
                <div class="col-4">
                    <small class="text-muted d-block">Units Lost</small>
                    <h4 class="fw-bold text-dark mb-0">${an.total_units_wasted || 0}</h4>
                </div>
                <div class="col-4">
                    <small class="text-muted d-block">Incidents</small>
                    <h4 class="fw-bold text-warning mb-0">${an.total_incidents || (an.reason_breakdown ? Object.keys(an.reason_breakdown).length : 0)}</h4>
                </div>
            `;

            const resLogs = await fetch('/api/waste/logs');
            const logsData = await resLogs.json();
            const logs = logsData.waste_logs || [];
            logsBody.innerHTML = logs.map(l => `
                <tr>
                    <td><small>${(l.logged_at || l.timestamp || '').slice(11, 16)}</small></td>
                    <td><strong>${l.item_name}</strong></td>
                    <td>${l.quantity}</td>
                    <td><span class="badge bg-warning text-dark">${l.reason}</span></td>
                    <td>${l.staff_name}</td>
                    <td class="text-danger fw-bold">£${(l.financial_loss || l.cost_impact || 0).toFixed(2)}</td>
                </tr>
            `).join('');
        }

        async function submitWasteLog(e) {
            if(e) e.preventDefault();
            const itemId = document.getElementById('wasteItemId').value;
            const qty = parseInt(document.getElementById('wasteQty').value) || 1;
            const reason = document.getElementById('wasteReason').value;
            const staff = document.getElementById('wasteStaffName').value.trim() || 'Head Chef';

            const res = await fetch('/api/waste/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: itemId, quantity: qty, reason: reason, staff_name: staff })
            });
            if(res.ok) {
                loadWaste();
                loadInventory();
            }
        }

        async function loadTax() {
            const container = document.getElementById('vatLedgerContainer');
            if(!container) return;
            const res = await fetch('/api/tax/vat-ledger?currency=' + currentCurr);
            const data = await res.json();
            const sym = data.currency_symbol || '£';
            const boxes = data.mtd_boxes || {};
            container.innerHTML = `
                <div class="row g-2 text-center mb-3">
                    <div class="col-4">
                        <div class="p-2 bg-light rounded border">
                            <small class="text-muted d-block">Gross Sales</small>
                            <strong class="text-dark">${sym}${(data.total_gross_revenue || boxes.box_6_total_value_sales_ex_vat || 0).toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="p-2 bg-light rounded border">
                            <small class="text-muted d-block">Net Revenue</small>
                            <strong class="text-primary">${sym}${(boxes.box_6_total_value_sales_ex_vat || 0).toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="p-2 bg-success bg-opacity-10 rounded border border-success">
                            <small class="text-success fw-bold d-block">VAT Due (Box 5)</small>
                            <strong class="text-success">${sym}${(boxes.box_5_net_vat_payable || 0).toFixed(2)}</strong>
                        </div>
                    </div>
                </div>
                <div class="small text-muted"><i class="fa-solid fa-check-circle text-success me-1"></i> HMRC Making Tax Digital (MTD) Compliant Ledger</div>
            `;
            loadTransfers();
        }

        async function loadFeedback() {
            const resNps = await fetch('/api/feedback/nps');
            const nps = await resNps.json();
            document.getElementById('npsScoreVal').innerText = (nps.nps_score >= 0 ? '+' : '') + nps.nps_score;
            document.getElementById('npsBreakdownText').innerText = `${nps.promoters_count || 0} Promoters | ${nps.passives_count || 0} Passives | ${nps.detractors_count || 0} Detractors`;

            const resSent = await fetch('/api/feedback/sentiment');
            const sent = await resSent.json();
            document.getElementById('sentimentDistributionContent').innerHTML = `
                <div class="d-flex justify-content-between small mb-1"><span>😊 Positive:</span> <strong>${sent.positive_reviews_count || 0}</strong></div>
                <div class="d-flex justify-content-between small mb-1"><span>😐 Neutral:</span> <strong>${sent.neutral_reviews_count || 0}</strong></div>
                <div class="d-flex justify-content-between small"><span>😟 Negative:</span> <strong class="text-danger">${sent.negative_reviews_count || 0}</strong></div>
            `;

            const resAlerts = await fetch('/api/feedback/alerts');
            const alertsData = await resAlerts.json();
            const alerts = alertsData.manager_alerts || [];
            document.getElementById('managerAlertsContent').innerHTML = alerts.length === 0
                ? '<div class="text-success small"><i class="fa-solid fa-check-circle me-1"></i> Zero critical guest alerts.</div>'
                : alerts.slice(0, 2).map(a => `<div class="small text-danger mb-1"><i class="fa-solid fa-triangle-exclamation me-1"></i> Table #${a.table_number}: "${a.comment}"</div>`).join('');

            const resRev = await fetch('/api/reviews');
            const revData = await resRev.json();
            const reviews = revData.reviews || [];
            const revContainer = document.getElementById('reviewsContainer');
            if(reviews.length === 0) {
                revContainer.innerHTML = '<div class="col-12 text-muted small">No guest reviews submitted yet.</div>';
                return;
            }
            revContainer.innerHTML = reviews.map(r => {
                const safeComment = (r.comment || '').replace(/'/g, "\'");
                return `
                    <div class="col-md-6">
                        <div class="p-3 border rounded-3 bg-light h-100 d-flex flex-column justify-content-between">
                            <div>
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <strong class="text-dark">Table #${r.table_number}</strong>
                                    <span class="text-warning fw-bold">${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}</span>
                                </div>
                                <p class="small text-dark mb-2">"${r.comment || 'Great experience!'}"</p>
                            </div>
                            <div class="d-flex justify-content-between align-items-center pt-2 border-top">
                                <span class="badge ${r.rating >= 4 ? 'bg-success' : 'bg-warning text-dark'}">${r.rating >= 4 ? '5★ Booster Eligible' : 'Manager Follow-Up'}</span>
                                <button class="btn btn-xs btn-dark fw-bold py-1 px-2" onclick="generateAiReviewResponse(${r.rating}, '${safeComment}', ${r.table_number})">
                                    <i class="fa-solid fa-wand-magic-sparkles text-warning me-1"></i> AI Auto-Reply
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function loadForecasting() {
            const tbody = document.getElementById('aiForecastTableBody');
            const matrixEl = document.getElementById('menuMatrixContainer');
            if(!tbody) return;

            const resPrep = await fetch('/api/forecasting/prep-demand');
            const prepData = await resPrep.json();
            const forecasts = prepData.prep_demand_forecasts || [];
            tbody.innerHTML = forecasts.map(f => `
                <tr>
                    <td><strong>${f.item_name}</strong></td>
                    <td>${f.baseline_daily_avg || f.historical_avg_daily || 15}</td>
                    <td><span class="badge bg-primary fs-6">${f.predicted_prep_units || f.recommended_prep_qty} units</span></td>
                    <td><span class="text-success fw-bold">${f.confidence_pct || f.confidence_score || 94}%</span></td>
                </tr>
            `).join('');

            const resMat = await fetch('/api/forecasting/menu-matrix');
            const matData = await resMat.json();
            const mat = matData.matrix || {};
            let matHtml = '';
            Object.keys(mat).forEach(quad => {
                (mat[quad] || []).forEach(it => {
                    matHtml += `
                        <div class="p-2 border rounded mb-2 d-flex justify-content-between align-items-center">
                            <div>
                                <strong class="text-dark small d-block">${it.item_name || it.name}</strong>
                                <small class="text-muted">Margin: £${(it.profit_margin || 0).toFixed(2)}</small>
                            </div>
                            <span class="badge bg-info text-dark">${quad}</span>
                        </div>
                    `;
                });
            });
            matrixEl.innerHTML = matHtml || '<div class="text-muted small">Matrix calculated.</div>';
        }

        async function loadStaff() {
            const resLabor = await fetch('/api/staff/labor-summary?currency=' + currentCurr);
            const labor = await resLabor.json();
            const sym = labor.currency_symbol || '£';
            document.getElementById('activeStaffBadge').innerText = `${labor.active_staff_count} Active`;
            document.getElementById('laborSummaryContent').innerHTML = `
                <div class="col-4">
                    <small class="text-muted d-block">Labor Cost</small>
                    <strong class="fs-5 text-dark">${sym}${labor.total_labor_cost.toFixed(2)}</strong>
                </div>
                <div class="col-4">
                    <small class="text-muted d-block">Labor % of Sales</small>
                    <strong class="fs-5 text-primary">${labor.labor_cost_percentage}%</strong>
                </div>
                <div class="col-4">
                    <small class="text-muted d-block">Total Hours</small>
                    <strong class="fs-5 text-success">${labor.total_hours_worked}h</strong>
                </div>
            `;

            const resTips = await fetch('/api/finance/tips');
            const tips = await resTips.json();
            document.getElementById('troncSummaryContainer').innerHTML = `
                <div class="d-flex justify-content-between mb-1 small"><span>Total Service Charge Pool:</span> <strong class="text-success">£${(tips.total_tronc_pool || 0).toFixed(2)}</strong></div>
                <div class="d-flex justify-content-between small"><span>Active Staff Share:</span> <strong>£${(tips.per_staff_share || 0).toFixed(2)} / person</strong></div>
            `;

            const resShifts = await fetch('/api/staff/shifts');
            const shifts = await resShifts.json();
            document.getElementById('shiftHistoryContainer').innerHTML = (shifts || []).map(s => `
                <div class="p-2 border-bottom small d-flex justify-content-between">
                    <span><strong>${s.name}</strong> (${s.role})</span>
                    <span class="badge ${s.status === 'CLOCKED_IN' ? 'bg-success' : 'bg-secondary'}">${s.status}</span>
                </div>
            `).join('');
        }

        async function staffClockIn() {
            const pin = document.getElementById('staffPinInput').value.trim();
            const res = await fetch('/api/staff/clock-in', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: pin })
            });
            const data = await res.json();
            alert(data.message || data.error || 'Clock-in processed.');
            loadStaff();
        }

        async function staffClockOut() {
            const pin = document.getElementById('staffPinInput').value.trim();
            const res = await fetch('/api/staff/clock-out', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: pin })
            });
            const data = await res.json();
            alert(data.message || data.error || 'Clock-out processed.');
            loadStaff();
        }


        // --- 1. Executive Peak-Hour Sales Heatmap & Table Turnover Analytics ---
        async function loadSalesHeatmap() {
            const heatmapEl = document.getElementById('salesHeatmapGrid');
            const zoneEl = document.getElementById('zoneTurnoverContainer');
            if(!heatmapEl || !zoneEl) return;

            try {
                const res = await fetch('/api/analytics/heatmap?currency=' + currentCurr);
                const data = await res.json();
                const sym = data.currency_symbol || '£';

                if(data.peak_window) {
                    const badge = document.getElementById('peakWindowBadge');
                    if(badge) badge.innerText = `Peak Rush: ${data.peak_window}`;
                }

                const maxRev = Math.max(...(data.hourly_heatmap || []).map(h => h.revenue), 1);
                heatmapEl.innerHTML = (data.hourly_heatmap || []).map(h => {
                    const widthPct = Math.max(12, Math.round((h.revenue / maxRev) * 100));
                    let barColor = 'bg-info';
                    let badgeClass = 'bg-secondary';
                    if(h.intensity === 'PEAK_RUSH') {
                        barColor = 'bg-danger';
                        badgeClass = 'bg-danger';
                    } else if(h.intensity === 'HIGH') {
                        barColor = 'bg-warning';
                        badgeClass = 'bg-warning text-dark';
                    } else if(h.intensity === 'MODERATE') {
                        barColor = 'bg-primary';
                        badgeClass = 'bg-primary';
                    }
                    return `
                        <div class="p-2 border rounded bg-light">
                            <div class="d-flex justify-content-between align-items-center small mb-1">
                                <div>
                                    <strong class="text-dark me-2">${h.hour}</strong>
                                    <span class="badge ${badgeClass}">${h.intensity}</span>
                                    <small class="text-muted ms-2"><i class="fa-solid fa-user-check me-1"></i>Rec. Staff: <strong>${h.recommended_staff}</strong></small>
                                </div>
                                <strong class="text-dark">${sym}${h.revenue.toFixed(2)} <small class="text-muted fw-normal">(${h.orders_count} ord)</small></strong>
                            </div>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar ${barColor}" role="progressbar" style="width: ${widthPct}%"></div>
                            </div>
                        </div>
                    `;
                }).join('');

                zoneEl.innerHTML = (data.zone_turnover || []).map(z => {
                    const isFast = z.avg_turn_mins <= z.target_turn_mins;
                    return `
                        <div class="p-3 border rounded-3 bg-light d-flex justify-content-between align-items-center">
                            <div>
                                <strong class="text-dark d-block">${z.zone}</strong>
                                <small class="text-muted">Target: ${z.target_turn_mins}m • Active Tables: ${z.tables_count}</small>
                            </div>
                            <div class="text-end">
                                <span class="fs-5 fw-bold ${isFast ? 'text-success' : 'text-warning'}"><i class="fa-solid fa-clock-rotate-left me-1"></i>${z.avg_turn_mins} min</span>
                                <small class="d-block ${isFast ? 'text-success' : 'text-danger'} fw-bold">${isFast ? 'Optimal Flow' : 'High Dwell'}</small>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch(e) {
                console.error('Failed to load sales heatmap', e);
            }
        }

        // --- 2. Digital Kitchen Recipe & Natasha's Law Allergen Matrix ---
        async function openChefRecipeModal() {
            const container = document.getElementById('chefRecipesContainer');
            const modal = new bootstrap.Modal(document.getElementById('chefRecipeModal'));
            modal.show();

            try {
                const res = await fetch('/api/kds/recipes');
                const data = await res.json();
                const recipes = data.recipes || [];

                container.innerHTML = recipes.map(r => `
                    <div class="col-md-6">
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
                                <div>
                                    <span class="badge station-badge-${r.station} me-2">${r.station}</span>
                                    <strong class="fs-5 text-dark">${r.dish_name}</strong>
                                </div>
                                <span class="badge bg-dark"><i class="fa-solid fa-stopwatch me-1 text-warning"></i>${r.prep_mins} mins</span>
                            </div>
                            <div class="card-body">
                                <div class="mb-2">
                                    <small class="fw-bold text-uppercase text-muted d-block">🌡️ Core Cooking Temp & Target:</small>
                                    <span class="badge bg-danger bg-opacity-10 text-danger border border-danger fw-bold">${r.cooking_temp}</span>
                                </div>
                                <div class="mb-3">
                                    <small class="fw-bold text-uppercase text-muted d-block mb-1">⚖️ Standardized Ingredients & Weights:</small>
                                    <ul class="small text-dark mb-0 ps-3">
                                        ${(r.ingredients || []).map(ing => `<li>${ing}</li>`).join('')}
                                    </ul>
                                </div>
                                <div class="mb-3">
                                    <small class="fw-bold text-uppercase text-muted d-block mb-1">🍽️ Chef Plating Specification:</small>
                                    <p class="small text-muted mb-0">${r.plating_guide}</p>
                                </div>
                                <div class="p-2 rounded bg-warning bg-opacity-10 border border-warning">
                                    <small class="fw-bold text-dark d-block"><i class="fa-solid fa-triangle-exclamation text-danger me-1"></i>UK Natasha's Law Allergen Matrix:</small>
                                    <div class="d-flex flex-wrap gap-1 my-1">
                                        ${(r.allergens || []).length > 0
                                            ? r.allergens.map(a => `<span class="badge bg-danger text-uppercase">${a}</span>`).join('')
                                            : '<span class="badge bg-success">Allergen-Free Spec</span>'
                                        }
                                    </div>
                                    <small class="text-danger fw-semibold d-block">${r.cross_contamination_note}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch(e) {
                console.error('Failed to load chef recipes', e);
            }
        }

        // --- 3. Interactive Delivery Aggregator Command Center ---
        async function loadDeliveryHub() {
            const grid = document.getElementById('deliveryChannelsGrid');
            if(!grid) return;

            const res = await fetch('/api/integrations/channels');
            const data = await res.json();
            const channels = data.channels || [];

            const icons = {
                'DELIVEROO': 'fa-solid fa-person-biking text-info',
                'UBEREATS': 'fa-solid fa-utensils text-success',
                'DELIVERECT': 'fa-solid fa-network-wired text-primary',
                'TOAST': 'fa-solid fa-bread-slice text-warning'
            };

            grid.innerHTML = channels.map(c => `
                <div class="col-md-3">
                    <div class="card card-custom p-3 bg-white shadow-sm h-100 border-top border-4 border-info">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <strong class="text-dark"><i class="${icons[c.channel] || 'fa-solid fa-plug'} me-1"></i> ${c.channel}</strong>
                            <span class="badge bg-success">${c.status}</span>
                        </div>
                        <div class="my-2">
                            <small class="text-muted d-block">Orders Injected</small>
                            <h4 class="fw-bold text-dark mb-0">${c.processed_orders_count}</h4>
                            <small class="text-success fw-bold">£${c.total_revenue_processed.toFixed(2)} rev</small>
                        </div>
                        <button class="btn btn-xs btn-outline-dark fw-bold w-100 mt-auto py-1" onclick="syncChannelMenu('${c.channel}')">
                            <i class="fa-solid fa-rotate me-1"></i> 1-Click Sync Menu
                        </button>
                    </div>
                </div>
            `).join('');
        }

        async function syncChannelMenu(platform) {
            const res = await fetch(`/api/integrations/sync-menu/${platform}`, { method: 'POST' });
            const data = await res.json();
            const box = document.getElementById('deliverySyncResultBox');
            if(box) {
                box.innerText = JSON.stringify(data, null, 2);
            }
            alert(`✅ Synced ${data.synced_items_count} menu items & stock quantities to ${platform}!`);
        }

        async function triggerSimulatedDeliveryWebhook(e) {
            if(e) e.preventDefault();
            const platform = document.getElementById('simDeliveryPlatform').value;
            const customer = document.getElementById('simDeliveryCustomer').value.trim();
            const address = document.getElementById('simDeliveryAddress').value.trim();
            const itemCombo = document.getElementById('simDeliveryItems').value.split(',');

            const itemsPayload = itemCombo.map(id => ({ item_id: id.trim() }));
            const extRef = `${platform.slice(0,3)}-${Math.floor(1000 + Math.random() * 9000)}`;

            const res = await fetch(`/api/integrations/webhook/${platform}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    external_order_ref: extRef,
                    customer_name: customer,
                    delivery_address: address,
                    items: itemsPayload,
                    table_number: 99
                })
            });
            const data = await res.json();
            if(res.ok) {
                playOrderChime();
                alert(`🛵 [${platform} Webhook] Order ${data.order_id} (Ref: ${data.external_ref}) injected into Kitchen KDS!`);
                loadDeliveryHub();
                loadKDS();
                loadExecutiveKPIs();
            } else {
                alert(data.error || 'Webhook failed');
            }
        }

        // --- 4. Live Table Service Calls Queue & Guest Active Promos ---
        async function loadServiceCallsQueue() {
            const card = document.getElementById('staffServiceCallsCard');
            const list = document.getElementById('staffServiceCallsList');
            const badge = document.getElementById('activeServiceCallsCountBadge');
            if(!card || !list) return;

            try {
                const res = await fetch('/api/service-calls');
                const data = await res.json();
                const calls = data.active_calls || [];
                if(calls.length === 0) {
                    card.classList.add('d-none');
                    return;
                }
                card.classList.remove('d-none');
                badge.innerText = `${calls.length} Pending`;
                list.innerHTML = calls.map(c => `
                    <div class="d-flex align-items-center gap-2 bg-white border border-warning rounded-pill px-3 py-1 shadow-sm">
                        <span class="badge bg-dark">Table #${c.table_number}</span>
                        <strong class="small text-dark">${c.label}</strong>
                        <button class="btn btn-xs btn-success rounded-pill py-0 px-2 fw-bold small" onclick="resolveServiceCall('${c.id}')">✓ Resolve</button>
                    </div>
                `).join('');
            } catch(e) { console.error(e); }
        }

        async function resolveServiceCall(callId) {
            await fetch(`/api/service-calls/${callId}/resolve`, { method: 'POST' });
            loadServiceCallsQueue();
        }

        async function loadGuestActivePromos() {
            const container = document.getElementById('guestPromoBadgesContainer');
            if(!container) return;
            try {
                const res = await fetch('/api/promos');
                const promos = await res.json();
                const entries = Object.entries(promos || {});
                container.innerHTML = entries.map(([code, p]) => {
                    const pct = typeof p === 'object' ? Math.round(p.discount_pct) : Math.round(p * 100);
                    return `
                        <button class="btn btn-xs btn-warning text-dark fw-bold rounded-pill px-2 py-0 small" onclick="applyPromoToGuestCart('${code}', ${pct})">
                            <i class="fa-solid fa-tag me-1"></i>${code} (${pct}% OFF)
                        </button>
                    `;
                }).join('');
            } catch(e) { console.error(e); }
        }

        function applyPromoToGuestCart(code, pct) {
            const p1 = document.getElementById('promoInput');
            const p2 = document.getElementById('mobilePromoInput');
            if(p1) p1.value = code;
            if(p2) p2.value = code;
            alert(`🎉 Promo code ${code} (${pct}% OFF) applied to your Table Cart!`);
        }

        // --- 5. Interactive Z-Report Reconciliation & Promo Campaign Studio ---
        async function loadZReportAndPromos() {
            const zContainer = document.getElementById('zReportInteractiveContainer');
            const pContainer = document.getElementById('staffPromosListContainer');
            if(zContainer) {
                const res = await fetch(`/api/finance/z-report?currency=${currentCurr}`);
                const z = await res.json();
                const sym = currSymbols[currentCurr] || '£';
                const topDishesHtml = (z.top_dishes || []).map(([name, qty]) => `
                    <span class="badge bg-light text-dark border me-1 mb-1">${name}: <strong>${qty} sold</strong></span>
                `).join('') || '<span class="text-muted small">No dishes sold yet</span>';

                zContainer.innerHTML = `
                    <div class="row g-2 mb-3">
                        <div class="col-sm-4">
                            <div class="p-3 bg-light rounded-3 border text-center">
                                <small class="text-muted d-block">Gross Sales</small>
                                <h5 class="fw-bold text-dark mb-0">${sym}${z.gross_sales.toFixed(2)}</h5>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="p-3 bg-light rounded-3 border text-center">
                                <small class="text-muted d-block">${z.vat_label}</small>
                                <h5 class="fw-bold text-danger mb-0">${sym}${z.vat_amount.toFixed(2)}</h5>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="p-3 bg-success bg-opacity-10 rounded-3 border border-success text-center">
                                <small class="text-success fw-bold d-block">Total Net Collected</small>
                                <h5 class="fw-bold text-success mb-0">${sym}${z.total_revenue.toFixed(2)}</h5>
                            </div>
                        </div>
                    </div>
                    <table class="table table-sm table-bordered small mb-3">
                        <tbody>
                            <tr><td class="text-muted">Discounts & Promo Redemptions</td><td class="text-end fw-bold text-warning">-${sym}${z.discounts.toFixed(2)}</td></tr>
                            <tr><td class="text-muted">Net Taxable Sales (excl. VAT)</td><td class="text-end fw-bold">${sym}${z.net_sales.toFixed(2)}</td></tr>
                            <tr><td class="text-muted">Voided / Cancelled Orders Value</td><td class="text-end fw-bold text-danger">${sym}${z.voided_value.toFixed(2)} (${z.cancelled_tickets} voided)</td></tr>
                            <tr><td class="text-muted">Tickets Issued / Average Ticket Value (ATV)</td><td class="text-end fw-bold text-primary">${z.total_tickets} tickets • ATV ${sym}${z.atv.toFixed(2)}</td></tr>
                        </tbody>
                    </table>
                    <div>
                        <small class="fw-bold text-muted d-block mb-1">Top 5 Best-Selling Dishes Today:</small>
                        <div>${topDishesHtml}</div>
                    </div>
                `;
            }

            if(pContainer) {
                const pRes = await fetch('/api/promos');
                const promos = await pRes.json();
                pContainer.innerHTML = Object.entries(promos || {}).map(([code, p]) => {
                    const pct = typeof p === 'object' ? Math.round(p.discount_pct) : Math.round(p * 100);
                    return `
                        <div class="d-flex justify-content-between align-items-center p-2 bg-light rounded border">
                            <div>
                                <span class="badge bg-dark text-warning fw-bold me-2">${code}</span>
                                <strong class="small text-success">${pct}% Discount</strong>
                            </div>
                            <button class="btn btn-xs btn-outline-danger py-0 px-2 small" onclick="deletePromoCampaign('${code}')"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    `;
                }).join('');
            }
        }

        async function createPromoCampaign(e) {
            if(e) e.preventDefault();
            const code = document.getElementById('newPromoCodeInput').value.trim().toUpperCase();
            const pct = parseFloat(document.getElementById('newPromoDiscountInput').value);
            const res = await fetch('/api/promos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code, discount_pct: pct })
            });
            if(res.ok) {
                document.getElementById('newPromoCodeInput').value = '';
                loadZReportAndPromos();
                loadGuestActivePromos();
                alert(`🚀 Live Promo ${code} (${pct}% OFF) launched across all Guest QR Menus!`);
            }
        }

        async function deletePromoCampaign(code) {
            await fetch(`/api/promos/${code}`, { method: 'DELETE' });
            loadZReportAndPromos();
            loadGuestActivePromos();
        }

        // --- 6. Page 8 KPI Horizon Switcher & Page 10/11 ROI & Consultation Handlers ---
        function switchBlueprintKpiHorizon(horizon) {
            ['daily', 'monthly', 'annual'].forEach(h => {
                const btn = document.getElementById('kpiHorizon-' + h);
                if(btn) {
                    btn.className = (h === horizon) ? 'btn btn-dark fw-bold active' : 'btn btn-outline-dark fw-bold';
                }
            });
            const label = document.getElementById('bpHorizonLabel');
            const rev = document.getElementById('bpHorizonRev');
            const ord = document.getElementById('bpHorizonOrders');
            const top = document.getElementById('bpHorizonTopItem');
            if(horizon === 'daily') {
                if(label) label.innerText = 'DAILY';
                if(rev) rev.innerText = '£3,735.50 Sales';
                if(ord) ord.innerText = '152 Tickets';
                if(top) top.innerText = 'Top: Classic Pub Burger';
            } else if(horizon === 'monthly') {
                if(label) label.innerText = 'MONTHLY';
                if(rev) rev.innerText = '£108,450.00 Sales';
                if(ord) ord.innerText = '4,420 Tickets';
                if(top) top.innerText = 'Top: Brixham Fish & Chips';
            } else {
                if(label) label.innerText = 'ANNUAL (YTD)';
                if(rev) rev.innerText = '£1,240,000.00 Sales ↑';
                if(ord) ord.innerText = '51,800 Tickets';
                if(top) top.innerText = 'Top: Craft IPA & Wagyu Burger';
            }
        }

        function calculateBlueprintRoi() {
            const saasCount = parseInt(document.getElementById('roiSaasCount')?.value || 5);
            const tablesCount = parseInt(document.getElementById('roiTablesCount')?.value || 15);
            // £5,000 hardware trap saved + £95/mo per disconnected SaaS tool + £280/table annual labor & error savings
            const annualSavings = 5000 + (saasCount * 95 * 12) + (tablesCount * 160);
            const el = document.getElementById('roiAnnualSavingsLabel');
            if(el) el.innerText = `£${annualSavings.toLocaleString()} / yr`;
        }

        async function submitBlueprintConsultation(e) {
            if(e) e.preventDefault();
            const venueName = document.getElementById('consultVenueName').value.trim();
            const contact = document.getElementById('consultEmail').value.trim();
            const res = await fetch('/api/blueprint/consultation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ venue_name: venueName, contact: contact })
            });
            const data = await res.json();
            if(res.ok) {
                alert(`🎉 ${data.message}`);
                document.getElementById('consultVenueName').value = '';
                document.getElementById('consultEmail').value = '';
            }
        }

        // --- 7. 🇬🇧 UK Statutory Compliance & EHO Hub Functions ---
        async function loadUkComplianceHub() {
            await previewNatashasLawLabel();
            await loadTipsAct2024Panel();
            await loadChallenge25Panel();
            await loadFoodSafetyPanel();
            await simulateHmrcVatMode('COLD_TAKEAWAY');
            await loadUkGdprSecurityPanel();
        }

        async function previewNatashasLawLabel() {
            const itemId = document.getElementById('ppdsDishSelect')?.value || 'item-1';
            const res = await fetch(`/api/uk-compliance/natashas-law/${itemId}`);
            const data = await res.json();
            const box = document.getElementById('ppdsLabelPreviewBox');
            if(box) box.innerHTML = data.natashas_law_label_html;
        }

        async function buildCustomPpdsLabel() {
            const rawStr = document.getElementById('ppdsCustomIngInput')?.value || '';
            const ingredients = rawStr.split(',').map(s => s.trim()).filter(Boolean);
            if(ingredients.length === 0) return previewNatashasLawLabel();
            const res = await fetch('/api/uk-compliance/natashas-law/build', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: 'custom-deli', ingredients: ingredients })
            });
            const data = await res.json();
            const box = document.getElementById('ppdsLabelPreviewBox');
            if(box) box.innerHTML = data.natashas_law_label_html;
        }

        function printPpdsGrabAndGoLabel() {
            alert("🏷️ [Natasha's Law PPDS Printer] Sent compliant Prepacked for Direct Sale (PPDS) label with BOLD allergen ingredients & Use-By timestamp to Deli Label Printer!");
        }

        async function loadTipsAct2024Panel() {
            const res = await fetch('/api/uk-compliance/tips-act-2024');
            const data = await res.json();
            const polBox = document.getElementById('tipsActPolicyBox');
            const logsBox = document.getElementById('tipsActPayoutLogsContainer');
            if(polBox && data.written_policy) {
                polBox.innerHTML = `
                    <strong class="text-dark d-block">${data.written_policy.legislation}</strong>
                    <span class="text-muted">${data.written_policy.policy_summary}</span>
                `;
            }
            if(logsBox) {
                logsBox.innerHTML = `
                    <table class="table table-sm table-bordered small mb-0">
                        <thead class="table-light">
                            <tr><th>Staff</th><th>Role</th><th>Hrs</th><th>Employer Ded.</th><th class="text-end">100% Net Paid</th></tr>
                        </thead>
                        <tbody>
                            ${(data.staff_payout_logs || []).map(p => `
                                <tr>
                                    <td class="fw-bold">${p.staff_name}</td>
                                    <td>${p.role}</td>
                                    <td>${p.hours_worked}h</td>
                                    <td class="text-success fw-bold">£0.00 (0%)</td>
                                    <td class="text-end fw-bold text-success">£${p.net_payout_gbp.toFixed(2)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            }
        }

        async function recordUkTipPayout(e) {
            if(e) e.preventDefault();
            const name = document.getElementById('tipStaffName').value.trim();
            const role = document.getElementById('tipStaffRole').value.trim();
            const hrs = parseFloat(document.getElementById('tipStaffHours').value || 38);
            await fetch('/api/uk-compliance/tips-act-2024/payout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ staff_name: name, role: role, hours_worked: hrs, amount_gbp: +(hrs * 4.25).toFixed(2) })
            });
            document.getElementById('tipStaffName').value = '';
            loadTipsAct2024Panel();
        }

        async function loadChallenge25Panel() {
            const res = await fetch('/api/uk-compliance/challenge25/logs');
            const data = await res.json();
            const box = document.getElementById('challenge25LogsContainer');
            if(!box) return;
            box.innerHTML = (data.logs || []).map(c => `
                <div class="p-2 rounded border bg-light d-flex justify-content-between align-items-center small">
                    <div>
                        <span class="badge ${c.decision === 'APPROVED' ? 'bg-success' : 'bg-danger'} me-1">${c.decision}</span>
                        <strong>Table #${c.table_number}</strong> • ${c.id_type}
                        <small class="text-muted d-block">Verified by: ${c.verified_by_staff}</small>
                    </div>
                    <small class="text-muted">${c.check_id}</small>
                </div>
            `).join('');
        }

        async function submitChallenge25Check(e) {
            if(e) e.preventDefault();
            const tbl = parseInt(document.getElementById('ch25TableNum').value || 4);
            const idType = document.getElementById('ch25IdType').value;
            const dec = document.getElementById('ch25Decision').value;
            await fetch('/api/uk-compliance/challenge25/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ table_number: tbl, order_id: 'ORD-LIVE', decision: dec, id_type: idType })
            });
            loadChallenge25Panel();
        }

        async function loadFoodSafetyPanel() {
            const res = await fetch('/api/uk-compliance/food-safety');
            const data = await res.json();
            const badge = document.getElementById('ehoReadyStatusBadge');
            if(badge) {
                badge.className = data.eho_inspection_ready ? 'badge bg-success' : 'badge bg-danger';
                badge.innerText = data.eho_inspection_ready ? '✓ 5-Star EHO Inspection Ready' : '⚠️ CCP Action Required';
            }
            const tBox = document.getElementById('fridgeTempLogsContainer');
            if(tBox) {
                tBox.innerHTML = (data.fridge_temp_logs || []).map(l => `
                    <div class="d-flex justify-content-between align-items-center p-1 px-2 border-bottom small">
                        <span><strong>${l.unit_name}</strong> <small class="text-muted">(${l.target_range})</small></span>
                        <span class="badge ${l.status === 'COMPLIANT' ? 'bg-success' : 'bg-danger'}">${l.recorded_temp_c}°C • ${l.status}</span>
                    </div>
                `).join('');
            }
            const hBox = document.getElementById('haccpChecklistContainer');
            if(hBox) {
                hBox.innerHTML = (data.cleaning_haccp_checklists || []).map(t => `
                    <div class="form-check small">
                        <input class="form-check-input" type="checkbox" ${t.completed ? 'checked' : ''} onchange="toggleHaccpTask('${t.task_id}')">
                        <label class="form-check-label ${t.completed ? 'text-decoration-line-through text-muted' : 'fw-bold text-dark'}">
                            [${t.category}] ${t.task}
                        </label>
                    </div>
                `).join('');
            }
        }

        async function submitFridgeTempLog(e) {
            if(e) e.preventDefault();
            const rawUnit = document.getElementById('safetyUnitName').value.split('|');
            const tempVal = parseFloat(document.getElementById('safetyTempVal').value);
            await fetch('/api/uk-compliance/food-safety/temp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ unit_name: rawUnit[0], unit_type: rawUnit[1], recorded_temp_c: tempVal, checked_by: 'Duty Manager' })
            });
            loadFoodSafetyPanel();
        }

        async function toggleHaccpTask(taskId) {
            await fetch('/api/uk-compliance/food-safety/haccp-toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: taskId })
            });
            loadFoodSafetyPanel();
        }

        async function simulateHmrcVatMode(mode) {
            const res = await fetch('/api/uk-compliance/vat-mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dining_mode: mode, items: ['item-1', 'item-3', 'item-4'] })
            });
            const data = await res.json();
            const box = document.getElementById('hmrcVat709ResultBox');
            if(!box) return;
            box.innerHTML = `
                <div class="d-flex justify-content-between mb-2 border-bottom pb-1">
                    <strong>Mode: <span class="text-primary">${data.dining_mode}</span></strong>
                    <span class="badge bg-dark">Total VAT: £${data.total_vat_payable_gbp.toFixed(2)}</span>
                </div>
                ${(data.items_breakdown || []).map(i => `
                    <div class="d-flex justify-content-between text-muted">
                        <span>${i.name} (${i.vat_rate_pct}% VAT)</span>
                        <span>Net £${i.net_price_gbp.toFixed(2)} + VAT £${i.vat_amount_gbp.toFixed(2)}</span>
                    </div>
                `).join('')}
                <div class="mt-2 pt-1 border-top d-flex justify-content-between fw-bold text-dark">
                    <span>Zero-Rated (0%) Sales: £${data.net_zero_rated_gbp.toFixed(2)}</span>
                    <span class="text-success">Standard (20%) Net: £${data.net_standard_rated_gbp.toFixed(2)}</span>
                </div>
            `;
        }

        async function loadUkGdprSecurityPanel() {
            const res = await fetch('/api/uk-compliance/gdpr-security');
            const data = await res.json();
            const box = document.getElementById('ukGdprSecurityBox');
            if(!box) return;
            box.innerHTML = `
                <div class="mb-2"><strong><i class="fa-solid fa-cloud text-primary me-1"></i>Hosting Residency:</strong> ${data.data_residency}</div>
                <div class="mb-2"><strong><i class="fa-solid fa-shield-halved text-success me-1"></i>Cyber Security:</strong> ${data.cyber_security_certification}</div>
                <div class="mb-2"><strong><i class="fa-solid fa-key text-warning me-1"></i>Encryption:</strong> ${data.encryption_standard}</div>
                <ul class="mb-0 ps-3 text-muted">
                    ${(data.guest_privacy_controls || []).map(c => `<li>${c}</li>`).join('')}
                </ul>
            `;
        }

        // --- 8. 💷 Money & Margins Hub & Percentage Bill Split Functions ---
        async function calculatePercentageSplit() {
            const raw = document.getElementById('pctSplitInput')?.value || '50, 25, 25';
            const pcts = raw.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
            const orderId = activeOrderForTable ? activeOrderForTable.id : 'ORD-0001';
            const res = await fetch(`/api/orders/${orderId}/split/percentage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ percentages: pcts, include_service_charge: true })
            });
            const data = await res.json();
            const box = document.getElementById('pctSplitResultContainer');
            if(!res.ok) {
                alert(data.error || 'Percentages must sum to 100%');
                return;
            }
            if(box) {
                box.innerHTML = (data.shares || []).map(s => `
                    <div class="p-2 mb-2 rounded border bg-light d-flex justify-content-between align-items-center small">
                        <div>
                            <strong class="text-dark">Guest #${s.guest_index} (${s.percentage}% Share)</strong>
                            <small class="text-success d-block">Pay-by-Bank saves £${s.merchant_saving_with_pay_by_bank_gbp.toFixed(2)} in card fees</small>
                        </div>
                        <span class="badge bg-dark text-warning fs-6">£${s.amount_due_gbp.toFixed(2)}</span>
                    </div>
                `).join('');
            }
        }

        async function loadMoneyAndMarginsHub() {
            await loadAccountingProviders();
            await loadRecipeGpMatrix();
            await loadWholesalersAndInvoices();
            await loadRotaLabourAndPayroll();
        }

        async function loadAccountingProviders() {
            const grid = document.getElementById('accountingProvidersGrid');
            if(!grid) return;
            const res = await fetch('/api/margins/accounting/status');
            const data = await res.json();
            grid.innerHTML = (data.providers || []).map(p => `
                <div class="col-md-3">
                    <div class="p-3 border rounded-3 bg-light h-100 d-flex flex-column justify-content-between">
                        <div>
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <strong class="text-dark">${p.provider}</strong>
                                <span class="badge bg-success">${p.status}</span>
                            </div>
                            <small class="text-muted d-block mb-2">${p.display_name}</small>
                            <div class="small fw-bold text-primary mb-2">Posted: £${p.total_posted_gbp.toLocaleString()} (${p.synced_journals_count} jnls)</div>
                        </div>
                        <button class="btn btn-xs btn-dark text-warning fw-bold w-100 py-1" onclick="syncAccountingProvider('${p.provider}')">
                            <i class="fa-solid fa-cloud-arrow-up me-1"></i> Sync Daily MTD Journal
                        </button>
                    </div>
                </div>
            `).join('');
        }

        async function syncAccountingProvider(provider) {
            const res = await fetch(`/api/margins/accounting/sync/${provider}`, { method: 'POST' });
            const data = await res.json();
            if(res.ok) {
                alert(`✅ [${data.display_name}] Posted Journal ${data.journal_ref} to Nominal Ledger!`);
                loadAccountingProviders();
            }
        }

        async function loadRecipeGpMatrix() {
            const box = document.getElementById('recipeGpMatrixContainer');
            if(!box) return;
            const res = await fetch('/api/margins/recipe-gp');
            const data = await res.json();
            const badge = document.getElementById('avgMenuGpBadge');
            if(badge) badge.innerText = `Avg Menu GP: ${data.average_menu_gp_pct}% (Target 70%)`;

            box.innerHTML = (data.dishes_gp_matrix || []).map(d => `
                <div class="p-2 px-3 rounded border bg-light d-flex justify-content-between align-items-center small">
                    <div>
                        <strong class="text-dark">${d.dish_name}</strong>
                        <span class="badge ${d.low_stock_alert ? 'bg-danger' : 'bg-secondary'} ms-1">Stock: ${d.stock_qty}</span>
                        <small class="text-muted d-block">Menu £${d.gross_menu_price_gbp.toFixed(2)} (Net £${d.net_price_excl_vat_gbp.toFixed(2)}) • COGS £${d.recipe_cogs_gbp.toFixed(2)}</small>
                    </div>
                    <div class="text-end">
                        <span class="badge ${d.gp_percentage >= 70 ? 'bg-success' : 'bg-warning text-dark'} fs-6">${d.gp_percentage}% GP</span>
                        <small class="d-block text-success fw-bold">+£${d.gross_profit_gbp.toFixed(2)} profit/dish</small>
                    </div>
                </div>
            `).join('');
        }

        async function loadWholesalersAndInvoices() {
            const wBox = document.getElementById('ukWholesalersContainer');
            const sBox = document.getElementById('scannedInvoicesAlertBox');
            if(!wBox) return;
            const res = await fetch('/api/margins/suppliers');
            const data = await res.json();

            wBox.innerHTML = (data.wholesalers || []).map(w => `
                <div class="p-2 px-3 rounded border bg-light d-flex justify-content-between align-items-center small">
                    <div>
                        <strong class="text-dark">${w.name}</strong> <span class="badge bg-secondary">${w.account_ref}</span>
                        <small class="text-muted d-block">${w.delivery_schedule} • ${w.reorder_items.length} core lines</small>
                    </div>
                    <button class="btn btn-xs btn-primary fw-bold py-1 px-2" onclick="orderFromUkWholesaler('${w.supplier_code}')">
                        <i class="fa-solid fa-paper-plane me-1"></i> 1-Click Reorder
                    </button>
                </div>
            `).join('');

            if(sBox && data.scanned_invoices && data.scanned_invoices.length > 0) {
                const latest = data.scanned_invoices[0];
                sBox.innerHTML = `
                    <div class="p-2 rounded bg-warning bg-opacity-10 border border-warning text-dark">
                        <strong><i class="fa-solid fa-triangle-exclamation text-danger me-1"></i>${latest.scan_id} (${latest.supplier}):</strong>
                        ${(latest.price_variance_alerts || []).join(' ')}
                    </div>
                `;
            }
        }

        async function orderFromUkWholesaler(code) {
            const res = await fetch(`/api/margins/suppliers/order/${code}`, { method: 'POST' });
            const data = await res.json();
            if(res.ok) {
                alert(`🚛 [EDI Order ${data.po_reference}] Sent to ${data.supplier_name} (£${data.total_order_net_gbp.toFixed(2)} net) — Stock replenished!`);
                loadRecipeGpMatrix();
            }
        }

        async function scanSupplierInvoice(e) {
            if(e) e.preventDefault();
            const sup = document.getElementById('scanSupplierSelect').value;
            const codCost = parseFloat(document.getElementById('scanCodCostInput').value || 2.75);
            const res = await fetch('/api/margins/suppliers/scan-invoice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ supplier_code: sup, invoice_ref: `${sup}-INV-LIVE`, cod_unit_cost_gbp: codCost })
            });
            if(res.ok) {
                await loadWholesalersAndInvoices();
                await loadRecipeGpMatrix();
            }
        }

        async function loadRotaLabourAndPayroll() {
            const box = document.getElementById('rotaLabourPayrollContainer');
            if(!box) return;
            const res = await fetch('/api/margins/labour-payroll');
            const data = await res.json();
            const badge = document.getElementById('liveLabourRatioBadge');
            if(badge) {
                badge.className = data.labour_cost_pct_of_sales <= 28 ? 'badge bg-success fs-6 px-3 py-2' : 'badge bg-danger fs-6 px-3 py-2';
                badge.innerText = `Labour vs Net Sales: ${data.labour_cost_pct_of_sales}% (Weekly Sales £${data.weekly_net_sales_gbp.toLocaleString()})`;
            }
            box.innerHTML = `
                <table class="table table-sm table-bordered align-middle small mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Employee</th>
                            <th>Role</th>
                            <th>Rate</th>
                            <th>Rota Hrs</th>
                            <th>Base Gross</th>
                            <th>UK Holiday Accrual (12.07%)</th>
                            <th>Employer NIC (15%)</th>
                            <th class="text-end">Total Employer Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${(data.rota_payroll_schedule || []).map(r => `
                            <tr>
                                <td class="fw-bold">${r.name} <span class="badge bg-light text-muted border">${r.staff_id}</span></td>
                                <td>${r.role}</td>
                                <td>£${r.hourly_rate_gbp.toFixed(2)}/h</td>
                                <td>${r.rota_hours_week}h</td>
                                <td>£${r.base_gross_pay_gbp.toFixed(2)}</td>
                                <td class="text-primary fw-bold">${r.holiday_hours_accrued_12_07_pct}h (£${r.holiday_pay_accrual_gbp.toFixed(2)})</td>
                                <td>£${r.employer_nic_gbp.toFixed(2)}</td>
                                <td class="text-end fw-bold text-dark">£${r.total_employer_labour_cost_gbp.toFixed(2)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                    <tfoot class="table-light fw-bold">
                        <tr>
                            <td colspan="3">WEEKLY ROTA TOTALS</td>
                            <td>${data.total_rota_hours}h</td>
                            <td>£${data.total_base_wages_gbp.toFixed(2)}</td>
                            <td class="text-primary">£${data.total_holiday_accrual_gbp.toFixed(2)}</td>
                            <td>£${data.total_employer_nic_gbp.toFixed(2)}</td>
                            <td class="text-end text-success">£${data.total_fully_loaded_labour_cost_gbp.toFixed(2)}</td>
                        </tr>
                    </tfoot>
                </table>
            `;
        }
    </script>
</body>
</html>"""

TV_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guest TV Order Pickup Display | The Waiter</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; background-color: #0b0c10; color: #fff; overflow: hidden; height: 100vh; }
        .tv-header { background: #1f2833; border-bottom: 4px solid #66fcf1; padding: 20px 40px; }
        .column-header-prep { background: #ff9800; color: #000; font-size: 1.8rem; font-weight: 800; text-transform: uppercase; padding: 15px; border-radius: 12px 12px 0 0; text-align: center; }
        .column-header-ready { background: #4caf50; color: #fff; font-size: 1.8rem; font-weight: 800; text-transform: uppercase; padding: 15px; border-radius: 12px 12px 0 0; text-align: center; }
        .tv-panel { background: #1f2833; border-radius: 0 0 12px 12px; padding: 25px; height: calc(100vh - 170px); overflow-y: auto; }
        .ticket-badge { font-size: 2.5rem; font-weight: 900; padding: 15px 25px; border-radius: 16px; margin-bottom: 15px; text-align: center; box-shadow: 0 8px 16px rgba(0,0,0,0.4); }
        .badge-preparing { background: #332200; color: #ffb74d; border: 2px solid #ff9800; }
        .badge-ready { background: #1b5e20; color: #81c784; border: 3px solid #4caf50; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }
    </style>
</head>
<body>
    <div class="tv-header d-flex justify-content-between align-items-center">
        <h2 class="fw-bold mb-0 text-info"><i class="fa-solid fa-utensils me-3"></i>THE WAITER — LIVE ORDER PICKUP</h2>
        <div class="d-flex align-items-center gap-3">
            <span class="badge bg-success fs-5"><i class="fa-solid fa-bolt me-1"></i> Live TV Feed</span>
            <a href="/" class="btn btn-outline-light"><i class="fa-solid fa-house me-1"></i> Back</a>
        </div>
    </div>

    <div class="container-fluid p-4">
        <div class="row g-4">
            <!-- Preparing Column -->
            <div class="col-6">
                <div class="column-header-prep"><i class="fa-solid fa-fire-burner me-2"></i> PREPARING 🍳</div>
                <div class="tv-panel" id="preparingContainer">
                    <!-- Dynamically populated -->
                </div>
            </div>

            <!-- Ready Column -->
            <div class="col-6">
                <div class="column-header-ready"><i class="fa-solid fa-bell me-2"></i> READY FOR PICKUP 🎉</div>
                <div class="tv-panel" id="readyContainer">
                    <!-- Dynamically populated -->
                </div>
            </div>
        </div>
    </div>

    <script>
        function renderTVData(data) {
            const prepContainer = document.getElementById('preparingContainer');
            if(!data.preparing || data.preparing.length === 0) {
                prepContainer.innerHTML = '<div class="text-center text-muted fs-4 my-5">No orders preparing</div>';
            } else {
                prepContainer.innerHTML = data.preparing.map(id => `
                    <div class="ticket-badge badge-preparing">${id}</div>
                `).join('');
            }

            const readyContainer = document.getElementById('readyContainer');
            if(!data.ready || data.ready.length === 0) {
                readyContainer.innerHTML = '<div class="text-center text-muted fs-4 my-5">No orders ready</div>';
            } else {
                readyContainer.innerHTML = data.ready.map(id => `
                    <div class="ticket-badge badge-ready">${id}</div>
                `).join('');
            }
        }

        async function updateTVDisplay() {
            try {
                const res = await fetch('/api/kds/tv');
                const data = await res.json();
                renderTVData(data);
            } catch(e) { console.error(e); }
        }

        updateTVDisplay();

        // Zero-Latency Server-Sent Events (SSE) Stream
        if ('EventSource' in window) {
            const evtSource = new EventSource('/api/kds/events');
            evtSource.addEventListener('kds_update', function(e) {
                const payload = JSON.parse(e.data);
                if (payload.tv) {
                    renderTVData(payload.tv);
                } else {
                    updateTVDisplay();
                }
            });
            evtSource.onerror = function() {
                setInterval(updateTVDisplay, 5000);
            };
        } else {
            setInterval(updateTVDisplay, 3000);
        }
    </script>

</body>
</html>
"""

TERMINAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Netoff Terminal Pro | Counter Kiosk POS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; background-color: #1a1a24; color: #fff; user-select: none; }
        .terminal-header { background: #12121a; border-bottom: 2px solid #00b4db; padding: 15px 25px; }
        .touch-btn { height: 90px; border-radius: 12px; font-size: 1.1rem; font-weight: 700; border: none; transition: transform 0.1s; }
        .touch-btn:active { transform: scale(0.96); }
        .table-btn { height: 60px; border-radius: 10px; font-weight: bold; border: 2px solid #333; background: #252538; color: #fff; }
        .table-btn.selected { border-color: #00b4db; background: #00b4db; color: #fff; }
        .kiosk-cart { background: #252538; border-radius: 16px; padding: 20px; height: calc(100vh - 120px); display: flex; flex-direction: column; }
        .scan-bar { background: #12121a; border: 1px solid #333; border-radius: 8px; color: #fff; font-family: monospace; }
        .pay-btn { height: 70px; font-size: 1.4rem; font-weight: bold; }
    </style>
</head>
<body>
    <div class="terminal-header d-flex justify-content-between align-items-center">
        <div>
            <h3 class="fw-bold mb-0 text-info"><i class="fa-solid fa-desktop me-2"></i>Netoff Terminal Pro</h3>
            <span class="small text-muted">All-in-One Counter POS Kiosk • UK Storefront</span>
        </div>
        <div class="d-flex align-items-center gap-3">
            <span class="badge bg-success p-2"><i class="fa-solid fa-wifi me-1"></i> Cloud Synced</span>
            <a href="/" class="btn btn-outline-light btn-sm"><i class="fa-solid fa-house me-1"></i> Main App</a>
        </div>
    </div>

    <div class="container-fluid p-4">
        <div class="row g-4">
            <div class="col-md-7 col-lg-8">
                <div class="input-group mb-4">
                    <span class="input-group-text scan-bar"><i class="fa-solid fa-barcode text-info"></i></span>
                    <input type="text" id="barcodeScanner" class="form-control scan-bar py-2" placeholder="Scan Item Barcode / QR Code..." onkeydown="handleBarcode(event)">
                    <button class="btn btn-info fw-bold" onclick="simulateScan('item-1')"><i class="fa-solid fa-qrcode me-1"></i> Scan Cod</button>
                    <button class="btn btn-warning text-dark fw-bold" onclick="simulateScan('item-3')"><i class="fa-solid fa-qrcode me-1"></i> Scan IPA</button>
                </div>

                <h6 class="text-uppercase text-muted fw-bold mb-2">Select Table</h6>
                <div class="row g-2 mb-4" id="tableGrid">
                    <!-- Loaded dynamically -->
                </div>

                <h6 class="text-uppercase text-muted fw-bold mb-2">Touch Menu Catalogue</h6>
                <div class="row g-3" id="kioskMenuGrid">
                    <!-- Loaded dynamically -->
                </div>
            </div>

            <div class="col-md-5 col-lg-4">
                <div class="kiosk-cart">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4 class="fw-bold mb-0">Current Ticket</h4>
                        <span class="badge bg-info fs-6" id="kioskTableBadge">Table #1</span>
                    </div>
                    
                    <div id="kioskCartItems" class="flex-grow-1 overflow-auto mb-3 text-muted small">
                        No items added to current ticket.
                    </div>

                    <div class="border-top border-secondary pt-3">
                        <div class="d-flex justify-content-between fs-5 mb-1">
                            <span>Subtotal:</span>
                            <span id="kioskSubtotal">£0.00</span>
                        </div>
                        <div class="d-flex justify-content-between fs-6 text-success mb-2">
                            <span>UK VAT (20% Inc):</span>
                            <span id="kioskVat">£0.00</span>
                        </div>
                        <div class="d-flex justify-content-between fs-3 fw-bold mb-3 text-warning">
                            <span>TOTAL:</span>
                            <span id="kioskTotal">£0.00</span>
                        </div>

                        <div class="row g-2">
                            <div class="col-6">
                                <button class="btn btn-success pay-btn w-100" onclick="processTerminalCheckout('CARD')">
                                    <i class="fa-solid fa-credit-card d-block mb-1"></i> CARD
                                </button>
                            </div>
                            <div class="col-6">
                                <button class="btn btn-primary pay-btn w-100" onclick="processTerminalCheckout('CASH')">
                                    <i class="fa-solid fa-money-bill-wave d-block mb-1"></i> CASH
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let selectedTable = 1;
        let kioskCart = [];

        function renderTableGrid() {
            const container = document.getElementById('tableGrid');
            let html = '';
            for(let i=1; i<=12; i++) {
                const isSel = i === selectedTable ? 'selected' : '';
                html += `<div class="col-3 col-sm-2">
                    <button class="btn table-btn w-100 ${isSel}" onclick="selectTable(${i})">T-${i}</button>
                </div>`;
            }
            container.innerHTML = html;
        }

        function selectTable(num) {
            selectedTable = num;
            document.getElementById('kioskTableBadge').innerText = 'Table #' + num;
            renderTableGrid();
        }

        async function loadKioskMenu() {
            const res = await fetch('/api/menu?lang=en');
            const data = await res.json();
            const container = document.getElementById('kioskMenuGrid');
            
            const btnColors = ['btn-primary', 'btn-success', 'btn-warning text-dark', 'btn-info text-dark', 'btn-secondary'];
            container.innerHTML = data.map((item, idx) => `
                <div class="col-6 col-sm-4">
                    <button class="btn ${btnColors[idx % btnColors.length]} touch-btn w-100 d-flex flex-column justify-content-center align-items-center" onclick="addKioskCart('${item.id}', '${item.name_translated}', ${item.price})">
                        <span>${item.name_translated}</span>
                        <span class="fs-6 fw-normal mt-1">£${item.price.toFixed(2)}</span>
                    </button>
                </div>
            `).join('');
        }

        function addKioskCart(id, name, price) {
            kioskCart.push({ id, name, price });
            renderKioskCart();
        }

        function renderKioskCart() {
            const container = document.getElementById('kioskCartItems');
            if(kioskCart.length === 0) {
                container.innerHTML = 'No items added to current ticket.';
                document.getElementById('kioskSubtotal').innerText = '£0.00';
                document.getElementById('kioskVat').innerText = '£0.00';
                document.getElementById('kioskTotal').innerText = '£0.00';
                return;
            }

            let subtotal = 0;
            container.innerHTML = kioskCart.map((item, idx) => {
                subtotal += item.price;
                return `<div class="d-flex justify-content-between align-items-center mb-2 fs-5 bg-dark p-2 rounded">
                    <span>${item.name}</span>
                    <div>
                        <span class="text-warning me-3">£${item.price.toFixed(2)}</span>
                        <button class="btn btn-sm btn-outline-danger" onclick="removeKioskCart(${idx})">&times;</button>
                    </div>
                </div>`;
            }).join('');

            const vat = subtotal * 0.20 / 1.20;
            document.getElementById('kioskSubtotal').innerText = '£' + subtotal.toFixed(2);
            document.getElementById('kioskVat').innerText = '£' + vat.toFixed(2);
            document.getElementById('kioskTotal').innerText = '£' + subtotal.toFixed(2);
        }

        function removeKioskCart(idx) {
            kioskCart.splice(idx, 1);
            renderKioskCart();
        }

        function simulateScan(itemId) {
            fetch('/api/menu?lang=en').then(r => r.json()).then(menu => {
                const item = menu.find(m => m.id === itemId);
                if(item) addKioskCart(item.id, item.name_translated, item.price);
            });
        }

        function handleBarcode(e) {
            if(e.key === 'Enter') {
                const val = e.target.value.trim();
                if(val) simulateScan(val);
                e.target.value = '';
            }
        }

        async function processTerminalCheckout(method) {
            if(kioskCart.length === 0) return alert('Cannot process empty ticket.');
            const res = await fetch('/api/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table_number: selectedTable,
                    items: kioskCart.map(i => i.id)
                })
            });
            const order = await res.json();
            alert(`[Netoff Terminal Pro] Ticket ${order.id} Paid via ${method}! Printing thermal receipt...`);
            
            window.open('/api/receipt/' + order.id + '/txt', '_blank');

            kioskCart = [];
            renderKioskCart();
        }

        renderTableGrid();
        loadKioskMenu();

        // --- 4. Live Table Service Calls Queue & Guest Active Promos ---
        async function loadServiceCallsQueue() {
            const card = document.getElementById('staffServiceCallsCard');
            const list = document.getElementById('staffServiceCallsList');
            const badge = document.getElementById('activeServiceCallsCountBadge');
            if(!card || !list) return;

            try {
                const res = await fetch('/api/service-calls');
                const data = await res.json();
                const calls = data.active_calls || [];
                if(calls.length === 0) {
                    card.classList.add('d-none');
                    return;
                }
                card.classList.remove('d-none');
                badge.innerText = `${calls.length} Pending`;
                list.innerHTML = calls.map(c => `
                    <div class="d-flex align-items-center gap-2 bg-white border border-warning rounded-pill px-3 py-1 shadow-sm">
                        <span class="badge bg-dark">Table #${c.table_number}</span>
                        <strong class="small text-dark">${c.label}</strong>
                        <button class="btn btn-xs btn-success rounded-pill py-0 px-2 fw-bold small" onclick="resolveServiceCall('${c.id}')">✓ Resolve</button>
                    </div>
                `).join('');
            } catch(e) { console.error(e); }
        }

        async function resolveServiceCall(callId) {
            await fetch(`/api/service-calls/${callId}/resolve`, { method: 'POST' });
            loadServiceCallsQueue();
        }

        async function loadGuestActivePromos() {
            const container = document.getElementById('guestPromoBadgesContainer');
            if(!container) return;
            try {
                const res = await fetch('/api/promos');
                const promos = await res.json();
                const entries = Object.entries(promos || {});
                container.innerHTML = entries.map(([code, disc]) => `
                    <button class="btn btn-xs btn-warning text-dark fw-bold rounded-pill px-2 py-0 small" onclick="applyPromoToGuestCart('${code}', ${Math.round(disc * 100)})">
                        <i class="fa-solid fa-tag me-1"></i>${code} (${Math.round(disc * 100)}% OFF)
                    </button>
                `).join('');
            } catch(e) { console.error(e); }
        }

        function applyPromoToGuestCart(code, pct) {
            const p1 = document.getElementById('promoInput');
            const p2 = document.getElementById('mobilePromoInput');
            if(p1) p1.value = code;
            if(p2) p2.value = code;
            alert(`🎉 Promo code ${code} (${pct}% OFF) applied to your Table Cart!`);
        }

        // --- 5. Interactive Z-Report Reconciliation & Promo Campaign Studio ---
        async function loadZReportAndPromos() {
            const zContainer = document.getElementById('zReportInteractiveContainer');
            const pContainer = document.getElementById('staffPromosListContainer');
            if(zContainer) {
                const res = await fetch(`/api/finance/z-report?currency=${currentCurr}`);
                const z = await res.json();
                const sym = currSymbols[currentCurr] || '£';
                const topDishesHtml = (z.top_dishes || []).map(([name, qty]) => `
                    <span class="badge bg-light text-dark border me-1 mb-1">${name}: <strong>${qty} sold</strong></span>
                `).join('') || '<span class="text-muted small">No dishes sold yet</span>';

                zContainer.innerHTML = `
                    <div class="row g-2 mb-3">
                        <div class="col-sm-4">
                            <div class="p-3 bg-light rounded-3 border text-center">
                                <small class="text-muted d-block">Gross Sales</small>
                                <h5 class="fw-bold text-dark mb-0">${sym}${z.gross_sales.toFixed(2)}</h5>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="p-3 bg-light rounded-3 border text-center">
                                <small class="text-muted d-block">${z.vat_label}</small>
                                <h5 class="fw-bold text-danger mb-0">${sym}${z.vat_amount.toFixed(2)}</h5>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="p-3 bg-success bg-opacity-10 rounded-3 border border-success text-center">
                                <small class="text-success fw-bold d-block">Total Net Collected</small>
                                <h5 class="fw-bold text-success mb-0">${sym}${z.total_revenue.toFixed(2)}</h5>
                            </div>
                        </div>
                    </div>
                    <table class="table table-sm table-bordered small mb-3">
                        <tbody>
                            <tr><td class="text-muted">Discounts & Promo Redemptions</td><td class="text-end fw-bold text-warning">-${sym}${z.discounts.toFixed(2)}</td></tr>
                            <tr><td class="text-muted">Net Taxable Sales (excl. VAT)</td><td class="text-end fw-bold">${sym}${z.net_sales.toFixed(2)}</td></tr>
                            <tr><td class="text-muted">Voided / Cancelled Orders Value</td><td class="text-end fw-bold text-danger">${sym}${z.voided_value.toFixed(2)} (${z.cancelled_tickets} voided)</td></tr>
                            <tr><td class="text-muted">Tickets Issued / Average Ticket Value (ATV)</td><td class="text-end fw-bold text-primary">${z.total_tickets} tickets • ATV ${sym}${z.atv.toFixed(2)}</td></tr>
                        </tbody>
                    </table>
                    <div>
                        <small class="fw-bold text-muted d-block mb-1">Top 5 Best-Selling Dishes Today:</small>
                        <div>${topDishesHtml}</div>
                    </div>
                `;
            }

            if(pContainer) {
                const pRes = await fetch('/api/promos');
                const promos = await pRes.json();
                pContainer.innerHTML = Object.entries(promos || {}).map(([code, disc]) => `
                    <div class="d-flex justify-content-between align-items-center p-2 bg-light rounded border">
                        <div>
                            <span class="badge bg-dark text-warning fw-bold me-2">${code}</span>
                            <strong class="small text-success">${Math.round(disc * 100)}% Discount</strong>
                        </div>
                        <button class="btn btn-xs btn-outline-danger py-0 px-2 small" onclick="deletePromoCampaign('${code}')"><i class="fa-solid fa-trash"></i></button>
                    </div>
                `).join('');
            }
        }

        async function createPromoCampaign(e) {
            if(e) e.preventDefault();
            const code = document.getElementById('newPromoCodeInput').value.trim().toUpperCase();
            const pct = parseFloat(document.getElementById('newPromoDiscountInput').value);
            const res = await fetch('/api/promos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code, discount_pct: pct })
            });
            if(res.ok) {
                document.getElementById('newPromoCodeInput').value = '';
                loadZReportAndPromos();
                loadGuestActivePromos();
                alert(`🚀 Live Promo ${code} (${pct}% OFF) launched across all Guest QR Menus!`);
            }
        }

        async function deletePromoCampaign(code) {
            await fetch(`/api/promos/${code}`, { method: 'DELETE' });
            loadZReportAndPromos();
            loadGuestActivePromos();
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(INDEX_HTML)

@app.route("/tv")
def tv_display():
    return render_template_string(TV_HTML)

@app.route("/terminal")
def terminal():
    return render_template_string(TERMINAL_HTML)

# --- 1. CSV Export Endpoints ---
@app.route("/api/export/orders/csv", methods=["GET"])
def export_orders_csv():
    csv_data = exporter_service.export_orders_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=Orders_Export.csv"}
    )

@app.route("/api/export/inventory/csv", methods=["GET"])
def export_inventory_csv():
    csv_data = exporter_service.export_inventory_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=Inventory_Export.csv"}
    )

@app.route("/api/export/reviews/csv", methods=["GET"])
def export_reviews_csv():
    csv_data = exporter_service.export_reviews_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=Reviews_Export.csv"}
    )

# --- 1b. Z-Report Endpoints ---
@app.route("/api/finance/z-report", methods=["GET"])
def get_z_report():
    date_param = request.args.get("date")
    curr = request.args.get("currency", "GBP")
    return jsonify(finance_service.generate_z_report(date_str=date_param, currency=curr))

@app.route("/api/finance/z-report/pdf", methods=["GET"])
def download_z_report_pdf():
    date_param = request.args.get("date")
    curr = request.args.get("currency", "GBP")
    pdf_bytes = finance_service.generate_pdf_z_report(date_str=date_param, currency=curr)
    file_date = date_param or "Today"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename=Z_Report_{file_date}.pdf"}
    )

# --- 1c. Venue Endpoints ---
@app.route("/api/venues", methods=["GET"])
def get_venues():
    return jsonify({
        "venues": venue_service.get_venues(),
        "active_venue": venue_service.get_active_venue()
    })

@app.route("/api/venues/switch", methods=["POST"])
def switch_venue():
    data = request.json or {}
    venue_id = data.get("venue_id", "")
    if venue_service.set_active_venue(venue_id):
        return jsonify({"success": True, "active_venue": venue_service.get_active_venue()})
    return jsonify({"success": False, "error": "Invalid venue_id"}), 400

# --- 1d. SSE Real-Time KDS & TV Event Stream ---
@app.route("/api/kds/events", methods=["GET"])
def stream_kds_events():
    def event_stream():
        q = kds_service.subscribe()
        try:
            yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"
            while True:
                try:
                    msg = q.get(timeout=15)
                    yield msg
                except queue.Empty:
                    yield ": heartbeat\n\n"
        finally:
            kds_service.unsubscribe(q)

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )

# --- 1e. Staff Time Clock & Shift Endpoints ---
@app.route("/api/staff/roster", methods=["GET"])
def get_staff_roster():
    return jsonify(staff_service.get_staff_members())

@app.route("/api/staff/shifts", methods=["GET"])
def get_staff_shifts():
    return jsonify({
        "shifts": staff_service.get_shifts(),
        "active_shifts": staff_service.get_active_shifts()
    })

@app.route("/api/staff/clock-in", methods=["POST"])
def staff_clock_in():
    data = request.json or {}
    pin = data.get("pin", "")
    res = staff_service.clock_in(pin)
    if res.get("success"):
        return jsonify(res)
    return jsonify(res), 400

@app.route("/api/staff/clock-out", methods=["POST"])
def staff_clock_out():
    data = request.json or {}
    pin = data.get("pin", "")
    res = staff_service.clock_out(pin)
    if res.get("success"):
        return jsonify(res)
    return jsonify(res), 400

@app.route("/api/staff/labor-summary", methods=["GET"])
def get_labor_summary():
    curr = request.args.get("currency", "GBP")
    return jsonify(staff_service.get_labor_analytics(currency=curr))

# --- 1f. Floor Plan Map & Reservation Endpoints ---
@app.route("/api/floorplan/tables", methods=["GET"])
def get_floorplan():
    return jsonify(floor_plan_service.get_floor_plan())

@app.route("/api/floorplan/reserve", methods=["POST"])
def reserve_table():
    data = request.json or {}
    table_num = int(data.get("table_number", 0))
    guest = data.get("guest_name", "Guest")
    time_slot = data.get("time_slot", "19:00")
    res = floor_plan_service.reserve_table(table_num, guest, time_slot)
    return jsonify(res)

@app.route("/api/floorplan/release", methods=["POST"])
def release_table():
    data = request.json or {}
    table_num = int(data.get("table_number", 0))
    res = floor_plan_service.release_table(table_num)
    return jsonify(res)

# --- 1g. Customer Loyalty & Rewards Endpoints ---
@app.route("/api/loyalty/account", methods=["GET"])
def get_loyalty_account():
    identifier = request.args.get("identifier", "")
    acc = loyalty_service.get_account(identifier)
    if acc:
        return jsonify({"success": True, "account": acc})
    return jsonify({"success": False, "error": "Account not found"}), 404

@app.route("/api/loyalty/register", methods=["POST"])
def register_loyalty_account():
    data = request.json or {}
    identifier = data.get("phone_or_email") or data.get("identifier", "")
    guest = data.get("guest_name", "")
    res = loyalty_service.register_account(identifier, guest)
    if res.get("success"):
        return jsonify(res)
    return jsonify(res), 400

@app.route("/api/loyalty/earn", methods=["POST"])
def earn_loyalty_points():
    data = request.json or {}
    identifier = data.get("phone_or_email") or data.get("identifier", "")
    order_id = data.get("order_id", "")
    res = loyalty_service.earn_points(identifier, order_id)
    if res.get("success"):
        return jsonify(res)
    return jsonify(res), 400

@app.route("/api/loyalty/redeem", methods=["POST"])
def redeem_loyalty_reward():
    data = request.json or {}
    identifier = data.get("phone_or_email") or data.get("identifier", "")
    reward_key = data.get("reward_key", "")
    res = loyalty_service.redeem_reward(identifier, reward_key)
    if res.get("success"):
        return jsonify(res)
    return jsonify(res), 400

# --- 1h. Allergen & Dietary Filtered Menu Endpoint ---
@app.route("/api/menu/filtered", methods=["GET"])
def get_filtered_menu():
    lang = request.args.get("lang", "en")
    curr = request.args.get("currency", "GBP")
    dietary = request.args.get("dietary")
    exclude_param = request.args.get("exclude", "")
    exclude_list = [a.strip() for a in exclude_param.split(",") if a.strip()]
    return jsonify(allergen_service.get_filtered_menu(
        language=lang,
        currency=curr,
        dietary_filter=dietary,
        exclude_allergens=exclude_list
    ))

# --- 1i. Kitchen Prep Time & Station Routing Endpoints ---
@app.route("/api/kds/stations", methods=["GET"])
def get_kds_stations():
    return jsonify(prep_routing_service.get_station_queues())

@app.route("/api/kds/eta/<order_id>", methods=["GET"])
def get_order_eta(order_id):
    eta = prep_routing_service.calculate_order_eta(order_id)
    if eta:
        return jsonify(eta)
    return jsonify({"error": "Order not found"}), 404

# --- 1j. Tip & Service Charge (Tronc) Distribution Endpoints ---
@app.route("/api/finance/tips", methods=["GET"])
def get_tips_tronc_summary():
    curr = request.args.get("currency", "GBP")
    return jsonify(tips_tronc_service.get_tronc_summary(currency=curr))









# --- 2. PIN Auth Endpoint ---
@app.route("/api/auth/pin", methods=["POST"])
def verify_pin():
    data = request.json or {}
    pin = data.get("pin", "")
    if auth_service.verify_pin(pin):
        return jsonify({"success": True, "role": "ADMIN"})
    return jsonify({"success": False, "error": "Invalid PIN"}), 401

# --- 3. Inventory Endpoints ---
@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory_service.get_inventory_status())

@app.route("/api/inventory/restock/<item_id>", methods=["POST"])
def restock_item(item_id):
    qty = int(request.args.get("qty", 20))
    res = inventory_service.restock(item_id, qty)
    if res:
        return jsonify(res)
    return jsonify({"error": "Item not found"}), 404

# --- 4. QR Code & Table Tent Generation Endpoints ---
@app.route("/api/qr/table/<int:table_num>", methods=["GET"])
def get_table_qr_png(table_num):
    base_url = request.host_url.rstrip("/")
    png_bytes = qr_generator_service.generate_table_qr_png(table_num, base_url)
    return Response(png_bytes, mimetype="image/png")

@app.route("/api/qr/table/<int:table_num>/preview", methods=["GET"])
def get_table_qr_preview(table_num):
    base_url = request.host_url.rstrip("/")
    table_url = f"{base_url}/?table={table_num}"
    b64_img = qr_generator_service.generate_table_qr_base64(table_num, base_url)
    return jsonify({
        "table_number": table_num,
        "table_url": table_url,
        "qr_base64": b64_img
    })

@app.route("/api/qr/cards/pdf", methods=["GET"])
def get_table_tents_pdf():
    tables = int(request.args.get("tables", 12))
    base_url = request.host_url.rstrip("/")
    pdf_bytes = qr_generator_service.generate_pdf_table_tents(tables, base_url)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "inline; filename=Table_Tent_Cards_1_to_12.pdf"}
    )

# --- 5. QR Ordering Endpoints ---
@app.route("/api/menu", methods=["GET"])
def get_menu():
    lang = request.args.get("lang", "en")
    curr = request.args.get("currency", "GBP")
    return jsonify(qr_ordering_service.get_menu(lang, curr))

@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.json or {}
    table_num = data.get("table_number", 1)
    raw_items = data.get("items", ["item-1", "item-3"])
    items = [it if isinstance(it, str) else (it.get("item_id") or it.get("id")) for it in raw_items]
    items = [i for i in items if i]
    promo = data.get("promo_code")
    order = qr_ordering_service.submit_order(table_num, items, promo)
    return jsonify(order), 201

@app.route("/api/order/cancel/<order_id>", methods=["POST"])
def cancel_order(order_id):
    cancelled = db.cancel_order(order_id)
    if cancelled:
        return jsonify(cancelled)
    return jsonify({"error": "Order not found"}), 404

# --- 6. KDS Endpoints ---
@app.route("/api/kds/active", methods=["GET"])
def kds_active():
    st = request.args.get("station")
    orders = kds_service.get_active_kitchen_orders(station=st)
    counts = kds_service.get_station_counts()
    return jsonify({
        "station": st or "ALL",
        "orders": orders,
        "station_counts": counts
    })

@app.route("/api/kds/tv", methods=["GET"])
def kds_tv():
    return jsonify(kds_service.get_tv_display_status())

@app.route("/api/kds/advance/<order_id>", methods=["POST"])
def kds_advance(order_id):
    updated = kds_service.advance_order_status(order_id)
    if updated:
        return jsonify(updated)
    return jsonify({"error": "Order not found"}), 404

# --- 7. Promo Code Endpoints ---
@app.route("/api/promos", methods=["GET"])
def get_promos():
    return jsonify(db.promos)

# --- 8. Review Endpoints ---
@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    return jsonify({
        "average_rating": review_service.get_average_rating(),
        "reviews": review_service.get_all_reviews()
    })

@app.route("/api/reviews", methods=["POST"])
def submit_review():
    data = request.json or {}
    table_num = data.get("table_number", 1)
    rating = data.get("rating", 5)
    comment = data.get("comment", "Great service!")
    rev = review_service.submit_review(table_num, rating, comment)
    return jsonify(rev), 201

# --- 9. Finance, Invoicing & Thermal Receipt Endpoints ---
@app.route("/api/invoice/<order_id>", methods=["GET"])
def get_invoice(order_id):
    curr = request.args.get("currency", "GBP")
    invoice = finance_service.generate_invoice(order_id, curr)
    if invoice:
        return jsonify(invoice)
    return jsonify({"error": "Order not found"}), 404

@app.route("/api/invoice/<order_id>/pdf", methods=["GET"])
def get_invoice_pdf(order_id):
    curr = request.args.get("currency", "GBP")
    pdf_bytes = finance_service.generate_pdf_invoice(order_id, curr)
    if pdf_bytes:
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Invoice_{order_id}_{curr}.pdf"}
        )
    return jsonify({"error": "Order not found"}), 404

@app.route("/api/receipt/<order_id>/txt", methods=["GET"])
def get_thermal_receipt_txt(order_id):
    width = int(request.args.get("width", 32))
    receipt_txt = thermal_printer_service.format_receipt_text(order_id, width)
    if receipt_txt:
        return Response(receipt_txt, mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "Order not found"}), 404

@app.route("/api/receipt/<order_id>/escpos", methods=["GET"])
def get_thermal_receipt_escpos(order_id):
    width = int(request.args.get("width", 32))
    escpos_bytes = thermal_printer_service.generate_escpos_bytes(order_id, width)
    if escpos_bytes:
        return Response(
            escpos_bytes,
            mimetype="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=Receipt_{order_id}.bin"}
        )
    return jsonify({"error": "Order not found"}), 404

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    curr = request.args.get("currency", "GBP")
    return jsonify(finance_service.calculate_analytics(currency=curr))

@app.route("/docs/strategy")
def strategy_doc():
    doc_path = os.path.join(os.path.dirname(__file__), "..", "docs", "UK_MARKET_STRATEGY.md")
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
    return f"<pre style='white-space: pre-wrap; font-family: monospace; padding: 20px;'>{content}</pre>"

# --- 10. Bill Splitting & Group Payment Endpoints ---
@app.route("/api/orders/<order_id>/split/even", methods=["POST"])
def split_order_evenly(order_id):
    data = request.json or {}
    num_guests = int(data.get("num_guests", 2))
    include_sc = bool(data.get("include_service_charge", True))
    try:
        res = bill_splitting_service.split_evenly(order_id, num_guests, include_sc)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/orders/<order_id>/split/itemized", methods=["POST"])
def split_order_itemized(order_id):
    data = request.json or {}
    guest_assignments = data.get("guest_assignments", [])
    include_sc = bool(data.get("include_service_charge", True))
    try:
        res = bill_splitting_service.split_itemized(order_id, guest_assignments, include_sc)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/orders/<order_id>/pay-share", methods=["POST"])
def pay_order_split_share(order_id):
    data = request.json or {}
    split_target = data.get("split_id_or_index", 1)
    payment_method = data.get("payment_method", "CARD")
    try:
        res = bill_splitting_service.pay_split_share(order_id, split_target, payment_method)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/orders/<order_id>/split/status", methods=["GET"])
def get_order_split_status(order_id):
    try:
        res = bill_splitting_service.get_split_status(order_id)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/orders/<order_id>/split/sub-receipt/<split_target>", methods=["GET"])
def get_order_sub_receipt(order_id, split_target):
    width = int(request.args.get("width", 32))
    try:
        sub_receipt_txt = bill_splitting_service.generate_sub_receipt(order_id, split_target, width)
        return Response(sub_receipt_txt, mimetype="text/plain; charset=utf-8")
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

# --- 11. Automated Purchase Order Endpoints ---
@app.route("/api/inventory/low-stock", methods=["GET"])
def get_low_stock_inventory():
    threshold = int(request.args.get("threshold", 10))
    items = purchase_order_service.get_low_stock_items(threshold)
    return jsonify({"threshold": threshold, "low_stock_count": len(items), "items": items})

@app.route("/api/inventory/purchase-orders", methods=["GET"])
def get_purchase_orders():
    threshold = int(request.args.get("threshold", 10))
    reorder_qty = int(request.args.get("reorder_qty", 50))
    pos = purchase_order_service.generate_purchase_orders(threshold, reorder_qty)
    return jsonify({"purchase_orders": pos})

@app.route("/api/inventory/purchase-orders/<supplier_category>/pdf", methods=["GET"])
def download_po_pdf(supplier_category):
    threshold = int(request.args.get("threshold", 10))
    pos = purchase_order_service.generate_purchase_orders(threshold)
    target_po = next((p for p in pos if p["supplier_category"].upper() == supplier_category.upper()), None)
    if not target_po:
        return jsonify({"error": f"No active purchase order found for supplier category '{supplier_category}'"}), 404
    pdf_bytes = purchase_order_service.generate_po_pdf(target_po)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename={target_po['po_number']}_{supplier_category}.pdf"}
    )

@app.route("/api/inventory/purchase-orders/<supplier_category>/email", methods=["GET"])
def get_po_email_text(supplier_category):
    threshold = int(request.args.get("threshold", 10))
    pos = purchase_order_service.generate_purchase_orders(threshold)
    target_po = next((p for p in pos if p["supplier_category"].upper() == supplier_category.upper()), None)
    if not target_po:
        return jsonify({"error": f"No active purchase order found for supplier category '{supplier_category}'"}), 404
    email_text = purchase_order_service.generate_po_email_text(target_po)
    return Response(email_text, mimetype="text/plain; charset=utf-8")

# --- 12. Kitchen Waste & Food Loss Endpoints ---
@app.route("/api/waste/log", methods=["POST"])
def log_kitchen_waste():
    data = request.json or {}
    item_id = data.get("item_id")
    quantity = int(data.get("quantity", 1))
    reason = data.get("reason", "EXPIRED")
    staff_name = data.get("staff_name", "Head Chef")
    try:
        res = waste_tracker_service.log_waste(item_id, quantity, reason, staff_name)
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/waste/logs", methods=["GET"])
def get_kitchen_waste_logs():
    reason = request.args.get("reason")
    logs = waste_tracker_service.get_waste_logs(reason)
    return jsonify({"waste_logs": logs})

@app.route("/api/waste/analytics", methods=["GET"])
def get_kitchen_waste_analytics():
    curr = request.args.get("currency", "GBP")
    return jsonify(waste_tracker_service.get_waste_analytics(currency=curr))

@app.route("/api/waste/report/pdf", methods=["GET"])
def download_waste_pdf_report():
    curr = request.args.get("currency", "GBP")
    pdf_bytes = waste_tracker_service.generate_waste_pdf_report(currency=curr)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename=Waste_Audit_Report_{curr}.pdf"}
    )

# --- 13. Guest Feedback, NPS & Sentiment Endpoints ---
@app.route("/api/feedback/nps", methods=["GET"])
def get_feedback_nps():
    return jsonify(feedback_analytics_service.calculate_nps())

@app.route("/api/feedback/sentiment", methods=["GET"])
def get_feedback_sentiment():
    return jsonify(feedback_analytics_service.extract_sentiment())

@app.route("/api/feedback/alerts", methods=["GET"])
def get_feedback_alerts():
    return jsonify({"manager_alerts": feedback_analytics_service.get_manager_alerts()})

@app.route("/api/feedback/report/pdf", methods=["GET"])
def download_feedback_pdf_report():
    pdf_bytes = feedback_analytics_service.generate_feedback_pdf_report()
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "inline; filename=Feedback_NPS_Report.pdf"}
    )

# --- 14. Table Reservation Booking Endpoints ---
@app.route("/api/bookings", methods=["POST"])
def create_table_booking():
    data = request.json or {}
    g_name = data.get("guest_name", "Guest")
    g_phone = data.get("guest_phone", "+44 7700 900077")
    g_email = data.get("guest_email", "guest@example.com")
    party_size = int(data.get("party_size", 2))
    bkg_date = data.get("booking_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    time_slot = data.get("time_slot", "19:00")
    special_reqs = data.get("special_requests", "")
    venue_id = data.get("venue_id")

    try:
        booking = table_booking_service.create_booking(
            guest_name=g_name,
            guest_phone=g_phone,
            guest_email=g_email,
            party_size=party_size,
            booking_date=bkg_date,
            time_slot=time_slot,
            special_requests=special_reqs,
            venue_id=venue_id
        )
        return jsonify(booking), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/bookings", methods=["GET"])
def get_table_bookings():
    bkg_date = request.args.get("date")
    status = request.args.get("status")
    venue_id = request.args.get("venue_id")
    bookings = table_booking_service.get_bookings(booking_date=bkg_date, status=status, venue_id=venue_id)
    return jsonify({"bookings": bookings})

@app.route("/api/bookings/<booking_id>", methods=["GET"])
def get_table_booking_details(booking_id):
    booking = table_booking_service.get_booking_by_id(booking_id)
    if booking:
        return jsonify(booking)
    return jsonify({"error": "Booking not found"}), 404

@app.route("/api/bookings/<booking_id>/status", methods=["POST"])
def update_table_booking_status(booking_id):
    data = request.json or {}
    new_status = data.get("status", "SEATED")
    try:
        updated = table_booking_service.update_booking_status(booking_id, new_status)
        return jsonify(updated)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/bookings/<booking_id>/pdf", methods=["GET"])
def download_booking_pdf(booking_id):
    try:
        pdf_bytes = table_booking_service.generate_booking_pdf(booking_id)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Reservation_{booking_id}.pdf"}
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

# --- 15. Inter-Venue Stock Transfer Endpoints ---
@app.route("/api/transfers", methods=["POST"])
def create_store_transfer():
    data = request.json or {}
    src_v = data.get("source_venue_id", "venue-1")
    tgt_v = data.get("target_venue_id", "venue-2")
    items = data.get("items", [])
    requested_by = data.get("requested_by", "Central Kitchen Manager")
    notes = data.get("notes", "")

    try:
        transfer = store_transfers_service.request_transfer(
            source_venue_id=src_v,
            target_venue_id=tgt_v,
            items=items,
            requested_by=requested_by,
            notes=notes
        )
        return jsonify(transfer), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/transfers", methods=["GET"])
def get_store_transfers():
    v_id = request.args.get("venue_id")
    status = request.args.get("status")
    transfers = store_transfers_service.get_transfers(venue_id=v_id, status=status)
    return jsonify({"transfers": transfers})

@app.route("/api/transfers/<transfer_id>", methods=["GET"])
def get_store_transfer_details(transfer_id):
    transfer = store_transfers_service.get_transfer_by_id(transfer_id)
    if transfer:
        return jsonify(transfer)
    return jsonify({"error": "Transfer not found"}), 404

@app.route("/api/transfers/<transfer_id>/status", methods=["POST"])
def update_store_transfer_status(transfer_id):
    data = request.json or {}
    new_status = data.get("status", "APPROVED")
    try:
        updated = store_transfers_service.update_transfer_status(transfer_id, new_status)
        return jsonify(updated)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/transfers/<transfer_id>/pdf", methods=["GET"])
def download_transfer_manifest_pdf(transfer_id):
    try:
        pdf_bytes = store_transfers_service.generate_transfer_manifest_pdf(transfer_id)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Waybill_Manifest_{transfer_id}.pdf"}
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

# --- 16. Multi-Tax Compliance & HMRC MTD VAT Endpoints ---
@app.route("/api/tax/breakdown/<order_id>", methods=["GET"])
def get_tax_breakdown(order_id):
    try:
        breakdown = tax_compliance_service.calculate_tax_breakdown(order_id)
        return jsonify(breakdown)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/tax/vat-ledger", methods=["GET"])
def get_vat_ledger():
    curr = request.args.get("currency", "GBP")
    ledger = tax_compliance_service.generate_vat_ledger(currency=curr)
    return jsonify(ledger)

@app.route("/api/tax/report/pdf", methods=["GET"])
def download_vat_report_pdf():
    curr = request.args.get("currency", "GBP")
    pdf_bytes = tax_compliance_service.generate_vat_report_pdf(currency=curr)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename=HMRC_VAT_Report_{curr}.pdf"}
    )

# --- 17. Delivery Aggregator & Enterprise POS Integration Endpoints ---
@app.route("/api/integrations/webhook/<platform>", methods=["POST"])
def receive_delivery_webhook(platform):
    data = request.json or {}
    ext_ref = data.get("external_order_ref", f"ORD-EXT-{platform[:3]}-1001")
    c_name = data.get("customer_name", "Delivery Customer")
    items = data.get("items", [{"item_id": "item-1"}, {"item_id": "item-3"}])
    addr = data.get("delivery_address", "12 Floral St, London")
    tbl_num = int(data.get("table_number", 99))

    try:
        res = integrations_service.process_inbound_webhook(
            platform=platform,
            external_order_ref=ext_ref,
            customer_name=c_name,
            items=items,
            delivery_address=addr,
            table_number=tbl_num
        )
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/integrations/sync-menu/<platform>", methods=["POST"])
def sync_menu_to_platform(platform):
    try:
        res = integrations_service.sync_menu_to_aggregator(platform)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/integrations/channels", methods=["GET"])
def get_integration_channels_status():
    channels = integrations_service.get_integration_channels()
    return jsonify({"channels": channels})

# --- 18. AI Menu Analytics & Demand Forecasting Endpoints ---
@app.route("/api/forecasting/prep-demand", methods=["GET"])
def get_ai_prep_demand_forecast():
    target_day = request.args.get("day")
    day_idx = int(target_day) if target_day and target_day.isdigit() else None
    forecasts = ai_forecasting_service.predict_prep_demand(target_day_of_week=day_idx)
    return jsonify({"prep_demand_forecasts": forecasts})

@app.route("/api/forecasting/menu-matrix", methods=["GET"])
def get_ai_menu_engineering_matrix():
    return jsonify(ai_forecasting_service.get_menu_engineering_matrix())

@app.route("/api/forecasting/report/pdf", methods=["GET"])
def download_ai_forecasting_pdf_report():
    curr = request.args.get("currency", "GBP")
    pdf_bytes = ai_forecasting_service.generate_forecasting_pdf_report(currency=curr)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename=AI_Demand_Forecast_Report_{curr}.pdf"}
    )

# --- 19. White-Label Brand & Theme Customizer Endpoints ---
@app.route("/api/brand/config", methods=["GET"])
def get_brand_config():
    return jsonify(brand_customizer_service.get_config())

@app.route("/api/brand/config", methods=["POST"])
def update_brand_config():
    data = request.json or {}
    updated = brand_customizer_service.update_config(data)
    return jsonify(updated)

# --- 20. Online Table Payments & Tip Selector Endpoints ---
@app.route("/api/payments/methods", methods=["GET"])
def get_payment_methods():
    return jsonify(payments_service.get_payment_methods())

@app.route("/api/payments/checkout", methods=["POST"])
def process_payment_checkout():
    data = request.json or {}
    order_id = data.get("order_id")
    method = data.get("payment_method", "CARD_STRIPE")
    tip_pct = float(data.get("tip_percentage", 12.5))
    custom_tip = float(data.get("custom_tip")) if data.get("custom_tip") is not None else None
    curr = data.get("currency", "GBP")

    try:
        res = payments_service.process_checkout(
            order_id=order_id,
            payment_method=method,
            tip_percentage=tip_pct,
            custom_tip_amount=custom_tip,
            currency=curr
        )
        return jsonify(res), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# --- 21. PWA & Service Worker Endpoints ---
@app.route("/manifest.json", methods=["GET"])
def pwa_manifest():
    manifest = {
        "name": "The Waiter — Digital Hospitality Platform",
        "short_name": "The Waiter",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0f172a",
        "orientation": "any",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/3448/3448609.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "https://cdn-icons-png.flaticon.com/512/3448/3448609.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return jsonify(manifest)

@app.route("/sw.js", methods=["GET"])
def pwa_service_worker():
    sw_code = """
const CACHE_NAME = 'waiter-pwa-cache-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS_TO_CACHE))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.map(key => {
                if (key !== CACHE_NAME) return caches.delete(key);
            })
        ))
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;
    event.respondWith(
        fetch(event.request)
            .then(networkResponse => {
                if (networkResponse && networkResponse.status === 200) {
                    const resClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, resClone));
                }
                return networkResponse;
            })
            .catch(() => caches.match(event.request))
    );
});
"""
    return Response(sw_code, mimetype="application/javascript")



# --- 22. AI Sommelier & Dish Pairing Companion Endpoint ---
@app.route("/api/ai/sommelier", methods=["POST"])
def ai_sommelier_assistant():
    data = request.json or {}
    prompt = (data.get("prompt") or "").strip().lower()

    recommendations = []
    response_text = ""

    if "wine" in prompt or "fish" in prompt or "cod" in prompt:
        response_text = "For Fish & Chips, I recommend pairing it with a crisp Sauvignon Blanc or our Craft IPA Pint! The citrus notes cut through the golden batter perfectly."
        recommendations = [
            {"item_id": "item-1", "name": "Fish & Chips", "price": 14.50, "category": "Mains"},
            {"item_id": "item-3", "name": "Craft IPA Pint", "price": 6.20, "category": "Drinks"}
        ]
    elif "burger" in prompt or "wagyu" in prompt or "beer" in prompt:
        response_text = "For our Gourmet Wagyu Beef Burger, a full-bodied Malbec or an artisanal Craft IPA Pint enhances the rich, savory umami flavor!"
        recommendations = [
            {"item_id": "item-2", "name": "Wagyu Beef Burger", "price": 16.80, "category": "Mains"},
            {"item_id": "item-3", "name": "Craft IPA Pint", "price": 6.20, "category": "Drinks"}
        ]
    elif "gluten" in prompt or "vegan" in prompt or "diet" in prompt:
        response_text = "We have excellent Gluten-Free and Vegan options! Try our Fresh Mediterranean Garden Salad paired with Sparkling Mineral Water."
        recommendations = [
            {"item_id": "item-4", "name": "Mediterranean Garden Salad", "price": 9.50, "category": "Starters"}
        ]
    else:
        response_text = "Welcome to our AI Sommelier! I can recommend perfect wine & beverage pairings, dietary options, or top chef specials. Try asking 'What wine pairs with Fish & Chips?'"
        recommendations = [
            {"item_id": "item-1", "name": "Fish & Chips", "price": 14.50, "category": "Mains"},
            {"item_id": "item-3", "name": "Craft IPA Pint", "price": 6.20, "category": "Drinks"}
        ]

    return jsonify({
        "response_text": response_text,
        "recommendations": recommendations
    })



# --- 23. AI Customer Review Auto-Responder Endpoint ---
@app.route("/api/reviews/auto-respond", methods=["POST"])
def ai_review_auto_responder():
    data = request.json or {}
    rating = int(data.get("rating", 5))
    comment = (data.get("comment") or "").strip()
    table_num = data.get("table_number", 1)

    if rating >= 4:
        response_draft = f"Thank you so much for the fantastic {rating}-star review! We are delighted that you enjoyed your visit to Table #{table_num}. Our team looks forward to welcoming you back to Covent Garden Flagship soon!"
    elif rating == 3:
        response_draft = f"Thank you for sharing your feedback regarding Table #{table_num}. We appreciate your honest notes on '{comment or 'service'}' and are using your insights to deliver a 5-star experience next time!"
    else:
        response_draft = f"Thank you for reaching out regarding Table #{table_num}. We sincerely apologize that your visit fell short of your expectations. Please contact our General Manager directly at manager@waiter.com so we can make this right!"

    return jsonify({
        "success": True,
        "rating": rating,
        "response_draft": response_draft
    })



# --- 24. Executive Peak-Hour Sales Heatmap & Table Turnover Analytics Endpoint ---
@app.route("/api/analytics/heatmap", methods=["GET"])
def get_executive_sales_heatmap():
    curr = request.args.get("currency", "GBP").upper()
    sym = Config.CURRENCY_SYMBOLS.get(curr, "£")
    rate = Config.EXCHANGE_RATES.get(curr, 1.0)

    # Calculate live order supplement for current hour
    live_orders_rev = sum(o["total"] for o in db.orders.values() if o["status"] != "Cancelled")
    live_orders_cnt = len([o for o in db.orders.values() if o["status"] != "Cancelled"])

    baseline_hours = [
        {"hour": "12:00 - 13:00", "orders_count": 14, "base_gbp": 310.50, "intensity": "MODERATE", "recommended_staff": 5},
        {"hour": "13:00 - 14:00", "orders_count": 22, "base_gbp": 495.00, "intensity": "HIGH", "recommended_staff": 7},
        {"hour": "15:00 - 17:00", "orders_count": 8,  "base_gbp": 165.00, "intensity": "LOW", "recommended_staff": 4},
        {"hour": "18:00 - 19:00", "orders_count": 25, "base_gbp": 620.00, "intensity": "HIGH", "recommended_staff": 8},
        {"hour": "19:00 - 20:00", "orders_count": 34 + live_orders_cnt, "base_gbp": 890.00 + live_orders_rev, "intensity": "PEAK_RUSH", "recommended_staff": 10},
        {"hour": "20:00 - 21:00", "orders_count": 31, "base_gbp": 815.00, "intensity": "PEAK_RUSH", "recommended_staff": 10},
        {"hour": "21:00 - 22:00", "orders_count": 18, "base_gbp": 440.00, "intensity": "MODERATE", "recommended_staff": 6},
    ]

    hourly_heatmap = []
    for h in baseline_hours:
        hourly_heatmap.append({
            "hour": h["hour"],
            "orders_count": h["orders_count"],
            "revenue": round(h["base_gbp"] * rate, 2),
            "intensity": h["intensity"],
            "recommended_staff": h["recommended_staff"]
        })

    zone_turnover = [
        {"zone": "Main Dining Room", "tables_count": 4, "avg_turn_mins": 48, "target_turn_mins": 55},
        {"zone": "VIP Booth",        "tables_count": 2, "avg_turn_mins": 64, "target_turn_mins": 60},
        {"zone": "Patio & Terrace",  "tables_count": 3, "avg_turn_mins": 42, "target_turn_mins": 50},
        {"zone": "Bar Lounge",       "tables_count": 2, "avg_turn_mins": 32, "target_turn_mins": 40},
    ]

    return jsonify({
        "currency": curr,
        "currency_symbol": sym,
        "peak_window": "19:00 - 21:00",
        "avg_table_turn_mins": 55,
        "hourly_heatmap": hourly_heatmap,
        "zone_turnover": zone_turnover
    })


# --- 25. Digital Kitchen Recipe & Natasha's Law Allergen Matrix Endpoint ---
@app.route("/api/kds/recipes", methods=["GET"])
def get_kds_chef_recipes():
    recipes = [
        {
            "item_id": "item-1",
            "dish_name": "Fish & Chips (Brixham Cod)",
            "station": "FRYER",
            "prep_mins": 12,
            "cooking_temp": "185°C Deep Fryer (6 mins) • Core Temp ≥ 75°C",
            "ingredients": [
                "220g Fresh Brixham Atlantic Cod Fillet (skinless, pin-boned)",
                "150ml Crisp Craft IPA Beer Batter (chilled to 4°C)",
                "200g Triple-Cooked Maris Piper Chips",
                "60g Crushed Minty Marrowfat Mushy Peas",
                "45ml House Caper & Dill Tartar Sauce"
            ],
            "plating_guide": "Line cast-iron basket with branded greaseproof parchment. Stack triple-cooked chips on left, lay golden cod fillet diagonally across, place tartar ramekin & charred lemon wedge on side.",
            "allergens": ["fish", "gluten", "eggs"],
            "cross_contamination_note": "MANDATORY: Cook in Dedicated Seafood Fryer #1 only. Use blue-handle allergen tongs."
        },
        {
            "item_id": "item-2",
            "dish_name": "Gourmet Wagyu Beef Burger",
            "station": "GRILL",
            "prep_mins": 10,
            "cooking_temp": "230°C Flat-Top Grill (4 mins/side) • Core Temp ≥ 75°C",
            "ingredients": [
                "200g British Wagyu Chuck & Brisket Patty",
                "1x Glazed Artisan Brioche Bun (toasted on clarified butter)",
                "40g Aged Somerset Cheddar Slice",
                "30g Caramelized Red Onion Marmalade & House Truffle Mayo"
            ],
            "plating_guide": "Skewer burger through center with branded bamboo pick. Serve on warmed slate board with house pickles.",
            "allergens": ["gluten", "dairy", "eggs"],
            "cross_contamination_note": "Gluten-Free bun available on request — prepare on sanitized purple allergen board."
        },
        {
            "item_id": "item-3",
            "dish_name": "Craft IPA Pint (Camden Pale)",
            "station": "BAR",
            "prep_mins": 2,
            "cooking_temp": "Cellar Line Chilled at 4.5°C • 45° Pour Angle",
            "ingredients": [
                "568ml (1 Imperial Pint) Fresh Draft Craft IPA",
                "15mm Tight Micro-Foam Crown"
            ],
            "plating_guide": "Pour into nucleated branded tulip pint glass. Wipe base dry and serve on branded coaster.",
            "allergens": ["gluten"],
            "cross_contamination_note": "Contains malted barley gluten. Keep nozzle clear of glass rim."
        },
        {
            "item_id": "item-4",
            "dish_name": "Truffle & Parmesan Fries",
            "station": "LARDER",
            "prep_mins": 3,
            "cooking_temp": "190°C Crisp Flash Fry (3 mins) • Toss Warm",
            "ingredients": [
                "180g Skin-On Julienne Fries",
                "15ml White Alba Truffle Infused Olive Oil",
                "25g Freshly Grated 24-Month Parmigiano-Reggiano",
                "5g Finely Chopped Flat-Leaf Parsley & Cornish Sea Salt"
            ],
            "plating_guide": "Toss immediately in stainless bowl while hot, pile high in warmed copper dish, finish with extra parmesan snow.",
            "allergens": ["dairy"],
            "cross_contamination_note": "Vegan option available by omitting Parmesan — use vegan fryer basket."
        },
        {
            "item_id": "item-5",
            "dish_name": "Sticky Toffee Pudding",
            "station": "LARDER",
            "prep_mins": 4,
            "cooking_temp": "175°C Steam-Convection Oven Regen (4 mins) • Sauce at 65°C",
            "ingredients": [
                "160g Medjool Date & Muscovado Sponge",
                "75ml Warm Butterscotch Toffee Sauce",
                "1 Scoop (60g) Cornish Clotted Cream Vanilla Bean Ice Cream"
            ],
            "plating_guide": "Place warm sponge in center of deep ceramic bowl, pour rich butterscotch river around base, top with quenelle of vanilla bean ice cream & mint sprig.",
            "allergens": ["gluten", "dairy", "eggs"],
            "cross_contamination_note": "Verify nut-free garnish area before plating dessert."
        }
    ]
    return jsonify({"recipes": recipes, "count": len(recipes)})




# --- 26. Smart Table Service Call Bell & Staff Dispatch Endpoints ---
SERVICE_CALLS_LOG = []

@app.route("/api/service-calls", methods=["GET"])
def get_active_service_calls():
    active = [c for c in SERVICE_CALLS_LOG if c["status"] == "PENDING"]
    return jsonify({"active_calls": active, "count": len(active)})

@app.route("/api/service-calls", methods=["POST"])
def create_service_call():
    data = request.json or {}
    table_num = int(data.get("table_number", 1))
    req_type = data.get("request_type", "SERVER")
    label = data.get("label", "🙋 Call Server to Table")
    call_obj = {
        "id": f"CALL-{100 + len(SERVICE_CALLS_LOG) + 1}",
        "table_number": table_num,
        "request_type": req_type,
        "label": label,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    SERVICE_CALLS_LOG.append(call_obj)
    return jsonify(call_obj), 201

@app.route("/api/service-calls/<call_id>/resolve", methods=["POST"])
def resolve_service_call(call_id):
    for c in SERVICE_CALLS_LOG:
        if c["id"] == call_id:
            c["status"] = "RESOLVED"
            return jsonify(c)
    return jsonify({"error": "Service call not found"}), 404


# --- 27. Dynamic Happy Hour & Promo Campaign Endpoints ---
@app.route("/api/promos", methods=["POST"])
def create_or_update_promo():
    data = request.json or {}
    code = (data.get("code") or "").strip().upper()
    discount_pct = float(data.get("discount_pct", 10))
    if not code or discount_pct <= 0 or discount_pct > 95:
        return jsonify({"error": "Invalid promo code or discount percentage"}), 400
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO promos (code, discount_pct, max_uses, current_uses, active) VALUES (?, ?, 500, 0, 1)",
            (code, discount_pct)
        )
        conn.commit()
    return jsonify({
        "success": True,
        "code": code,
        "discount_pct": discount_pct,
        "discount_rate": round(discount_pct / 100.0, 2),
        "promos": db.promos
    }), 201

@app.route("/api/promos/<code>", methods=["DELETE"])
def delete_promo_code(code):
    code_up = code.strip().upper()
    if code_up in db.promos:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM promos WHERE code = ?", (code_up,))
            conn.commit()
        return jsonify({"success": True, "deleted": code_up, "promos": db.promos})
    return jsonify({"error": "Promo code not found"}), 404




# --- 28. Business Blueprint ROI & UK Consultation Booking Endpoints (Pages 8, 10, 11) ---
CONSULTATION_LEADS = []

@app.route("/api/blueprint/consultation", methods=["POST"])
def book_blueprint_consultation():
    data = request.json or {}
    venue_name = (data.get("venue_name") or "UK Hospitality Venue").strip()
    contact = (data.get("contact") or "manager@venue.co.uk").strip()
    lead = {
        "id": f"TRIAL-{100 + len(CONSULTATION_LEADS) + 1}",
        "venue_name": venue_name,
        "contact": contact,
        "trial_days": 7,
        "setup_minutes": 3,
        "uk_team_phone": "+44 7594 560831",
        "uk_team_email": "nidaazzielmehdi@gmail.com",
        "website": "waiter.com",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    CONSULTATION_LEADS.append(lead)
    return jsonify({
        "success": True,
        "lead": lead,
        "message": f"7-Day Free Trial & UK Consultation booked for '{venue_name}'! Our UK team (+44 7594 560831 / nidaazzielmehdi@gmail.com) will reach out to {contact}."
    }), 201




# --- 29. UK Statutory Compliance & EHO Inspection Endpoints ---
@app.route("/api/uk-compliance/natashas-law/<item_id>", methods=["GET"])
def get_natashas_law_item_label(item_id):
    return jsonify(uk_compliance_service.build_dish_allergen_profile(item_id))

@app.route("/api/uk-compliance/natashas-law/build", methods=["POST"])
def build_custom_natashas_law_label():
    data = request.json or {}
    item_id = data.get("item_id", "custom-deli")
    ingredients = data.get("ingredients", ["Wheat Flour", "Butter (Milk)", "Free-Range Eggs"])
    return jsonify(uk_compliance_service.build_dish_allergen_profile(item_id, custom_ingredients=ingredients))

@app.route("/api/uk-compliance/tips-act-2024", methods=["GET"])
def get_tips_act_2024_status():
    return jsonify(uk_compliance_service.get_tips_act_2024_compliance())

@app.route("/api/uk-compliance/tips-act-2024/payout", methods=["POST"])
def record_tips_act_2024_payout():
    data = request.json or {}
    entry = uk_compliance_service.record_staff_tip_payout(
        staff_name=data.get("staff_name", "Floor Server"),
        role=data.get("role", "FOH Waiter"),
        hours_worked=float(data.get("hours_worked", 38.0)),
        amount_gbp=float(data.get("amount_gbp", 150.0))
    )
    return jsonify(entry), 201

@app.route("/api/uk-compliance/challenge25/logs", methods=["GET"])
def get_challenge25_logs():
    return jsonify({
        "logs": uk_compliance_service.challenge25_logs,
        "count": len(uk_compliance_service.challenge25_logs)
    })

@app.route("/api/uk-compliance/challenge25/verify", methods=["POST"])
def verify_challenge25_age_check():
    data = request.json or {}
    rec = uk_compliance_service.verify_challenge25_id(
        table_number=int(data.get("table_number", 1)),
        order_id=data.get("order_id", "ORD-0001"),
        decision=data.get("decision", "APPROVED"),
        id_type=data.get("id_type", "UK Photocard Driving Licence"),
        verified_by_staff=data.get("verified_by_staff", "Duty Manager (Personal Licence Holder)")
    )
    return jsonify(rec), 201

@app.route("/api/uk-compliance/food-safety", methods=["GET"])
def get_uk_food_safety_status():
    return jsonify(uk_compliance_service.get_food_safety_status())

@app.route("/api/uk-compliance/food-safety/temp", methods=["POST"])
def log_uk_fridge_temperature():
    data = request.json or {}
    entry = uk_compliance_service.log_fridge_temperature(
        unit_name=data.get("unit_name", "Walk-In Cold Room #1"),
        unit_type=data.get("unit_type", "CHILLER"),
        recorded_temp_c=float(data.get("recorded_temp_c", 3.2)),
        checked_by=data.get("checked_by", "Head Chef")
    )
    return jsonify(entry), 201

@app.route("/api/uk-compliance/food-safety/haccp-toggle", methods=["POST"])
def toggle_uk_haccp_task():
    data = request.json or {}
    updated = uk_compliance_service.toggle_haccp_task(data.get("task_id", "HACCP-01"))
    if updated:
        return jsonify(updated)
    return jsonify({"error": "Task not found"}), 404

@app.route("/api/uk-compliance/vat-mode", methods=["POST"])
def calculate_uk_vat_709_mode():
    data = request.json or {}
    items = data.get("items", ["item-1", "item-3", "item-4"])
    mode = data.get("dining_mode", "EAT_IN")
    return jsonify(uk_compliance_service.calculate_order_mode_vat(items, dining_mode=mode))

@app.route("/api/uk-compliance/gdpr-security", methods=["GET"])
def get_uk_gdpr_security_posture():
    return jsonify(uk_compliance_service.get_uk_gdpr_and_security_posture())

@app.route("/api/uk-compliance/eho-report/pdf", methods=["GET"])
def download_uk_eho_compliance_pdf():
    pdf_bytes = uk_compliance_service.generate_eho_compliance_pdf()
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "inline; filename=UK_EHO_Compliance_Audit_Pack.pdf"}
    )




# --- 30. Money & Margins Endpoints (Percentage Split, Xero/QuickBooks/Sage/FreeAgent, Recipe GP%, Booker/Bidfood/Brakes OCR, Rota Labour & Payroll) ---
@app.route("/api/orders/<order_id>/split/percentage", methods=["POST"])
def split_order_by_percentage(order_id):
    data = request.json or {}
    percentages = data.get("percentages", [50, 50])
    include_sc = bool(data.get("include_service_charge", True))
    try:
        res = money_margins_service.split_bill_by_percentage(order_id, percentages, include_sc)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/margins/accounting/status", methods=["GET"])
def get_uk_accounting_status():
    return jsonify(money_margins_service.get_accounting_status())

@app.route("/api/margins/accounting/sync/<provider>", methods=["POST"])
def sync_uk_accounting_provider(provider):
    try:
        res = money_margins_service.sync_to_accounting_provider(provider)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/margins/recipe-gp", methods=["GET"])
def get_live_recipe_costing_gp():
    return jsonify(money_margins_service.get_recipe_costing_and_gp_report())

@app.route("/api/margins/suppliers", methods=["GET"])
def get_uk_wholesalers_and_scanned_invoices():
    return jsonify(money_margins_service.get_wholesalers_and_invoices())

@app.route("/api/margins/suppliers/order/<supplier_code>", methods=["POST"])
def submit_uk_wholesaler_order(supplier_code):
    try:
        res = money_margins_service.submit_wholesaler_order(supplier_code)
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/margins/suppliers/scan-invoice", methods=["POST"])
def scan_uk_supplier_invoice():
    data = request.json or {}
    sup = data.get("supplier_code", "BRAKES")
    inv_ref = data.get("invoice_ref", "BRK-INV-9901")
    cod_cost = float(data.get("cod_unit_cost_gbp", 2.75))
    res = money_margins_service.scan_and_ingest_supplier_invoice(sup, inv_ref, cod_cost)
    return jsonify(res), 201

@app.route("/api/margins/labour-payroll", methods=["GET"])
def get_rota_labour_and_holiday_accrual():
    return jsonify(money_margins_service.get_labour_vs_sales_and_payroll())

@app.route("/api/margins/payroll/export/csv", methods=["GET"])
def export_uk_payroll_holiday_csv():
    csv_data = money_margins_service.export_uk_payroll_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=UK_Payroll_Holiday_Accrual_Export.csv"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
