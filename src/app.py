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

app = Flask(__name__)







app.config['SECRET_KEY'] = Config.SECRET_KEY

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Waiter | UK & Global Hospitality SaaS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background-color: #f4f6f9; }
        .hero { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); color: white; padding: 35px 0; border-bottom: 4px solid #00b4db; }
        .card-custom { border-radius: 12px; border: 1px solid #e3e8ee; box-shadow: 0 4px 12px rgba(0,0,0,0.03); transition: transform 0.2s; }
        .card-custom:hover { transform: translateY(-2px); }
        .badge-status { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; padding: 5px 10px; border-radius: 12px; }
        .upsell-box { background: #fff8e1; border: 1px dashed #ffa000; border-radius: 8px; padding: 12px; }
        .kds-card { border-left: 4px solid #00b4db; }
        .kds-preparing { border-left: 4px solid #ff9800; }
        .kds-ready { border-left: 4px solid #4caf50; }
        .star-rating { cursor: pointer; color: #ffc107; font-size: 1.5rem; }
        .star-rating .far { color: #ccc; }
        .receipt-preview { font-family: 'Courier New', Courier, monospace; background: #fff; border: 1px solid #ddd; padding: 15px; font-size: 0.85rem; border-radius: 6px; }
        .pin-input { letter-spacing: 12px; font-size: 2rem; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <div class="hero text-center">
        <div class="container">
            <h1 class="fw-bold"><i class="fa-solid fa-utensils me-2"></i>The Waiter</h1>
            <p class="lead mb-2">UK & Global Digital Hospitality Ecosystem & "Scan to Invoice" Platform</p>
            <div class="d-flex justify-content-center flex-wrap gap-2 mt-3">
                <span class="badge bg-light text-dark"><i class="fa-solid fa-globe me-1"></i>Multi-Currency (£ / € / $)</span>
                <span class="badge bg-info text-dark"><i class="fa-solid fa-mobile-screen me-1"></i>BYOD Enterprise</span>
                <span class="badge bg-success"><i class="fa-solid fa-boxes-stacked me-1"></i>Stock Auto-Deduction</span>
                <span class="badge bg-primary"><i class="fa-solid fa-print me-1"></i>ESC/POS Thermal Print</span>
                <a href="/tv" target="_blank" class="badge bg-warning text-dark text-decoration-none"><i class="fa-solid fa-tv me-1"></i>Guest TV Display</a>
                <a href="/api/qr/cards/pdf" target="_blank" class="badge bg-danger text-decoration-none"><i class="fa-solid fa-file-pdf me-1"></i>Print Table QR Cards (PDF)</a>
                <a href="/api/finance/z-report/pdf" target="_blank" class="badge bg-dark text-warning text-decoration-none"><i class="fa-solid fa-chart-line me-1"></i>Z-Report Daily PDF</a>
                <a href="/api/waste/report/pdf" target="_blank" class="badge bg-danger text-white text-decoration-none"><i class="fa-solid fa-trash-can me-1"></i>Waste Audit PDF</a>
                <a href="/api/tax/report/pdf" target="_blank" class="badge bg-success text-white text-decoration-none"><i class="fa-solid fa-file-invoice-dollar me-1"></i>HMRC VAT PDF</a>
                <a href="/api/feedback/report/pdf" target="_blank" class="badge bg-primary text-white text-decoration-none"><i class="fa-solid fa-star me-1"></i>NPS Report PDF</a>
                <a href="/api/inventory/purchase-orders/SEAFOOD/pdf" target="_blank" class="badge bg-info text-dark text-decoration-none"><i class="fa-solid fa-truck-ramp-box me-1"></i>Supplier PO PDF</a>
                <button class="badge bg-dark text-white border-0" id="pinAuthBtn" data-bs-toggle="modal" data-bs-target="#pinModal"><i class="fa-solid fa-lock me-1"></i> Manager Mode (PIN: 1234)</button>
                <a href="/terminal" target="_blank" class="badge bg-secondary text-white text-decoration-none"><i class="fa-solid fa-desktop me-1"></i>Netoff Terminal Pro</a>
            </div>
        </div>
    </div>

    <div class="container my-4">
        <!-- Store Location / Venue Switcher Bar -->
        <div class="d-flex justify-content-between align-items-center mb-3 p-3 bg-white border rounded shadow-sm">
            <div class="d-flex align-items-center gap-2">
                <i class="fa-solid fa-store text-primary fs-4"></i>
                <div>
                    <span class="small text-muted d-block fw-bold text-uppercase">Active Store Location</span>
                    <strong id="activeVenueName" class="fs-6 text-dark">Covent Garden Flagship (UK)</strong>
                </div>
            </div>
            <div class="d-flex align-items-center gap-2">
                <label for="venueSelect" class="small fw-bold text-muted mb-0"><i class="fa-solid fa-location-dot me-1"></i>Switch Venue:</label>
                <select id="venueSelect" class="form-select form-select-sm w-auto fw-bold text-dark border-primary" onchange="switchVenue(this.value)">
                    <!-- Dynamically populated -->
                </select>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <ul class="nav nav-pills mb-4 justify-content-center" id="mainTabs" role="tablist">

            <li class="nav-item">
                <button class="nav-link active fw-bold" id="ordering-tab" data-bs-toggle="tab" data-bs-target="#ordering" type="button"><i class="fa-solid fa-qrcode me-1"></i> Scan & Order</button>
            </li>
            <li class="nav-item">
                <button class="nav-link fw-bold" id="kds-tab" data-bs-toggle="tab" data-bs-target="#kds" type="button" onclick="loadKDS()"><i class="fa-solid fa-fire-burner me-1"></i> Kitchen KDS</button>
            </li>
            <li class="nav-item">
                <button class="nav-link fw-bold" id="inventory-tab" data-bs-toggle="tab" data-bs-target="#inventory" type="button" onclick="loadInventory()"><i class="fa-solid fa-boxes-stacked me-1"></i> Inventory Stock</button>
            </li>
            <li class="nav-item">
                <button class="nav-link fw-bold" id="reviews-tab" data-bs-toggle="tab" data-bs-target="#reviews" type="button" onclick="loadReviews()"><i class="fa-solid fa-star me-1"></i> Avis Clients (Reviews)</button>
            </li>
            <li class="nav-item">
                <button class="nav-link fw-bold" id="analytics-tab" data-bs-toggle="tab" data-bs-target="#analytics" type="button" onclick="loadAnalytics()"><i class="fa-solid fa-chart-line me-1"></i> RevPASH Analytics</button>
            </li>
            <li class="nav-item">
                <button class="nav-link fw-bold" id="reports-tab" data-bs-toggle="tab" data-bs-target="#reports" type="button"><i class="fa-solid fa-file-csv me-1"></i> CSV Reports</button>
            </li>
            <li class="nav-item">
                <button class="nav-link fw-bold" id="staff-tab" data-bs-toggle="tab" data-bs-target="#staff" type="button" onclick="loadStaff()"><i class="fa-solid fa-user-clock me-1"></i> Staff Shift Clock</button>
            </li>
            <li class="nav-item">
                <button class="nav-link fw-bold" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" type="button"><i class="fa-solid fa-file-contract me-1"></i> Strategy Report</button>
            </li>

        </ul>

        <div class="tab-content" id="mainTabContent">
            <!-- TAB 1: QR Ordering -->
            <div class="tab-pane fade show active" id="ordering" role="tabpanel">
                <div class="row">
                    <div class="col-md-8">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h4 class="fw-bold mb-0">Digital Menu</h4>
                            <div class="d-flex gap-2">
                                <div class="btn-group btn-group-sm" id="langGroup">
                                    <button class="btn btn-outline-dark active" onclick="setLanguage('en', this)">EN</button>
                                    <button class="btn btn-outline-dark" onclick="setLanguage('fr', this)">FR</button>
                                    <button class="btn btn-outline-dark" onclick="setLanguage('ar', this)">AR</button>
                                </div>
                                <div class="btn-group btn-group-sm" id="currGroup">
                                    <button class="btn btn-dark active" onclick="setCurrency('GBP', this)">£ GBP</button>
                                    <button class="btn btn-outline-dark" onclick="setCurrency('EUR', this)">€ EUR</button>
                                    <button class="btn btn-outline-dark" onclick="setCurrency('USD', this)">$ USD</button>
                                </div>
                            </div>
                        </div>

                        <!-- Dietary & Allergen Filter Bar -->
                        <div class="d-flex flex-wrap align-items-center gap-2 mb-3 p-2 bg-light rounded border">
                            <span class="small fw-bold text-muted me-1"><i class="fa-solid fa-filter me-1"></i>Dietary & Allergens:</span>
                            <button class="btn btn-xs btn-outline-success active rounded-pill px-2 py-0 fw-bold" onclick="filterMenuDiet('all', this)">All</button>
                            <button class="btn btn-xs btn-outline-success rounded-pill px-2 py-0 fw-bold" onclick="filterMenuDiet('vegan', this)">🌱 Vegan</button>
                            <button class="btn btn-xs btn-outline-success rounded-pill px-2 py-0 fw-bold" onclick="filterMenuDiet('vegetarian', this)">🥬 Vegetarian</button>
                            <button class="btn btn-xs btn-outline-success rounded-pill px-2 py-0 fw-bold" onclick="filterMenuDiet('halal', this)">🕌 Halal</button>
                            <button class="btn btn-xs btn-outline-danger rounded-pill px-2 py-0 fw-bold ms-auto" onclick="toggleExclusion('gluten', this)">🌾 Exclude Gluten</button>
                        </div>

                        <div id="menuContainer" class="row g-3">

                            <!-- Dynamically loaded -->
                        </div>
                    </div>

                    <!-- Cart Sidebar -->
                    <div class="col-md-4">
                        <div class="card card-custom p-3 bg-white">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0"><i class="fa-solid fa-cart-shopping me-2"></i>Your Order</h5>
                                <span class="badge bg-info text-dark" id="activeTableBadge">Table #1</span>
                            </div>
                            <hr class="mt-2">
                            <div id="cartItems" class="mb-3 text-muted small">Cart is empty. Select dishes from menu.</div>
                            
                            <!-- Smart Upsell Box -->
                            <div id="upsellBox" class="upsell-box mb-3 d-none">
                                <strong class="small text-dark"><i class="fa-solid fa-lightbulb text-warning me-1"></i>Recommended Add-on:</strong>
                                <div id="upsellContent" class="mt-1"></div>
                            </div>

                            <div class="mb-3">
                                <input type="text" id="promoInput" class="form-control form-control-sm" placeholder="Promo code (e.g. WELCOME10)">
                            </div>

                            <div class="d-flex justify-content-between fw-bold mb-3">
                                <span>Total:</span>
                                <span id="cartTotal">£0.00</span>
                            </div>

                            <button class="btn btn-primary w-100 fw-bold mb-2" onclick="placeOrder()"><i class="fa-solid fa-check-circle me-1"></i> Submit Order</button>
                            <button class="btn btn-outline-warning text-dark w-100 btn-sm" data-bs-toggle="modal" data-bs-target="#reviewModal"><i class="fa-solid fa-comment-dots me-1"></i> Leave Private Feedback</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: KDS -->
            <div class="tab-pane fade" id="kds" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0">Kitchen Display System (KDS) & Thermal Printing</h4>
                    <button class="btn btn-sm btn-outline-secondary" onclick="loadKDS()"><i class="fa-solid fa-rotate me-1"></i> Refresh</button>
                </div>
                <div id="kdsContainer" class="row g-3">
                    <!-- Loaded dynamically -->
                </div>
            </div>

            <!-- TAB 3: Inventory Stock -->
            <div class="tab-pane fade" id="inventory" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h4 class="fw-bold mb-0">Automated Stock & Ingredient Tracking</h4>
                        <p class="text-muted small mb-0">Real-time inventory deduction upon order placement.</p>
                    </div>
                    <button class="btn btn-sm btn-outline-secondary" onclick="loadInventory()"><i class="fa-solid fa-rotate me-1"></i> Refresh</button>
                </div>
                <div id="inventoryContainer" class="row g-3">
                    <!-- Loaded dynamically -->
                </div>
            </div>

            <!-- TAB 4: Reviews (Avis Clients) -->
            <div class="tab-pane fade" id="reviews" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h4 class="fw-bold mb-0">Private Customer Reviews ("Avis clients")</h4>
                        <p class="text-muted small mb-0">Internal feedback captured before public social reviews.</p>
                    </div>
                    <div class="text-end">
                        <span class="fs-4 fw-bold text-warning" id="avgRatingScore">0.0</span>
                        <span class="text-muted fs-6">/ 5.0</span>
                        <div id="avgRatingStars" class="small text-warning"></div>
                    </div>
                </div>
                <div id="reviewsContainer" class="row g-3">
                    <!-- Dynamically populated -->
                </div>
            </div>

            <!-- TAB 5: Analytics -->
            <div class="tab-pane fade" id="analytics" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0">RevPASH & Performance Analytics</h4>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-dark" onclick="loadAnalytics('GBP')">£ GBP</button>
                        <button class="btn btn-outline-dark" onclick="loadAnalytics('EUR')">€ EUR</button>
                        <button class="btn btn-outline-dark" onclick="loadAnalytics('USD')">$ USD</button>
                    </div>
                </div>
                <div class="row g-3 mb-4" id="analyticsStats">
                    <!-- Dynamically populated -->
                </div>
            </div>

            <!-- TAB 6: CSV Reports Exporter -->
            <div class="tab-pane fade" id="reports" role="tabpanel">
                <div class="card card-custom p-4 bg-white">
                    <h4 class="fw-bold mb-3"><i class="fa-solid fa-file-csv text-success me-2"></i>Download CSV Business Reports</h4>
                    <p class="text-muted">Export operational data for accounting software (Xero, QuickBooks, Sage) and inventory audits.</p>
                    <div class="row g-3 mt-2">
                        <div class="col-md-3">
                            <div class="card p-3 border text-center">
                                <i class="fa-solid fa-receipt fs-1 text-primary mb-2"></i>
                                <h6 class="fw-bold">Order Sales History</h6>
                                <p class="text-muted small">Full log of transactions, table #s, items, and tax amounts.</p>
                                <a href="/api/export/orders/csv" target="_blank" class="btn btn-primary btn-sm"><i class="fa-solid fa-download me-1"></i> Orders CSV</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center">
                                <i class="fa-solid fa-boxes-stacked fs-1 text-success mb-2"></i>
                                <h6 class="fw-bold">Inventory Audit</h6>
                                <p class="text-muted small">Current stock levels, dish prices, and stock status warnings.</p>
                                <a href="/api/export/inventory/csv" target="_blank" class="btn btn-success btn-sm"><i class="fa-solid fa-download me-1"></i> Inventory CSV</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center">
                                <i class="fa-solid fa-comments fs-1 text-warning mb-2"></i>
                                <h6 class="fw-bold">Private Guest Feedback</h6>
                                <p class="text-muted small">Complete customer rating scores and private review comments.</p>
                                <a href="/api/export/reviews/csv" target="_blank" class="btn btn-warning text-dark btn-sm"><i class="fa-solid fa-download me-1"></i> Reviews CSV</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center">
                                <i class="fa-solid fa-file-pdf fs-1 text-danger mb-2"></i>
                                <h6 class="fw-bold">Daily Z-Report PDF</h6>
                                <p class="text-muted small">Formal End-of-Day closing report with VAT sub-totals and sign-off.</p>
                                <a href="/api/finance/z-report/pdf" target="_blank" class="btn btn-danger btn-sm"><i class="fa-solid fa-file-pdf me-1"></i> Z-Report PDF</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 7: Staff Time Clock & Shift Tracking -->
            <div class="tab-pane fade" id="staff" role="tabpanel">
                <div class="row g-4">
                    <!-- Clock In/Out Terminal -->
                    <div class="col-md-5">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h4 class="fw-bold mb-3"><i class="fa-solid fa-clock text-primary me-2"></i>Staff Shift Clock In/Out</h4>
                            <p class="text-muted small">Enter staff PIN (Manager: <code>1234</code>, Chef: <code>5555</code>, Server: <code>7777</code> / <code>8888</code>)</p>
                            <input type="password" id="staffPinInput" class="form-control pin-input mb-3" maxlength="4" placeholder="••••">
                            <div class="row g-2">
                                <div class="col-6">
                                    <button class="btn btn-success w-100 fw-bold" onclick="staffClockIn()"><i class="fa-solid fa-right-to-bracket me-1"></i> Clock In</button>
                                </div>
                                <div class="col-6">
                                    <button class="btn btn-danger w-100 fw-bold" onclick="staffClockOut()"><i class="fa-solid fa-right-from-bracket me-1"></i> Clock Out</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Shift Log & Labor Cost Summary -->
                    <div class="col-md-7">
                        <div class="card card-custom p-4 bg-white shadow-sm mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold mb-0"><i class="fa-solid fa-user-check text-success me-2"></i>Active Staff & Labor Cost</h5>
                                <span class="badge bg-primary fs-6" id="activeStaffBadge">0 Active</span>
                            </div>
                            <div id="laborSummaryContent" class="row text-center mb-3">
                                <!-- Dynamically populated -->
                            </div>
                        </div>
                        <div class="card card-custom p-3 bg-white shadow-sm">
                            <h6 class="fw-bold mb-2">Shift History Log</h6>
                            <div id="shiftHistoryContainer" style="max-height: 250px; overflow-y: auto;">
                                <!-- Dynamically populated -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 8: Strategy Document -->
            <div class="tab-pane fade" id="strategy" role="tabpanel">

                <div class="card card-custom p-4 bg-white">
                    <h3 class="fw-bold mb-3">UK Market Strategy & Operational Blueprint</h3>
                    <iframe src="/docs/strategy" style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 8px;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- Manager PIN Authentication Modal -->
    <div class="modal fade" id="pinModal" tabindex="-1" aria-labelledby="pinModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="pinModalLabel"><i class="fa-solid fa-user-shield text-warning me-2"></i>Manager Mode</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center">
                    <p class="text-muted small">Enter 4-digit Manager PIN (Default: <code>1234</code>)</p>
                    <input type="password" id="pinInput" class="form-control pin-input mb-3" maxlength="4" placeholder="••••">
                    <button type="button" class="btn btn-warning text-dark w-100 fw-bold" onclick="authenticatePIN()"><i class="fa-solid fa-unlock me-1"></i> Unlock Admin Access</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Review Modal for Guests -->
    <div class="modal fade" id="reviewModal" tabindex="-1" aria-labelledby="reviewModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-header-title fw-bold" id="reviewModalLabel"><i class="fa-solid fa-heart text-danger me-2"></i>How was your experience?</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center">
                    <p class="text-muted small">Your feedback is kept private and goes directly to restaurant management.</p>
                    <div class="star-rating mb-3" id="modalStars">
                        <i class="fa-solid fa-star" onclick="setRating(1)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(2)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(3)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(4)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(5)"></i>
                    </div>
                    <input type="hidden" id="selectedRating" value="5">
                    <textarea id="reviewComment" class="form-control mb-3" rows="3" placeholder="Tell us about the food quality, speed of service, or staff..."></textarea>
                    <button type="button" class="btn btn-primary w-100 fw-bold" onclick="submitGuestReview()">Submit Private Review</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Receipt Thermal Preview Modal -->
    <div class="modal fade" id="receiptModal" tabindex="-1" aria-labelledby="receiptModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold small" id="receiptModalLabel"><i class="fa-solid fa-print me-1"></i> Thermal Receipt Preview</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <pre id="receiptPreviewContent" class="receipt-preview mb-3"></pre>
                    <div class="d-grid gap-2">
                        <a id="escposDownloadBtn" href="#" target="_blank" class="btn btn-sm btn-dark"><i class="fa-solid fa-download me-1"></i> Download ESC/POS Bytes</a>
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

        const urlParams = new URLSearchParams(window.location.search);
        if(urlParams.has('table')) {
            activeTable = parseInt(urlParams.get('table')) || 1;
        }

        function updateTableDisplay() {
            document.getElementById('activeTableBadge').innerText = 'Table #' + activeTable;
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
                document.getElementById('pinAuthBtn').className = 'badge bg-success border-0';
                document.getElementById('pinAuthBtn').innerHTML = '<i class="fa-solid fa-shield-halved me-1"></i> Admin Unlocked';
                const modalEl = document.getElementById('pinModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                modal.hide();
                alert('Manager Mode Unlocked! Admin controls active.');
            } else {
                alert('Invalid Manager PIN. Try 1234');
            }
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
                container.innerHTML = '<div class="text-muted text-center my-4 fs-6"><i class="fa-solid fa-filter-circle-xmark me-2 text-warning"></i>No dishes match your selected allergen and dietary filters.</div>';
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
                        <div class="card card-custom p-3 h-100 bg-white">
                            <div class="d-flex justify-content-between align-items-start">
                                <h6 class="fw-bold mb-1">${item.name_translated} ${stockBadge}</h6>
                                <span class="badge bg-primary">${item.price_formatted}</span>
                            </div>
                            <p class="text-muted small mb-2">${item.description_translated}</p>
                            <button class="btn btn-sm btn-outline-primary mt-auto" ${btnDisabled} onclick="addToCart('${item.id}', '${item.name_translated}', ${item.price}, '${item.price_formatted}')">
                                <i class="fa-solid fa-plus me-1"></i> Add to Order
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
            const container = document.getElementById('cartItems');
            const sym = currSymbols[currentCurr] || '£';
            if(currentCart.length === 0) {
                container.innerHTML = 'Cart is empty. Select dishes from menu.';
                document.getElementById('cartTotal').innerText = sym + '0.00';
                return;
            }
            let subtotal = 0;
            container.innerHTML = currentCart.map((item, idx) => {
                subtotal += item.price;
                return `<div class="d-flex justify-content-between align-items-center mb-1">
                    <span>${item.name}</span>
                    <div>
                        <span class="me-2">${item.priceFormatted || sym + item.price.toFixed(2)}</span>
                        <button class="btn btn-link btn-sm text-danger p-0" onclick="removeFromCart(${idx})">&times;</button>
                    </div>
                </div>`;
            }).join('');
            document.getElementById('cartTotal').innerText = sym + subtotal.toFixed(2);
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
                            <span class="small fw-bold">${side.name_translated} (+${side.price_formatted})</span>
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
            const promo = document.getElementById('promoInput').value.trim();
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
            currentCart = [];
            renderCart();
            document.getElementById('upsellBox').classList.add('d-none');
            loadMenu();
            
            const reviewModal = new bootstrap.Modal(document.getElementById('reviewModal'));
            reviewModal.show();
        }

        async function loadInventory() {
            const res = await fetch('/api/inventory');
            const items = await res.json();
            const container = document.getElementById('inventoryContainer');
            
            container.innerHTML = items.map(item => {
                let badgeClass = 'bg-success';
                if(item.stock_status === 'OUT_OF_STOCK') badgeClass = 'bg-danger';
                else if(item.stock_status === 'LOW_STOCK') badgeClass = 'bg-warning text-dark';

                return `
                    <div class="col-md-6 col-lg-4">
                        <div class="card card-custom p-3 bg-white">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="fw-bold mb-0">${item.name.en}</h6>
                                <span class="badge ${badgeClass}">${item.stock_status}</span>
                            </div>
                            <p class="text-muted small mb-2">Current Stock: <strong class="fs-5 text-dark">${item.stock_qty}</strong> units</p>
                            <button class="btn btn-sm btn-outline-success" onclick="restockItem('${item.id}')">
                                <i class="fa-solid fa-plus me-1"></i> Restock (+20 Units)
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function restockItem(id) {
            if(!isAdminUnlocked) {
                alert('Manager PIN required to restock inventory!');
                const modal = new bootstrap.Modal(document.getElementById('pinModal'));
                modal.show();
                return;
            }
            await fetch(`/api/inventory/restock/${id}`, { method: 'POST' });
            loadInventory();
            loadMenu();
        }

        function setRating(stars) {
            document.getElementById('selectedRating').value = stars;
            const starElements = document.querySelectorAll('#modalStars i');
            starElements.forEach((s, idx) => {
                if(idx < stars) {
                    s.className = 'fa-solid fa-star';
                } else {
                    s.className = 'fa-regular fa-star';
                }
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
            modal.hide();
            document.getElementById('reviewComment').value = '';
        }

        async function loadReviews() {
            const res = await fetch('/api/reviews');
            const data = await res.json();
            
            document.getElementById('avgRatingScore').innerText = data.average_rating.toFixed(1);
            
            const fullStars = Math.floor(data.average_rating);
            let starsHtml = '';
            for(let i=0; i<5; i++) {
                if(i < fullStars) starsHtml += '<i class="fa-solid fa-star me-1"></i>';
                else starsHtml += '<i class="fa-regular fa-star me-1"></i>';
            }
            document.getElementById('avgRatingStars').innerHTML = starsHtml;

            const container = document.getElementById('reviewsContainer');
            if(data.reviews.length === 0) {
                container.innerHTML = '<div class="col-12 text-muted">No private reviews received yet.</div>';
                return;
            }

            container.innerHTML = data.reviews.map(rev => {
                let rStars = '';
                for(let i=0; i<5; i++) {
                    if(i < rev.rating) rStars += '<i class="fa-solid fa-star text-warning"></i>';
                    else rStars += '<i class="fa-regular fa-star text-warning"></i>';
                }
                return `
                    <div class="col-md-6">
                        <div class="card card-custom p-3 bg-white">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="fw-bold">Table #${rev.table_number}</span>
                                <div>${rStars}</div>
                            </div>
                            <p class="text-dark mb-1 font-italic">"${rev.comment || 'No written comment.'}"</p>
                            <small class="text-muted">${rev.created_at.substring(0, 19).replace('T', ' ')} UTC</small>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function loadKDS() {
            const res = await fetch('/api/kds/active');
            const orders = await res.json();
            const container = document.getElementById('kdsContainer');

            if(orders.length === 0) {
                container.innerHTML = '<div class="col-12 text-muted">No active kitchen orders.</div>';
                return;
            }

            container.innerHTML = orders.map(order => `
                <div class="col-md-4">
                    <div class="card card-custom p-3 bg-white kds-card kds-${order.status.toLowerCase()}">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0">${order.id} (Table #${order.table_number})</h6>
                            <span class="badge bg-secondary badge-status">${order.status}</span>
                        </div>
                        <ul class="small text-muted mb-3 ps-3">
                            ${order.items.map(i => `<li>${i.name}</li>`).join('')}
                        </ul>
                        <div class="d-flex flex-wrap gap-1 align-items-center">
                            <button class="btn btn-sm btn-success" onclick="advanceKDS('${order.id}')">Advance Status</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="cancelOrder('${order.id}')"><i class="fa-solid fa-ban"></i> Cancel/Refund</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="previewThermalReceipt('${order.id}')"><i class="fa-solid fa-print"></i> Thermal</button>
                            <a href="/api/invoice/${order.id}/pdf?currency=${currentCurr}" target="_blank" class="btn btn-sm btn-outline-dark"><i class="fa-solid fa-file-pdf text-danger"></i> PDF</a>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        async function previewThermalReceipt(id) {
            const res = await fetch('/api/receipt/' + id + '/txt');
            const text = await res.text();
            document.getElementById('receiptPreviewContent').innerText = text;
            document.getElementById('escposDownloadBtn').href = '/api/receipt/' + id + '/escpos';
            const modal = new bootstrap.Modal(document.getElementById('receiptModal'));
            modal.show();
        }

        async function advanceKDS(id) {
            await fetch('/api/kds/advance/' + id, { method: 'POST' });
            loadKDS();
        }

        async function cancelOrder(id) {
            if(!isAdminUnlocked) {
                alert('Manager PIN required to cancel & refund orders!');
                const modal = new bootstrap.Modal(document.getElementById('pinModal'));
                modal.show();
                return;
            }
            if(!confirm(`Are you sure you want to cancel & refund order ${id}? Items will be returned to inventory.`)) return;
            await fetch('/api/order/cancel/' + id, { method: 'POST' });
            alert(`Order ${id} cancelled and refunded. Stock returned.`);
            loadKDS();
            loadMenu();
        }

        async function loadAnalytics(currency) {
            const curr = currency || currentCurr;
            const res = await fetch('/api/analytics?currency=' + curr);
            const data = await res.json();
            const container = document.getElementById('analyticsStats');
            const sym = data.currency_symbol || '£';
            container.innerHTML = `
                <div class="col-md-3">
                    <div class="card card-custom p-3 bg-white text-center">
                        <small class="text-muted text-uppercase">Total Revenue (${data.currency})</small>
                        <h3 class="fw-bold text-success">${sym}${data.total_revenue.toFixed(2)}</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card card-custom p-3 bg-white text-center">
                        <small class="text-muted text-uppercase">Total Orders</small>
                        <h3 class="fw-bold text-primary">${data.total_orders}</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card card-custom p-3 bg-white text-center">
                        <small class="text-muted text-uppercase">Avg Order Value</small>
                        <h3 class="fw-bold text-info">${sym}${data.average_transaction_value.toFixed(2)}</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card card-custom p-3 bg-white text-center">
                        <small class="text-muted text-uppercase">RevPASH (${data.currency})</small>
                        <h3 class="fw-bold text-warning text-dark">${sym}${data.rev_pash.toFixed(2)}</h3>
                    </div>
                </div>
            `;
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
                    if(data.active_venue.currency) {
                        changeCurrency(data.active_venue.currency);
                    }
                    alert(`Switched active store location to: ${data.active_venue.name}`);
                }
            } catch(e) { console.error(e); }
        }

        async function staffClockIn() {
            const pin = document.getElementById('staffPinInput').value.trim();
            if(!pin) return alert('Enter staff PIN');
            const res = await fetch('/api/staff/clock-in', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: pin })
            });
            const data = await res.json();
            if(data.success) {
                alert(data.already_clocked_in ? `Already clocked in as ${data.shift.staff_name}` : `Clocked in successfully as ${data.shift.staff_name}`);
                document.getElementById('staffPinInput').value = '';
                loadStaff();
            } else {
                alert(data.error || 'Failed to clock in');
            }
        }

        async function staffClockOut() {
            const pin = document.getElementById('staffPinInput').value.trim();
            if(!pin) return alert('Enter staff PIN');
            const res = await fetch('/api/staff/clock-out', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: pin })
            });
            const data = await res.json();
            if(data.success) {
                alert(`Clocked out ${data.shift.staff_name}. Shift hours: ${data.shift.total_hours} hrs, Labor cost: £${data.shift.labor_cost.toFixed(2)}`);
                document.getElementById('staffPinInput').value = '';
                loadStaff();
            } else {
                alert(data.error || 'Failed to clock out');
            }
        }

        async function loadStaff() {
            try {
                const resShifts = await fetch('/api/staff/shifts');
                const dataShifts = await resShifts.json();
                
                document.getElementById('activeStaffBadge').innerText = `${dataShifts.active_shifts.length} Active Staff`;

                const resLabor = await fetch('/api/staff/labor-summary?currency=' + currentCurr);
                const dataLabor = await resLabor.json();

                const sym = dataLabor.currency_symbol || '£';
                document.getElementById('laborSummaryContent').innerHTML = `
                    <div class="col-4">
                        <div class="p-2 border rounded bg-light">
                            <small class="text-muted d-block text-uppercase">Active Staff</small>
                            <strong class="fs-5 text-primary">${dataLabor.active_staff_count}</strong>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="p-2 border rounded bg-light">
                            <small class="text-muted d-block text-uppercase">Total Hours</small>
                            <strong class="fs-5 text-success">${dataLabor.total_hours} hrs</strong>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="p-2 border rounded bg-light">
                            <small class="text-muted d-block text-uppercase">Labor Cost</small>
                            <strong class="fs-5 text-danger">${sym}${dataLabor.total_labor_cost.toFixed(2)} (${dataLabor.labor_cost_percentage}%)</strong>
                        </div>
                    </div>
                `;

                const logContainer = document.getElementById('shiftHistoryContainer');
                if(dataShifts.shifts.length === 0) {
                    logContainer.innerHTML = '<div class="text-muted small text-center my-3">No shifts recorded yet</div>';
                } else {
                    logContainer.innerHTML = dataShifts.shifts.map(s => `
                        <div class="d-flex justify-content-between align-items-center p-2 mb-2 border-bottom">
                            <div>
                                <strong class="d-block">${s.staff_name} <span class="badge bg-secondary ms-1">${s.role}</span></strong>
                                <small class="text-muted">In: ${s.clock_in.substring(11, 16)} | Out: ${s.clock_out ? s.clock_out.substring(11, 16) : 'ACTIVE'}</small>
                            </div>
                            <div class="text-end">
                                <span class="badge ${s.status === 'ACTIVE' ? 'bg-success' : 'bg-dark'}">${s.status}</span>
                                <small class="d-block text-muted">${s.total_hours}h (${sym}${s.labor_cost.toFixed(2)})</small>
                            </div>
                        </div>
                    `).join('');
                }
            } catch(e) { console.error(e); }
        }

        // Initial load
        loadVenues();
        updateTableDisplay();
        loadMenu();


        // Zero-Latency Server-Sent Events (SSE) Listener
        if ('EventSource' in window) {
            const evtSource = new EventSource('/api/kds/events');
            evtSource.addEventListener('kds_update', function(e) {
                loadKDS();
            });
        }


    </script>
</body>
</html>
"""

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
    identifier = data.get("phone_or_email", "")
    guest = data.get("guest_name", "")
    res = loyalty_service.register_account(identifier, guest)
    if res.get("success"):
        return jsonify(res)
    return jsonify(res), 400

@app.route("/api/loyalty/earn", methods=["POST"])
def earn_loyalty_points():
    data = request.json or {}
    identifier = data.get("phone_or_email", "")
    order_id = data.get("order_id", "")
    res = loyalty_service.earn_points(identifier, order_id)
    if res.get("success"):
        return jsonify(res)
    return jsonify(res), 400

@app.route("/api/loyalty/redeem", methods=["POST"])
def redeem_loyalty_reward():
    data = request.json or {}
    identifier = data.get("phone_or_email", "")
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
    return jsonify(kds_service.get_active_kitchen_orders())

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
