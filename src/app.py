from flask import Flask, jsonify, request, render_template_string
import os
import sys

# Ensure src path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.config import Config
from src.core.db import db
from src.modules.qr_ordering import qr_ordering_service
from src.modules.kds import kds_service
from src.modules.promos import promo_service
from src.modules.reviews import review_service
from src.modules.finance import finance_service

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Simple HTML dashboard template for demonstration & interactive testing
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Waiter | UK Hospitality SaaS Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; }
        .hero { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 40px 0; }
        .card-custom { border-radius: 12px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .status-badge { font-size: 0.85rem; padding: 6px 12px; border-radius: 20px; }
    </style>
</head>
<body>
    <div class="hero text-center">
        <div class="container">
            <h1 class="display-4 fw-bold">The Waiter</h1>
            <p class="lead">UK Market Strategy & Operational Blueprint Implementation</p>
            <span class="badge bg-light text-dark me-2">UK Currency (£)</span>
            <span class="badge bg-success me-2">Scan-to-Invoice Active</span>
            <span class="badge bg-warning text-dark">BYOD Multi-Device</span>
        </div>
    </div>

    <div class="container my-5">
        <div class="row g-4">
            <!-- 1. QR Ordering -->
            <div class="col-md-6 col-lg-4">
                <div class="card card-custom h-100 p-4">
                    <h4 class="fw-bold text-primary">📱 1. QR Ordering & Menu</h4>
                    <p class="text-muted">Dynamic catalogue with multi-lang (EN, FR, AR) and AI upsell support.</p>
                    <div class="d-grid gap-2">
                        <a href="/api/menu?lang=en" target="_blank" class="btn btn-outline-primary btn-sm">View Menu (EN)</a>
                        <a href="/api/menu?lang=fr" target="_blank" class="btn btn-outline-primary btn-sm">View Menu (FR)</a>
                        <a href="/api/menu?lang=ar" target="_blank" class="btn btn-outline-primary btn-sm">View Menu (AR)</a>
                    </div>
                </div>
            </div>

            <!-- 2. KDS Kitchen -->
            <div class="col-md-6 col-lg-4">
                <div class="card card-custom h-100 p-4">
                    <h4 class="fw-bold text-success">🍳 2. KDS Kitchen Screen</h4>
                    <p class="text-muted">Live order line digitalization (New ➔ Preparing ➔ Ready).</p>
                    <div class="d-grid gap-2">
                        <a href="/api/kds/active" target="_blank" class="btn btn-outline-success btn-sm">Kitchen Queue API</a>
                        <a href="/api/kds/tv" target="_blank" class="btn btn-outline-success btn-sm">Guest TV Screen API</a>
                    </div>
                </div>
            </div>

            <!-- 3. Promos & Retention -->
            <div class="col-md-6 col-lg-4">
                <div class="card card-custom h-100 p-4">
                    <h4 class="fw-bold text-warning text-dark">🏷️ 3. Promo Codes</h4>
                    <p class="text-muted">Targeted discounts (WELCOME10, OFFPEAK20) for off-peak demand.</p>
                    <div class="d-grid gap-2">
                        <a href="/api/promos" target="_blank" class="btn btn-outline-warning btn-sm text-dark">View Active Promos</a>
                    </div>
                </div>
            </div>

            <!-- 4. Private Reviews -->
            <div class="col-md-6 col-lg-4">
                <div class="card card-custom h-100 p-4">
                    <h4 class="fw-bold text-danger">⭐ 4. Private Reviews</h4>
                    <p class="text-muted">Internal "Avis clients" capturing module before public posting.</p>
                    <div class="d-grid gap-2">
                        <a href="/api/reviews" target="_blank" class="btn btn-outline-danger btn-sm">View Guest Reviews</a>
                    </div>
                </div>
            </div>

            <!-- 5. Finance & RevPASH -->
            <div class="col-md-6 col-lg-4">
                <div class="card card-custom h-100 p-4">
                    <h4 class="fw-bold text-info text-dark">📊 5. RevPASH & Invoicing</h4>
                    <p class="text-muted">PDF Invoicing with UK VAT 20% & RevPASH performance analytics.</p>
                    <div class="d-grid gap-2">
                        <a href="/api/analytics" target="_blank" class="btn btn-outline-info btn-sm text-dark">View RevPASH Analytics</a>
                    </div>
                </div>
            </div>

            <!-- 6. Strategy & Docs -->
            <div class="col-md-6 col-lg-4">
                <div class="card card-custom h-100 p-4">
                    <h4 class="fw-bold text-dark">📄 6. Strategic Blueprint</h4>
                    <p class="text-muted">Read executive market report and technical architecture documentation.</p>
                    <div class="d-grid gap-2">
                        <a href="/docs/strategy" class="btn btn-dark btn-sm">View UK Market Strategy</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(INDEX_HTML)

# --- 1. QR Ordering Endpoints ---
@app.route("/api/menu", methods=["GET"])
def get_menu():
    lang = request.args.get("lang", "en")
    return jsonify(qr_ordering_service.get_menu(lang))

@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.json or {}
    table_num = data.get("table_number", 1)
    items = data.get("items", ["item-1", "item-3"])
    promo = data.get("promo_code")
    order = qr_ordering_service.submit_order(table_num, items, promo)
    return jsonify(order), 201

# --- 2. KDS Endpoints ---
@app.route("/api/kds/active", methods=["GET"])
def kds_active():
    return jsonify(kds_service.get_active_kitchen_orders())

@app.route("/api/kds/tv", methods=["GET"])
def kds_tv():
    return jsonify(kds_service.get_tv_display_status())

@app.route("/api/kds/advance/<order_id>", methods=["POST"])
def kds_advance(order_id):
    updated = kds_service.advance_order_status(order_id)
    if updated:
        return jsonify(updated)
    return jsonify({"error": "Order not found"}), 404

# --- 3. Promo Code Endpoints ---
@app.route("/api/promos", methods=["GET"])
def get_promos():
    return jsonify(db.promos)

# --- 4. Review Endpoints ---
@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    return jsonify({
        "average_rating": review_service.get_average_rating(),
        "reviews": review_service.get_all_reviews()
    })

@app.route("/api/reviews", methods=["POST"])
def submit_review():
    data = request.json or {}
    table_num = data.get("table_number", 1)
    rating = data.get("rating", 5)
    comment = data.get("comment", "Great service!")
    rev = review_service.submit_review(table_num, rating, comment)
    return jsonify(rev), 201

# --- 5. Finance & Analytics Endpoints ---
@app.route("/api/invoice/<order_id>", methods=["GET"])
def get_invoice(order_id):
    invoice = finance_service.generate_invoice(order_id)
    if invoice:
        return jsonify(invoice)
    return jsonify({"error": "Order not found"}), 404

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    return jsonify(finance_service.calculate_analytics())

@app.route("/docs/strategy")
def strategy_doc():
    doc_path = os.path.join(os.path.dirname(__file__), "..", "docs", "UK_MARKET_STRATEGY.md")
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
    return f"<pre style='white-space: pre-wrap; font-family: monospace; padding: 20px;'>{content}</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
