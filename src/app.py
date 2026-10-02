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
                    <span id="pwaNetworkBadge" class="badge bg-success rounded-pill px-3 py-2 ms-2"><i class="fa-solid fa-wifi me-1"></i> Online</span>
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
        <div class="p-3 bg-white rounded-3 border shadow-sm mb-3 d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-2">
                <i class="fa-solid fa-heart text-danger fs-5"></i>
                <span class="fw-semibold text-dark" id="guestWelcomeMsgText">Welcome! Tap dishes below to order directly from Table #1</span>
            </div>
            <span class="badge bg-success bg-opacity-25 text-success border border-success"><i class="fa-solid fa-bolt me-1"></i> Fast Digital Service</span>
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
            <button class="btn btn-sm btn-dark w-100 fw-bold" onclick="showOnlinePaymentModal()"><i class="fa-solid fa-credit-card text-success me-1"></i> Pay Bill at Table Now</button>
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
                        <div class="col-4">
                            <div class="pay-method-card text-center selected" id="pmApplePay" onclick="selectPaymentMethod('APPLE_PAY', this)">
                                <i class="fa-brands fa-apple fs-3 text-dark mb-1"></i>
                                <span class="d-block small fw-bold">Apple Pay</span>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="pay-method-card text-center" id="pmGooglePay" onclick="selectPaymentMethod('GOOGLE_PAY', this)">
                                <i class="fa-brands fa-google-pay fs-3 text-primary mb-1"></i>
                                <span class="d-block small fw-bold">Google Pay</span>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="pay-method-card text-center" id="pmCardStripe" onclick="selectPaymentMethod('CARD_STRIPE', this)">
                                <i class="fa-solid fa-credit-card fs-3 text-success mb-1"></i>
                                <span class="d-block small fw-bold">Card Stripe</span>
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
                <button class="nav-link active" id="kds-tab" data-bs-toggle="tab" data-bs-target="#kds" type="button" onclick="loadKDS()"><i class="fa-solid fa-fire-burner me-1"></i> Kitchen KDS</button>
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
                <button class="nav-link" id="reports-tab" data-bs-toggle="tab" data-bs-target="#reports" type="button"><i class="fa-solid fa-file-csv me-1"></i> Reports Exporter</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" type="button"><i class="fa-solid fa-file-contract me-1"></i> Strategy</button>
            </li>
        </ul>

        <div class="tab-content" id="staffTabContent">

            <!-- TAB 1: KDS with Station Routing & Sound Generator -->
            <div class="tab-pane fade show active" id="kds" role="tabpanel">
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
                    
                    <button class="btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold ms-auto" id="chimeToggleBtn" onclick="toggleOrderChime()"><i class="fa-solid fa-volume-high me-1"></i> Audio Chime On</button>
                </div>

                <div id="kdsContainer" class="row g-3">
                    <!-- Loaded dynamically -->
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

            <!-- TAB 11: Reports Hub -->
            <div class="tab-pane fade" id="reports" role="tabpanel">
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h4 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-file-csv text-success me-2"></i>Download CSV Business Reports</h4>
                    <div class="row g-3 mt-2">
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-receipt fs-1 text-primary mb-2"></i>
                                <h6 class="fw-bold">Orders CSV</h6>
                                <a href="/api/export/orders/csv" target="_blank" class="btn btn-primary btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-boxes-stacked fs-1 text-success mb-2"></i>
                                <h6 class="fw-bold">Inventory CSV</h6>
                                <a href="/api/export/inventory/csv" target="_blank" class="btn btn-success btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-comments fs-1 text-warning mb-2"></i>
                                <h6 class="fw-bold">Reviews CSV</h6>
                                <a href="/api/export/reviews/csv" target="_blank" class="btn btn-warning text-dark btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-file-pdf fs-1 text-danger mb-2"></i>
                                <h6 class="fw-bold">Daily Z-Report PDF</h6>
                                <a href="/api/finance/z-report/pdf" target="_blank" class="btn btn-danger btn-sm mt-auto"><i class="fa-solid fa-file-pdf me-1"></i> Download</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 12: Strategy Blueprint -->
            <div class="tab-pane fade" id="strategy" role="tabpanel">
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h3 class="fw-bold mb-3 text-dark">UK Market Strategy Blueprint</h3>
                    <iframe src="/docs/strategy" style="width: 100%; height: 600px; border: 1px solid #cbd5e1; border-radius: 8px;"></iframe>
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
                            <button class="nav-link fw-bold" id="tab-itemized-tab" data-bs-toggle="tab" data-bs-target="#tab-itemized" type="button" role="tab" onclick="loadItemizedSplitOptions()"><i class="fa-solid fa-list-check me-1"></i> Itemized Split</button>
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

        function callWaiter() {
            const banner = document.getElementById('waiterAlertBanner');
            banner.classList.remove('d-none');
            setTimeout(() => banner.classList.add('d-none'), 6000);
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

            container.innerHTML = data.map(item => {
                let stockBadge = '';
                let btnDisabled = '';
                if(item.stock_status === 'OUT_OF_STOCK') {
                    stockBadge = '<span class="badge bg-danger ms-2">Out of Stock</span>';
                    btnDisabled = 'disabled';
                } else if(item.stock_status === 'LOW_STOCK') {
                    stockBadge = `<span class="badge bg-warning text-dark ms-2">Only ${item.stock_qty} left!</span>`;
                }

                return `
                    <div class="col-md-6">
                        <div class="dish-card">
                            <div>
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h6 class="fw-bold mb-0 text-dark">${item.name_translated} ${stockBadge}</h6>
                                    <span class="dish-price">${item.price_formatted}</span>
                                </div>
                                <p class="text-muted small mb-3">${item.description_translated}</p>
                            </div>
                            <button class="btn btn-sm btn-outline-primary w-100 add-btn" ${btnDisabled} onclick="addToCart('${item.id}', '${item.name_translated}', ${item.price}, '${item.price_formatted}')">
                                <i class="fa-solid fa-plus me-1"></i> Add to Table Order
                            </button>
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
                sPrep.className = 'order-step' + (latestOrder.status === 'PREPARING' || latestOrder.status === 'READY' ? ' active' : '');
                sReady.className = 'order-step' + (latestOrder.status === 'READY' ? ' active' : '');
            } catch(e) { console.error(e); }
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
            const splitModalEl = document.getElementById('splitModal');
            const splitModal = bootstrap.Modal.getInstance(splitModalEl);
            if(splitModal) splitModal.hide();

            // Open payment modal pre-loaded with split target & amount
            showPaymentModal();
            document.getElementById('checkoutSubtotalLabel').innerText = '£' + amount.toFixed(2);
            updatePaymentTotals();
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
            const rating = parseInt(document.getElementById('selectedRating').value);
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

            alert('Thank you! Your feedback has been sent to management.');
            const modalEl = document.getElementById('reviewModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            document.getElementById('reviewComment').value = '';
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
            const promoInput = document.getElementById('cartPromoInput');
            if(promoInput) {
                promoInput.value = code;
                applyPromoCode();
            }
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
                const match = cmd.match(/\d+/);
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
