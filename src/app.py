from flask import Flask, jsonify, request, render_template_string, Response, redirect
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
from src.modules.pub_features import pub_features_service
from src.modules.growth_customers import growth_customers_service
from src.modules.reliability import reliability_service
from src.modules.navy_brass_ui import NAVY_BRASS_SUITE_HTML, render_navy_brass_page
from src.modules.restaurant_ordering_ui import render_restaurant_ordering_html
from src.modules.admin_dashboard_ui import render_admin_dashboard, render_admin_login_page
from src.modules.admin_kitchen_ui import render_admin_kitchen_page

app = Flask(__name__)







app.config['SECRET_KEY'] = Config.SECRET_KEY

INDEX_HTML = NAVY_BRASS_SUITE_HTML

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
@app.route("/landing")
def home():
    return render_template_string(render_navy_brass_page("all"))

@app.route("/order/menu")
@app.route("/order/menu/")
@app.route("/order/menu/<path:subpath>")
def restaurant_order_menu_page(subpath=None):
    table = request.args.get("table", 12)
    try:
        table_num = int(table)
    except Exception:
        table_num = 12
    return render_template_string(render_restaurant_ordering_html(table_num=table_num, initial_item_id=subpath))

@app.route("/menu")
@app.route("/guest")
@app.route("/order")
def guest_menu_page():
    return render_template_string(render_navy_brass_page("menu"))

@app.route("/kitchen")
@app.route("/kds")
def kitchen_display_page():
    return render_template_string(render_navy_brass_page("kitchen"))

@app.route("/today")
@app.route("/owner")
@app.route("/dashboard")
def owner_today_page():
    return render_template_string(render_navy_brass_page("today"))

@app.route("/admin")
@app.route("/admin/")
def admin_console_page():
    token = request.cookies.get("admin_token") or request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    user = auth_service.validate_session(token) if token else None
    if not user:
        return redirect("/admin/login")
    active_tab = request.args.get("tab", "menu")
    return render_template_string(render_admin_dashboard(active_tab=active_tab))

@app.route("/admin/login")
@app.route("/admin/login/")
def admin_login_page():
    return render_template_string(render_admin_login_page(return_url="/admin/"))

@app.route("/admin/kitchen")
@app.route("/admin/kitchen/")
def admin_kitchen_page():
    token = request.cookies.get("admin_token") or request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    user = auth_service.validate_session(token) if token else None
    if not user:
        return redirect("/admin/login?returnUrl=/admin/kitchen")
    return render_template_string(render_admin_kitchen_page())

@app.route("/till")
@app.route("/pos")
def till_pos_page():
    return render_template_string(render_navy_brass_page("till"))

@app.route("/reservations")
@app.route("/bookings")
def table_reservations_page():
    return render_template_string(render_navy_brass_page("reservations"))

@app.route("/stock")
@app.route("/cellar")
def stock_cellar_page():
    return render_template_string(render_navy_brass_page("stock"))

@app.route("/staff")
@app.route("/rota")
def staff_rota_page():
    return render_template_string(render_navy_brass_page("staff"))

@app.route("/settings")
@app.route("/printers")
@app.route("/reliability")
def reliability_settings_page():
    return render_template_string(render_navy_brass_page("settings"))

@app.route("/tv")
def tv_display():
    return render_template_string(render_navy_brass_page("kitchen"))

@app.route("/terminal")
def terminal():
    return render_template_string(render_navy_brass_page("till"))

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
    promo = data.get("promo_code")
    notes = data.get("notes")
    tip = data.get("tip_amount", 0.0)
    pay_method = data.get("payment_method", "CARD_STRIPE")
    customer = data.get("customer")
    
    order = qr_ordering_service.submit_order(
        table_number=table_num,
        items=raw_items,
        promo_code=promo,
        notes=notes,
        tip_amount=tip,
        payment_method=pay_method,
        customer=customer
    )
    return jsonify({"order": order, "status": "CREATED"}), 201

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




# --- 31. British Pub & Cellar Endpoints (Pre-Auth Bar Tabs, 'Same Again!' Rounds, Cellar Kegs, Sunday Roast, Quiz & Beer Garden) ---
@app.route("/api/pub/tabs", methods=["GET"])
def get_pub_bar_tabs():
    return jsonify({"tabs": pub_features_service.get_bar_tabs()})

