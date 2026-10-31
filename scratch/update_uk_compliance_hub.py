import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Import uk_compliance_service
    old_import = "from src.modules.payments import payments_service"
    new_import = "from src.modules.payments import payments_service\nfrom src.modules.uk_compliance import uk_compliance_service"
    if old_import in content and "uk_compliance_service" not in content:
        content = content.replace(old_import, new_import, 1)
        print("Imported uk_compliance_service in src/app.py!")

    # 2. Add HMRC VAT 709/1 Dining Mode Selector & Challenge 25 Alcohol Alert Banner into Guest Cart
    old_guest_cart_promo = '''                    <div class="mb-3">
                        <input type="text" id="promoInput" class="form-control form-control-sm" placeholder="Promo code (e.g. WELCOME10)">
                    </div>

                    <div class="d-flex justify-content-between fw-bold mb-3 fs-5">
                        <span>Total:</span>
                        <span id="cartTotal" class="text-success">£0.00</span>
                    </div>'''

    new_guest_cart_promo = '''                    <!-- UK Challenge 25 Alcohol Age Verification Alert (Licensing Act 2003) -->
                    <div id="challenge25CartBanner" class="p-2 mb-3 rounded-3 bg-danger bg-opacity-10 border border-danger small d-none">
                        <strong class="text-danger d-block"><i class="fa-solid fa-id-card me-1"></i>🔞 UK Challenge 25 Policy</strong>
                        <span class="text-dark">Alcohol item detected. Staff will verify photographic ID (Passport / UK Driving Licence / PASS 18+) at your table before serving.</span>
                    </div>

                    <!-- HMRC VAT Notice 709/1 Dining Mode Selector (Eat-In vs Hot vs Cold Takeaway) -->
                    <div class="mb-3 p-2 bg-light rounded-3 border">
                        <label class="small fw-bold text-muted d-block mb-1"><i class="fa-solid fa-scale-balanced text-primary me-1"></i>UK VAT Mode (HMRC 709/1):</label>
                        <select id="guestVatDiningMode" class="form-select form-select-sm fw-bold mb-1" onchange="renderCart()">
                            <option value="EAT_IN">🍽️ Eat-In (20% Standard UK VAT)</option>
                            <option value="HOT_TAKEAWAY">🔥 Hot Takeaway (20% Standard UK VAT)</option>
                            <option value="COLD_TAKEAWAY">❄️ Cold Takeaway Grab & Go (0% Zero-Rated Food)</option>
                        </select>
                        <div id="guestVatBreakdownLine" class="small text-muted d-flex justify-content-between">
                            <span>Net: £0.00</span>
                            <span>UK VAT: £0.00</span>
                        </div>
                    </div>

                    <div class="mb-3">
                        <input type="text" id="promoInput" class="form-control form-control-sm" placeholder="Promo code (e.g. WELCOME10)">
                    </div>

                    <div class="d-flex justify-content-between fw-bold mb-3 fs-5">
                        <span>Total:</span>
                        <span id="cartTotal" class="text-success">£0.00</span>
                    </div>'''

    if old_guest_cart_promo in content:
        content = content.replace(old_guest_cart_promo, new_guest_cart_promo, 1)
        print("Added Challenge 25 Banner & HMRC VAT 709/1 Mode Selector to Guest Cart!")

    # 3. Add UK Compliance & EHO tab button to #staffTabs
    old_strategy_tab_btn = '''            <li class="nav-item">
                <button class="nav-link" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" type="button"><i class="fa-solid fa-file-contract me-1"></i> Strategy</button>
            </li>'''

    new_strategy_tab_btn = '''            <li class="nav-item">
                <button class="nav-link" id="ukcompliance-tab" data-bs-toggle="tab" data-bs-target="#ukcompliance" type="button" onclick="loadUkComplianceHub()"><i class="fa-solid fa-shield-halved me-1 text-danger"></i> 🇬🇧 UK Compliance & EHO</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" type="button"><i class="fa-solid fa-file-contract me-1"></i> Strategy</button>
            </li>'''

    if old_strategy_tab_btn in content:
        content = content.replace(old_strategy_tab_btn, new_strategy_tab_btn, 1)
        print("Added 🇬🇧 UK Compliance & EHO tab button to #staffTabs!")

    # 4. Add #ukcompliance Tab Pane right before #strategy tab pane
    target_strategy_pane = '''            <!-- TAB 12: The Waiter Business Blueprint (Pages 2, 3, 10 & 11) -->'''

    uk_compliance_pane = '''            <!-- TAB 11B: 🇬🇧 UK Statutory Compliance, Natasha's Law, Tips Act 2024, Challenge 25, EHO Food Safety & GDPR Hub -->
            <div class="tab-pane fade" id="ukcompliance" role="tabpanel">
                <!-- Top UK Sovereign Cloud, GDPR & Cyber Essentials Banner -->
                <div class="card card-custom p-4 bg-dark text-white shadow-sm mb-4 border-start border-5 border-info">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                        <div>
                            <div class="d-flex flex-wrap gap-2 mb-2">
                                <span class="badge bg-info text-dark fw-bold"><i class="fa-solid fa-server me-1"></i>UK LONDON REGION (eu-west-2)</span>
                                <span class="badge bg-success fw-bold"><i class="fa-solid fa-lock me-1"></i>NCSC CYBER ESSENTIALS</span>
                                <span class="badge bg-warning text-dark fw-bold"><i class="fa-solid fa-user-Halved me-1"></i>UK GDPR & DPA 2018</span>
                                <span class="badge bg-primary fw-bold"><i class="fa-solid fa-star me-1"></i>FSA 5-STAR EHO READY</span>
                            </div>
                            <h4 class="fw-bold mb-1 text-white">🇬🇧 UK Statutory Hospitality Compliance & Environmental Health (EHO) Hub</h4>
                            <small class="text-light opacity-75">Natasha's Law (PPDS) • Employment (Allocation of Tips) Act Oct 2024 • Challenge 25 • FSA SFBB / HACCP • HMRC VAT 709/1</small>
                        </div>
                        <a href="/api/uk-compliance/eho-report/pdf" target="_blank" class="btn btn-warning text-dark fw-bold px-3 py-2 shadow">
                            <i class="fa-solid fa-file-shield me-1"></i> Export EHO & Compliance Audit PDF
                        </a>
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <!-- Pillar 1: Natasha's Law (PPDS) Ingredient-to-14-Allergen Builder & Label Printer -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-warning">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-tag text-warning me-2"></i>1. Natasha's Law (PPDS) Label Engine</h5>
                                <span class="badge bg-dark text-warning">14 UK FSA Allergens</span>
                            </div>
                            <small class="text-muted d-block mb-3">Build dishes from raw ingredients, auto-tag the 14 UK allergens in <strong>BOLD CAPITALS</strong>, and print PPDS grab-and-go labels.</small>

                            <div class="row g-2 mb-3">
                                <div class="col-sm-5">
                                    <select id="ppdsDishSelect" class="form-select form-select-sm fw-bold" onchange="previewNatashasLawLabel()">
                                        <option value="item-1">Brixham Cod Fish & Chips</option>
                                        <option value="item-2">British Wagyu Beef Burger</option>
                                        <option value="item-4">Truffle & Parmesan Fries</option>
                                        <option value="item-5">Sticky Toffee Pudding Pot</option>
                                    </select>
                                </div>
                                <div class="col-sm-7">
                                    <div class="input-group input-group-sm">
                                        <input type="text" id="ppdsCustomIngInput" class="form-control" placeholder="Or custom ingredients (e.g. Wheat Flour, Milk, Egg, Mustard)">
                                        <button class="btn btn-dark fw-bold" onclick="buildCustomPpdsLabel()">Auto-Tag</button>
                                    </div>
                                </div>
                            </div>

                            <!-- Printable PPDS Grab-and-Go Sticker Preview -->
                            <div id="ppdsLabelPreviewBox" class="p-3 rounded-3 border border-2 border-dark bg-light small mb-3" style="font-family: 'Segoe UI', sans-serif;">
                                <!-- Populated dynamically -->
                            </div>
                            <button class="btn btn-sm btn-outline-dark fw-bold w-100" onclick="printPpdsGrabAndGoLabel()">
                                <i class="fa-solid fa-print me-1"></i> Print Compliant PPDS Grab-and-Go Label
                            </button>
                        </div>
                    </div>

                    <!-- Pillar 2: Employment (Allocation of Tips) Act 2023 (Effective Oct 2024) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-success">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-hand-holding-dollar text-success me-2"></i>2. Employment (Allocation of Tips) Act 2024</h5>
                                <span class="badge bg-success">100% Pass-Through (0% Ded.)</span>
                            </div>
                            <div id="tipsActPolicyBox" class="p-2 px-3 bg-success bg-opacity-10 border border-success rounded-3 small mb-3">
                                <!-- Written policy summary -->
                            </div>
                            <form onsubmit="recordUkTipPayout(event)" class="row g-2 mb-3">
                                <div class="col-sm-4">
                                    <input type="text" id="tipStaffName" class="form-control form-control-sm" placeholder="Staff Name" required>
                                </div>
                                <div class="col-sm-3">
                                    <input type="text" id="tipStaffRole" class="form-control form-control-sm" placeholder="Role (e.g. FOH)" required>
                                </div>
                                <div class="col-sm-2">
                                    <input type="number" id="tipStaffHours" class="form-control form-control-sm" placeholder="Hrs" value="38" required>
                                </div>
                                <div class="col-sm-3">
                                    <button type="submit" class="btn btn-sm btn-success w-100 fw-bold">+ Log Payout</button>
                                </div>
                            </form>
                            <div id="tipsActPayoutLogsContainer" class="table-responsive" style="max-height: 175px; overflow-y: auto;">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <!-- Pillar 3: Challenge 25 Age Verification & Refusal Register (Licensing Act 2003) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-danger">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-id-card-clip text-danger me-2"></i>3. Challenge 25 Alcohol Age Verification</h5>
                                <span class="badge bg-danger">Licensing Act 2003</span>
                            </div>
                            <small class="text-muted d-block mb-3">Confirm photographic ID (Passport, Driving Licence, PASS) before serving alcohol orders to protect the Premises Licence.</small>

                            <form onsubmit="submitChallenge25Check(event)" class="row g-2 mb-3">
                                <div class="col-sm-3">
                                    <input type="number" id="ch25TableNum" class="form-control form-control-sm" placeholder="Table #" value="4" min="1" required>
                                </div>
                                <div class="col-sm-4">
                                    <select id="ch25IdType" class="form-select form-select-sm">
                                        <option value="UK Photocard Driving Licence">UK Driving Licence</option>
                                        <option value="UK / Biometric Passport">Passport</option>
                                        <option value="PASS Hologram Card">PASS Card (18+)</option>
                                        <option value="NO VALID ID — SALE REFUSED">No ID (Refuse Sale)</option>
                                    </select>
                                </div>
                                <div class="col-sm-5 d-flex gap-1">
                                    <button type="submit" class="btn btn-sm btn-success flex-grow-1 fw-bold" onclick="document.getElementById('ch25Decision').value='APPROVED'">✓ Confirm 18+</button>
                                    <button type="submit" class="btn btn-sm btn-danger fw-bold" onclick="document.getElementById('ch25Decision').value='REFUSED'">✕ Refuse</button>
                                    <input type="hidden" id="ch25Decision" value="APPROVED">
                                </div>
                            </form>
                            <div id="challenge25LogsContainer" class="vstack gap-2" style="max-height: 180px; overflow-y: auto;">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>

                    <!-- Pillar 4: FSA Food Safety Logs (Digital Fridge Temps, Cleaning & HACCP Checklists) -->
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100 border-top border-4 border-primary">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-temperature-low text-primary me-2"></i>4. FSA Food Safety, Fridge Temps & HACCP</h5>
                                <span class="badge bg-primary" id="ehoReadyStatusBadge">EHO Inspection Ready</span>
                            </div>
                            <form onsubmit="submitFridgeTempLog(event)" class="row g-2 mb-3">
                                <div class="col-sm-5">
                                    <select id="safetyUnitName" class="form-select form-select-sm">
                                        <option value="Walk-In Cold Room #1|CHILLER">Walk-In Chiller #1 (0-5°C)</option>
                                        <option value="Grab & Go Display Fridge #2|CHILLER">Display Fridge #2 (0-5°C)</option>
                                        <option value="Deep Freeze Chest #1|FREEZER">Freezer Chest #1 (≤-18°C)</option>
                                        <option value="Kitchen Hot Pass Hold|HOT_HOLD">Hot Hold Pass (≥63°C)</option>
                                    </select>
                                </div>
                                <div class="col-sm-3">
                                    <div class="input-group input-group-sm">
                                        <input type="number" step="0.1" id="safetyTempVal" class="form-control fw-bold" value="3.1" required>
                                        <span class="input-group-text">°C</span>
                                    </div>
                                </div>
                                <div class="col-sm-4">
                                    <button type="submit" class="btn btn-sm btn-primary w-100 fw-bold">+ Log Probe Temp</button>
                                </div>
                            </form>
                            <div id="fridgeTempLogsContainer" class="mb-2" style="max-height: 110px; overflow-y: auto;"></div>
                            <h6 class="small fw-bold text-uppercase text-muted mb-1">Daily SFBB Opening / Closing & CCP Checklist:</h6>
                            <div id="haccpChecklistContainer" class="vstack gap-1"></div>
                        </div>
                    </div>
                </div>

                <!-- Pillar 5 & Pillar 6: HMRC VAT Notice 709/1 Matrix & UK GDPR / Cyber Essentials Security -->
                <div class="row g-4">
                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-1 text-dark"><i class="fa-solid fa-percent text-info me-2"></i>5. HMRC VAT Notice 709/1 (Eat-In vs Hot vs Cold Takeaway)</h5>
                            <small class="text-muted d-block mb-3">Simulate UK split-rate VAT liability across Eat-In (20%), Hot Takeaway (20%), and Cold Takeaway Grab-and-Go (0% Zero-Rated Food).</small>
                            <div class="btn-group btn-group-sm mb-3" role="group">
                                <button type="button" class="btn btn-dark fw-bold" onclick="simulateHmrcVatMode('EAT_IN')">🍽️ Eat-In (20%)</button>
                                <button type="button" class="btn btn-outline-dark fw-bold" onclick="simulateHmrcVatMode('HOT_TAKEAWAY')">🔥 Hot Takeaway (20%)</button>
                                <button type="button" class="btn btn-outline-dark fw-bold" onclick="simulateHmrcVatMode('COLD_TAKEAWAY')">❄️ Cold Takeaway (0% Food)</button>
                            </div>
                            <div id="hmrcVat709ResultBox" class="p-3 bg-light rounded-3 border small"></div>
                        </div>
                    </div>

                    <div class="col-lg-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-1 text-dark"><i class="fa-solid fa-lock text-success me-2"></i>6. UK GDPR, London Cloud Residency & Cyber Essentials</h5>
                            <small class="text-muted d-block mb-3">Sovereign UK data residency, ICO Data Protection Act 2018 compliance, and NCSC Cyber Essentials posture.</small>
                            <div id="ukGdprSecurityBox" class="p-3 bg-light rounded-3 border small"></div>
                        </div>
                    </div>
                </div>
            </div>

'''

    if target_strategy_pane in content and 'id="ukcompliance"' not in content:
        content = content.replace(target_strategy_pane, uk_compliance_pane + target_strategy_pane, 1)
        print("Added #ukcompliance tab pane to Staff Workspace!")

    # 5. Update renderCart() in Guest View to compute Challenge 25 banner & HMRC VAT 709/1 breakdown
    old_render_cart_end = '''            document.getElementById('cartTotal').innerText = `${sym}${total.toFixed(2)}`;
            document.getElementById('mobileCartTotal').innerText = `${sym}${total.toFixed(2)}`;
            document.getElementById('mobileModalCartTotal').innerText = `${sym}${total.toFixed(2)}`;
            document.getElementById('mobileCartCount').innerText = currentCart.length;
        }'''

    new_render_cart_end = '''            document.getElementById('cartTotal').innerText = `${sym}${total.toFixed(2)}`;
            document.getElementById('mobileCartTotal').innerText = `${sym}${total.toFixed(2)}`;
            document.getElementById('mobileModalCartTotal').innerText = `${sym}${total.toFixed(2)}`;
            document.getElementById('mobileCartCount').innerText = currentCart.length;

            // UK Challenge 25 Check (flag item-3 Craft IPA)
            const ch25Banner = document.getElementById('challenge25CartBanner');
            if(ch25Banner) {
                const hasAlcohol = currentCart.some(i => i.id === 'item-3');
                if(hasAlcohol) ch25Banner.classList.remove('d-none');
                else ch25Banner.classList.add('d-none');
            }

            // HMRC VAT Notice 709/1 Breakdown (Eat-In 20% vs Hot Takeaway 20% vs Cold Takeaway 0% Food)
            const vatModeEl = document.getElementById('guestVatDiningMode');
            const vatLineEl = document.getElementById('guestVatBreakdownLine');
            if(vatModeEl && vatLineEl) {
                const mode = vatModeEl.value;
                let vatTotal = 0;
                let netTotal = 0;
                currentCart.forEach(item => {
                    if(mode === 'COLD_TAKEAWAY' && item.id !== 'item-3') {
                        netTotal += item.price;
                    } else {
                        const net = item.price / 1.20;
                        netTotal += net;
                        vatTotal += (item.price - net);
                    }
                });
                vatLineEl.innerHTML = `<span>Net: <strong>${sym}${netTotal.toFixed(2)}</strong></span><span>UK VAT (${mode === 'COLD_TAKEAWAY' ? '0% Cold Food' : '20% Std'}): <strong class="text-danger">${sym}${vatTotal.toFixed(2)}</strong></span>`;
            }
        }'''

    if old_render_cart_end in content:
        content = content.replace(old_render_cart_end, new_render_cart_end, 1)
        print("Updated renderCart() with live Challenge 25 detection & HMRC 709/1 VAT calculation!")

    # 6. Add JS functions for UK Compliance Hub before </script>\n</body>\n</html>"""
    js_uk_compliance = '''
        // --- 7. 🇬🇧 UK Statutory Compliance & EHO Hub Functions ---
        async function loadUkComplianceHub() {
            await previewNatashasLawLabel();
            await loadTipsAct2024Panel();
            await loadChallenge25Panel();
            await loadFoodSafetyPanel();
            await simulateHmrcVatMode('COLD_TAKEAWAY');
            await loadUkGdprSecurityPanel();
        }

        async function previewNatashasLawLabel() {
            const itemId = document.getElementById('ppdsDishSelect')?.value || 'item-1';
            const res = await fetch(`/api/uk-compliance/natashas-law/${itemId}`);
            const data = await res.json();
            const box = document.getElementById('ppdsLabelPreviewBox');
            if(box) box.innerHTML = data.natashas_law_label_html;
        }

        async function buildCustomPpdsLabel() {
            const rawStr = document.getElementById('ppdsCustomIngInput')?.value || '';
            const ingredients = rawStr.split(',').map(s => s.trim()).filter(Boolean);
            if(ingredients.length === 0) return previewNatashasLawLabel();
            const res = await fetch('/api/uk-compliance/natashas-law/build', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: 'custom-deli', ingredients: ingredients })
            });
            const data = await res.json();
            const box = document.getElementById('ppdsLabelPreviewBox');
            if(box) box.innerHTML = data.natashas_law_label_html;
        }

        function printPpdsGrabAndGoLabel() {
            alert("🏷️ [Natasha's Law PPDS Printer] Sent compliant Prepacked for Direct Sale (PPDS) label with BOLD allergen ingredients & Use-By timestamp to Deli Label Printer!");
        }

        async function loadTipsAct2024Panel() {
            const res = await fetch('/api/uk-compliance/tips-act-2024');
            const data = await res.json();
            const polBox = document.getElementById('tipsActPolicyBox');
            const logsBox = document.getElementById('tipsActPayoutLogsContainer');
            if(polBox && data.written_policy) {
                polBox.innerHTML = `
                    <strong class="text-dark d-block">${data.written_policy.legislation}</strong>
                    <span class="text-muted">${data.written_policy.policy_summary}</span>
                `;
            }
            if(logsBox) {
                logsBox.innerHTML = `
                    <table class="table table-sm table-bordered small mb-0">
                        <thead class="table-light">
                            <tr><th>Staff</th><th>Role</th><th>Hrs</th><th>Employer Ded.</th><th class="text-end">100% Net Paid</th></tr>
                        </thead>
                        <tbody>
                            ${(data.staff_payout_logs || []).map(p => `
                                <tr>
                                    <td class="fw-bold">${p.staff_name}</td>
                                    <td>${p.role}</td>
                                    <td>${p.hours_worked}h</td>
                                    <td class="text-success fw-bold">£0.00 (0%)</td>
                                    <td class="text-end fw-bold text-success">£${p.net_payout_gbp.toFixed(2)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            }
        }

        async function recordUkTipPayout(e) {
            if(e) e.preventDefault();
            const name = document.getElementById('tipStaffName').value.trim();
            const role = document.getElementById('tipStaffRole').value.trim();
            const hrs = parseFloat(document.getElementById('tipStaffHours').value || 38);
            await fetch('/api/uk-compliance/tips-act-2024/payout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ staff_name: name, role: role, hours_worked: hrs, amount_gbp: +(hrs * 4.25).toFixed(2) })
            });
            document.getElementById('tipStaffName').value = '';
            loadTipsAct2024Panel();
        }

        async function loadChallenge25Panel() {
            const res = await fetch('/api/uk-compliance/challenge25/logs');
            const data = await res.json();
            const box = document.getElementById('challenge25LogsContainer');
            if(!box) return;
            box.innerHTML = (data.logs || []).map(c => `
                <div class="p-2 rounded border bg-light d-flex justify-content-between align-items-center small">
                    <div>
                        <span class="badge ${c.decision === 'APPROVED' ? 'bg-success' : 'bg-danger'} me-1">${c.decision}</span>
                        <strong>Table #${c.table_number}</strong> • ${c.id_type}
                        <small class="text-muted d-block">Verified by: ${c.verified_by_staff}</small>
                    </div>
                    <small class="text-muted">${c.check_id}</small>
                </div>
            `).join('');
        }

        async function submitChallenge25Check(e) {
            if(e) e.preventDefault();
            const tbl = parseInt(document.getElementById('ch25TableNum').value || 4);
            const idType = document.getElementById('ch25IdType').value;
            const dec = document.getElementById('ch25Decision').value;
            await fetch('/api/uk-compliance/challenge25/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ table_number: tbl, order_id: 'ORD-LIVE', decision: dec, id_type: idType })
            });
            loadChallenge25Panel();
        }

        async function loadFoodSafetyPanel() {
            const res = await fetch('/api/uk-compliance/food-safety');
            const data = await res.json();
            const badge = document.getElementById('ehoReadyStatusBadge');
            if(badge) {
                badge.className = data.eho_inspection_ready ? 'badge bg-success' : 'badge bg-danger';
                badge.innerText = data.eho_inspection_ready ? '✓ 5-Star EHO Inspection Ready' : '⚠️ CCP Action Required';
            }
            const tBox = document.getElementById('fridgeTempLogsContainer');
            if(tBox) {
                tBox.innerHTML = (data.fridge_temp_logs || []).map(l => `
                    <div class="d-flex justify-content-between align-items-center p-1 px-2 border-bottom small">
                        <span><strong>${l.unit_name}</strong> <small class="text-muted">(${l.target_range})</small></span>
                        <span class="badge ${l.status === 'COMPLIANT' ? 'bg-success' : 'bg-danger'}">${l.recorded_temp_c}°C • ${l.status}</span>
                    </div>
                `).join('');
            }
            const hBox = document.getElementById('haccpChecklistContainer');
            if(hBox) {
                hBox.innerHTML = (data.cleaning_haccp_checklists || []).map(t => `
                    <div class="form-check small">
                        <input class="form-check-input" type="checkbox" ${t.completed ? 'checked' : ''} onchange="toggleHaccpTask('${t.task_id}')">
                        <label class="form-check-label ${t.completed ? 'text-decoration-line-through text-muted' : 'fw-bold text-dark'}">
                            [${t.category}] ${t.task}
                        </label>
                    </div>
                `).join('');
            }
        }

        async function submitFridgeTempLog(e) {
            if(e) e.preventDefault();
            const rawUnit = document.getElementById('safetyUnitName').value.split('|');
            const tempVal = parseFloat(document.getElementById('safetyTempVal').value);
            await fetch('/api/uk-compliance/food-safety/temp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ unit_name: rawUnit[0], unit_type: rawUnit[1], recorded_temp_c: tempVal, checked_by: 'Duty Manager' })
            });
            loadFoodSafetyPanel();
        }

        async function toggleHaccpTask(taskId) {
            await fetch('/api/uk-compliance/food-safety/haccp-toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: taskId })
            });
            loadFoodSafetyPanel();
        }

        async function simulateHmrcVatMode(mode) {
            const res = await fetch('/api/uk-compliance/vat-mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dining_mode: mode, items: ['item-1', 'item-3', 'item-4'] })
            });
            const data = await res.json();
            const box = document.getElementById('hmrcVat709ResultBox');
            if(!box) return;
            box.innerHTML = `
                <div class="d-flex justify-content-between mb-2 border-bottom pb-1">
                    <strong>Mode: <span class="text-primary">${data.dining_mode}</span></strong>
                    <span class="badge bg-dark">Total VAT: £${data.total_vat_payable_gbp.toFixed(2)}</span>
                </div>
                ${(data.items_breakdown || []).map(i => `
                    <div class="d-flex justify-content-between text-muted">
                        <span>${i.name} (${i.vat_rate_pct}% VAT)</span>
                        <span>Net £${i.net_price_gbp.toFixed(2)} + VAT £${i.vat_amount_gbp.toFixed(2)}</span>
                    </div>
                `).join('')}
                <div class="mt-2 pt-1 border-top d-flex justify-content-between fw-bold text-dark">
                    <span>Zero-Rated (0%) Sales: £${data.net_zero_rated_gbp.toFixed(2)}</span>
                    <span class="text-success">Standard (20%) Net: £${data.net_standard_rated_gbp.toFixed(2)}</span>
                </div>
            `;
        }

        async function loadUkGdprSecurityPanel() {
            const res = await fetch('/api/uk-compliance/gdpr-security');
            const data = await res.json();
            const box = document.getElementById('ukGdprSecurityBox');
            if(!box) return;
            box.innerHTML = `
                <div class="mb-2"><strong><i class="fa-solid fa-cloud text-primary me-1"></i>Hosting Residency:</strong> ${data.data_residency}</div>
                <div class="mb-2"><strong><i class="fa-solid fa-shield-halved text-success me-1"></i>Cyber Security:</strong> ${data.cyber_security_certification}</div>
                <div class="mb-2"><strong><i class="fa-solid fa-key text-warning me-1"></i>Encryption:</strong> ${data.encryption_standard}</div>
                <ul class="mb-0 ps-3 text-muted">
                    ${(data.guest_privacy_controls || []).map(c => `<li>${c}</li>`).join('')}
                </ul>
            `;
        }
    </script>
</body>
</html>"""'''

    target_index_end = '''    </script>
</body>
</html>"""'''

    if target_index_end in content:
        content = content.replace(target_index_end, js_uk_compliance, 1)
        print("Added JS handlers for UK Compliance & EHO Hub!")

    # 7. Add Backend Routes for all 6 UK Compliance Pillars before if __name__ == "__main__":
    backend_uk_routes = '''

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
'''

    target_main = 'if __name__ == "__main__":'
    if target_main in content:
        content = content.replace(target_main, backend_uk_routes + "\n\n" + target_main, 1)
        print("Added backend routes for all 6 UK Compliance pillars!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
