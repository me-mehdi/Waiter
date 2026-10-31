import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Guest Promo Flash Banner & Quick-Service Call Bell Bar + Enhanced Live Order ETA Card in #guestViewSection
    old_guest_welcome = '''        <div class="p-3 bg-white rounded-3 border shadow-sm mb-3 d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-2">
                <i class="fa-solid fa-heart text-danger fs-5"></i>
                <span class="fw-semibold text-dark" id="guestWelcomeMsgText">Welcome! Tap dishes below to order directly from Table #1</span>
            </div>
            <span class="badge bg-success bg-opacity-25 text-success border border-success"><i class="fa-solid fa-bolt me-1"></i> Fast Digital Service</span>
        </div>'''

    new_guest_welcome = '''        <div class="p-3 bg-white rounded-3 border shadow-sm mb-2 d-flex align-items-center justify-content-between">
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
        </div>'''

    if old_guest_welcome in content:
        content = content.replace(old_guest_welcome, new_guest_welcome, 1)
        print("Added Guest Promo Flash Banner & 1-Tap Table Concierge Bar!")

    # 2. Upgrade #tableLiveOrderCard with Live Kitchen Station Routing & ETA Progress
    old_live_card = '''            <button class="btn btn-sm btn-dark w-100 fw-bold" onclick="showOnlinePaymentModal()"><i class="fa-solid fa-credit-card text-success me-1"></i> Pay Bill at Table Now</button>
        </div>'''

    new_live_card = '''            <div id="liveOrderStationEtaBox" class="p-2 bg-light rounded-3 border mb-3 small">
                <!-- Populated dynamically by loadTableLiveOrderStatus() via GET /api/kds/eta/<order_id> -->
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-sm btn-dark flex-grow-1 fw-bold" onclick="showOnlinePaymentModal()"><i class="fa-solid fa-credit-card text-success me-1"></i> Pay Bill at Table Now</button>
                <button class="btn btn-sm btn-outline-danger fw-bold d-none" id="btnCancelGuestOrder" onclick="cancelActiveGuestOrder()"><i class="fa-solid fa-ban me-1"></i> Cancel Order</button>
            </div>
        </div>'''

    if old_live_card in content:
        content = content.replace(old_live_card, new_live_card, 1)
        print("Upgraded #tableLiveOrderCard with Kitchen Station ETA & Cancel button!")

    # 3. Add onclick="loadZReportAndPromos()" to #reports-tab button
    old_reports_tab_btn = '''<button class="nav-link" id="reports-tab" data-bs-toggle="tab" data-bs-target="#reports" type="button"><i class="fa-solid fa-file-csv me-1"></i> Reports Exporter</button>'''
    new_reports_tab_btn = '''<button class="nav-link" id="reports-tab" data-bs-toggle="tab" data-bs-target="#reports" type="button" onclick="loadZReportAndPromos()"><i class="fa-solid fa-chart-pie me-1"></i> Z-Report & Promos</button>'''

    if old_reports_tab_btn in content:
        content = content.replace(old_reports_tab_btn, new_reports_tab_btn, 1)
        print("Updated #reports-tab button with loadZReportAndPromos()!")

    # 4. Add Live Active Table Service Calls Queue at top of #floorplan tab
    old_floorplan_start = '''            <!-- TAB 0: Visual Blueprint Floor Plan Layout (Page 1 Blueprint) -->
            <div class="tab-pane fade show active" id="floorplan" role="tabpanel">'''

    new_floorplan_start = '''            <!-- TAB 0: Visual Blueprint Floor Plan Layout (Page 1 Blueprint) -->
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
                </div>'''

    if old_floorplan_start in content:
        content = content.replace(old_floorplan_start, new_floorplan_start, 1)
        print("Added Live Table Service Calls Dispatch Queue to #floorplan!")

    # 5. Upgrade #reports tab with Interactive Z-Report Financial Reconciliation & Dynamic Happy Hour Promo Studio
    old_reports_pane = '''            <!-- TAB 11: Reports Hub -->
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
            </div>'''

    new_reports_pane = '''            <!-- TAB 11: Interactive Z-Report Financial Reconciliation, Promo Studio & CSV Hub -->
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
            </div>'''

    if old_reports_pane in content:
        content = content.replace(old_reports_pane, new_reports_pane, 1)
        print("Upgraded #reports tab with Z-Report Reconciliation & Promo Campaign Studio!")

    # 6. Upgrade callWaiter() and loadTableLiveOrderStatus() and add JS functions
    old_call_waiter = '''        function callWaiter() {
            const banner = document.getElementById('waiterAlertBanner');
            banner.classList.remove('d-none');
            setTimeout(() => banner.classList.add('d-none'), 6000);
        }'''

    new_call_waiter = '''        async function callWaiter() {
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
        }'''

    if old_call_waiter in content:
        content = content.replace(old_call_waiter, new_call_waiter, 1)
        print("Upgraded callWaiter() with requestTableService()!")

    old_live_order_fn = '''                sRec.className = 'order-step active';
                sPrep.className = 'order-step' + (latestOrder.status === 'PREPARING' || latestOrder.status === 'READY' ? ' active' : '');
                sReady.className = 'order-step' + (latestOrder.status === 'READY' ? ' active' : '');
            } catch(e) { console.error(e); }
        }'''

    new_live_order_fn = '''                sRec.className = 'order-step active';
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
        }'''

    if old_live_order_fn in content:
        content = content.replace(old_live_order_fn, new_live_order_fn, 1)
        print("Upgraded loadTableLiveOrderStatus() with live Kitchen Station ETA & Cancel handler!")

    # 7. Inject JS functions for Service Calls Queue, Z-Report Reconciliation, and Promo Studio before </script>
    js_additions = '''
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
    </script>'''

    if "    </script>" in content:
        idx = content.rfind("    </script>")
        content = content[:idx] + js_additions + content[idx + len("    </script>"):]
        print("Added JS functions for Service Calls, Z-Report Reconciliation, and Promo Studio!")

    # 8. Hook loadGuestActivePromos() and loadServiceCallsQueue() into initial load
    old_init = '''        loadSalesHeatmap();
    </script>'''
    new_init = '''        loadSalesHeatmap();
        loadGuestActivePromos();
        loadServiceCallsQueue();
    </script>'''
    if "loadSalesHeatmap();" in content:
        content = content.replace("loadSalesHeatmap();", "loadSalesHeatmap();\n        loadGuestActivePromos();\n        loadServiceCallsQueue();", 1)
        print("Hooked loadGuestActivePromos() and loadServiceCallsQueue() into initial load!")

    # 9. Add Backend Routes for Service Calls & Dynamic Promo Management before if __name__ == "__main__":
    backend_routes = '''

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
    db.promos[code] = round(discount_pct / 100.0, 2)
    return jsonify({"success": True, "code": code, "discount_rate": db.promos[code], "promos": db.promos}), 201

@app.route("/api/promos/<code>", methods=["DELETE"])
def delete_promo_code(code):
    code_up = code.strip().upper()
    if code_up in db.promos:
        del db.promos[code_up]
        return jsonify({"success": True, "deleted": code_up, "promos": db.promos})
    return jsonify({"error": "Promo code not found"}), 404
'''

    target_main = 'if __name__ == "__main__":'
    if target_main in content:
        content = content.replace(target_main, backend_routes + "\n\n" + target_main, 1)
        print("Added backend routes for Service Calls and Dynamic Promo Campaigns!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
