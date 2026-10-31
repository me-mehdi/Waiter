import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Google & TripAdvisor Review Booster Modal HTML
    old_modal_end = '    <!-- Bootstrap JS & Interactivity Script -->'
    new_booster_modal = '''    <!-- Google & TripAdvisor Review Booster Modal -->
    <div class="modal fade" id="reviewBoosterModal" tabindex="-1" aria-labelledby="reviewBoosterModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title fw-bold" id="reviewBoosterModalLabel"><i class="fa-solid fa-star text-warning me-2"></i>Thank You for 5 Stars! 🎉</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-4 text-center">
                    <h6 class="fw-bold text-dark mb-2">Help others discover The Waiter!</h6>
                    <p class="small text-muted mb-4">Would you mind sharing your 5-star experience on Google Reviews or TripAdvisor? It takes less than 30 seconds!</p>
                    <div class="d-grid gap-2 mb-3">
                        <a href="https://maps.google.com" target="_blank" class="btn btn-outline-danger fw-bold py-2"><i class="fa-brands fa-google me-2"></i> Post on Google Reviews</a>
                        <a href="https://tripadvisor.com" target="_blank" class="btn btn-outline-success fw-bold py-2"><i class="fa-solid fa-owl me-2"></i> Post on TripAdvisor</a>
                    </div>
                    <button type="button" class="btn btn-sm btn-link text-muted" data-bs-dismiss="modal">Done / Skip</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS & Interactivity Script -->'''

    if old_modal_end in content:
        content = content.replace(old_modal_end, new_booster_modal)
        print("Added reviewBoosterModal HTML successfully!")
    else:
        print("Could not find old_modal_end in app.py!")

    # 2. Update submitGuestReview to trigger Review Booster for 5-star ratings
    old_submit_review = '''        async function submitGuestReview() {
            const rating = parseInt(document.getElementById('selectedRating').value);
            const comment = document.getElementById('reviewComment').value.trim();

            await fetch('/api/reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table_number: activeTable,
                    rating: rating,
                    comment: comment
                })
            });

            alert('Thank you! Your feedback has been sent to management.');
            const modalEl = document.getElementById('reviewModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            document.getElementById('reviewComment').value = '';
        }'''

    new_submit_review = '''        async function submitGuestReview() {
            const rating = parseInt(document.getElementById('selectedRating').value) || 5;
            const comment = document.getElementById('reviewComment').value.trim();

            await fetch('/api/reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table_number: activeTable,
                    rating: rating,
                    comment: comment
                })
            });

            const modalEl = document.getElementById('reviewModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            document.getElementById('reviewComment').value = '';

            if (rating >= 4) {
                const boosterModal = new bootstrap.Modal(document.getElementById('reviewBoosterModal'));
                boosterModal.show();
            } else {
                alert('Thank you! Your feedback has been sent directly to our General Manager.');
            }
        }'''

    if old_submit_review in content:
        content = content.replace(old_submit_review, new_submit_review)
        print("Updated submitGuestReview function successfully!")
    else:
        print("Could not find old_submit_review in app.py!")

    # 3. Add JS auto-responder function before script end
    auto_responder_js_code = '''
        // --- AI Customer Review Auto-Responder Engine ---
        async function generateAiReviewResponse(rating, comment, tableNum) {
            try {
                const res = await fetch('/api/reviews/auto-respond', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rating: rating, comment: comment, table_number: tableNum })
                });
                const data = await res.json();
                if (data.response_draft) {
                    prompt('AI Generated Staff Response Draft (Copy & Send):', data.response_draft);
                }
            } catch(e) {
                console.error('AI Auto-responder error', e);
            }
        }
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, auto_responder_js_code + "\n" + target_script_end)
        print("Added auto-responder JS functions before script end!")
    else:
        print("Could not find target_script_end in app.py!")

    # 4. Add Python API route POST /api/reviews/auto-respond
    backend_review_route = '''
# --- 23. AI Customer Review Auto-Responder Endpoint ---
@app.route("/api/reviews/auto-respond", methods=["POST"])
def ai_review_auto_responder():
    data = request.json or {}
    rating = int(data.get("rating", 5))
    comment = (data.get("comment") or "").strip()
    table_num = data.get("table_number", 1)

    if rating >= 4:
        response_draft = f"Thank you so much for the fantastic {rating}-star review! We are delighted that you enjoyed your visit to Table #{table_num}. Our team looks forward to welcoming you back to Covent Garden Flagship soon!"
    elif rating == 3:
        response_draft = f"Thank you for sharing your feedback regarding Table #{table_num}. We appreciate your honest notes on '{comment or 'service'}' and are using your insights to deliver a 5-star experience next time!"
    else:
        response_draft = f"Thank you for reaching out regarding Table #{table_num}. We sincerely apologize that your visit fell short of your expectations. Please contact our General Manager directly at manager@waiter.com so we can make this right!"

    return jsonify({
        "success": True,
        "rating": rating,
        "response_draft": response_draft
    })
'''

    main_block = 'if __name__ == "__main__":'
    if main_block in content:
        content = content.replace(main_block, backend_review_route + "\n\n" + main_block)
        print("Added backend route POST /api/reviews/auto-respond!")
    else:
        print("Could not find main_block in app.py!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