@app.route("/api/pub/tabs/open", methods=["POST"])
def open_pub_bar_tab():
    data = request.json or {}
    tab = pub_features_service.open_bar_tab(
        customer_name=data.get("customer_name", "Pub Guest"),
        table_or_zone=data.get("table_or_zone", "Bar Stool S1"),
        pre_auth_limit_gbp=float(data.get("pre_auth_limit_gbp", 50.0))
    )
    return jsonify(tab), 201

@app.route("/api/pub/tabs/<tab_id>/same-again", methods=["POST"])
def pub_tab_same_again_round(tab_id):
    try:
        res = pub_features_service.order_same_again_round(tab_id)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/pub/cellar", methods=["GET"])
def get_pub_cellar_status():
    return jsonify(pub_features_service.get_cellar_status())

@app.route("/api/pub/cellar/clean-line/<int:tap_number>", methods=["POST"])
def clean_pub_cellar_line(tap_number):
    try:
        tap = pub_features_service.log_beer_line_clean(tap_number)
        return jsonify(tap)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/pub/extras", methods=["GET"])
def get_pub_extras():
    return jsonify(pub_features_service.get_pub_extras_status())

@app.route("/api/pub/roast/preorder", methods=["POST"])
def preorder_pub_sunday_roast():
    data = request.json or {}
    try:
        res = pub_features_service.preorder_sunday_roast(
            roast_id=data.get("roast_id", "ROAST-BEEF"),
            quantity=int(data.get("quantity", 1)),
            guest_name=data.get("guest_name", "Table Guest")
        )
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/pub/events/book", methods=["POST"])
def book_pub_quiz_or_event():
    data = request.json or {}
    try:
        res = pub_features_service.book_pub_quiz_team(
            event_id=data.get("event_id", "QUIZ-WED"),
            team_name=data.get("team_name", "The Quizards"),
            team_size=int(data.get("team_size", 4))
        )
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/pub/garden", methods=["GET"])
def get_pub_beer_garden_status():
    return jsonify(pub_features_service.get_beer_garden_status())

@app.route("/api/pub/garden/toggle", methods=["POST"])
def toggle_pub_beer_garden():
    data = request.json or {}
    res = pub_features_service.update_beer_garden_weather_or_toggle(
        garden_open=data.get("garden_open"),
        simulate_weather=data.get("simulate_weather")
    )
    return jsonify(res)



# --- 32. Growth & Customers Endpoints (Deliveroo/UberEats/JustEat + 0% Click & Collect, Deposit Bookings, Wallet Stamps, 10 UK Languages) ---
@app.route("/api/growth/dashboard", methods=["GET"])
def get_growth_customers_dashboard():
    lang = request.args.get("lang", "en")
    return jsonify(growth_customers_service.get_full_growth_dashboard(active_lang=lang))

@app.route("/api/growth/aggregator-order", methods=["POST"])
def inject_growth_aggregator_kds_order():
    data = request.json or {}
    try:
        res = growth_customers_service.inject_aggregator_order(
            platform=data.get("platform", "JUSTEAT"),
            customer_name=data.get("customer_name", "Just Eat Customer"),
            item_ids=data.get("item_ids", ["item-1", "item-4"]),
            external_ref=data.get("external_ref"),
            delivery_address=data.get("delivery_address", "Central London Delivery")
        )
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/growth/click-and-collect", methods=["POST"])
def submit_commission_free_click_and_collect():
    data = request.json or {}
    try:
        res = growth_customers_service.submit_click_and_collect_order(
            customer_name=data.get("customer_name", "Direct Guest"),
            customer_phone=data.get("customer_phone", "+447700900111"),
            item_ids=data.get("item_ids", ["item-1"]),
            pickup_slot=data.get("pickup_slot", "ASAP (15 mins)"),
            promo_code=data.get("promo_code")
        )
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/growth/reservations/deposit", methods=["POST"])
def create_deposit_protected_reservation():
    data = request.json or {}
    try:
        res = growth_customers_service.create_deposit_reservation(
            guest_name=data.get("guest_name", "Google Guest"),
            guest_phone=data.get("guest_phone", "+447700900222"),
            guest_email=data.get("guest_email", "guest@example.co.uk"),
            party_size=int(data.get("party_size", 4)),
            table_number=int(data.get("table_number", 4)),
            booking_date=data.get("booking_date", "2026-11-15"),
            time_slot=data.get("time_slot", "19:30"),
            deposit_per_head_gbp=float(data.get("deposit_per_head_gbp", 10.0)),
            booking_source=data.get("booking_source", "GOOGLE_BUSINESS_PROFILE"),
            card_last4=data.get("card_last4", "4242"),
            special_requests=data.get("special_requests", "")
        )
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/growth/wallet-stamp", methods=["POST"])
def add_wallet_stamp_and_prompt_google_review():
    data = request.json or {}
    res = growth_customers_service.add_stamp_and_trigger_google_review(
        phone=data.get("phone", "+447700900111"),
        guest_name=data.get("guest_name", "Valued Guest"),
        order_id=data.get("order_id"),
        stamps_to_add=int(data.get("stamps_to_add", 1))
    )
    return jsonify(res), 201

