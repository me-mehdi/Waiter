import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix applyPromoCodeDirect to populate promoInput and mobilePromoInput
    old_apply_promo = '''        function applyPromoCodeDirect(code) {
            const promoInput = document.getElementById('cartPromoInput');
            if(promoInput) {
                promoInput.value = code;
                applyPromoCode();
            }
            const modalEl = document.getElementById('loyaltyModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if(modal) modal.hide();
        }'''

    new_apply_promo = '''        function applyPromoCodeDirect(code) {
            const pDesktop = document.getElementById('promoInput');
            const pMobile = document.getElementById('mobilePromoInput');
            if(pDesktop) pDesktop.value = code;
            if(pMobile) pMobile.value = code;
            const modalEl = document.getElementById('loyaltyModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if(modal) modal.hide();
        }'''

    if old_apply_promo in content:
        content = content.replace(old_apply_promo, new_apply_promo)
        print("Fixed applyPromoCodeDirect!")

    # 2. Fix payShareAmount to call POST /api/orders/${orderId}/pay-share and refreshSplitStatus
    old_pay_share = '''        async function payShareAmount(orderId, splitTarget, amount) {
            const splitModalEl = document.getElementById('splitModal');
            const splitModal = bootstrap.Modal.getInstance(splitModalEl);
            if(splitModal) splitModal.hide();

            // Open payment modal pre-loaded with split target & amount
            showPaymentModal();
            document.getElementById('checkoutSubtotalLabel').innerText = '£' + amount.toFixed(2);
            updatePaymentTotals();
        }'''

    new_pay_share = '''        async function payShareAmount(orderId, splitTarget, amount) {
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
        }'''

    if old_pay_share in content:
        content = content.replace(old_pay_share, new_pay_share)
        print("Fixed payShareAmount!")

    # 3. Fix loadVisualFloorplan to handle array response and t.table_number
    old_floorplan_js = '''        async function loadVisualFloorplan() {
            const container = document.getElementById('visualFloorplanGrid');
            if(!container) return;

            const res = await fetch('/api/floorplan/tables');
            const data = await res.json();
            const tables = data.tables || [];

            let html = '';
            tables.forEach(t => {
                let statusColor = 'border-success bg-success bg-opacity-10';
                let badgeBg = 'bg-success';
                if(t.status === 'Occupied') {
                    statusColor = 'border-danger bg-danger bg-opacity-10';
                    badgeBg = 'bg-danger';
                } else if(t.status === 'Reserved') {
                    statusColor = 'border-warning bg-warning bg-opacity-10';
                    badgeBg = 'bg-warning text-dark';
                }

                html += `
                    <div class="col-6 col-sm-4 col-md-3">
                        <div class="card p-3 text-white border-2 ${statusColor} rounded-3 shadow-sm text-center position-relative">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <strong class="fs-5 text-white">Table #${t.number}</strong>
                                <span class="badge ${badgeBg} rounded-pill">${t.status}</span>
                            </div>
                            <div class="my-2">
                                <i class="fa-solid fa-chair fs-3 opacity-75"></i>
                                <div class="small text-light opacity-75 mt-1">${t.capacity} Seats (${t.shape || 'Booth'})</div>
                            </div>
                            <small class="text-warning fw-bold"><i class="fa-solid fa-clock me-1"></i> ${t.status === 'Occupied' ? 'Turn: 35m' : 'Ready'}</small>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }'''

    new_floorplan_js = '''        async function loadVisualFloorplan() {
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
        }'''

    if old_floorplan_js in content:
        content = content.replace(old_floorplan_js, new_floorplan_js)
        print("Fixed loadVisualFloorplan and added interactive table reserve/release!")

    # 4. Add missing Staff Tab loaders (Bookings, Inventory, Waste, Tax, Feedback, Forecasting, Staff)
    staff_loaders_js = '''
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
                return `
                    <div class="col-md-4">
                        <div class="card p-3 border ${isLow ? 'border-danger bg-danger bg-opacity-10' : 'bg-white'} shadow-sm">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <strong class="text-dark">${it.name}</strong>
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
                                <small class="text-muted">${po.supplier_name} • Est. Total: £${po.estimated_total_cost.toFixed(2)}</small>
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
                    <h4 class="fw-bold text-danger mb-0">${sym}${(an.total_waste_cost || 0).toFixed(2)}</h4>
                </div>
                <div class="col-4">
                    <small class="text-muted d-block">Units Lost</small>
                    <h4 class="fw-bold text-dark mb-0">${an.total_units_wasted || 0}</h4>
                </div>
                <div class="col-4">
                    <small class="text-muted d-block">Incidents</small>
                    <h4 class="fw-bold text-warning mb-0">${an.total_incidents || 0}</h4>
                </div>
            `;

            const resLogs = await fetch('/api/waste/logs');
            const logsData = await resLogs.json();
            const logs = logsData.waste_logs || [];
            logsBody.innerHTML = logs.map(l => `
                <tr>
                    <td><small>${(l.logged_at || '').slice(11, 16)}</small></td>
                    <td><strong>${l.item_name}</strong></td>
                    <td>${l.quantity}</td>
                    <td><span class="badge bg-warning text-dark">${l.reason}</span></td>
                    <td>${l.staff_name}</td>
                    <td class="text-danger fw-bold">£${(l.cost_impact || 0).toFixed(2)}</td>
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
            container.innerHTML = `
                <div class="row g-2 text-center mb-3">
                    <div class="col-4">
                        <div class="p-2 bg-light rounded border">
                            <small class="text-muted d-block">Gross Sales</small>
                            <strong class="text-dark">${sym}${(data.total_gross_sales || 0).toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="p-2 bg-light rounded border">
                            <small class="text-muted d-block">Net Revenue</small>
                            <strong class="text-primary">${sym}${(data.total_net_sales || 0).toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="p-2 bg-success bg-opacity-10 rounded border border-success">
                            <small class="text-success fw-bold d-block">VAT Due (HMRC)</small>
                            <strong class="text-success">${sym}${(data.total_vat_payable || 0).toFixed(2)}</strong>
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
            document.getElementById('npsBreakdownText').innerText = `${nps.promoters} Promoters | ${nps.passives} Passives | ${nps.detractors} Detractors`;

            const resSent = await fetch('/api/feedback/sentiment');
            const sent = await resSent.json();
            const dist = sent.sentiment_distribution || {};
            document.getElementById('sentimentDistributionContent').innerHTML = `
                <div class="d-flex justify-content-between small mb-1"><span>😊 Positive:</span> <strong>${dist.POSITIVE || 0}</strong></div>
                <div class="d-flex justify-content-between small mb-1"><span>😐 Neutral:</span> <strong>${dist.NEUTRAL || 0}</strong></div>
                <div class="d-flex justify-content-between small"><span>😟 Negative:</span> <strong class="text-danger">${dist.NEGATIVE || 0}</strong></div>
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
                const safeComment = (r.comment || '').replace(/'/g, "\\'");
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
                    <td>${f.historical_avg_daily}</td>
                    <td><span class="badge bg-primary fs-6">${f.recommended_prep_qty} units</span></td>
                    <td><span class="text-success fw-bold">${f.confidence_score}%</span></td>
                </tr>
            `).join('');

            const resMat = await fetch('/api/forecasting/menu-matrix');
            const mat = await resMat.json();
            const items = mat.items || [];
            matrixEl.innerHTML = items.map(it => `
                <div class="p-2 border rounded mb-2 d-flex justify-content-between align-items-center">
                    <div>
                        <strong class="text-dark small d-block">${it.name}</strong>
                        <small class="text-muted">${it.Strategic_Action || ''}</small>
                    </div>
                    <span class="badge bg-info text-dark">${it.quadrant}</span>
                </div>
            `).join('');
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
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, staff_loaders_js + "\n" + target_script_end)
        print("Added complete Staff Workspace tab loaders and AI Review Auto-Responder UI buttons!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
