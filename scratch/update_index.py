import os
import re

app_py_path = "/Users/elmehdinidazi/Downloads/Waiter/src/app.py"

index_html_content = """INDEX_HTML = \"\"\"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>The Waiter | Table Guest Menu & Enterprise OS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-bg: #0f172a;
            --accent-blue: #0284c7;
            --accent-green: #10b981;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
        }
        body {
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            background-color: #f8fafc;
            color: var(--text-main);
            padding-bottom: 80px; /* space for mobile sticky cart */
        }

        /* Top Header Bar */
        .app-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 14px 20px;
            border-bottom: 3px solid #38bdf8;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .table-badge {
            background: #38bdf8;
            color: #0f172a;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.95rem;
        }

        /* Mode Switcher Pill */
        .mode-switch-btn {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.25);
            color: white;
            font-weight: 600;
            font-size: 0.8rem;
            padding: 6px 12px;
            border-radius: 20px;
            transition: all 0.2s;
        }
        .mode-switch-btn:hover, .mode-switch-btn.active {
            background: white;
            color: #0f172a;
        }

        /* Cards & Buttons */
        .card-custom {
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            background: var(--card-bg);
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        @media(min-width: 768px) {
            .card-custom:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
        }

        /* Dish Card Styling */
        .dish-card {
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            background: white;
            padding: 16px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .dish-price {
            font-weight: 800;
            font-size: 1.1rem;
            color: var(--accent-blue);
        }
        .add-btn {
            border-radius: 12px;
            font-weight: 700;
            padding: 8px 16px;
        }

        /* Floating Sticky Mobile Bottom Cart Bar */
        .mobile-cart-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 1040;
            background: #0f172a;
            color: white;
            padding: 14px 20px;
            border-top: 2px solid #38bdf8;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.2);
        }

        /* Nav Pills */
        .nav-pills .nav-link {
            color: #475569;
            font-weight: 600;
            padding: 10px 18px;
            border-radius: 12px;
            font-size: 0.88rem;
            white-space: nowrap;
        }
        .nav-pills .nav-link.active {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
        }

        /* Live status progress bar */
        .order-step {
            flex: 1;
            text-align: center;
            position: relative;
            font-size: 0.75rem;
            font-weight: 700;
            color: #94a3b8;
        }
        .order-step.active {
            color: #0284c7;
        }
        .order-step-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 6px;
        }
        .order-step.active .order-step-icon {
            background: #0284c7;
            color: white;
        }
    </style>
</head>
<body>

    <!-- Unified Cross-Platform App Header -->
    <header class="app-header">
        <div class="container-fluid px-md-4">
            <div class="d-flex justify-content-between align-items-center">
                <!-- Branding & Active Table -->
                <div class="d-flex align-items-center gap-3">
                    <div class="lh-1">
                        <h4 class="fw-bold mb-0 text-white"><i class="fa-solid fa-utensils me-2 text-info"></i>The Waiter</h4>
                        <small class="text-light opacity-75 d-none d-sm-inline" id="activeStoreLabel">Covent Garden Flagship</small>
                    </div>
                    <div class="table-badge d-flex align-items-center gap-2">
                        <i class="fa-solid fa-qrcode"></i>
                        <span>Table #<span id="activeTableBadgeNum">1</span></span>
                    </div>
                </div>

                <!-- Call Waiter & Mode Switcher Controls -->
                <div class="d-flex align-items-center gap-2">
                    <button class="btn btn-sm btn-warning text-dark font-weight-bold rounded-pill px-3" onclick="callWaiter()"><i class="fa-solid fa-bell me-1"></i> Call Waiter</button>
                    <button class="mode-switch-btn active" id="btnGuestView" onclick="setAppMode('guest')"><i class="fa-solid fa-mobile-screen me-1"></i> Table View</button>
                    <button class="mode-switch-btn" id="btnStaffView" onclick="setAppMode('staff')"><i class="fa-solid fa-user-shield me-1"></i> Staff Workspace</button>
                </div>
            </div>
        </div>
    </header>

    <!-- GUEST TABLE VIEW CONTAINER (Default Guest View - Clean & Focused) -->
    <main id="guestViewSection" class="container my-4">
        <!-- Call Waiter Alert Banner -->
        <div id="waiterAlertBanner" class="alert alert-success alert-dismissible fade show d-none shadow-sm rounded-3" role="alert">
            <i class="fa-solid fa-circle-check me-2"></i><strong>Server Notified!</strong> A staff member is on their way to Table #<span id="alertTableNum">1</span>.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>

        <!-- Live Order Progress Bar for Table -->
        <div id="tableLiveOrderCard" class="card card-custom p-3 bg-white shadow-sm mb-4 d-none">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-clock-rotate-left text-primary me-2"></i>Live Order Status (Table #<span id="liveTableNum">1</span>)</h6>
                <span class="badge bg-primary" id="liveOrderRef">ORD-1001</span>
            </div>
            <div class="d-flex justify-content-between align-items-center">
                <div class="order-step active" id="stepReceived">
                    <div class="order-step-icon"><i class="fa-solid fa-check"></i></div>
                    Received
                </div>
                <div class="order-step" id="stepPreparing">
                    <div class="order-step-icon"><i class="fa-solid fa-fire-burner"></i></div>
                    Preparing
                </div>
                <div class="order-step" id="stepReady">
                    <div class="order-step-icon"><i class="fa-solid fa-bell"></i></div>
                    Ready
                </div>
            </div>
        </div>

        <div class="row g-4">
            <!-- Digital Menu Main Area -->
            <div class="col-lg-8">
                <!-- Header Toolbar: Language, Currency, Filter -->
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                    <h4 class="fw-bold mb-0 text-dark">Digital Menu</h4>
                    <div class="d-flex align-items-center gap-2">
                        <div class="btn-group btn-group-sm" id="langGroup">
                            <button class="btn btn-outline-dark active fw-bold" onclick="setLanguage('en', this)">EN</button>
                            <button class="btn btn-outline-dark fw-bold" onclick="setLanguage('fr', this)">FR</button>
                            <button class="btn btn-outline-dark fw-bold" onclick="setLanguage('ar', this)">AR</button>
                        </div>
                        <div class="btn-group btn-group-sm" id="currGroup">
                            <button class="btn btn-dark active fw-bold" onclick="setCurrency('GBP', this)">£ GBP</button>
                            <button class="btn btn-outline-dark fw-bold" onclick="setCurrency('EUR', this)">€ EUR</button>
                            <button class="btn btn-outline-dark fw-bold" onclick="setCurrency('USD', this)">$ USD</button>
                        </div>
                    </div>
                </div>

                <!-- Dietary & Allergen Exclusion Chips -->
                <div class="d-flex flex-wrap align-items-center gap-2 mb-3 p-3 bg-white rounded-3 border shadow-sm">
                    <span class="small fw-bold text-muted me-1"><i class="fa-solid fa-filter me-1 text-primary"></i>Dietary Filters:</span>
                    <button class="btn btn-sm btn-outline-success active rounded-pill px-3 py-1 fw-bold" onclick="filterMenuDiet('all', this)">All Dishes</button>
                    <button class="btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold" onclick="filterMenuDiet('vegan', this)">🌱 Vegan</button>
                    <button class="btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold" onclick="filterMenuDiet('vegetarian', this)">🥬 Vegetarian</button>
                    <button class="btn btn-sm btn-outline-success rounded-pill px-3 py-1 fw-bold" onclick="filterMenuDiet('halal', this)">🕌 Halal</button>
                    <button class="btn btn-sm btn-outline-danger rounded-pill px-3 py-1 fw-bold ms-auto" onclick="toggleExclusion('gluten', this)">🌾 Exclude Gluten</button>
                </div>

                <!-- Dishes Grid -->
                <div id="menuContainer" class="row g-3">
                    <!-- Dynamically populated -->
                </div>
            </div>

            <!-- Cart & Table Quick Tools Sidebar (Desktop view) -->
            <div class="col-lg-4 d-none d-lg-block">
                <div class="card card-custom p-4 bg-white sticky-top" style="top: 20px;">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold mb-0"><i class="fa-solid fa-cart-shopping text-primary me-2"></i>Table Cart</h5>
                        <span class="badge bg-secondary">Table #<span id="desktopTableNum">1</span></span>
                    </div>
                    <hr class="my-2">
                    <div id="cartItems" class="mb-3 text-muted small py-2">Cart is empty. Select dishes from menu.</div>
                    
                    <!-- Smart Upsell Box -->
                    <div id="upsellBox" class="upsell-box mb-3 d-none">
                        <strong class="small text-dark"><i class="fa-solid fa-lightbulb text-warning me-1"></i>Recommended Add-on:</strong>
                        <div id="upsellContent" class="mt-1"></div>
                    </div>

                    <div class="mb-3">
                        <input type="text" id="promoInput" class="form-control form-control-sm" placeholder="Promo code (e.g. WELCOME10)">
                    </div>

                    <div class="d-flex justify-content-between fw-bold mb-3 fs-5">
                        <span>Total:</span>
                        <span id="cartTotal" class="text-success">£0.00</span>
                    </div>

                    <button class="btn btn-primary w-100 fw-bold mb-2 py-2" onclick="placeOrder()"><i class="fa-solid fa-check-circle me-1"></i> Submit Order</button>
                    <button class="btn btn-outline-success text-dark w-100 btn-sm fw-bold mb-2" onclick="showSplitBillModal()"><i class="fa-solid fa-calculator me-1"></i> Split Table Bill</button>
                    <button class="btn btn-outline-warning text-dark w-100 btn-sm fw-bold" data-bs-toggle="modal" data-bs-target="#reviewModal"><i class="fa-solid fa-comment-dots me-1"></i> Leave Private Feedback</button>
                </div>
            </div>
        </div>
    </main>

    <!-- FLOATING STICKY MOBILE BOTTOM CART BAR (Mobile < 992px) -->
    <div class="mobile-cart-bar d-lg-none" id="mobileCartBar">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <small class="text-light opacity-75 d-block">Table #<span id="mobileTableNum">1</span> Order Total</small>
                <strong class="fs-5 text-info" id="mobileCartTotal">£0.00</strong>
            </div>
            <button class="btn btn-info text-dark font-weight-bold px-4 py-2 rounded-pill shadow-sm" data-bs-toggle="modal" data-bs-target="#mobileCartModal">
                <i class="fa-solid fa-bag-shopping me-1"></i> View Cart (<span id="mobileCartCount">0</span>)
            </button>
        </div>
    </div>

    <!-- MOBILE CART MODAL (Full sheet drawer on small screens) -->
    <div class="modal fade" id="mobileCartModal" tabindex="-1" aria-labelledby="mobileCartModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="mobileCartModalLabel"><i class="fa-solid fa-cart-shopping text-primary me-2"></i>Table Cart</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div id="mobileCartItems" class="mb-3 text-muted small">Cart is empty.</div>
                    <div class="mb-3">
                        <input type="text" id="mobilePromoInput" class="form-control form-control-sm" placeholder="Promo code (e.g. WELCOME10)">
                    </div>
                    <div class="d-flex justify-content-between fw-bold mb-3 fs-5">
                        <span>Total:</span>
                        <span id="mobileModalCartTotal" class="text-success">£0.00</span>
                    </div>
                    <button class="btn btn-primary w-100 fw-bold mb-2 py-2" onclick="placeOrder(); bootstrap.Modal.getInstance(document.getElementById('mobileCartModal')).hide();"><i class="fa-solid fa-check-circle me-1"></i> Submit Order</button>
                    <button class="btn btn-outline-success w-100 btn-sm fw-bold mb-2" onclick="showSplitBillModal()"><i class="fa-solid fa-calculator me-1"></i> Split Bill</button>
                    <button class="btn btn-outline-warning text-dark w-100 btn-sm fw-bold" data-bs-toggle="modal" data-bs-target="#reviewModal"><i class="fa-solid fa-comment-dots me-1"></i> Leave Private Feedback</button>
                </div>
            </div>
        </div>
    </div>


    <!-- STAFF & MANAGER WORKSPACE CONTAINER (Hidden from table guests by default) -->
    <main id="staffViewSection" class="container my-4 d-none">
        <!-- Store Location Switcher Bar -->
        <div class="d-flex justify-content-between align-items-center mb-4 p-3 bg-white border rounded-3 shadow-sm">
            <div class="d-flex align-items-center gap-3">
                <div class="p-2 bg-primary bg-opacity-10 text-primary rounded-3 fs-4"><i class="fa-solid fa-store"></i></div>
                <div>
                    <span class="small fw-bold text-muted text-uppercase d-block">Active Store Location</span>
                    <strong id="activeVenueName" class="fs-6 text-dark">Covent Garden Flagship (UK)</strong>
                </div>
            </div>
            <div class="d-flex align-items-center gap-2">
                <label for="venueSelect" class="small fw-bold text-muted mb-0"><i class="fa-solid fa-location-dot me-1"></i>Venue Switcher:</label>
                <select id="venueSelect" class="form-select form-select-sm w-auto fw-bold text-dark border-primary" onchange="switchVenue(this.value)">
                    <!-- Dynamically populated -->
                </select>
            </div>
        </div>

        <!-- Executive Real-time Live KPIs Summary Row -->
        <div class="row g-3 mb-4">
            <div class="col-6 col-md-3">
                <div class="card card-custom p-3 shadow-sm">
                    <small class="text-muted text-uppercase fw-bold">Gross Revenue</small>
                    <div class="fs-3 fw-bold text-success" id="kpiGrossRev">£0.00</div>
                    <span class="small text-muted" id="kpiTotalOrdersCount">0 orders today</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card card-custom p-3 shadow-sm">
                    <small class="text-muted text-uppercase fw-bold">Active KDS Tickets</small>
                    <div class="fs-3 fw-bold text-primary" id="kpiActiveKds">0</div>
                    <span class="small text-muted">Real-time KDS stream</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card card-custom p-3 shadow-sm">
                    <small class="text-muted text-uppercase fw-bold">Active Staff & Labor</small>
                    <div class="fs-3 fw-bold text-info" id="kpiActiveStaff">0 Staff</div>
                    <span class="small text-muted" id="kpiLaborCost">£0.00 (0% labor)</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card card-custom p-3 shadow-sm">
                    <small class="text-muted text-uppercase fw-bold">NPS Guest Score</small>
                    <div class="fs-3 fw-bold text-warning" id="kpiNpsScore">0.0</div>
                    <span class="small text-muted" id="kpiNpsLabel">0 Reviews</span>
                </div>
            </div>
        </div>

        <!-- PDF Quick Action Badges Bar -->
        <div class="d-flex flex-wrap gap-2 mb-4 p-2 bg-white rounded-3 border shadow-sm">
            <span class="small fw-bold text-muted me-2 align-self-center"><i class="fa-solid fa-file-pdf text-danger me-1"></i>Quick PDF Exports:</span>
            <a href="/api/qr/cards/pdf" target="_blank" class="badge bg-danger text-white text-decoration-none p-2"><i class="fa-solid fa-qrcode me-1"></i> Table QR Tents</a>
            <a href="/api/finance/z-report/pdf" target="_blank" class="badge bg-dark text-warning text-decoration-none p-2"><i class="fa-solid fa-chart-line me-1"></i> Daily Z-Report</a>
            <a href="/api/waste/report/pdf" target="_blank" class="badge bg-danger text-white text-decoration-none p-2"><i class="fa-solid fa-trash-can me-1"></i> Waste Audit</a>
            <a href="/api/tax/report/pdf" target="_blank" class="badge bg-success text-white text-decoration-none p-2"><i class="fa-solid fa-file-invoice-dollar me-1"></i> HMRC MTD VAT</a>
            <a href="/api/feedback/report/pdf" target="_blank" class="badge bg-primary text-white text-decoration-none p-2"><i class="fa-solid fa-star me-1"></i> NPS Feedback</a>
            <a href="/api/inventory/purchase-orders/SEAFOOD/pdf" target="_blank" class="badge bg-info text-dark text-decoration-none p-2"><i class="fa-solid fa-truck-ramp-box me-1"></i> Supplier PO</a>
            <a href="/api/forecasting/report/pdf" target="_blank" class="badge bg-secondary text-white text-decoration-none p-2"><i class="fa-solid fa-brain me-1"></i> AI Forecast</a>
        </div>

        <!-- Staff Navigation Tabs Bar -->
        <ul class="nav nav-pills mb-4 justify-content-start justify-content-md-center flex-nowrap overflow-auto py-1" id="staffTabs" role="tablist">
            <li class="nav-item">
                <button class="nav-link active" id="kds-tab" data-bs-toggle="tab" data-bs-target="#kds" type="button" onclick="loadKDS()"><i class="fa-solid fa-fire-burner me-1"></i> Kitchen KDS</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="bookings-tab" data-bs-toggle="tab" data-bs-target="#bookings" type="button" onclick="loadBookings()"><i class="fa-solid fa-calendar-check me-1"></i> Reservations</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="inventory-tab" data-bs-toggle="tab" data-bs-target="#inventory" type="button" onclick="loadInventory()"><i class="fa-solid fa-boxes-stacked me-1"></i> Stock & POs</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="waste-tab" data-bs-toggle="tab" data-bs-target="#waste" type="button" onclick="loadWaste()"><i class="fa-solid fa-trash-can me-1"></i> Kitchen Waste</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="tax-tab" data-bs-toggle="tab" data-bs-target="#tax" type="button" onclick="loadTax()"><i class="fa-solid fa-file-invoice-dollar me-1"></i> MTD VAT & Transfers</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="feedback-tab" data-bs-toggle="tab" data-bs-target="#feedback" type="button" onclick="loadFeedback()"><i class="fa-solid fa-comments me-1"></i> Guest NPS</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="forecasting-tab" data-bs-toggle="tab" data-bs-target="#forecasting" type="button" onclick="loadForecasting()"><i class="fa-solid fa-brain me-1"></i> AI Forecast</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="staff-tab" data-bs-toggle="tab" data-bs-target="#staff" type="button" onclick="loadStaff()"><i class="fa-solid fa-user-clock me-1"></i> Staff & Tronc</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="reports-tab" data-bs-toggle="tab" data-bs-target="#reports" type="button"><i class="fa-solid fa-file-csv me-1"></i> Reports Exporter</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" type="button"><i class="fa-solid fa-file-contract me-1"></i> Strategy</button>
            </li>
        </ul>

        <div class="tab-content" id="staffTabContent">

            <!-- TAB 1: KDS -->
            <div class="tab-pane fade show active" id="kds" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-fire-burner text-warning me-2"></i>Kitchen Display System (KDS)</h4>
                    <button class="btn btn-sm btn-outline-primary fw-bold" onclick="loadKDS()"><i class="fa-solid fa-rotate me-1"></i> Refresh</button>
                </div>
                <div id="kdsContainer" class="row g-3">
                    <!-- Loaded dynamically -->
                </div>
            </div>

            <!-- TAB 2: Bookings -->
            <div class="tab-pane fade" id="bookings" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-calendar-check text-success me-2"></i>Guest Reservations</h4>
                    <button class="btn btn-sm btn-success fw-bold" data-bs-toggle="modal" data-bs-target="#bookingModal"><i class="fa-solid fa-plus me-1"></i> New Reservation</button>
                </div>
                <div class="card card-custom p-3 bg-white shadow-sm">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Ref</th>
                                    <th>Guest Name</th>
                                    <th>Party</th>
                                    <th>Date & Time</th>
                                    <th>Special Requests</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="bookingsTableBody">
                                <!-- Loaded dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB 3: Inventory Stock & Automated POs -->
            <div class="tab-pane fade" id="inventory" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-boxes-stacked text-primary me-2"></i>Stock & Purchase Orders</h4>
                    <button class="btn btn-sm btn-outline-primary fw-bold" onclick="loadInventory()"><i class="fa-solid fa-rotate me-1"></i> Refresh</button>
                </div>
                <div id="inventoryContainer" class="row g-3 mb-4">
                    <!-- Loaded dynamically -->
                </div>
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h5 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-truck-ramp-box text-info me-2"></i>Supplier Purchase Orders</h5>
                    <div id="purchaseOrdersContainer" class="row g-3">
                        <!-- Loaded dynamically -->
                    </div>
                </div>
            </div>

            <!-- TAB 4: Kitchen Waste Tracker -->
            <div class="tab-pane fade" id="waste" role="tabpanel">
                <div class="row g-4">
                    <div class="col-md-5">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h5 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-trash-can text-danger me-2"></i>Log Kitchen Waste</h5>
                            <form id="wasteLogForm" onsubmit="submitWasteLog(event)">
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Item Wasted</label>
                                    <select id="wasteItemId" class="form-select form-select-sm" required>
                                        <option value="item-1">Fresh Atlantic Cod (Fillet)</option>
                                        <option value="item-2">Wagyu Beef Burger (200g Patty)</option>
                                        <option value="item-3">Truffle Parmesan Fries</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Quantity</label>
                                    <input type="number" id="wasteQty" class="form-control form-control-sm" value="1" min="1" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Reason</label>
                                    <select id="wasteReason" class="form-select form-select-sm">
                                        <option value="SPOILAGE">Spoilage / Expired</option>
                                        <option value="PREP_TRIM">Preparation Trim</option>
                                        <option value="OVER_PREP">Over-Prepared Unsold</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold text-muted">Staff Name</label>
                                    <input type="text" id="wasteStaffName" class="form-control form-control-sm" value="Head Chef" required>
                                </div>
                                <button type="submit" class="btn btn-danger w-100 fw-bold"><i class="fa-solid fa-floppy-disk me-1"></i> Record Waste</button>
                            </form>
                        </div>
                    </div>

                    <div class="col-md-7">
                        <div class="card card-custom p-4 bg-white shadow-sm mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-chart-pie text-warning me-2"></i>Waste Financial Analytics</h5>
                                <a href="/api/waste/report/pdf" target="_blank" class="btn btn-sm btn-outline-danger"><i class="fa-solid fa-file-pdf me-1"></i> Waste Audit PDF</a>
                            </div>
                            <div id="wasteAnalyticsContent" class="row text-center">
                                <!-- Loaded dynamically -->
                            </div>
                        </div>
                        <div class="card card-custom p-3 bg-white shadow-sm">
                            <h6 class="fw-bold mb-2">Recent Kitchen Waste Log</h6>
                            <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
                                <table class="table table-sm table-hover align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th>Time</th>
                                            <th>Item</th>
                                            <th>Qty</th>
                                            <th>Reason</th>
                                            <th>Staff</th>
                                            <th>Cost</th>
                                        </tr>
                                    </thead>
                                    <tbody id="wasteLogsTableBody">
                                        <!-- Loaded dynamically -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 5: MTD VAT & Transfers -->
            <div class="tab-pane fade" id="tax" role="tabpanel">
                <div class="row g-4">
                    <div class="col-md-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-building-columns text-success me-2"></i>HMRC MTD VAT Ledger (UK)</h5>
                                <a href="/api/tax/report/pdf" target="_blank" class="btn btn-sm btn-success fw-bold"><i class="fa-solid fa-file-pdf me-1"></i> HMRC PDF</a>
                            </div>
                            <div id="vatLedgerContainer">
                                <!-- Loaded dynamically -->
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card card-custom p-4 bg-white shadow-sm h-100">
                            <h5 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-truck-arrow-right text-primary me-2"></i>Inter-Venue Stock Transfer</h5>
                            <form id="transferForm" onsubmit="submitStoreTransfer(event)">
                                <div class="row g-2 mb-2">
                                    <div class="col-6">
                                        <label class="form-label small fw-bold text-muted">Source Venue</label>
                                        <select id="transferSourceVenue" class="form-select form-select-sm">
                                            <option value="venue-1">Covent Garden Flagship</option>
                                            <option value="venue-2">Soho Bistro</option>
                                        </select>
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label small fw-bold text-muted">Target Venue</label>
                                        <select id="transferTargetVenue" class="form-select form-select-sm">
                                            <option value="venue-2" selected>Soho Bistro</option>
                                            <option value="venue-1">Covent Garden Flagship</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mb-2">
                                    <label class="form-label small fw-bold text-muted">Stock Item & Qty</label>
                                    <div class="input-group input-group-sm">
                                        <select id="transferItemId" class="form-select">
                                            <option value="item-1">Fresh Atlantic Cod (Fillet)</option>
                                            <option value="item-2">Wagyu Beef Burger (200g Patty)</option>
                                        </select>
                                        <input type="number" id="transferQty" class="form-control" value="10" min="1" style="max-width: 90px;">
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary btn-sm w-100 fw-bold mb-3"><i class="fa-solid fa-paper-plane me-1"></i> Dispatch Transfer Waybill</button>
                            </form>
                            <div id="transfersListContainer" style="max-height: 180px; overflow-y: auto;">
                                <!-- Loaded dynamically -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 6: Guest NPS & Private Feedback -->
            <div class="tab-pane fade" id="feedback" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-star text-warning me-2"></i>Guest Sentiment & NPS</h4>
                    <a href="/api/feedback/report/pdf" target="_blank" class="btn btn-sm btn-outline-primary fw-bold"><i class="fa-solid fa-file-pdf me-1"></i> NPS Report PDF</a>
                </div>
                <div class="row g-3 mb-4">
                    <div class="col-md-4">
                        <div class="card card-custom p-4 bg-white text-center shadow-sm">
                            <span class="small fw-bold text-muted text-uppercase mb-2">Net Promoter Score</span>
                            <div class="fs-1 fw-bold text-primary" id="npsScoreVal">+0</div>
                            <small class="text-muted" id="npsBreakdownText">0 Promoters | 0 Passives | 0 Detractors</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <span class="small fw-bold text-muted text-uppercase mb-2">Sentiment Distribution</span>
                            <div id="sentimentDistributionContent" class="py-2"></div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <span class="small fw-bold text-muted text-uppercase mb-2">Manager Action Alerts</span>
                            <div id="managerAlertsContent" class="py-1"></div>
                        </div>
                    </div>
                </div>
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h5 class="fw-bold mb-3 text-dark">Recent Reviews</h5>
                    <div id="reviewsContainer" class="row g-3"></div>
                </div>
            </div>

            <!-- TAB 7: AI Demand Forecasting -->
            <div class="tab-pane fade" id="forecasting" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-brain text-info me-2"></i>AI Demand Forecasting</h4>
                    <a href="/api/forecasting/report/pdf" target="_blank" class="btn btn-sm btn-info text-dark fw-bold"><i class="fa-solid fa-file-pdf me-1"></i> AI Report PDF</a>
                </div>
                <div class="row g-4">
                    <div class="col-md-7">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h5 class="fw-bold mb-3 text-dark">Predicted Kitchen Prep Demand</h5>
                            <div class="table-responsive">
                                <table class="table table-sm table-hover align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th>Dish</th>
                                            <th>Avg Sales</th>
                                            <th>Predicted Prep</th>
                                            <th>Confidence</th>
                                        </tr>
                                    </thead>
                                    <tbody id="aiForecastTableBody"></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-5">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h5 class="fw-bold mb-3 text-dark">Menu Engineering Matrix</h5>
                            <div id="menuMatrixContainer"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 8: Staff Clock & Tronc -->
            <div class="tab-pane fade" id="staff" role="tabpanel">
                <div class="row g-4">
                    <div class="col-md-5">
                        <div class="card card-custom p-4 bg-white shadow-sm">
                            <h4 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-clock text-primary me-2"></i>Staff Shift Clock</h4>
                            <p class="text-muted small">Enter staff PIN (Manager: <code>1234</code>, Chef: <code>5555</code>, Server: <code>7777</code>)</p>
                            <input type="password" id="staffPinInput" class="form-control text-center fs-3 fw-bold mb-3" maxlength="4" placeholder="••••">
                            <div class="row g-2">
                                <div class="col-6">
                                    <button class="btn btn-success w-100 fw-bold py-2" onclick="staffClockIn()"><i class="fa-solid fa-right-to-bracket me-1"></i> Clock In</button>
                                </div>
                                <div class="col-6">
                                    <button class="btn btn-danger w-100 fw-bold py-2" onclick="staffClockOut()"><i class="fa-solid fa-right-from-bracket me-1"></i> Clock Out</button>
                                </div>
                            </div>
                        </div>
                        <div class="card card-custom p-4 bg-white shadow-sm mt-4">
                            <h5 class="fw-bold mb-2 text-dark"><i class="fa-solid fa-hand-holding-dollar text-warning me-2"></i>12.5% Tronc Pool</h5>
                            <div id="troncSummaryContainer"></div>
                        </div>
                    </div>
                    <div class="col-md-7">
                        <div class="card card-custom p-4 bg-white shadow-sm mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold mb-0 text-dark">Active Roster & Labor Analytics</h5>
                                <span class="badge bg-primary fs-6" id="activeStaffBadge">0 Active</span>
                            </div>
                            <div id="laborSummaryContent" class="row text-center mb-1"></div>
                        </div>
                        <div class="card card-custom p-3 bg-white shadow-sm">
                            <h6 class="fw-bold mb-2">Shift History Log</h6>
                            <div id="shiftHistoryContainer" style="max-height: 250px; overflow-y: auto;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 9: Reports Hub -->
            <div class="tab-pane fade" id="reports" role="tabpanel">
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h4 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-file-csv text-success me-2"></i>Download CSV Business Reports</h4>
                    <div class="row g-3 mt-2">
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-receipt fs-1 text-primary mb-2"></i>
                                <h6 class="fw-bold">Orders CSV</h6>
                                <a href="/api/export/orders/csv" target="_blank" class="btn btn-primary btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card card p-3 border text-center h-100">
                                <i class="fa-solid fa-boxes-stacked fs-1 text-success mb-2"></i>
                                <h6 class="fw-bold">Inventory CSV</h6>
                                <a href="/api/export/inventory/csv" target="_blank" class="btn btn-success btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-comments fs-1 text-warning mb-2"></i>
                                <h6 class="fw-bold">Reviews CSV</h6>
                                <a href="/api/export/reviews/csv" target="_blank" class="btn btn-warning text-dark btn-sm mt-auto"><i class="fa-solid fa-download me-1"></i> Download</a>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3 border text-center h-100">
                                <i class="fa-solid fa-file-pdf fs-1 text-danger mb-2"></i>
                                <h6 class="fw-bold">Daily Z-Report PDF</h6>
                                <a href="/api/finance/z-report/pdf" target="_blank" class="btn btn-danger btn-sm mt-auto"><i class="fa-solid fa-file-pdf me-1"></i> Download</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 10: Strategy Blueprint -->
            <div class="tab-pane fade" id="strategy" role="tabpanel">
                <div class="card card-custom p-4 bg-white shadow-sm">
                    <h3 class="fw-bold mb-3 text-dark">UK Market Strategy Blueprint</h3>
                    <iframe src="/docs/strategy" style="width: 100%; height: 600px; border: 1px solid #cbd5e1; border-radius: 8px;"></iframe>
                </div>
            </div>

        </div>
    </main>

    <!-- Manager PIN Auth Modal -->
    <div class="modal fade" id="pinModal" tabindex="-1" aria-labelledby="pinModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-sm modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="pinModalLabel"><i class="fa-solid fa-user-shield text-warning me-2"></i>Staff Workspace Lock</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center">
                    <p class="text-muted small">Enter Manager PIN to access Staff Workspace (Default: <code>1234</code>)</p>
                    <input type="password" id="pinInput" class="form-control text-center fs-2 fw-bold mb-3" maxlength="4" placeholder="••••">
                    <button type="button" class="btn btn-primary w-100 fw-bold" onclick="authenticatePIN()"><i class="fa-solid fa-unlock me-1"></i> Unlock Staff Workspace</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Review Modal for Guests -->
    <div class="modal fade" id="reviewModal" tabindex="-1" aria-labelledby="reviewModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="reviewModalLabel"><i class="fa-solid fa-heart text-danger me-2"></i>How was your experience?</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center">
                    <p class="text-muted small">Your feedback is sent directly to restaurant management.</p>
                    <div class="fs-2 text-warning mb-3" id="modalStars">
                        <i class="fa-solid fa-star" onclick="setRating(1)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(2)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(3)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(4)"></i>
                        <i class="fa-solid fa-star" onclick="setRating(5)"></i>
                    </div>
                    <input type="hidden" id="selectedRating" value="5">
                    <textarea id="reviewComment" class="form-control mb-3" rows="3" placeholder="Tell us about the food quality or service..."></textarea>
                    <button type="button" class="btn btn-primary w-100 fw-bold" onclick="submitGuestReview()">Submit Private Review</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Split Bill Modal -->
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
    </div>

    <!-- Bootstrap JS & Interactivity Script -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentCart = [];
        let currentLang = 'en';
        let currentCurr = 'GBP';
        let activeTable = 1;
        let isAdminUnlocked = false;
        let currSymbols = { 'GBP': '£', 'EUR': '€', 'USD': '$' };
        let activeOrderForTable = null;

        // URL Parameters detection
        const urlParams = new URLSearchParams(window.location.search);
        if(urlParams.has('table')) {
            activeTable = parseInt(urlParams.get('table')) || 1;
        }

        function updateTableDisplays() {
            document.getElementById('activeTableBadgeNum').innerText = activeTable;
            document.getElementById('desktopTableNum').innerText = activeTable;
            document.getElementById('mobileTableNum').innerText = activeTable;
            document.getElementById('alertTableNum').innerText = activeTable;
            loadTableLiveOrderStatus();
        }

        function setAppMode(mode) {
            if(mode === 'staff') {
                if(!isAdminUnlocked) {
                    const modal = new bootstrap.Modal(document.getElementById('pinModal'));
                    modal.show();
                    return;
                }
                document.getElementById('guestViewSection').classList.add('d-none');
                document.getElementById('mobileCartBar').classList.add('d-none');
                document.getElementById('staffViewSection').classList.remove('d-none');
                document.getElementById('btnGuestView').classList.remove('active');
                document.getElementById('btnStaffView').classList.add('active');
                loadExecutiveKPIs();
                loadKDS();
            } else {
                document.getElementById('staffViewSection').classList.add('d-none');
                document.getElementById('guestViewSection').classList.remove('d-none');
                document.getElementById('mobileCartBar').classList.remove('d-none');
                document.getElementById('btnStaffView').classList.remove('active');
                document.getElementById('btnGuestView').classList.add('active');
            }
        }

        async function authenticatePIN() {
            const pin = document.getElementById('pinInput').value.trim();
            const res = await fetch('/api/auth/pin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: pin })
            });
            const data = await res.json();
            if(data.success) {
                isAdminUnlocked = true;
                const modalEl = document.getElementById('pinModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
                setAppMode('staff');
            } else {
                alert('Invalid Manager PIN. Try 1234');
            }
        }

        function callWaiter() {
            const banner = document.getElementById('waiterAlertBanner');
            banner.classList.remove('d-none');
            setTimeout(() => banner.classList.add('d-none'), 6000);
        }

        function setLanguage(lang, btn) {
            currentLang = lang;
            document.querySelectorAll('#langGroup .btn').forEach(b => b.classList.remove('active', 'btn-dark'));
            document.querySelectorAll('#langGroup .btn').forEach(b => b.classList.add('btn-outline-dark'));
            btn.classList.add('active', 'btn-dark');
            loadMenu();
        }

        function setCurrency(curr, btn) {
            currentCurr = curr;
            document.querySelectorAll('#currGroup .btn').forEach(b => b.classList.remove('active', 'btn-dark'));
            document.querySelectorAll('#currGroup .btn').forEach(b => b.classList.add('btn-outline-dark'));
            btn.classList.add('active', 'btn-dark');
            currentCart = [];
            loadMenu();
        }

        let currentDietary = 'all';
        let excludedAllergens = [];

        function filterMenuDiet(diet, btn) {
            currentDietary = diet;
            document.querySelectorAll('[onclick^="filterMenuDiet"]').forEach(b => {
                b.classList.remove('active', 'btn-success');
                b.classList.add('btn-outline-success');
            });
            btn.classList.remove('btn-outline-success');
            btn.classList.add('active', 'btn-success');
            loadMenu();
        }

        function toggleExclusion(allergen, btn) {
            if(excludedAllergens.includes(allergen)) {
                excludedAllergens = excludedAllergens.filter(a => a !== allergen);
                btn.classList.remove('btn-danger');
                btn.classList.add('btn-outline-danger');
            } else {
                excludedAllergens.push(allergen);
                btn.classList.remove('btn-outline-danger');
                btn.classList.add('btn-danger');
            }
            loadMenu();
        }

        async function loadMenu() {
            let url = `/api/menu/filtered?lang=${currentLang}&currency=${currentCurr}`;
            if(currentDietary && currentDietary !== 'all') {
                url += `&dietary=${currentDietary}`;
            }
            if(excludedAllergens.length > 0) {
                url += `&exclude=${excludedAllergens.join(',')}`;
            }
            const res = await fetch(url);
            const data = await res.json();
            
            const container = document.getElementById('menuContainer');
            if(data.length === 0) {
                container.innerHTML = '<div class="text-muted text-center my-4 fs-6"><i class="fa-solid fa-filter-circle-xmark me-2 text-warning"></i>No dishes match your selected filters.</div>';
                return;
            }

            container.innerHTML = data.map(item => {
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
            }).join('');
            renderCart();
        }

        function addToCart(id, name, price, priceFormatted) {
            currentCart.push({ id, name, price, priceFormatted });
            renderCart();
            checkUpsells();
        }

        function renderCart() {
            const sym = currSymbols[currentCurr] || '£';
            const desktopItems = document.getElementById('cartItems');
            const mobileItems = document.getElementById('mobileCartItems');
            
            if(currentCart.length === 0) {
                const emptyMsg = 'Cart is empty. Select dishes from menu.';
                if(desktopItems) desktopItems.innerHTML = emptyMsg;
                if(mobileItems) mobileItems.innerHTML = emptyMsg;
                document.getElementById('cartTotal').innerText = sym + '0.00';
                document.getElementById('mobileCartTotal').innerText = sym + '0.00';
                document.getElementById('mobileModalCartTotal').innerText = sym + '0.00';
                document.getElementById('mobileCartCount').innerText = '0';
                return;
            }

            let subtotal = 0;
            const html = currentCart.map((item, idx) => {
                subtotal += item.price;
                return `<div class="d-flex justify-content-between align-items-center mb-2 text-dark font-weight-500">
                    <span>${item.name}</span>
                    <div>
                        <span class="me-2 text-primary fw-bold">${item.priceFormatted || sym + item.price.toFixed(2)}</span>
                        <button class="btn btn-link btn-sm text-danger p-0 fw-bold" onclick="removeFromCart(${idx})">&times;</button>
                    </div>
                </div>`;
            }).join('');

            if(desktopItems) desktopItems.innerHTML = html;
            if(mobileItems) mobileItems.innerHTML = html;

            const totalFormatted = sym + subtotal.toFixed(2);
            document.getElementById('cartTotal').innerText = totalFormatted;
            document.getElementById('mobileCartTotal').innerText = totalFormatted;
            document.getElementById('mobileModalCartTotal').innerText = totalFormatted;
            document.getElementById('mobileCartCount').innerText = currentCart.length;
        }

        function removeFromCart(idx) {
            currentCart.splice(idx, 1);
            renderCart();
            checkUpsells();
        }

        async function checkUpsells() {
            const itemIds = currentCart.map(i => i.id);
            if(itemIds.length === 0) {
                document.getElementById('upsellBox').classList.add('d-none');
                return;
            }
            const res = await fetch(`/api/menu?lang=${currentLang}&currency=${currentCurr}`);
            const menu = await res.json();
            
            const hasCod = itemIds.includes('item-1');
            const hasSide = itemIds.includes('item-4');
            const upsellContainer = document.getElementById('upsellContent');

            if(hasCod && !hasSide) {
                const side = menu.find(m => m.id === 'item-4');
                if(side && side.stock_status !== 'OUT_OF_STOCK') {
                    upsellContainer.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="small fw-bold text-dark">${side.name_translated} (+${side.price_formatted})</span>
                            <button class="btn btn-xs btn-warning text-dark py-0 px-2 fw-bold" onclick="addToCart('item-4', '${side.name_translated}', ${side.price}, '${side.price_formatted}')">+ Add</button>
                        </div>
                    `;
                    document.getElementById('upsellBox').classList.remove('d-none');
                    return;
                }
            }
            document.getElementById('upsellBox').classList.add('d-none');
        }

        async function placeOrder() {
            if(currentCart.length === 0) return alert('Please add items to cart first.');
            const promo = document.getElementById('promoInput').value.trim() || document.getElementById('mobilePromoInput').value.trim();
            const res = await fetch('/api/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table_number: activeTable,
                    items: currentCart.map(i => i.id),
                    promo_code: promo
                })
            });
            const order = await res.json();
            const sym = currSymbols[currentCurr] || '£';
            alert(`Order ${order.id} submitted for Table #${activeTable}! Total: ${sym}${order.total.toFixed(2)}`);
            activeOrderForTable = order;
            currentCart = [];
            renderCart();
            document.getElementById('upsellBox').classList.add('d-none');
            loadMenu();
            loadTableLiveOrderStatus();
            
            const reviewModal = new bootstrap.Modal(document.getElementById('reviewModal'));
            reviewModal.show();
        }

        async function loadTableLiveOrderStatus() {
            try {
                const res = await fetch('/api/kds/active');
                const orders = await res.json();
                const tableOrders = orders.filter(o => o.table_number === activeTable);
                const liveCard = document.getElementById('tableLiveOrderCard');

                if(tableOrders.length === 0) {
                    liveCard.classList.add('d-none');
                    return;
                }

                const latestOrder = tableOrders[tableOrders.length - 1];
                activeOrderForTable = latestOrder;
                document.getElementById('liveTableNum').innerText = activeTable;
                document.getElementById('liveOrderRef').innerText = latestOrder.id;
                liveCard.classList.remove('d-none');

                const sRec = document.getElementById('stepReceived');
                const sPrep = document.getElementById('stepPreparing');
                const sReady = document.getElementById('stepReady');

                sRec.className = 'order-step active';
                sPrep.className = 'order-step' + (latestOrder.status === 'PREPARING' || latestOrder.status === 'READY' ? ' active' : '');
                sReady.className = 'order-step' + (latestOrder.status === 'READY' ? ' active' : '');
            } catch(e) { console.error(e); }
        }

        function showSplitBillModal() {
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
        }

        async function loadKDS() {
            const res = await fetch('/api/kds/active');
            const orders = await res.json();
            const container = document.getElementById('kdsContainer');

            if(orders.length === 0) {
                container.innerHTML = '<div class="col-12 text-muted text-center py-4">No active kitchen orders.</div>';
                return;
            }

            container.innerHTML = orders.map(order => `
                <div class="col-md-4">
                    <div class="card card-custom p-3 bg-white shadow-sm">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0 text-dark">${order.id} (Table #${order.table_number})</h6>
                            <span class="badge bg-secondary">${order.status}</span>
                        </div>
                        <ul class="small text-dark mb-3 ps-3">
                            ${order.items.map(i => `<li><strong>${i.name}</strong></li>`).join('')}
                        </ul>
                        <div class="d-flex flex-wrap gap-1 align-items-center">
                            <button class="btn btn-sm btn-success fw-bold" onclick="advanceKDS('${order.id}')">Advance Status</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="cancelOrder('${order.id}')">Refund</button>
                            <a href="/api/invoice/${order.id}/pdf?currency=${currentCurr}" target="_blank" class="btn btn-sm btn-outline-dark"><i class="fa-solid fa-file-pdf text-danger"></i> PDF</a>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        async function advanceKDS(id) {
            await fetch('/api/kds/advance/' + id, { method: 'POST' });
            loadKDS();
            loadTableLiveOrderStatus();
        }

        async function cancelOrder(id) {
            if(!isAdminUnlocked) return alert('Manager PIN required');
            if(!confirm(`Cancel & refund order ${id}?`)) return;
            await fetch('/api/order/cancel/' + id, { method: 'POST' });
            loadKDS();
            loadMenu();
            loadTableLiveOrderStatus();
        }

        function setRating(stars) {
            document.getElementById('selectedRating').value = stars;
            const starElements = document.querySelectorAll('#modalStars i');
            starElements.forEach((s, idx) => {
                s.className = idx < stars ? 'fa-solid fa-star' : 'fa-regular fa-star';
            });
        }

        async function submitGuestReview() {
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
        }

        async function loadExecutiveKPIs() {
            try {
                const res = await fetch('/api/analytics?currency=' + currentCurr);
                const data = await res.json();
                const sym = data.currency_symbol || '£';
                document.getElementById('kpiGrossRev').innerText = sym + data.total_revenue.toFixed(2);
                document.getElementById('kpiTotalOrdersCount').innerText = `${data.total_orders} orders today`;

                const resKds = await fetch('/api/kds/active');
                const kdsOrders = await resKds.json();
                document.getElementById('kpiActiveKds').innerText = kdsOrders.length;

                const resLabor = await fetch('/api/staff/labor-summary?currency=' + currentCurr);
                const labor = await resLabor.json();
                document.getElementById('kpiActiveStaff').innerText = `${labor.active_staff_count} Staff`;
                document.getElementById('kpiLaborCost').innerText = `${sym}${labor.total_labor_cost.toFixed(2)} (${labor.labor_cost_percentage}% labor)`;

                const resNps = await fetch('/api/feedback/nps');
                const nps = await resNps.json();
                document.getElementById('kpiNpsScore').innerText = (nps.nps_score > 0 ? '+' : '') + nps.nps_score.toFixed(0);
                document.getElementById('kpiNpsLabel').innerText = `${nps.total_responses} Guest Feedback`;
            } catch(e) { console.error(e); }
        }

        async function loadVenues() {
            try {
                const res = await fetch('/api/venues');
                const data = await res.json();
                const select = document.getElementById('venueSelect');
                select.innerHTML = data.venues.map(v => `
                    <option value="${v.id}" ${v.id === data.active_venue.id ? 'selected' : ''}>
                        ${v.name} (${v.market} - ${v.currency})
                    </option>
                `).join('');
                document.getElementById('activeVenueName').innerText = `${data.active_venue.name} (${data.active_venue.market})`;
                document.getElementById('activeStoreLabel').innerText = `${data.active_venue.name}`;
            } catch(e) { console.error(e); }
        }

        async function switchVenue(venueId) {
            try {
                const res = await fetch('/api/venues/switch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ venue_id: venueId })
                });
                const data = await res.json();
                if(data.success) {
                    document.getElementById('activeVenueName').innerText = `${data.active_venue.name} (${data.active_venue.market})`;
                    document.getElementById('activeStoreLabel').innerText = `${data.active_venue.name}`;
                    alert(`Switched active venue to: ${data.active_venue.name}`);
                }
            } catch(e) { console.error(e); }
        }

        // Initial Load
        updateTableDisplays();
        loadVenues();
        loadMenu();

        // SSE Real-Time Listener
        if ('EventSource' in window) {
            const evtSource = new EventSource('/api/kds/events');
            evtSource.addEventListener('kds_update', function(e) {
                loadTableLiveOrderStatus();
                if(isAdminUnlocked) {
                    loadKDS();
                    loadExecutiveKPIs();
                }
            });
        }
    </script>
</body>
</html>\"\"\"
"""

with open(app_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace INDEX_HTML = """ ... """
pattern = r'INDEX_HTML = """.*?"""'
new_content = re.sub(pattern, index_html_content.strip(), content, flags=re.DOTALL)

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Responsive Table Guest View successfully updated in app.py!")