@app.route("/api/growth/languages", methods=["GET"])
def get_uk_multicultural_languages_matrix():
    lang = request.args.get("lang", "en")
    return jsonify(growth_customers_service.get_multicultural_and_dietary_matrix(active_lang=lang))



# --- 33. Reliability & Open Printer Compatibility Endpoints (Offline Queue Sync + Epson/Star Thermal Printers) ---
@app.route("/api/reliability/dashboard", methods=["GET"])
def get_reliability_dashboard_status():
    return jsonify(reliability_service.get_reliability_dashboard())

@app.route("/api/reliability/network-mode", methods=["POST"])
def set_venue_reliability_network_mode():
    data = request.json or {}
    try:
        res = reliability_service.set_network_mode(data.get("mode", "ONLINE"))
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/reliability/offline-queue", methods=["POST"])
def queue_local_offline_order():
    data = request.json or {}
    try:
        res = reliability_service.queue_offline_order(
            table_number=int(data.get("table_number", 1)),
            item_ids=data.get("item_ids", ["item-1", "item-3"]),
            scenario=data.get("scenario", "CELLAR_DEAD_ZONE"),
            location_note=data.get("location_note", "Pub Cellar / Rural Signal Drop"),
            client_offline_id=data.get("client_offline_id"),
            promo_code=data.get("promo_code")
        )
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/reliability/offline-sync", methods=["POST"])
def sync_local_offline_orders_to_kds():
    data = request.json or {}
    res = reliability_service.sync_offline_queue(
        client_queued_orders=data.get("client_queued_orders")
    )
    return jsonify(res)

@app.route("/api/reliability/printers", methods=["GET"])
def get_certified_thermal_printers():
    brand = request.args.get("brand", "all")
    return jsonify(reliability_service.get_supported_printers_matrix(brand_filter=brand))

@app.route("/api/reliability/printers/test", methods=["POST"])
def run_certified_printer_diagnostic():
    data = request.json or {}
    res = reliability_service.run_printer_diagnostic_test(
        model_id=data.get("model_id", "EPSON-TM-T88VII"),
        order_id=data.get("order_id")
    )
    return jsonify(res)



# --- 34. Navy & Brass UK Hospitality 4-Screen + Back-of-House Suite (/uk) ---
@app.route("/uk", methods=["GET"])
def render_navy_and_brass_uk_suite():
    return render_template_string(NAVY_BRASS_SUITE_HTML)


# =====================================================================
# 35. Admin Control Console API Endpoints (CRUD & Venue Management)
# =====================================================================

@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    data = request.get_json() or {}
    pin = data.get("pin")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1").split(",")[0].strip()
    ua = request.headers.get("User-Agent", "")

    if pin:
        ok, session, err = auth_service.authenticate_pin(pin, ip_address=ip, user_agent=ua)
    else:
        username = data.get("username", "")
        password = data.get("password", "")
        ok, session, err = auth_service.authenticate_user(username, password, ip_address=ip, user_agent=ua)

    if not ok:
        return jsonify({"success": False, "error": err or "Invalid credentials"}), 401

    resp = jsonify({"success": True, "session": session})
    resp.set_cookie(
        "admin_token",
        session["token"],
        httponly=True,
        samesite="Strict",
        max_age=8 * 3600
    )
    return resp

@app.route("/api/admin/logout", methods=["POST"])
def api_admin_logout():
    cookie_token = request.cookies.get("admin_token")
    header_token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if cookie_token:
        auth_service.revoke_session(cookie_token)
    if header_token:
        auth_service.revoke_session(header_token)
    resp = jsonify({"success": True, "message": "Logged out successfully"})
    resp.delete_cookie("admin_token")
    return resp

