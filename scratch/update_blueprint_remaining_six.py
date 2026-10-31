import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Page 1 Floorplan Header (4 Blueprint KPIs + Architectural Bar Stools & Kitchen Pass)
    old_fp_header = '''                        <div class="d-flex gap-3 text-end">
                            <div>
                                <small class="text-muted d-block">AVG TABLE TURN</small>
                                <h5 class="fw-bold text-warning mb-0"><i class="fa-solid fa-rotate me-1"></i> 55 MIN</h5>
                            </div>
                            <div>
                                <small class="text-muted d-block">REVENUE YTD</small>
                                <h5 class="fw-bold text-success mb-0">£1.2M ↑</h5>
                            </div>
                        </div>
                    </div>

                    <!-- Floorplan Graphic Canvas / Table Grid -->
                    <div class="p-4 bg-secondary bg-opacity-25 rounded-3 border border-secondary mb-3">
                        <div class="row g-3" id="visualFloorplanGrid">
                            <!-- Dynamically generated visual table map -->
                        </div>
                    </div>'''

    new_fp_header = '''                        <div class="d-flex flex-wrap gap-3 text-end">
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
                    </div>'''

    if old_fp_header in content:
        content = content.replace(old_fp_header, new_fp_header, 1)
        print("Added Page 1 4-KPI Blueprint Header & Architectural Bar Stools + Kitchen Pass!")

    # 2. Add Page 8 Live Auto-Generated Invoice Preview + Daily/Monthly/Annual Horizon Toggle & Page 9 Cloud Sync Ecosystem Hub to #floorplan
    old_heatmap_row_end = '''                            <div id="zoneTurnoverContainer" class="vstack gap-3">
                                <!-- Populated dynamically by loadSalesHeatmap() -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>'''

    new_heatmap_row_end = '''                            <div id="zoneTurnoverContainer" class="vstack gap-3">
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
            </div>'''

    if old_heatmap_row_end in content:
        content = content.replace(old_heatmap_row_end, new_heatmap_row_end, 1)
        print("Added Page 8 Automated Invoice Preview + KPI Horizon Switcher & Page 9 6-Device Cloud Sync Hub!")

    # 3. Upgrade #strategy tab with Pages 2, 3, 10 ("The Operational Shift" Matrix & SaaS/Hardware ROI Calculator) and Page 11 (UK Consultation & 7-Day Free Trial Hub)
    old_strategy_pane = '''            <!-- TAB 12: Strategy Blueprint -->
            <div class="tab-pane fade" id="strategy" role="tabpanel">
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h3 class="fw-bold mb-3 text-dark">UK Market Strategy Blueprint</h3>
                    <iframe src="/docs/strategy" style="width: 100%; height: 600px; border: 1px solid #cbd5e1; border-radius: 8px;"></iframe>
                </div>
            </div>'''

    new_strategy_pane = '''            <!-- TAB 12: The Waiter Business Blueprint (Pages 2, 3, 10 & 11) -->
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
            </div>'''

    if old_strategy_pane in content:
        content = content.replace(old_strategy_pane, new_strategy_pane, 1)
        print("Upgraded #strategy tab with Pages 2, 3, 10 Operational Shift Matrix, ROI Calculator & Page 11 UK Consultation Hub!")

    # 4. Upgrade loadMenu() in Guest View to render Page 6 Rich Dish Photography & Inline Allergen Alert Badges
    old_load_menu_card = '''            container.innerHTML = data.map(item => {
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
            }).join('');'''

    new_load_menu_card = '''            const dishPhotos = {
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
            }).join('');'''

    if old_load_menu_card in content:
        content = content.replace(old_load_menu_card, new_load_menu_card, 1)
        print("Upgraded loadMenu() with Page 6 Rich Dish Photography & Inline Allergen Alert Badges!")

    # 5. Add JS functions for KPI Horizon Switcher, ROI Calculator, and Consultation Form before </script>\n</body>\n</html>"""
    js_blueprint_additions = '''
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
    </script>
</body>
</html>"""'''

    target_index_end = '''    </script>
</body>
</html>"""'''

    if target_index_end in content:
        content = content.replace(target_index_end, js_blueprint_additions, 1)
        print("Added JS handlers for Page 8 KPI Horizon Switcher, Page 10 ROI Calculator & Page 11 Consultation Booking!")

    # 6. Add Backend Endpoint POST /api/blueprint/consultation and GET /api/blueprint/summary
    backend_blueprint_routes = '''

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
'''

    target_main = 'if __name__ == "__main__":'
    if target_main in content:
        content = content.replace(target_main, backend_blueprint_routes + "\n\n" + target_main, 1)
        print("Added backend route POST /api/blueprint/consultation!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
