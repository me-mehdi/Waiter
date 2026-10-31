import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Import money_margins_service
    old_import = "from src.modules.uk_compliance import uk_compliance_service"
    new_import = "from src.modules.uk_compliance import uk_compliance_service\nfrom src.modules.money_margins import money_margins_service"
    if old_import in content and "money_margins_service" not in content:
        content = content.replace(old_import, new_import, 1)
        print("Imported money_margins_service in src/app.py!")

    # 2. Upgrade #paymentModal to include UK Open Banking "Pay by Bank" (0.2% Fee vs 1.5% Card) alongside Apple Pay, Google Pay, Card Stripe
    old_pay_methods = '''                    <div class="row g-2 mb-3">
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
                    </div>'''

    new_pay_methods = '''                    <div class="row g-2 mb-3">
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
                    </div>'''

    if old_pay_methods in content:
        content = content.replace(old_pay_methods, new_pay_methods, 1)
        print("Added UK Open Banking 'Pay by Bank' (0.2% fee) to #paymentModal!")

    # 3. Upgrade #splitModal to include Split by Percentage (%) alongside Split Evenly and Itemized Split
    old_split_tabs = '''                    <ul class="nav nav-pills nav-fill mb-3" id="splitTab" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active fw-bold" id="tab-even-tab" data-bs-toggle="tab" data-bs-target="#tab-even" type="button" role="tab"><i class="fa-solid fa-users me-1"></i> Split Evenly</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link fw-bold" id="tab-itemized-tab" data-bs-toggle="tab" data-bs-target="#tab-itemized" type="button" role="tab" onclick="loadItemizedSplitOptions()"><i class="fa-solid fa-list-check me-1"></i> Itemized Split</button>
                        </li>
                    </ul>'''

    new_split_tabs = '''                    <ul class="nav nav-pills nav-fill mb-3" id="splitTab" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active fw-bold" id="tab-even-tab" data-bs-toggle="tab" data-bs-target="#tab-even" type="button" role="tab"><i class="fa-solid fa-users me-1"></i> Split Evenly</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link fw-bold" id="tab-itemized-tab" data-bs-toggle="tab" data-bs-target="#tab-itemized" type="button" role="tab" onclick="loadItemizedSplitOptions()"><i class="fa-solid fa-list-check me-1"></i> Split by Item</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link fw-bold" id="tab-pct-tab" data-bs-toggle="tab" data-bs-target="#tab-pct" type="button" role="tab"><i class="fa-solid fa-percent me-1"></i> Split by Percentage</button>
                        </li>
                    </ul>'''

    if old_split_tabs in content:
        content = content.replace(old_split_tabs, new_split_tabs, 1)
        print("Added 'Split by Percentage' tab pill to #splitModal!")

    old_split_panes = '''                        <!-- Tab 2: Itemized Split -->
                        <div class="tab-pane fade" id="tab-itemized" role="tabpanel">
                            <p class="small text-muted mb-3"><i class="fa-solid fa-info-circle me-1"></i> Assign specific ordered dishes to Guest 1, Guest 2, etc. Unassigned items default to shared table balance.</p>
                            <div id="itemizedSplitContainer" class="mb-3"></div>
                            <button class="btn btn-primary w-100 fw-bold" onclick="submitItemizedSplit()"><i class="fa-solid fa-check-circle me-1"></i> Apply Itemized Split</button>
                        </div>
                    </div>'''

    new_split_panes = '''                        <!-- Tab 2: Itemized Split -->
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
                    </div>'''

    if old_split_panes in content:
        content = content.replace(old_split_panes, new_split_panes, 1)
        print("Added #tab-pct pane to #splitModal!")

    # 4. Add 💷 Money & Margins tab pill to #staffTabs
    old_uk_tab = '''            <li class="nav-item">
                <button class="nav-link" id="ukcompliance-tab" data-bs-toggle="tab" data-bs-target="#ukcompliance" type="button" onclick="loadUkComplianceHub()"><i class="fa-solid fa-shield-halved me-1 text-danger"></i> 🇬🇧 UK Compliance & EHO</button>
            </li>'''

    new_uk_tab = '''            <li class="nav-item">
                <button class="nav-link" id="margins-tab" data-bs-toggle="tab" data-bs-target="#margins" type="button" onclick="loadMoneyAndMarginsHub()"><i class="fa-solid fa-sterling-sign me-1 text-success"></i> 💷 Money & Margins</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="ukcompliance-tab" data-bs-toggle="tab" data-bs-target="#ukcompliance" type="button" onclick="loadUkComplianceHub()"><i class="fa-solid fa-shield-halved me-1 text-danger"></i> 🇬🇧 UK Compliance & EHO</button>
            </li>'''

    if old_uk_tab in content:
        content = content.replace(old_uk_tab, new_uk_tab, 1)
        print("Added 💷 Money & Margins tab pill to #staffTabs!")

    # 5. Add #margins Tab Pane right before #ukcompliance tab pane
    target_uk_pane = '''            <!-- TAB 11B: 🇬🇧 UK Statutory Compliance, Natasha's Law, Tips Act 2024, Challenge 25, EHO Food Safety & GDPR Hub -->'''

    margins_pane = '''            <!-- TAB 11A: 💷 Money & Margins Hub (Xero/QuickBooks/Sage/FreeAgent, Recipe Costing & GP%, Booker/Bidfood/Brakes & Invoice OCR, Rota Labour % & Holiday Accrual) -->
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

'''

    if target_uk_pane in content and 'id="margins"' not in content:
        content = content.replace(target_uk_pane, margins_pane + target_uk_pane, 1)
        print("Added #margins tab pane to Staff Workspace!")

    # 6. Add JS functions for Percentage Bill Split and Money & Margins Hub before </script>\n</body>\n</html>"""
    js_margins = '''
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
</html>"""'''

    target_index_end = '''    </script>
</body>
</html>"""'''

    if target_index_end in content:
        content = content.replace(target_index_end, js_margins, 1)
        print("Added JS handlers for Money & Margins Hub and Percentage Bill Split!")

    # 7. Add Backend Routes for Money & Margins before if __name__ == "__main__":
    backend_margins_routes = '''

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
'''

    target_main = 'if __name__ == "__main__":'
    if target_main in content:
        content = content.replace(target_main, backend_margins_routes + "\n\n" + target_main, 1)
        print("Added backend routes for all 5 Money & Margins pillars!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