@app.route("/api/admin/me", methods=["GET"])
def api_admin_me():
    token = request.cookies.get("admin_token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    user = auth_service.validate_session(token)
    if not user:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": user})

@app.route("/api/admin/audit-logs", methods=["GET"])
def api_admin_audit_logs():
    return jsonify({"success": True, "logs": auth_service.get_audit_logs(limit=50)})

@app.route("/api/admin/menu", methods=["GET"])
def api_admin_get_menu():
    items = list(db.menu_items.values())
    return jsonify({"success": True, "items": items, "count": len(items)})

@app.route("/api/admin/menu", methods=["POST"])
def api_admin_add_menu():
    data = request.get_json() or {}
    item = db.add_menu_item(data)
    return jsonify({"success": True, "item": item}), 201

@app.route("/api/admin/menu/<item_id>", methods=["PUT"])
def api_admin_update_menu(item_id):
    data = request.get_json() or {}
    item = db.update_menu_item(item_id, data)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404
    return jsonify({"success": True, "item": item})

@app.route("/api/admin/menu/<item_id>", methods=["DELETE"])
def api_admin_delete_menu(item_id):
    deleted = db.delete_menu_item(item_id)
    return jsonify({"success": deleted})

@app.route("/api/admin/menu/<item_id>/toggle-86", methods=["POST"])
def api_admin_toggle_86(item_id):
    data = request.get_json() or {}
    is_avail = data.get("is_available")
    item = db.toggle_menu_item_86(item_id, is_avail)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404
    return jsonify({"success": True, "item": item})

@app.route("/api/admin/orders", methods=["GET"])
def api_admin_get_orders():
    orders = list(db.orders.values())
    return jsonify({"success": True, "orders": orders, "count": len(orders)})

@app.route("/api/admin/orders/<order_id>/status", methods=["POST"])
def api_admin_update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get("status", "Preparing")
    updated = db.update_order_status(order_id, new_status)
    return jsonify({"success": bool(updated), "order": updated})

@app.route("/api/admin/orders/<order_id>/void", methods=["POST"])
def api_admin_void_order(order_id):
    res = db.cancel_order(order_id)
    return jsonify({"success": bool(res), "order": res})

@app.route("/api/admin/tables", methods=["GET"])
def api_admin_get_tables():
    tables = db.get_tables()
    return jsonify({"success": True, "tables": tables})

@app.route("/api/admin/tables", methods=["POST"])
def api_admin_add_table():
    data = request.get_json() or {}
    num = int(data.get("table_number", 1))
    cap = int(data.get("capacity", 4))
    zone = str(data.get("zone", "Main Dining Room"))
    status = str(data.get("status", "AVAILABLE"))
    tbl = db.add_or_update_table(num, cap, zone, status)
    return jsonify({"success": True, "table": tbl})

@app.route("/api/admin/tables/<int:table_num>", methods=["DELETE"])
def api_admin_delete_table(table_num):
    deleted = db.delete_table(table_num)
    return jsonify({"success": deleted})

@app.route("/api/admin/tables/<int:table_num>/status", methods=["POST"])
def api_admin_update_table_status(table_num):
    data = request.get_json() or {}
    status = str(data.get("status", "AVAILABLE"))
    updated = db.update_table_status(table_num, status)
    return jsonify({"success": updated})

@app.route("/api/admin/compliance/fridge", methods=["GET", "POST"])
def api_admin_fridge_logs():
    if request.method == "POST":
        data = request.get_json() or {}
        appliance = str(data.get("appliance", "Walk-in Meat Chiller"))
        temp = float(data.get("temperature", 3.0))
        by = str(data.get("recorded_by", "Manager"))
        log = db.add_fridge_log(appliance, temp, by)
        return jsonify({"success": True, "log": log}), 201
    return jsonify({"success": True, "logs": db.get_fridge_logs()})

@app.route("/api/admin/compliance/c25", methods=["GET", "POST"])
def api_admin_c25_logs():
    if request.method == "POST":
        data = request.get_json() or {}
        item = str(data.get("item_name", "Pint of Lager"))
        reason = str(data.get("reason", "No ID presented"))
        staff = str(data.get("staff_member", "Server"))
        log = db.add_challenge25_log(item, reason, staff)
        return jsonify({"success": True, "log": log}), 201
    return jsonify({"success": True, "logs": db.get_challenge25_logs()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
