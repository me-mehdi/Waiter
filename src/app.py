from flask import Flask, jsonify, request, render_template_string, Response
import os
import sys

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
                <button class="badge bg-dark text-white border-0" id="pinAuthBtn" data-bs-toggle="modal" data-bs-target="#pinModal"><i class="fa-solid fa-lock me-1"></i> Manager Mode (PIN: 1234)</button>
                <a href="/terminal" target="_blank" class="badge bg-secondary text-white text-decoration-none"><i class="fa-solid fa-desktop me-1"></i>Netoff Terminal Pro</a>
            </div>
        </div>
    </div>

    <div class="container my-4">
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
                        <div class="col-md-4">
                            <div class="card p-3 border text-center">
                                <i class="fa-solid fa-receipt fs-1 text-primary mb-2"></i>
                                <h6 class="fw-bold">Order Sales History</h6>
                                <p class="text-muted small">Full log of transactions, table #s, items, and tax amounts.</p>
                                <a href="/api/export/orders/csv" target="_blank" class="btn btn-primary btn-sm"><i class="fa-solid fa-download me-1"></i> Export Orders CSV</a>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card p-3 border text-center">
                                <i class="fa-solid fa-boxes-stacked fs-1 text-success mb-2"></i>
                                <h6 class="fw-bold">Inventory Audit</h6>
                                <p class="text-muted small">Current stock levels, dish prices, and stock status warnings.</p>
                                <a href="/api/export/inventory/csv" target="_blank" class="btn btn-success btn-sm"><i class="fa-solid fa-download me-1"></i> Export Inventory CSV</a>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card p-3 border text-center">
                                <i class="fa-solid fa-comments fs-1 text-warning mb-2"></i>
                                <h6 class="fw-bold">Private Guest Feedback</h6>
                                <p class="text-muted small">Complete customer rating scores and private review comments.</p>
                                <a href="/api/export/reviews/csv" target="_blank" class="btn btn-warning text-dark btn-sm"><i class="fa-solid fa-download me-1"></i> Export Reviews CSV</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 7: Strategy Document -->
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

        async function loadMenu() {
            const res = await fetch(`/api/menu?lang=${currentLang}&currency=${currentCurr}`);
            const data = await res.json();
            
            const container = document.getElementById('menuContainer');
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

        // Initial load
        updateTableDisplay();
        loadMenu();
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
        async function updateTVDisplay() {
            try {
                const res = await fetch('/api/kds/tv');
                const data = await res.json();
                
                const prepContainer = document.getElementById('preparingContainer');
                if(data.preparing.length === 0) {
                    prepContainer.innerHTML = '<div class="text-center text-muted fs-4 my-5">No orders preparing</div>';
                } else {
                    prepContainer.innerHTML = data.preparing.map(id => `
                        <div class="ticket-badge badge-preparing">${id}</div>
                    `).join('');
                }

                const readyContainer = document.getElementById('readyContainer');
                if(data.ready.length === 0) {
                    readyContainer.innerHTML = '<div class="text-center text-muted fs-4 my-5">No orders ready</div>';
                } else {
                    readyContainer.innerHTML = data.ready.map(id => `
                        <div class="ticket-badge badge-ready">${id}</div>
                    `).join('');
                }
            } catch(e) { console.error(e); }
        }

        updateTVDisplay();
        setInterval(updateTVDisplay, 3000); // 3-second live auto refresh
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
    items = data.get("items", ["item-1", "item-3"])
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
