# The Waiter — Cloud Hospitality Operating System

> **One system for every table, ticket, and till.** Built specifically for how modern UK pubs, restaurants, and bars trade.

[![Live Web App](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-c8a86b?style=for-the-badge&logo=github)](https://me-mehdi.github.io/Waiter/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-0f1520?style=for-the-badge&logo=python)](https://python.org)
[![Realtime Engine](https://img.shields.io/badge/Realtime-MQTT%20Dual--Broker-0284c7?style=for-the-badge&logo=mqtt)](https://mqtt.org)
[![Database](https://img.shields.io/badge/Database-SQLite%203%20Persistent-059669?style=for-the-badge&logo=sqlite)](https://sqlite.org)
[![UK Compliance](https://img.shields.io/badge/UK%20Statutory-Natasha's%20Law%20%7C%20Tips%20Act%202024-dc2626?style=for-the-badge)](https://www.legislation.gov.uk)
[![Deploy Ready](https://img.shields.io/badge/Deploy-CloudPanel%20%7C%20Docker%20%7C%20Render-6366f1?style=for-the-badge)](https://www.cloudpanel.io)

---

## 🌐 Live Deployments & Application Links

All modules are live and deployed on GitHub Pages with instant cross-device synchronization:

| Application Module | Live URL | Description |
|:---|:---|:---|
| **Guest Mobile Ordering** | [me-mehdi.github.io/Waiter/order/menu/](https://me-mehdi.github.io/Waiter/order/menu/) | Direct Table QR order web app (`?table=X`), allergen filtering, modifiers, and cart drawer. |
| **Direct Table 4 QR Demo** | [me-mehdi.github.io/Waiter/order/menu/?table=4](https://me-mehdi.github.io/Waiter/order/menu/?table=4) | Live simulation of a diner scanning the Table 4 QR stand card. |
| **Kitchen Display System (KDS)** | [me-mehdi.github.io/Waiter/admin/kitchen/](https://me-mehdi.github.io/Waiter/admin/kitchen/) | Dedicated kitchen tablet screen with ticket columns (**NEW**, **PREPARING**, **READY**), sound alerts, and order highlighting. |
| **Master Admin Dashboard** | [me-mehdi.github.io/Waiter/admin/](https://me-mehdi.github.io/Waiter/admin/) | Full management suite for live orders, dishes, categories, floor plan, staff, compliance logs, and QR code stands. |
| **Admin Secure Login** | [me-mehdi.github.io/Waiter/admin/login/](https://me-mehdi.github.io/Waiter/admin/login/) | PBKDF2/SHA-256 password & PIN authentication with audit logging and auto-expiry. |
| **UK Showcase Suite** | [me-mehdi.github.io/Waiter/](https://me-mehdi.github.io/Waiter/) | Multi-device demonstration hub featuring live guest phone frame, kitchen display, POS, reservations, and cellar management. |

---

## 💾 Where to Find the Database

The persistent database for **The Waiter** is stored as a single, high-performance SQLite 3 database file.

### 1. Database File Location

- **Local Development / Repository Root**:
  ```bash
  /Users/.../Waiter/waiter.db
  ```
- **Server Deployment (CloudPanel / Hostinger VPS / Docker)**:
  ```bash
  /home/<user>/htdocs/<domain>/waiter.db
  ```
  *(or your configured Python application root directory)*.
- **Python Database Store Module**:
  [`src/core/db.py`](file:///Users/elmehdinidazi/Downloads/Waiter/src/core/db.py) initializes, validates, migrates, and connects to `waiter.db` with thread-safe locking and connection pooling.

### 2. Database Tables & Schemas

The `waiter.db` file contains 17 relational tables:

| Table Name | Description | Key Fields |
|:---|:---|:---|
| `menu_items` | Full menu catalog & dishes | `id`, `name_en`, `name_fr`, `name_ar`, `desc_en`, `price`, `category`, `allergens_json`, `dietary_json`, `stock_qty`, `is_available` |
| `orders` | Dine-in & takeout orders | `id`, `table_number`, `items_json`, `status`, `subtotal`, `discount`, `total`, `created_at`, `updated_at`, `venue_id` |
| `dining_tables` | Restaurant floor plan & tables | `table_number`, `capacity`, `zone` (Indoor/Garden/Bar), `status` (Available/Occupied/Reserved) |
| `admin_users` | Authorized managers & owners | `id`, `username`, `password_hash` (PBKDF2), `role`, `pin_code`, `created_at` |
| `admin_sessions` | Secure session tokens | `session_token`, `user_id`, `created_at`, `expires_at`, `ip_address`, `user_agent` |
| `admin_audit_logs` | Tamper-evident admin audit trail | `id`, `timestamp`, `user_id`, `action`, `details_json`, `ip_address` |
| `table_bookings` | Guest reservations & covers | `id`, `guest_name`, `guest_phone`, `table_number`, `covers`, `booking_time`, `preauth_held` |
| `staff_shifts` | Staff clock-in/out & rota | `id`, `staff_name`, `role`, `clock_in`, `clock_out`, `hourly_rate`, `tronc_points` |
| `fridge_logs` | EHO statutory temperature logs | `id`, `fridge_name`, `temperature`, `recorded_by`, `status` (PASS/FAIL), `timestamp` |
| `loyalty_accounts` | Customer loyalty balances | `id`, `phone_number`, `points_balance`, `tier`, `last_visit` |
| `food_waste` | Kitchen waste tracking | `id`, `item_id`, `weight_kg`, `cost`, `reason`, `logged_at` |
| `challenge25_logs` | Statutory age verification records | `id`, `order_id`, `staff_name`, `id_verified`, `timestamp` |
| `invoices` | VAT receipts (20% breakdown) | `id`, `order_id`, `subtotal`, `vat_amount`, `grand_total`, `issued_at` |
| `order_splits` | Split-bill transactions | `id`, `order_id`, `split_index`, `amount`, `payment_method`, `paid_at` |
| `promos` | Discount vouchers & codes | `code`, `discount_percent`, `valid_until`, `usage_count` |
| `reviews` | Diner feedback & star ratings | `id`, `order_id`, `rating`, `comment`, `created_at` |
| `venues` | Multi-store location configs | `id`, `name`, `currency`, `timezone`, `vat_number`, `address` |

### 3. How to Inspect & Query the Database

You can inspect or query `waiter.db` at any time using your terminal or free GUI tools:

```bash
# Open interactive SQLite shell
sqlite3 waiter.db

# Show all tables
.tables

# View active menu dishes
SELECT id, name_en, price, category FROM menu_items LIMIT 5;

# View recent orders and table numbers
SELECT id, table_number, status, total, created_at FROM orders ORDER BY created_at DESC LIMIT 5;

# Exit SQLite shell
.quit
```

> **Recommended GUI Tools**:
> - [DB Browser for SQLite](https://sqlitebrowser.org/) (Free open-source GUI for macOS, Windows, Linux).
> - [DBeaver](https://dbeaver.io/) or the **SQLite Viewer** VS Code / Cursor extension.

### 4. Data Persistence on GitHub Pages vs Server

- **On GitHub Pages (`me-mehdi.github.io`)**: GitHub Pages is a static file CDN, so Python code cannot write to a server SQLite database. The application runs a browser-side data engine that persists changes in `localStorage` and replicates live catalog changes and incoming orders across all connected devices using **dual-broker MQTT over WebSockets** (`broker.hivemq.com` & `broker.emqx.io`).
- **On VPS / CloudPanel (`python src/app.py`)**: The full Flask backend interacts directly with `waiter.db` with ACID transaction safety and automatic schema seeding.

---

## ⚡ Direct Table QR Code Routing

When diners scan table QR stand cards or stickers, they are taken directly to their table:

1. **URL Format**:
   - `https://me-mehdi.github.io/Waiter/order/menu/?table=4` (or `?tbl=4`, `?t=4`)
2. **Instant Pre-selection**:
   - The ordering application automatically detects the table parameter, locks in the table context, and persists it in `sessionStorage` and `localStorage`.
   - **Header Tag**: Shows `TABLE 4` with a quick-switch option.
   - **Order Summary**: Shows `Table 4 · Dine-in`.
   - **Checkout**: Automatically fills `Table 4` with no typing required.
   - **Active Banner**: Displays visual confirmation: *"📍 Table 4 · Direct QR Order Active"*.
3. **QR Generator in Master Admin**:
   - Managers can navigate to **Admin $\rightarrow$ Tables**, click **QR** on any table, preview the scannable code, switch between tables (`T1` to `T12`), download printable high-resolution PNGs, or print foldable tent cards.

---

## 🔄 Real-Time Kitchen Display System (KDS) & Multi-Device Sync

The Waiter connects diners, kitchen staff, and managers in real-time without relying on rate-limited polling:

- **Dual-Broker MQTT Failover**: Connects via WebSockets over TLS to `broker.hivemq.com:8884` with automatic fallback to `broker.emqx.io:8084`.
- **Sub-Second Ticket Delivery**: As soon as a customer clicks **"Pay & Place Order"**, the order is broadcast across MQTT topics (`waiter/venue/live/orders`).
- **Kitchen Progression**: Kitchen staff advance tickets from **NEW** $\rightarrow$ **PREPARING** $\rightarrow$ **READY** with a single tap.
- **Customer Feedback**: The customer's mobile phone updates live in real-time (e.g., *"CHEF PREPARING (ON GRILL)"*), accompanied by audio chime alerts.
- **Order Highlighting**: When opened via `?highlight=ORD-xxxx`, the KDS board automatically scrolls to the ticket, pulses with an amber glow, and displays a **`★ YOUR ORDER`** badge.

---

## 🛡️ Security & Access Control

- **PBKDF2 Password Hashing**: Passwords stored using PBKDF2 with SHA-256 and unique per-user salts.
- **Session Tokens**: Cryptographically secure 256-bit session tokens with automatic timeout and device tracking.
- **Admin Audit Trail**: Every sensitive change (dish creation, deletion, price update, stock toggle) is permanently recorded in `admin_audit_logs`.
- **Open KDS Architecture**: Kitchen display screens on kitchen wall tablets remain accessible without session timeouts to prevent service interruptions during dinner rush.

---

## 🇬🇧 UK Statutory Hospitality Features

- **Natasha's Law (Food Information Regulations 2021)**: Full mandatory allergen declarations across all 14 statutory allergens (Gluten, Crustaceans, Eggs, Fish, Peanuts, Soybeans, Milk, Nuts, Celery, Mustard, Sesame, Sulphites, Lupin, Molluscs).
- **Challenge 25 Policy**: Prominent age verification cues on alcoholic beverages and draught pints, requiring ID checks upon delivery.
- **Employment (Allocation of Tips) Act 2024**: Transparent 100% tronc point distribution tracking without employer deductions.
- **HMRC VAT Breakdown**: Detailed 20% Standard Rate calculations on digital and printable VAT receipts.
- **EHO Food Safety Logging**: Daily statutory digital logs for fridge and freezer temperatures.

---

## 🚀 Quickstart & Local Development

### 1. Clone & Set Up

```bash
git clone https://github.com/me-mehdi/Waiter.git
cd Waiter

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Automated Verification Tests

```bash
# Verify Table QR Routing
python scratch/test_qr_table_routing.py

# Verify Multi-Device KDS Sync
python scratch/verify_all_three_kds.py
```

### 3. Launch the Server

```bash
python src/app.py
```
Open **[http://127.0.0.1:5050](http://127.0.0.1:5050)** in your browser.

---

## 🌐 Production Deployment Guide (CloudPanel on Hostinger VPS)

CloudPanel provides a fast, lightweight, and low-cost environment on a Hostinger VPS:

1. **Create Python Application**:
   - In CloudPanel, click **Add Site** $\rightarrow$ **Python Application**.
   - Set Domain Name (e.g., `pos.yourdomain.com`).
   - Select **Python 3.11** or **3.12**.
2. **Deploy Code**:
   ```bash
   cd /home/<site-user>/htdocs/<domain>/
   git clone https://github.com/me-mehdi/Waiter.git .
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configure Gunicorn Entrypoint**:
   - Entry file: `src/app.py`
   - Callable: `app`
   - Command: `gunicorn -w 4 -b 127.0.0.1:5050 src.app:app`
4. **Database File & Permissions**:
   - Ensure the site user owns `waiter.db`:
     ```bash
     touch waiter.db
     chmod 664 waiter.db
     ```
5. **Enable Free SSL**:
   - In CloudPanel site settings, navigate to **SSL/TLS** and click **Create Let's Encrypt Certificate**.

---

## 📄 License & Attribution

Built with pride for British hospitality operators, pubs, and independent restaurateurs.  
Copyright © 2024–2026 The Waiter Project. All rights reserved.
