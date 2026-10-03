import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Floating AI Sommelier Button to Guest View
    old_guest_view_start = '<main id="guestViewSection" class="container my-4">'
    new_guest_view_start = '''<main id="guestViewSection" class="container my-4">
        <!-- Floating AI Sommelier Companion Button (Page 6 Blueprint) -->
        <button class="btn btn-dark text-warning rounded-circle shadow-lg position-fixed bottom-0 end-0 m-4 z-3 d-flex align-items-center justify-content-center border border-warning" style="width: 58px; height: 58px;" onclick="showAiSommelierModal()" title="AI Sommelier & Culinary Assistant">
            <i class="fa-solid fa-wine-glass-empty fs-3"></i>
        </button>'''

    if old_guest_view_start in content:
        content = content.replace(old_guest_view_start, new_guest_view_start)
        print("Added Floating AI Sommelier Button to Guest View!")
    else:
        print("Could not find old_guest_view_start in app.py!")

    # 2. Add AI Sommelier Modal HTML
    old_modal_end = '    <!-- Bootstrap JS & Interactivity Script -->'
    new_sommelier_modal = '''    <!-- AI Sommelier & Culinary Companion Modal -->
    <div class="modal fade" id="aiSommelierModal" tabindex="-1" aria-labelledby="aiSommelierModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header text-white" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
                    <h5 class="modal-title fw-bold" id="aiSommelierModalLabel"><i class="fa-solid fa-wine-bottle text-warning me-2"></i>AI Sommelier & Culinary Assistant</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-4">
                    <div class="p-3 bg-light rounded-3 border mb-3">
                        <small class="text-muted fw-bold d-block mb-2"><i class="fa-solid fa-lightbulb text-warning me-1"></i> Quick Sommelier Prompts:</small>
                        <div class="d-flex flex-wrap gap-2">
                            <button class="btn btn-sm btn-outline-dark rounded-pill" onclick="askAiSommelier('What wine pairs best with Fish & Chips?')">🍷 Wine for Fish & Chips</button>
                            <button class="btn btn-sm btn-outline-dark rounded-pill" onclick="askAiSommelier('What beer goes with Wagyu Burger?')">🍺 Beer for Wagyu Burger</button>
                            <button class="btn btn-sm btn-outline-dark rounded-pill" onclick="askAiSommelier('Show gluten-free and vegan options')">🌱 Gluten-Free Options</button>
                        </div>
                    </div>

                    <div id="sommelierChatBox" class="p-3 bg-white border rounded-3 mb-3" style="min-height: 220px; max-height: 320px; overflow-y: auto;">
                        <div class="d-flex align-items-start gap-2 mb-3">
                            <div class="bg-dark text-warning rounded-circle p-2 fs-5"><i class="fa-solid fa-robot"></i></div>
                            <div class="p-3 bg-light rounded-3 text-dark border">
                                Hello! I am your AI Sommelier. Ask me for food & wine pairings, dietary options, or dish recommendations!
                            </div>
                        </div>
                    </div>

                    <div class="input-group">
                        <input type="text" id="sommelierInputPrompt" class="form-control" placeholder="Ask AI Sommelier (e.g., 'Best wine for steak?')..." onkeypress="if(event.key==='Enter') sendSommelierPrompt()">
                        <button class="btn btn-warning text-dark fw-bold px-4" onclick="sendSommelierPrompt()"><i class="fa-solid fa-paper-plane me-1"></i> Ask AI</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS & Interactivity Script -->'''

    if old_modal_end in content:
        content = content.replace(old_modal_end, new_sommelier_modal)
        print("Added aiSommelierModal HTML successfully!")
    else:
        print("Could not find old_modal_end in app.py!")

    # 3. Add JS functions before script end
    sommelier_js_code = '''
        // --- AI Sommelier & Culinary Companion Engine ---
        function showAiSommelierModal() {
            const modal = new bootstrap.Modal(document.getElementById('aiSommelierModal'));
            modal.show();
        }

        async function askAiSommelier(promptText) {
            document.getElementById('sommelierInputPrompt').value = promptText;
            await sendSommelierPrompt();
        }

        async function sendSommelierPrompt() {
            const input = document.getElementById('sommelierInputPrompt');
            const prompt = input.value.trim();
            if (!prompt) return;

            const chatBox = document.getElementById('sommelierChatBox');

            // Append User Message
            chatBox.innerHTML += `
                <div class="d-flex align-items-start gap-2 mb-3 justify-content-end">
                    <div class="p-3 bg-primary text-white rounded-3 shadow-sm" style="max-width: 80%;">
                        ${prompt}
                    </div>
                    <div class="bg-primary text-white rounded-circle p-2 fs-5"><i class="fa-solid fa-user"></i></div>
                </div>
            `;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/api/ai/sommelier', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, lang: currentLang })
                });
                const data = await res.json();

                let recsHtml = '';
                if (data.recommendations && data.recommendations.length > 0) {
                    recsHtml = `
                        <div class="mt-2 pt-2 border-top">
                            <small class="fw-bold text-dark d-block mb-1"><i class="fa-solid fa-star text-warning me-1"></i> Suggested Menu Pairings:</small>
                            <div class="vstack gap-2">
                                ${data.recommendations.map(r => `
                                    <div class="p-2 border rounded bg-white d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong class="text-dark small">${r.name}</strong>
                                            <small class="text-muted d-block">£${r.price.toFixed(2)}</small>
                                        </div>
                                        <button class="btn btn-xs btn-success fw-bold py-1 px-2" onclick="addToCart('${r.item_id}')"><i class="fa-solid fa-cart-plus me-1"></i> Add £${r.price.toFixed(2)}</button>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }

                // Append AI Response
                chatBox.innerHTML += `
                    <div class="d-flex align-items-start gap-2 mb-3">
                        <div class="bg-dark text-warning rounded-circle p-2 fs-5"><i class="fa-solid fa-robot"></i></div>
                        <div class="p-3 bg-light rounded-3 text-dark border shadow-sm" style="max-width: 85%;">
                            ${data.response_text}
                            ${recsHtml}
                        </div>
                    </div>
                `;
                chatBox.scrollTop = chatBox.scrollHeight;

            } catch(e) {
                console.error('Sommelier AI error', e);
            }
        }
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, sommelier_js_code + "\n" + target_script_end)
        print("Added AI Sommelier JS functions before script end!")
    else:
        print("Could not find target_script_end in app.py!")

    # 4. Add Python API route POST /api/ai/sommelier
    backend_sommelier_route = '''
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
'''

    main_block = 'if __name__ == "__main__":'
    if main_block in content:
        content = content.replace(main_block, backend_sommelier_route + "\n\n" + main_block)
        print("Added backend route POST /api/ai/sommelier!")
    else:
        print("Could not find main_block in app.py!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
