import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Import pub_features_service
    old_import = "from src.modules.money_margins import money_margins_service"
    new_import = "from src.modules.money_margins import money_margins_service\nfrom src.modules.pub_features import pub_features_service"
    if old_import in content and "pub_features_service" not in content:
        content = content.replace(old_import, new_import, 1)
        print("Imported pub_features_service in src/app.py!")

    # 2. Add British Pub Guest Quick Bar (1-Tap 'Same Again!' Round, Beer Garden Zone Selector & Sunday Roast Live Counter) in #guestViewSection
    old_concierge_bar = '''        <!-- 1-Tap Table Concierge & Service Call Bell Bar -->
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

    new_concierge_bar = '''        <!-- 1-Tap Table Concierge & Service Call Bell Bar -->
        <div class="p-2 px-3 bg-white rounded-3 border shadow-sm mb-2 d-flex flex-wrap align-items-center justify-content-between gap-2">
            <span class="small fw-bold text-muted"><i class="fa-solid fa-bell-concierge text-warning me-1"></i>Table Concierge:</span>
            <div class="d-flex flex-wrap gap-1">
                <button class="btn btn-xs btn-outline-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('WATER', '💧 Free Tap Water')">💧 Tap Water</button>
                <button class="btn btn-xs btn-outline-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('CUTLERY', '🍴 Extra Napkins & Cutlery')">🍴 Cutlery/Napkins</button>
                <button class="btn btn-xs btn-outline-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('CONDIMENTS', '🌶️ Condiments & Sauces')">🌶️ Sauces</button>
                <button class="btn btn-xs btn-outline-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('BILL', '🧾 Request Physical Bill')">🧾 Physical Bill</button>
                <button class="btn btn-xs btn-warning text-dark rounded-pill px-2 py-1 small fw-bold" onclick="requestTableService('SERVER', '🙋 Call Server to Table')">🙋 Call Server</button>
            </div>
        </div>

        <!-- British Pub Bar Tab, 1-Tap 'Same Again!', Sunday Roast Counter & Beer Garden Zone Strip -->
        <div class="p-2 px-3 bg-dark text-white rounded-3 shadow-sm mb-3 d-flex flex-wrap align-items-center justify-content-between gap-2 border border-warning">
            <div class="d-flex align-items-center flex-wrap gap-2 small">
                <span class="badge bg-warning text-dark fw-bold"><i class="fa-solid fa-beer-mug-empty me-1"></i>PUB BAR TAB</span>
                <span id="guestBarTabStatusText" class="text-light">Tab <strong>#TAB-101</strong> (Pre-Auth £75) • Bal: <strong class="text-warning">£18.60</strong></span>
                <span class="badge bg-success" id="guestGardenWeatherBadge"><i class="fa-solid fa-sun me-1"></i>🌳 Beer Garden Open (19.5°C)</span>
            </div>
            <div class="d-flex flex-wrap align-items-center gap-1">
                <select id="guestGardenZoneSelect" class="form-select form-select-sm w-auto py-0 small fw-bold bg-secondary text-white border-0" style="height: 28px;">
                    <option value="Indoor Table">🏠 Indoor Table</option>
                    <option value="Garden Bench #G1">🌳 Garden Bench #G1</option>
                    <option value="Garden Bench #G2">🌳 Garden Bench #G2</option>
                    <option value="Wisteria Pergola #G3">🌿 Pergola #G3 (Heated)</option>
                    <option value="Heated Cabana Pod #P1">🔥 Cabana Pod #P1</option>
                </select>
                <button class="btn btn-xs btn-warning text-dark rounded-pill px-3 py-1 small fw-bold shadow-sm" onclick="guestSameAgainRound()">
                    <i class="fa-solid fa-rotate-right me-1"></i>🍺 Same Again! (1-Tap Round)
                </button>
            </div>
        </div>'''

    if old_concierge_bar in content:
        content = content.replace(old_concierge_bar, new_concierge_bar, 1)
        print("Added British Pub Bar Tab, 1-Tap 'Same Again!' & Beer Garden Zone Selector to Guest View!")

    # 3. Add 🍺 Pub & Cellar tab pill to #staffTabs
    old_margins_tab = '''            <li class="nav-item">
                <button class="nav-link" id="margins-tab" data-bs-toggle="tab" data-bs-target="#margins" type="button" onclick="loadMoneyAndMarginsHub()"><i class="fa-solid fa-sterling-sign me-1 text-success"></i> 💷 Money & Margins</button>
            </li>'''

    new_margins_tab = '''            <li class="nav-item">
                <button class="nav-link" id="pubhub-tab" data-bs-toggle="tab" data-bs-target="#pubhub" type="button" onclick="loadPubAndCellarHub()"><i class="fa-solid fa-beer-mug-empty me-1 text-warning"></i> 🍺 Pub & Cellar</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="margins-tab" data-bs-toggle="tab" data-bs-target="#margins" type="button" onclick="loadMoneyAndMarginsHub()"><i class="fa-solid fa-sterling-sign me-1 text-success"></i> 💷 Money & Margins</button>
            </li>'''

    if old_margins_tab in content:
        content = content.replace(old_margins_tab, new_margins_tab, 1)
        print("Added 🍺 Pub & Cellar tab pill to #staffTabs!")

    # 4. Add #pubhub Tab Pane right before #margins tab pane
    target_margins_pane = '''            <!-- TAB 11A: 💷 Money & Margins Hub'''

    pubhub_pane = '''            <!-- TAB 11-PUB: 🍺 British Pub, Bar Tabs, Cellar Kegs, Sunday Roast & Beer Garden Hub -->
            <div class="tab-pane fade" id="pubhub" role="tabpanel">
                <!-- Top British Pub Banner -->
                <div class="card card-custom p-4 bg-dark text-white shadow-sm mb-4 border-start border-5 border-warning">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                        <div>
                            <div class="d-flex flex-wrap gap-2 mb-2">
                                <span class="badge bg-warning text-dark fw-bold"><i class="fa-solid fa-credit-card me-1"></i>PRE-AUTH BAR TABS & 1-TAP 'SAME AGAIN'</span>
                                <span class="badge bg-info text-dark fw-bold"><i class="fa-solid fa- barrel-water me-1"></i>SMART CELLAR & 7-DAY LINE CLEAN LOGS</span>
                                <span class="badge bg-danger fw-bold"><i class="fa-solid fa-utensils me-1"></i>SUNDAY ROAST LIVE COUNTER</span>
                                <span class="badge bg-success fw-bold"><i class="fa-solid fa-cloud-sun me-1"></i>WEATHER-TRIGGERED BEER GARDEN</span>
                            </div>
                            <h4 class="fw-bold mb-1 text-white">🍺 British Pub, Cellar Keg Management & Beer Garden Command Center</h4>
                            <small class="text-light opacity-75">Card Pre-Authorised Bar Tabs • 1-Tap Round Repeats • 88-Pint Keg Yield & Line Cleaning • Sunday Roast & Pub Quiz • Beer Garden Zones</small>
                        </div>
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <!-- Pillar 1: Bar Tabs (Card Pre-Authorisation, Round Ordering & 'Same Again' in 1 Tap) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-warning">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-beer-mug-empty text-warning me-2"></i>1. Pre-Authorised Bar Tabs & 'Same Again!'</h5>
                                <span class="badge bg-dark text-warning">Zero Walk-Out Risk</span>
                            </div>
                            <small class="text-muted d-block mb-3">Open card pre-authorised bar tabs (£50–£100 hold) and repeat drink rounds in one tap.</small>

                            <form onsubmit="openNewPubBarTab(event)" class="row g-2 mb-3">
                                <div class="col-sm-5">
                                    <input type="text" id="newTabGuestName" class="form-control form-control-sm" placeholder="Guest / Group Name" required>
                                </div>
                                <div class="col-sm-3">
                                    <input type="text" id="newTabZone" class="form-control form-control-sm" placeholder="Table / Garden #G1" value="Garden #G1" required>
                                </div>
                                <div class="col-sm-4">
                                    <button type="submit" class="btn btn-sm btn-dark text-warning w-100 fw-bold"><i class="fa-solid fa-lock me-1"></i> Pre-Auth £50 Tab</button>
                                </div>
                            </form>

                            <div id="pubBarTabsContainer" class="vstack gap-2">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>

                    <!-- Pillar 2: Cellar & Keg Management (Keg Tracking, Line-Cleaning Logs, Pour-Cost & Wastage) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-info">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-gauge-high text-info me-2"></i>2. Smart Cellar, Kegs & Line-Cleaning Log</h5>
                                <span class="badge bg-info text-dark" id="cellarYieldBadge">Yield: 96.8% • Temp: 11.4°C</span>
                            </div>
                            <small class="text-muted d-block mb-3">Live 88-pint keg levels, pour-cost %, drip-tray ullage wastage, and 7-day caustic beer line cleaning logs.</small>

                            <div id="cellarKegsContainer" class="vstack gap-2">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row g-4">
                    <!-- Pillar 3: Pub Extras (Sunday Roast Pre-Orders with Sold-Out Counters, Quiz Ticketing & Happy Hour) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-danger">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-drumstick-bite text-danger me-2"></i>3. Sunday Roast Pre-Orders, Quiz & Happy Hour</h5>
                                <span class="badge bg-danger">Live Sold-Out Counters</span>
                            </div>
                            <small class="text-muted d-block mb-2">Track live Sunday Roast joint allocations, book Wednesday Pub Quiz teams, and schedule Happy Hour.</small>

                            <div id="sundayRoastCounterBox" class="vstack gap-2 mb-3">
                                <!-- Populated dynamically -->
                            </div>

                            <div class="p-3 bg-light rounded-3 border">
                                <h6 class="fw-bold small text-uppercase text-dark mb-2"><i class="fa-solid fa-trophy text-warning me-1"></i>Pub Quiz & Live Sport Event Ticketing</h6>
                                <form onsubmit="bookPubQuizTeamForm(event)" class="row g-2 mb-2">
                                    <div class="col-sm-5">
                                        <input type="text" id="quizTeamNameInput" class="form-control form-control-sm" placeholder="Quiz Team Name" required>
                                    </div>
                                    <div class="col-sm-3">
                                        <input type="number" id="quizTeamSizeInput" class="form-control form-control-sm" value="4" min="1" max="6" required>
                                    </div>
                                    <div class="col-sm-4">
                                        <button type="submit" class="btn btn-sm btn-primary w-100 fw-bold">Book Quiz (£3/pp)</button>
                                    </div>
                                </form>
                                <div id="pubQuizEventsBox" class="small"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Pillar 4: Beer Garden Zones & Weather-Triggered 'Garden Open' Toggle -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-success">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-umbrella-beach text-success me-2"></i>4. Beer Garden Zones & Weather Auto-Toggle</h5>
                                <span class="badge bg-success" id="staffGardenOpenBadge">GARDEN OPEN</span>
                            </div>
                            <small class="text-muted d-block mb-3">Order to numbered outdoor benches (#G1–#G3) and heated pergola pods (#P1–#P2) with weather-triggered auto-close.</small>

                            <div class="d-flex flex-wrap gap-2 mb-3">
                                <button class="btn btn-sm btn-success fw-bold" onclick="triggerBeerGardenWeather('SUNNY')">
                                    <i class="fa-solid fa-sun me-1"></i>☀️ 21°C Sunny (Open All Garden Zones)
                                </button>
                                <button class="btn btn-sm btn-secondary fw-bold" onclick="triggerBeerGardenWeather('RAIN_STORM')">
                                    <i class="fa-solid fa-cloud-showers-heavy me-1"></i>🌧️ 11°C Rain Alert (Heated Pods Only)
                                </button>
                            </div>

                            <div id="beerGardenWeatherBanner" class="p-2 px-3 rounded-3 bg-success bg-opacity-10 border border-success small fw-bold text-dark mb-3"></div>
                            <div id="beerGardenZonesGrid" class="row g-2">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

'''

    if target_margins_pane in content and 'id="pubhub"' not in content:
        content = content.replace(target_margins_pane, pubhub_pane + target_margins_pane, 1)
        print("Added #pubhub tab pane to Staff Workspace!")

    # 5. Add JS functions for British Pub & Cellar Hub before </script>\n</body>\n</html>"""
    js_pub_features = '''
        // --- 9. 🍺 British Pub, Bar Tabs, Cellar Kegs, Sunday Roast & Beer Garden Functions ---
        async function guestSameAgainRound() {
            await repeatBarTabRound('TAB-101');
        }

        async function loadPubAndCellarHub() {
            await loadPubBarTabs();
            await loadCellarKegsStatus();
            await loadPubExtrasAndRoasts();
            await loadBeerGardenZones();
        }

        async function loadPubBarTabs() {
            const box = document.getElementById('pubBarTabsContainer');
            const res = await fetch('/api/pub/tabs');
            const data = await res.json();
            const tabs = data.tabs || [];

            if(tabs.length > 0) {
                const t0 = tabs[0];
                const guestStatus = document.getElementById('guestBarTabStatusText');
                if(guestStatus) {
                    guestStatus.innerHTML = `Tab <strong>#${t0.tab_id}</strong> (Pre-Auth £${t0.pre_auth_limit_gbp}) • Round #${t0.rounds.length} • Bal: <strong class="text-warning">£${t0.current_balance_gbp.toFixed(2)}</strong>`;
                }
            }

            if(!box) return;
            box.innerHTML = tabs.map(t => `
                <div class="p-3 rounded-3 border bg-light d-flex justify-content-between align-items-center small">
                    <div>
                        <span class="badge bg-dark text-warning me-1">${t.tab_id}</span>
                        <strong class="text-dark">${t.customer_name}</strong>
                        <span class="badge bg-secondary ms-1">${t.table_or_zone}</span>
                        <small class="text-muted d-block">Pre-Auth Hold: £${t.pre_auth_limit_gbp.toFixed(2)} (${t.pre_auth_token}) • <strong>${t.rounds.length} Rounds Ordered</strong></small>
                    </div>
                    <div class="text-end">
                        <div class="fs-6 fw-bold text-success mb-1">£${t.current_balance_gbp.toFixed(2)}</div>
                        <button class="btn btn-xs btn-warning text-dark fw-bold py-1 px-2" onclick="repeatBarTabRound('${t.tab_id}')">
                            <i class="fa-solid fa-rotate-right me-1"></i>🍺 Same Again!
                        </button>
                    </div>
                </div>
            `).join('');
        }

        async function openNewPubBarTab(e) {
            if(e) e.preventDefault();
            const name = document.getElementById('newTabGuestName').value.trim();
            const zone = document.getElementById('newTabZone').value.trim();
            const res = await fetch('/api/pub/tabs/open', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ customer_name: name, table_or_zone: zone, pre_auth_limit_gbp: 50.0 })
            });
            if(res.ok) {
                document.getElementById('newTabGuestName').value = '';
                loadPubBarTabs();
            }
        }

        async function repeatBarTabRound(tabId) {
            const res = await fetch(`/api/pub/tabs/${tabId}/same-again`, { method: 'POST' });
            const data = await res.json();
            if(res.ok) {
                playOrderChime();
                alert(`🍺 [Same Again! — Round #${data.repeated_round_number}] Added £${data.round_total_gbp.toFixed(2)} to ${data.customer_name} (${data.tab_id}). New Tab Balance: £${data.new_tab_balance_gbp.toFixed(2)}!`);
                loadPubBarTabs();
                loadCellarKegsStatus();
            }
        }

        async function loadCellarKegsStatus() {
            const box = document.getElementById('cellarKegsContainer');
            if(!box) return;
            const res = await fetch('/api/pub/cellar');
            const data = await res.json();
            const badge = document.getElementById('cellarYieldBadge');
            if(badge) {
                badge.innerText = `Yield: ${data.overall_keg_yield_pct}% • Pour Cost: ${data.average_draught_pour_cost_pct}% • Ullage Loss: £${data.total_ullage_lost_revenue_gbp.toFixed(2)}`;
            }
            box.innerHTML = (data.taps || []).map(k => {
                const pctLeft = Math.round((k.pints_remaining / k.total_pints_capacity) * 100);
                const needsClean = k.line_clean_status !== 'CLEAN_COMPLIANT';
                return `
                    <div class="p-2 px-3 rounded border bg-light small">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <div>
                                <span class="badge bg-dark me-1">Tap #${k.tap_number}</span>
                                <strong class="text-dark">${k.beer_name}</strong>
                            </div>
                            <span class="badge ${needsClean ? 'bg-danger' : 'bg-success'}">${k.line_clean_status}</span>
                        </div>
                        <div class="progress mb-1" style="height: 8px;">
                            <div class="progress-bar ${pctLeft <= 20 ? 'bg-danger' : 'bg-warning'}" style="width: ${pctLeft}%"></div>
                        </div>
                        <div class="d-flex justify-content-between align-items-center text-muted">
                            <span><strong>${k.pints_remaining}/${k.total_pints_capacity} pints left</strong> • Yield ${k.yield_efficiency_pct}% (Ullage: ${k.pints_ullage_waste}pt)</span>
                            <button class="btn btn-xs btn-outline-dark py-0 px-2 small fw-bold" onclick="cleanBeerTapLine(${k.tap_number})">🧼 Log Line Clean</button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function cleanBeerTapLine(tapNum) {
            await fetch(`/api/pub/cellar/clean-line/${tapNum}`, { method: 'POST' });
            loadCellarKegsStatus();
        }

        async function loadPubExtrasAndRoasts() {
            const rBox = document.getElementById('sundayRoastCounterBox');
            const qBox = document.getElementById('pubQuizEventsBox');
            if(!rBox) return;
            const res = await fetch('/api/pub/extras');
            const data = await res.json();

            rBox.innerHTML = (data.sunday_roasts || []).map(r => `
                <div class="p-2 px-3 rounded border bg-light d-flex justify-content-between align-items-center small">
                    <div>
                        <strong class="text-dark">${r.name}</strong>
                        <small class="text-muted d-block">£${r.price_gbp.toFixed(2)} • Allocated: ${r.initial_allocated}</small>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge ${r.sold_out ? 'bg-danger' : 'bg-warning text-dark'}">${r.sold_out ? 'SOLD OUT' : r.remaining_portions + ' Left'}</span>
                        <button class="btn btn-xs btn-dark text-warning fw-bold py-1 px-2" ${r.sold_out ? 'disabled' : ''} onclick="preorderSundayRoast('${r.roast_id}')">+ Pre-Order</button>
                    </div>
                </div>
            `).join('');

            if(qBox) {
                qBox.innerHTML = (data.quiz_and_events || []).map(ev => `
                    <div class="d-flex justify-content-between align-items-center border-top pt-1 mt-1">
                        <span><strong>${ev.title}</strong> (${ev.schedule})</span>
                        <span class="badge bg-primary">${ev.teams_booked}/${ev.max_teams} Teams Booked</span>
                    </div>
                `).join('');
            }
        }

        async function preorderSundayRoast(roastId) {
            const res = await fetch('/api/pub/roast/preorder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ roast_id: roastId, quantity: 1, guest_name: 'Table #4 Guest' })
            });
            const data = await res.json();
            if(res.ok) {
                alert(`🥩 Pre-ordered ${data.roast_name}! (${data.remaining_portions} portions remaining before sold out).`);
                loadPubExtrasAndRoasts();
            } else {
                alert(data.error || 'Sold out!');
            }
        }

        async function bookPubQuizTeamForm(e) {
            if(e) e.preventDefault();
            const name = document.getElementById('quizTeamNameInput').value.trim();
            const size = parseInt(document.getElementById('quizTeamSizeInput').value || 4);
            const res = await fetch('/api/pub/events/book', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ event_id: 'QUIZ-WED', team_name: name, team_size: size })
            });
            const data = await res.json();
            if(res.ok) {
                alert(`🎟️ Booked Quiz Team '${name}' (Ticket ${data.booking.ticket_ref} — £${data.booking.paid_gbp.toFixed(2)})!`);
                document.getElementById('quizTeamNameInput').value = '';
                loadPubExtrasAndRoasts();
            }
        }

        async function loadBeerGardenZones() {
            const banner = document.getElementById('beerGardenWeatherBanner');
            const grid = document.getElementById('beerGardenZonesGrid');
            const staffBadge = document.getElementById('staffGardenOpenBadge');
            const guestBadge = document.getElementById('guestGardenWeatherBadge');
            const res = await fetch('/api/pub/garden');
            const data = await res.json();

            if(staffBadge) {
                staffBadge.className = data.garden_open ? 'badge bg-success' : 'badge bg-warning text-dark';
                staffBadge.innerText = data.garden_open ? '🌳 GARDEN OPEN' : '🌧️ HEATED PODS ONLY';
            }
            if(guestBadge) {
                guestBadge.className = data.garden_open ? 'badge bg-success' : 'badge bg-warning text-dark';
                guestBadge.innerHTML = data.garden_open
                    ? `<i class="fa-solid fa-sun me-1"></i>🌳 Beer Garden Open (${data.current_weather.temp_c}°C)`
                    : `<i class="fa-solid fa-cloud-rain me-1"></i>🌧️ Garden Rain Alert (Heated Pods Open)`;
            }
            if(banner) banner.innerText = data.current_weather.summary;
            if(!grid) return;

            grid.innerHTML = (data.zones || []).map(z => `
                <div class="col-sm-6">
                    <div class="p-2 px-3 rounded border bg-light d-flex justify-content-between align-items-center small">
                        <div>
                            <strong class="text-dark">${z.name}</strong>
                            <small class="text-muted d-block">Cap: ${z.capacity} • ${z.covered_heated ? '🔥 Covered & Heated' : '☀️ Open Lawn'}</small>
                        </div>
                        <span class="badge ${z.status.startsWith('OPEN') ? 'bg-success' : 'bg-secondary'}">${z.status}</span>
                    </div>
                </div>
            `).join('');
        }

        async function triggerBeerGardenWeather(weatherMode) {
            await fetch('/api/pub/garden/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ simulate_weather: weatherMode })
            });
            loadBeerGardenZones();
        }
    </script>
</body>
</html>"""'''

    target_index_end = '''    </script>
</body>
</html>"""'''

    if target_index_end in content:
        content = content.replace(target_index_end, js_pub_features, 1)
        print("Added JS handlers for British Pub, Bar Tabs, Cellar Kegs, Sunday Roast & Beer Garden!")

    # 6. Add Backend Routes for British Pub Features before if __name__ == "__main__":
    backend_pub_routes = '''

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
'''

    target_main = 'if __name__ == "__main__":'
    if target_main in content:
        content = content.replace(target_main, backend_pub_routes + "\n\n" + target_main, 1)
        print("Added backend routes for all 4 British Pub pillars!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
