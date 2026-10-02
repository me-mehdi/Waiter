import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Replacement for splitModal
    old_split_modal = '''    <!-- Split Bill Modal -->
    <div class="modal fade" id="splitModal" tabindex="-1" aria-labelledby="splitModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="splitModalLabel"><i class="fa-solid fa-calculator text-success me-2"></i>Split Table Bill</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label small fw-bold text-muted">Number of Guests</label>
                        <input type="number" id="guestSplitNum" class="form-control" value="2" min="2" max="10">
                    </div>
                    <button class="btn btn-success w-100 fw-bold mb-3" onclick="calculateTableSplit()"><i class="fa-solid fa-scissors me-1"></i> Calculate Shares</button>
                    <div id="tableSplitResult"></div>
                </div>
            </div>
        </div>
    </div>'''

    new_split_modal = '''    <!-- Split Bill Modal & Shared Table Balances -->
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
    </div>'''

    if old_split_modal in content:
        content = content.replace(old_split_modal, new_split_modal)
        print("Updated splitModal HTML successfully!")
    else:
        print("Could not find old_split_modal in app.py!")

    # Replacement for JS functions showSplitBillModal and calculateTableSplit
    old_js_split = '''        function showSplitBillModal() {
            const modal = new bootstrap.Modal(document.getElementById('splitModal'));
            modal.show();
        }

        async function calculateTableSplit() {
            if(!activeOrderForTable) return alert('No active submitted order to split for Table #' + activeTable);
            const nGuests = parseInt(document.getElementById('guestSplitNum').value);
            const res = await fetch(`/api/orders/${activeOrderForTable.id}/split/even`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ num_guests: nGuests, include_service_charge: true })
            });
            const data = await res.json();
            const container = document.getElementById('tableSplitResult');

            if(data.splits) {
                container.innerHTML = `
                    <div class="p-3 bg-light rounded border mb-2">
                        <strong class="text-dark d-block">Order Total: £${data.grand_total.toFixed(2)}</strong>
                        <span class="small text-muted">Divided evenly across ${data.splits.length} guests</span>
                    </div>
                    ${data.splits.map((s, idx) => `
                        <div class="d-flex justify-content-between align-items-center p-2 mb-1 bg-white border rounded">
                            <span>Guest ${idx + 1} Share: <strong class="text-success">£${s.amount.toFixed(2)}</strong></span>
                            <a href="/api/orders/${data.order_id}/split/sub-receipt/${idx + 1}" target="_blank" class="btn btn-xs btn-outline-dark py-0 px-2"><i class="fa-solid fa-receipt me-1"></i> Receipt</a>
                        </div>
                    `).join('')}
                `;
            } else {
                container.innerHTML = `<div class="text-danger small">${data.error || 'Failed to split order.'}</div>`;
            }
        }'''

    new_js_split = '''        let activeSplitStatusData = null;

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
        }'''

    if old_js_split in content:
        content = content.replace(old_js_split, new_js_split)
        print("Updated JS split functions successfully!")
    else:
        print("Could not find old_js_split in app.py!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
