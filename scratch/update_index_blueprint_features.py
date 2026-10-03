import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add AI Language Toggle Matrix to Header
    old_header_badges = '<span id="pwaNetworkBadge" class="badge bg-success rounded-pill px-3 py-2 ms-2"><i class="fa-solid fa-wifi me-1"></i> Online</span>'
    new_header_badges = '''<span id="pwaNetworkBadge" class="badge bg-success rounded-pill px-3 py-2 ms-2 me-2"><i class="fa-solid fa-wifi me-1"></i> Online</span>
                    <!-- AI Language Toggle Matrix (Page 6 Blueprint) -->
                    <div class="btn-group btn-group-sm rounded-pill overflow-hidden border border-light" role="group" aria-label="AI Language Matrix">
                        <button type="button" class="btn btn-dark text-white fw-bold px-2" onclick="setAppLanguage('en')" id="langBtn-en" title="English">🇬🇧 EN</button>
                        <button type="button" class="btn btn-outline-light text-white fw-bold px-2" onclick="setAppLanguage('fr')" id="langBtn-fr" title="Français">🇫🇷 FR</button>
                        <button type="button" class="btn btn-outline-light text-white fw-bold px-2" onclick="setAppLanguage('ar')" id="langBtn-ar" title="العربية">🇸🇦 AR</button>
                    </div>'''

    if old_header_badges in content:
        content = content.replace(old_header_badges, new_header_badges)
        print("Added AI Language Toggle Matrix to Header!")
    else:
        print("Could not find old_header_badges in app.py!")

    # 2. Add Visual Floorplan Tab to Staff Workspace Tabs
    old_staff_tabs = '<button class="nav-link active" id="kds-tab" data-bs-toggle="tab" data-bs-target="#kds" type="button" onclick="loadKDS()"><i class="fa-solid fa-fire-burner me-1"></i> Kitchen KDS</button>'
    new_staff_tabs = '''<button class="nav-link active" id="floorplan-tab" data-bs-toggle="tab" data-bs-target="#floorplan" type="button" onclick="loadVisualFloorplan()"><i class="fa-solid fa-map-location-dot me-1"></i> Visual Floor Plan</button>
            <li class="nav-item">
                <button class="nav-link" id="kds-tab" data-bs-toggle="tab" data-bs-target="#kds" type="button" onclick="loadKDS()"><i class="fa-solid fa-fire-burner me-1"></i> Kitchen KDS</button>
            </li>'''

    if old_staff_tabs in content:
        content = content.replace(old_staff_tabs, new_staff_tabs)
        print("Added Visual Floorplan tab button to Staff Workspace!")
    else:
        print("Could not find old_staff_tabs in app.py!")

    # 3. Add Visual Floorplan Content Tab Pane
    old_kds_pane = '<!-- TAB 1: KDS with Station Routing & Sound Generator -->\n            <div class="tab-pane fade show active" id="kds" role="tabpanel">'
    new_floorplan_pane = '''<!-- TAB 0: Visual Blueprint Floor Plan Layout (Page 1 Blueprint) -->
            <div class="tab-pane fade show active" id="floorplan" role="tabpanel">
                <div class="card card-custom p-4 bg-dark text-white border-0 shadow-lg mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <span class="badge bg-info text-dark fw-bold mb-1"><i class="fa-solid fa-layer-group me-1"></i> BLUEPRINT ENGINE</span>
                            <h4 class="fw-bold mb-0 text-white"><i class="fa-solid fa-map-location-dot me-2 text-warning"></i>Live Interactive Floor Plan Map</h4>
                            <small class="text-light opacity-75">Real-time table turnover speed, occupancy status, and capacity tracking</small>
                        </div>
                        <div class="d-flex gap-3 text-end">
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
                    </div>

                    <div class="d-flex justify-content-between align-items-center small text-light opacity-75">
                        <div class="d-flex gap-3">
                            <span><i class="fa-solid fa-circle text-success me-1"></i> Available</span>
                            <span><i class="fa-solid fa-circle text-danger me-1"></i> Occupied</span>
                            <span><i class="fa-solid fa-circle text-warning me-1"></i> Reserved</span>
                        </div>
                        <span><i class="fa-solid fa-bolt text-info me-1"></i> Zero Hardware Lock-In Engine</span>
                    </div>
                </div>
            </div>

            <!-- TAB 1: KDS with Station Routing & Sound Generator -->
            <div class="tab-pane fade" id="kds" role="tabpanel">'''

    if old_kds_pane in content:
        content = content.replace(old_kds_pane, new_floorplan_pane)
        print("Added Visual Floorplan Content Pane HTML!")
    else:
        print("Could not find old_kds_pane in app.py!")

    # 4. Add JS functions for language matrix, visual floorplan, and smart upsell
    blueprint_js_code = '''
        // --- Blueprint Features: AI Language Toggle Matrix & Visual Floor Plan Map ---
        function setAppLanguage(lang) {
            currentLang = lang;
            ['en', 'fr', 'ar'].forEach(l => {
                const btn = document.getElementById(`langBtn-${l}`);
                if(btn) {
                    if(l === lang) {
                        btn.className = 'btn btn-dark text-white fw-bold px-2';
                    } else {
                        btn.className = 'btn btn-outline-light text-white fw-bold px-2';
                    }
                }
            });

            // Adjust document direction for Arabic
            if(lang === 'ar') {
                document.body.setAttribute('dir', 'rtl');
            } else {
                document.body.removeAttribute('dir');
            }

            loadMenu();
        }

        async function loadVisualFloorplan() {
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
        }

        // --- Automated Smart Upsell Recommendation Engine (Page 6 Blueprint) ---
        function triggerSmartUpsell(itemId, itemName) {
            const upsellItem = { id: 'item-3', name: 'Craft IPA Pint', price: 6.20 };
            const modalHtml = `
                <div class="modal fade" id="smartUpsellModal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content border-0 shadow-lg">
                            <div class="modal-header bg-gradient text-white" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);">
                                <h5 class="modal-title fw-bold"><i class="fa-solid fa-bolt text-warning me-2"></i>Automated Smart Upsell</h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body p-4 text-center">
                                <h6 class="fw-bold text-dark mb-2">Great choice with ${itemName}!</h6>
                                <p class="small text-muted mb-3">Guests who ordered this also paired it with our fresh Craft IPA Pint!</p>
                                <div class="p-3 bg-light rounded-3 border d-flex align-items-center justify-content-between mb-3">
                                    <div class="d-flex align-items-center gap-2">
                                        <i class="fa-solid fa-beer-mug-empty text-warning fs-3"></i>
                                        <div class="text-start">
                                            <strong class="d-block text-dark">${upsellItem.name}</strong>
                                            <small class="text-muted">Perfect pairing drink</small>
                                        </div>
                                    </div>
                                    <strong class="text-success fs-5">+£${upsellItem.price.toFixed(2)}</strong>
                                </div>
                                <button class="btn btn-success w-100 fw-bold py-2 mb-2" onclick="addUpsellToCart('${upsellItem.id}', '${upsellItem.name}', ${upsellItem.price})"><i class="fa-solid fa-plus me-1"></i> Add Pair to Order</button>
                                <button class="btn btn-link text-muted btn-sm text-decoration-none" data-bs-dismiss="modal">No thanks, continue</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            let existing = document.getElementById('smartUpsellModal');
            if(existing) existing.remove();

            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('smartUpsellModal'));
            modal.show();
        }

        function addUpsellToCart(id, name, price) {
            addToCart(id);
            const modalEl = document.getElementById('smartUpsellModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if(modal) modal.hide();
        }
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, blueprint_js_code + "\n" + target_script_end)
        print("Added Blueprint JS functions before script end!")
    else:
        print("Could not find target_script_end in app.py!")

    # Add loadVisualFloorplan call to initial load
    target_init = "loadBrandConfig();"
    if target_init in content:
        content = content.replace(target_init, "loadBrandConfig();\n        loadVisualFloorplan();")
        print("Added loadVisualFloorplan() to initial load!")
    else:
        print("Could not find loadBrandConfig in app.py!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
