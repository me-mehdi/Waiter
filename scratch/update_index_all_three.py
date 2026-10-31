import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Delivery Hub tab pill to #staffTabs
    old_tab_pill = '''            <li class="nav-item">
                <button class="nav-link" id="kds-tab" data-bs-toggle="tab" data-bs-target="#kds" type="button" onclick="loadKDS()"><i class="fa-solid fa-fire-burner me-1"></i> Kitchen KDS</button>
            </li>'''

    new_tab_pill = '''            <li class="nav-item">
                <button class="nav-link" id="kds-tab" data-bs-toggle="tab" data-bs-target="#kds" type="button" onclick="loadKDS()"><i class="fa-solid fa-fire-burner me-1"></i> Kitchen KDS</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="delivery-tab" data-bs-toggle="tab" data-bs-target="#delivery" type="button" onclick="loadDeliveryHub()"><i class="fa-solid fa-motorcycle me-1"></i> Delivery Hub</button>
            </li>'''

    if old_tab_pill in content:
        content = content.replace(old_tab_pill, new_tab_pill, 1)
        print("Added Delivery Hub tab pill to #staffTabs!")

    # 2. Add Executive Peak-Hour Sales Heatmap & Zone Turnover Analytics card inside #floorplan tab
    old_floorplan_end = '''                        <span><i class="fa-solid fa-bolt text-info me-1"></i> Zero Hardware Lock-In Engine</span>
                    </div>
                </div>
            </div>'''

    new_floorplan_end = '''                        <span><i class="fa-solid fa-bolt text-info me-1"></i> Zero Hardware Lock-In Engine</span>
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
            </div>'''

    if old_floorplan_end in content:
        content = content.replace(old_floorplan_end, new_floorplan_end, 1)
        print("Added Executive Peak-Hour Sales Heatmap & Zone Turnover card to #floorplan!")

    # 3. Add Chef Recipe & Allergen Matrix button to KDS Toolbar + Delivery Hub Tab Pane
    old_kds_toolbar_btn = '''<button class="btn btn-sm btn-outline-dark rounded-pill px-3 py-1 fw-bold me-2" onclick="openThermalPrinterEmulator()"><i class="fa-solid fa-print me-1 text-primary"></i> Thermal Docket Emulator</button>'''
    new_kds_toolbar_btn = '''<button class="btn btn-sm btn-outline-dark rounded-pill px-3 py-1 fw-bold me-1" onclick="openThermalPrinterEmulator()"><i class="fa-solid fa-print me-1 text-primary"></i> Thermal Docket</button>
                    <button class="btn btn-sm btn-warning text-dark rounded-pill px-3 py-1 fw-bold me-2" onclick="openChefRecipeModal()"><i class="fa-solid fa-book-open-reader me-1"></i> Chef Recipes & Natasha's Law Allergens</button>'''

    if old_kds_toolbar_btn in content:
        content = content.replace(old_kds_toolbar_btn, new_kds_toolbar_btn, 1)
        print("Added Chef Recipes & Allergen Matrix button to KDS toolbar!")

    # 4. Add #delivery tab pane right after #kds tab pane
    old_kds_pane_end = '''                <div id="kdsContainer" class="row g-3">
                    <!-- Loaded dynamically -->
                </div>
            </div>'''

    new_delivery_pane = '''                <div id="kdsContainer" class="row g-3">
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
            </div>'''

    if old_kds_pane_end in content:
        content = content.replace(old_kds_pane_end, new_delivery_pane, 1)
        print("Added #delivery tab pane HTML!")

    # 5. Add Digital Kitchen Recipe & Allergen Matrix Modal (#chefRecipeModal) before Bootstrap script
    old_modal_anchor = '    <!-- Bootstrap JS & Interactivity Script -->'
    new_recipe_modal = '''    <!-- Digital Kitchen Recipe & Natasha's Law Allergen Matrix Modal -->
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

    <!-- Bootstrap JS & Interactivity Script -->'''

    if old_modal_anchor in content:
        content = content.replace(old_modal_anchor, new_recipe_modal, 1)
        print("Added #chefRecipeModal HTML!")

    # 6. Add JS functions for Heatmap, Chef Recipes, and Delivery Hub
    js_all_three = '''
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
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, js_all_three + "\n" + target_script_end, 1)
        print("Added JS functions for Heatmap, Chef Recipes, and Delivery Hub!")

    # Call loadSalesHeatmap() inside loadVisualFloorplan()
    old_init_fp = "loadVisualFloorplan();"
    new_init_fp = "loadVisualFloorplan();\n        loadSalesHeatmap();"
    if old_init_fp in content:
        content = content.replace(old_init_fp, new_init_fp, 1)
        print("Hooked loadSalesHeatmap() into initial load!")

    # 7. Add backend routes GET /api/analytics/heatmap and GET /api/kds/recipes
    backend_new_routes = '''
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
'''

    main_block = 'if __name__ == "__main__":'
    if main_block in content:
        content = content.replace(main_block, backend_new_routes + "\n\n" + main_block, 1)
        print("Added backend routes GET /api/analytics/heatmap and GET /api/kds/recipes!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
