import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional
import threading
from contextlib import contextmanager

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "waiter.db")

class DatabaseStore:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = os.path.abspath(db_path)
        self._lock = threading.Lock()
        self.custom_settings = {}
        self.init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Menu Items Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_items (
                    id TEXT PRIMARY KEY,
                    name_en TEXT NOT NULL,
                    name_fr TEXT NOT NULL,
                    name_ar TEXT NOT NULL,
                    desc_en TEXT,
                    desc_fr TEXT,
                    desc_ar TEXT,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    upsell_ids TEXT,
                    stock_qty INTEGER DEFAULT 30
                )
            """)

            cursor.execute("PRAGMA table_info(menu_items)")
            cols = [col["name"] for col in cursor.fetchall()]
            if "stock_qty" not in cols:
                cursor.execute("ALTER TABLE menu_items ADD COLUMN stock_qty INTEGER DEFAULT 30")
            if "allergens_json" not in cols:
                cursor.execute("ALTER TABLE menu_items ADD COLUMN allergens_json TEXT DEFAULT '[]'")
            if "dietary_json" not in cols:
                cursor.execute("ALTER TABLE menu_items ADD COLUMN dietary_json TEXT DEFAULT '[]'")
            if "is_available" not in cols:
                cursor.execute("ALTER TABLE menu_items ADD COLUMN is_available INTEGER DEFAULT 1")

            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-1'", (json.dumps(["gluten", "fish"]), json.dumps(["halal"])))
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-2'", (json.dumps(["gluten", "eggs", "pork"]), json.dumps([])))
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-3'", (json.dumps(["gluten"]), json.dumps(["vegan", "vegetarian"])))
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-4'", (json.dumps(["eggs"]), json.dumps(["vegetarian", "gluten-free"])))
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-5'", (json.dumps([]), json.dumps(["vegan", "vegetarian", "halal", "gluten-free"])))



            # 2. Orders Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    table_number INTEGER NOT NULL,
                    items_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    subtotal REAL NOT NULL,
                    discount REAL NOT NULL,
                    total REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    venue_id TEXT DEFAULT 'venue-1'
                )
            """)

            cursor.execute("PRAGMA table_info(orders)")
            order_cols = [col["name"] for col in cursor.fetchall()]
            if "venue_id" not in order_cols:
                cursor.execute("ALTER TABLE orders ADD COLUMN venue_id TEXT DEFAULT 'venue-1'")
            if "notes" not in order_cols:
                cursor.execute("ALTER TABLE orders ADD COLUMN notes TEXT DEFAULT ''")
            if "payment_status" not in order_cols:
                cursor.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'UNPAID'")
            if "payment_method" not in order_cols:
                cursor.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT DEFAULT ''")
            if "tip_amount" not in order_cols:
                cursor.execute("ALTER TABLE orders ADD COLUMN tip_amount REAL DEFAULT 0")

            # 3. Venues Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS venues (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    tables_count INTEGER NOT NULL,
                    market TEXT NOT NULL
                )
            """)

            # 4. Promos Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS promos (
                    code TEXT PRIMARY KEY,
                    discount_pct REAL NOT NULL,
                    max_uses INTEGER NOT NULL,
                    current_uses INTEGER NOT NULL,
                    active INTEGER NOT NULL
                )
            """)

            # 5. Reviews Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    table_number INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    private INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 6. Invoices Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_number TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    table_number INTEGER NOT NULL,
                    items_json TEXT NOT NULL,
                    subtotal REAL NOT NULL,
                    discount REAL NOT NULL,
                    vat_rate TEXT NOT NULL,
                    vat_amount REAL NOT NULL,
                    total REAL NOT NULL,
                    currency TEXT NOT NULL,
                    currency_symbol TEXT NOT NULL,
                    issued_at TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)

            # 7. Staff Shifts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS staff_shifts (
                    id TEXT PRIMARY KEY,
                    staff_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    pin TEXT NOT NULL,
                    hourly_rate REAL NOT NULL,
                    clock_in TEXT NOT NULL,
                    clock_out TEXT,
                    total_hours REAL DEFAULT 0.0,
                    labor_cost REAL DEFAULT 0.0,
                    status TEXT NOT NULL
                )
            """)

            # 8. Loyalty Accounts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_accounts (
                    phone_or_email TEXT PRIMARY KEY,
                    guest_name TEXT NOT NULL,
                    points_balance INTEGER DEFAULT 0,
                    tier TEXT DEFAULT 'BRONZE',
                    total_spent REAL DEFAULT 0.0,
                    vouchers_json TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL
                )
            """)

            # 9. Order Splits Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_splits (
                    id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    split_type TEXT NOT NULL,
                    guest_name TEXT NOT NULL,
                    guest_index INTEGER NOT NULL,
                    items_json TEXT DEFAULT '[]',
                    subtotal REAL NOT NULL,
                    service_charge REAL NOT NULL,
                    total REAL NOT NULL,
                    status TEXT NOT NULL,
                    payment_method TEXT,
                    paid_at TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # 10. Food Waste Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS food_waste (
                    id TEXT PRIMARY KEY,
                    item_id TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_cost REAL NOT NULL,
                    total_loss REAL NOT NULL,
                    reason TEXT NOT NULL,
                    staff_name TEXT NOT NULL,
                    logged_at TEXT NOT NULL,
                    venue_id TEXT DEFAULT 'venue-1'
                )
            """)

            # 11. Table Bookings Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS table_bookings (
                    id TEXT PRIMARY KEY,
                    guest_name TEXT NOT NULL,
                    guest_phone TEXT NOT NULL,
                    guest_email TEXT NOT NULL,
                    party_size INTEGER NOT NULL,
                    table_number INTEGER NOT NULL,
                    booking_date TEXT NOT NULL,
                    time_slot TEXT NOT NULL,
                    special_requests TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    venue_id TEXT DEFAULT 'venue-1'
                )
            """)

            # 12. Store Transfers Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS store_transfers (
                    id TEXT PRIMARY KEY,
                    source_venue_id TEXT NOT NULL,
                    target_venue_id TEXT NOT NULL,
                    items_json TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    notes TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # 13. Dining Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dining_tables (
                    id TEXT PRIMARY KEY,
                    table_number INTEGER NOT NULL UNIQUE,
                    capacity INTEGER NOT NULL DEFAULT 4,
                    zone TEXT NOT NULL DEFAULT 'Main Dining Room',
                    status TEXT DEFAULT 'AVAILABLE'
                )
            """)

            # 14. Fridge & Freezer Temperature Logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fridge_logs (
                    id TEXT PRIMARY KEY,
                    appliance TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    status TEXT NOT NULL,
                    recorded_by TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 15. Challenge 25 Refusal Register
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS challenge25_logs (
                    id TEXT PRIMARY KEY,
                    item_name TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    staff_member TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 16. Admin Users Table (Enterprise Security)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    pin TEXT DEFAULT '1234',
                    name TEXT NOT NULL,
                    role TEXT DEFAULT 'MANAGER',
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TEXT,
                    last_login_at TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # 17. Admin Active Sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 18. Admin Security Audit Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_audit_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    event TEXT NOT NULL,
                    ip_address TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            conn.commit()
            self._seed_default_data(cursor, conn)



    def _seed_default_data(self, cursor, conn):
        cursor.execute("SELECT COUNT(*) FROM venues")
        if cursor.fetchone()[0] == 0:
            default_venues = [
                ("venue-1", "Covent Garden Flagship", "12 Floral St, London WC2E 9DH", "GBP", 12, "UK"),
                ("venue-2", "Soho Lounge", "45 Dean St, London W1D 4P", "GBP", 8, "UK"),
                ("venue-3", "Paris Opéra", "8 Boulevard des Capucines, 75009 Paris", "EUR", 15, "EU"),
                ("venue-4", "Manhattan Midtown", "350 5th Ave, New York NY 10118", "USD", 20, "US"),
            ]
            cursor.executemany("""
                INSERT INTO venues (id, name, address, currency, tables_count, market)
                VALUES (?, ?, ?, ?, ?, ?)
            """, default_venues)

        cursor.execute("SELECT COUNT(*) FROM menu_items")
        if cursor.fetchone()[0] == 0:

            default_items = [
                ("item-1", "Fish & Chips", "Poisson & Frites", "سمك وبطاطس",
                 "Fresh Atlantic cod with crispy chips", "Cabillaud frais et frites croustillantes", "قد أطلسي طازج مع بطاطس مقرمشة",
                 14.50, "Mains", json.dumps(["item-4"]), 25),
                ("item-2", "Full English Breakfast", "Petit déjeuner anglais", "إفطار إنجليزي كامل",
                 "Sausages, bacon, eggs, beans, toast", "Saucisses, bacon, œufs, haricots, pain grillé", "نقانق، لحم قديد، بيض، فاصوليا، نخب",
                 11.00, "Mains", json.dumps(["item-5"]), 20),
                ("item-3", "Craft IPA Pint", "Pinte de Bière Artisanale", "بيل ايل حرفية",
                 "Local UK craft brewery IPA", "Bière IPA artisanale britannique", "بيرة بريطانية حرفية",
                 6.20, "Drinks", json.dumps([]), 50),
                ("item-4", "Tartare Sauce & Peas", "Sauce Tartare & Petits Pois", "صلصة التارتار والبسلة",
                 "Homemade tartare sauce & crushed mint peas", "Sauce tartare maison et petits pois écrasés", "صلصة تارتار منزلية وبسلة بالنيداد",
                 2.50, "Sides", json.dumps([]), 35),
                ("item-5", "Fresh Orange Juice", "Jus d'Orange Frais", "عصير برتقال طازج",
                 "Freshly squeezed juice", "Jus fraîchement pressé", "عصير برتقال طازج مكرر",
                 3.80, "Drinks", json.dumps([]), 25)
            ]
            cursor.executemany("""
                INSERT INTO menu_items (id, name_en, name_fr, name_ar, desc_en, desc_fr, desc_ar, price, category, upsell_ids, stock_qty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, default_items)
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-1'", (json.dumps(["gluten", "fish"]), json.dumps(["halal"])))
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-2'", (json.dumps(["gluten", "eggs", "pork"]), json.dumps([])))
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-3'", (json.dumps(["gluten"]), json.dumps(["vegan", "vegetarian"])))
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-4'", (json.dumps(["eggs"]), json.dumps(["vegetarian", "gluten-free"])))
            cursor.execute("UPDATE menu_items SET allergens_json = ?, dietary_json = ? WHERE id = 'item-5'", (json.dumps([]), json.dumps(["vegan", "vegetarian", "halal", "gluten-free"])))

        cursor.execute("SELECT COUNT(*) FROM promos")
        if cursor.fetchone()[0] == 0:
            default_promos = [
                ("WELCOME10", 10.0, 100, 0, 1),
                ("OFFPEAK20", 20.0, 50, 0, 1)
            ]
            cursor.executemany("""
                INSERT INTO promos (code, discount_pct, max_uses, current_uses, active)
                VALUES (?, ?, ?, ?, ?)
            """, default_promos)

        cursor.execute("SELECT COUNT(*) FROM dining_tables")
        if cursor.fetchone()[0] == 0:
            default_tables = [
                ("tbl-1", 1, 2, "Main Dining Room", "AVAILABLE"),
                ("tbl-2", 2, 2, "Main Dining Room", "AVAILABLE"),
                ("tbl-3", 3, 4, "Main Dining Room", "AVAILABLE"),
                ("tbl-4", 4, 4, "Main Dining Room", "OCCUPIED"),
                ("tbl-5", 5, 6, "VIP Booth", "AVAILABLE"),
                ("tbl-6", 6, 6, "VIP Booth", "AVAILABLE"),
                ("tbl-7", 7, 2, "Patio & Terrace", "AVAILABLE"),
                ("tbl-8", 8, 2, "Patio & Terrace", "AVAILABLE"),
                ("tbl-9", 9, 4, "Patio & Terrace", "AVAILABLE"),
                ("tbl-10", 10, 4, "Bar Lounge", "AVAILABLE"),
                ("tbl-11", 11, 4, "Bar Lounge", "AVAILABLE"),
                ("tbl-12", 12, 8, "Banquet Table", "OCCUPIED")
            ]
            cursor.executemany("""
                INSERT INTO dining_tables (id, table_number, capacity, zone, status)
                VALUES (?, ?, ?, ?, ?)
            """, default_tables)

        cursor.execute("SELECT COUNT(*) FROM fridge_logs")
        if cursor.fetchone()[0] == 0:
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            default_fridge = [
                ("frg-1", "Walk-in Meat Chiller", 2.4, "NORMAL (PASS)", "Chef Gordon", now_iso),
                ("frg-2", "Cellar Keg Room", 11.2, "NORMAL (PASS)", "Alice Vance", now_iso),
                ("frg-3", "Fish & Seafood Fridge", 1.8, "NORMAL (PASS)", "Chef Gordon", now_iso)
            ]
            cursor.executemany("""
                INSERT INTO fridge_logs (id, appliance, temperature, status, recorded_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, default_fridge)

        cursor.execute("SELECT COUNT(*) FROM challenge25_logs")
        if cursor.fetchone()[0] == 0:
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            default_c25 = [
                ("c25-1", "Craft IPA Pint", "No valid ID presented (suspected underage)", "Charlie Parker", now_iso),
                ("c25-2", "House Red Wine Bottle", "Expired driving licence presented", "Diana Ross", now_iso)
            ]
            cursor.executemany("""
                INSERT INTO challenge25_logs (id, item_name, reason, staff_member, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, default_c25)

        cursor.execute("SELECT COUNT(*) FROM admin_users")
        if cursor.fetchone()[0] == 0:
            from werkzeug.security import generate_password_hash
            default_pwd = os.environ.get("ADMIN_PASSWORD", "WaiterAdmin2026!")
            pwd_hash = generate_password_hash(default_pwd)
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO admin_users (id, username, password_hash, pin, name, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("usr-admin", "admin", pwd_hash, "1234", "General Manager", "SUPER_ADMIN", now_iso))

        try:
            from src.core.seed_restaurant_menu import seed_menu
            seed_menu(conn)
        except Exception as _e:
            pass

        conn.commit()

    def reset(self):
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders")
            cursor.execute("DELETE FROM reviews")
            cursor.execute("DELETE FROM invoices")
            cursor.execute("DELETE FROM menu_items")
            cursor.execute("DELETE FROM promos")
            cursor.execute("DELETE FROM staff_shifts")
            cursor.execute("DELETE FROM loyalty_accounts")
            cursor.execute("DELETE FROM order_splits")
            cursor.execute("DELETE FROM food_waste")
            cursor.execute("DELETE FROM table_bookings")
            cursor.execute("DELETE FROM store_transfers")
            cursor.execute("DELETE FROM dining_tables")
            cursor.execute("DELETE FROM fridge_logs")
            cursor.execute("DELETE FROM challenge25_logs")
            cursor.execute("DELETE FROM admin_sessions")
            cursor.execute("DELETE FROM admin_audit_logs")
            cursor.execute("DELETE FROM admin_users")
            conn.commit()
            self._seed_default_data(cursor, conn)



    @property
    def menu_items(self) -> Dict[str, dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM menu_items")
            rows = cursor.fetchall()
            items = {}
            for row in rows:
                items[row["id"]] = {
                    "id": row["id"],
                    "name": {"en": row["name_en"], "fr": row["name_fr"], "ar": row["name_ar"]},
                    "description": {"en": row["desc_en"], "fr": row["desc_fr"], "ar": row["desc_ar"]},
                    "price": row["price"],
                    "category": row["category"],
                    "upsell_ids": json.loads(row["upsell_ids"] or "[]"),
                    "stock_qty": row["stock_qty"] if "stock_qty" in row.keys() else 30,
                    "allergens": json.loads(row["allergens_json"]) if ("allergens_json" in row.keys() and row["allergens_json"]) else [],
                    "dietary": json.loads(row["dietary_json"]) if ("dietary_json" in row.keys() and row["dietary_json"]) else [],
                    "kcal": row["kcal"] if "kcal" in row.keys() else 0,
                    "serves": row["serves"] if "serves" in row.keys() else "",
                    "is_featured": bool(row["is_featured"]) if "is_featured" in row.keys() else False,
                    "is_new": bool(row["is_new"]) if "is_new" in row.keys() else False,
                    "image_url": row["image_url"] if "image_url" in row.keys() else "",
                    "modifiers": json.loads(row["modifiers_json"]) if ("modifiers_json" in row.keys() and row["modifiers_json"]) else {},
                    "price_from": bool(row["price_from"]) if "price_from" in row.keys() else False,
                    "is_available": bool(row["is_available"]) if ("is_available" in row.keys() and row["is_available"] is not None) else (row["stock_qty"] > 0 if "stock_qty" in row.keys() else True)
                }
            return items


    @property
    def venues(self) -> Dict[str, dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM venues")
            rows = cursor.fetchall()
            venues_dict = {}
            for row in rows:
                venues_dict[row["id"]] = {
                    "id": row["id"],
                    "name": row["name"],
                    "address": row["address"],
                    "currency": row["currency"],
                    "tables_count": row["tables_count"],
                    "market": row["market"]
                }
            return venues_dict

    @property
    def orders(self) -> Dict[str, dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            rows = cursor.fetchall()
            orders_dict = {}
            for row in rows:
                items, meta = self.unwrap_order_items(row["items_json"])
                keys = row.keys()
                order = {
                    "id": row["id"],
                    "table_number": row["table_number"],
                    "items": items,
                    "status": row["status"],
                    "subtotal": row["subtotal"],
                    "discount": row["discount"],
                    "total": row["total"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "venue_id": row["venue_id"] if "venue_id" in keys else "venue-1",
                    "notes": (row["notes"] or "") if "notes" in keys else "",
                    "payment_status": (row["payment_status"] or "UNPAID") if "payment_status" in keys else "UNPAID",
                    "payment_method": (row["payment_method"] or "") if "payment_method" in keys else "",
                    "tip_amount": (row["tip_amount"] or 0.0) if "tip_amount" in keys else 0.0,
                }
                # Channel metadata (Deliveroo / Uber Eats / Just Eat / Click & Collect / offline sync)
                for meta_key in ("channel", "external_ref", "customer_name", "customer_phone",
                                 "delivery_address", "pickup_slot", "offline_id"):
                    if meta_key in meta:
                        order[meta_key] = meta[meta_key]
                orders_dict[row["id"]] = order
            return orders_dict

    @staticmethod
    def unwrap_order_items(items_json: str):
        """
        Orders normally store a JSON list of items. Channel orders (delivery aggregators,
        click & collect, offline sync) wrap the list in an object with channel metadata.
        Always returns (items_list, metadata_dict) so every module can rely on a list.
        """
        parsed = json.loads(items_json) if items_json else []
        if isinstance(parsed, dict):
            inner = parsed.get("items", [])
            meta = {k: v for k, v in parsed.items() if k != "items"}
            return (inner if isinstance(inner, list) else []), meta
        return parsed, {}


    @property
    def promos(self) -> Dict[str, dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM promos")
            rows = cursor.fetchall()
            promos_dict = {}
            for row in rows:
                promos_dict[row["code"]] = {
                    "code": row["code"],
                    "discount_pct": row["discount_pct"],
                    "max_uses": row["max_uses"],
                    "current_uses": row["current_uses"],
                    "active": bool(row["active"])
                }
            return promos_dict

    @property
    def reviews(self) -> List[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [{
                "id": row["id"],
                "table_number": row["table_number"],
                "rating": row["rating"],
                "comment": row["comment"],
                "private": bool(row["private"]),
                "created_at": row["created_at"]
            } for row in rows]

    @property
    def invoices(self) -> Dict[str, dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices")
            rows = cursor.fetchall()
            invoices_dict = {}
            for row in rows:
                invoices_dict[row["order_id"]] = {
                    "invoice_number": row["invoice_number"],
                    "order_id": row["order_id"],
                    "table_number": row["table_number"],
                    "items": json.loads(row["items_json"]),
                    "subtotal": row["subtotal"],
                    "discount": row["discount"],
                    "vat_rate": row["vat_rate"],
                    "vat_amount": row["vat_amount"],
                    "total": row["total"],
                    "currency": row["currency"],
                    "currency_symbol": row["currency_symbol"],
                    "issued_at": row["issued_at"],
                    "status": row["status"]
                }
            return invoices_dict

    @property
    def shifts(self) -> List[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM staff_shifts ORDER BY clock_in DESC")
            rows = cursor.fetchall()
            return [{
                "id": row["id"],
                "staff_name": row["staff_name"],
                "role": row["role"],
                "pin": row["pin"],
                "hourly_rate": row["hourly_rate"],
                "clock_in": row["clock_in"],
                "clock_out": row["clock_out"],
                "total_hours": row["total_hours"],
                "labor_cost": row["labor_cost"],
                "status": row["status"]
            } for row in rows]

    @property
    def loyalty_accounts(self) -> Dict[str, dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM loyalty_accounts")
            rows = cursor.fetchall()
            accounts = {}
            for row in rows:
                accounts[row["phone_or_email"]] = {
                    "phone_or_email": row["phone_or_email"],
                    "guest_name": row["guest_name"],
                    "points_balance": row["points_balance"],
                    "tier": row["tier"],
                    "total_spent": row["total_spent"],
                    "vouchers": json.loads(row["vouchers_json"] or "[]"),
                    "created_at": row["created_at"]
                }
            return accounts



    @property
    def invoice_counter(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM invoices")
            count = cursor.fetchone()[0]
            return 1001 + count

    # --- Write Operations ---
    def deduct_stock(self, item_id: str, qty: int = 1) -> bool:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stock_qty FROM menu_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if row and row["stock_qty"] >= qty:
                new_qty = row["stock_qty"] - qty
                cursor.execute("UPDATE menu_items SET stock_qty = ? WHERE id = ?", (new_qty, item_id))
                conn.commit()
                return True
            return False

    def restock_item(self, item_id: str, qty: int = 20) -> Optional[int]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stock_qty FROM menu_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if row:
                new_qty = row["stock_qty"] + qty
                cursor.execute("UPDATE menu_items SET stock_qty = ? WHERE id = ?", (new_qty, item_id))
                conn.commit()
                return new_qty
            return None

    def update_stock_qty(self, item_id: str, qty: int) -> Optional[int]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE menu_items SET stock_qty = ? WHERE id = ?", (qty, item_id))
            conn.commit()
            return qty

    def add_order(self, order_data: dict) -> dict:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0] + 1
            order_id = f"ORD-{order_count:04d}"

            now_iso = datetime.now(timezone.utc).isoformat()
            order = {
                "id": order_id,
                "table_number": order_data.get("table_number", 1),
                "items": order_data.get("items", []),
                "status": "New",
                "subtotal": order_data.get("subtotal", 0.0),
                "discount": order_data.get("discount", 0.0),
                "total": order_data.get("total", 0.0),
                "created_at": now_iso,
                "updated_at": now_iso,
                "venue_id": order_data.get("venue_id", "venue-1"),
                "notes": (order_data.get("notes") or "").strip(),
                "payment_status": order_data.get("payment_status", "UNPAID"),
                "payment_method": order_data.get("payment_method", ""),
                "tip_amount": round(float(order_data.get("tip_amount", 0.0)), 2),
            }

            cursor.execute("""
                INSERT INTO orders (id, table_number, items_json, status, subtotal, discount, total, created_at, updated_at, venue_id, notes, payment_status, payment_method, tip_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order["id"],
                order["table_number"],
                json.dumps(order["items"]),
                order["status"],
                order["subtotal"],
                order["discount"],
                order["total"],
                order["created_at"],
                order["updated_at"],
                order["venue_id"],
                order["notes"],
                order["payment_status"],
                order["payment_method"],
                order["tip_amount"]
            ))

            
            for item in order["items"]:
                item_id = item.get("item_id")
                if item_id:
                    cursor.execute("UPDATE menu_items SET stock_qty = MAX(0, stock_qty - 1) WHERE id = ?", (item_id,))

            conn.commit()
            return order

    def update_order_status(self, order_id: str, new_status: str) -> Optional[dict]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                UPDATE orders SET status = ?, updated_at = ? WHERE id = ?
            """, (new_status, now_iso, order_id))
            conn.commit()
            return self.orders.get(order_id)

    def increment_promo_use(self, code: str) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute("UPDATE promos SET current_uses = current_uses + 1 WHERE code = ?", (code,))
            conn.commit()

    def mark_order_paid(self, order_id: str, payment_method: str = "", tip_amount: float = 0.0) -> Optional[dict]:
        """
        Records settlement without touching the kitchen status, so a ticket that is
        still being prepared never disappears from the KDS just because the guest paid.
        """
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                UPDATE orders
                SET payment_status = 'PAID', payment_method = ?, tip_amount = ?, updated_at = ?
                WHERE id = ?
            """, (payment_method, float(tip_amount or 0.0), now_iso, order_id))
            conn.commit()
        return self.orders.get(order_id)

    def cancel_order(self, order_id: str) -> Optional[dict]:
        """
        Cancels order, returns items to inventory stock, and marks invoice as REFUNDED.
        """
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            order_row = cursor.fetchone()
            if not order_row:
                return None

            if order_row["status"] == "CANCELLED":
                return self.orders.get(order_id)

            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute("UPDATE orders SET status = 'CANCELLED', updated_at = ? WHERE id = ?", (now_iso, order_id))

            # Return stock back to inventory (channel orders wrap their items in an object)
            items, _meta = self.unwrap_order_items(order_row["items_json"])
            for item in items:
                item_id = item.get("item_id")
                if item_id:
                    cursor.execute("UPDATE menu_items SET stock_qty = stock_qty + 1 WHERE id = ?", (item_id,))

            # Update invoice status to REFUNDED if invoice exists
            cursor.execute("UPDATE invoices SET status = 'REFUNDED' WHERE order_id = ?", (order_id,))

            conn.commit()
            return self.orders.get(order_id)

    def add_review(self, review_data: dict) -> dict:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM reviews")
            rev_count = cursor.fetchone()[0] + 1
            rev_id = f"REV-{rev_count:04d}"

            now_iso = datetime.now(timezone.utc).isoformat()
            review = {
                "id": rev_id,
                "table_number": review_data.get("table_number"),
                "rating": review_data.get("rating", 5),
                "comment": review_data.get("comment", ""),
                "private": True,
                "created_at": now_iso
            }

            cursor.execute("""
                INSERT INTO reviews (id, table_number, rating, comment, private, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                review["id"],
                review["table_number"],
                review["rating"],
                review["comment"],
                1,
                review["created_at"]
            ))
            conn.commit()
            return review

    # --- Admin CRUD & Control Methods ---
    def add_menu_item(self, item_data: dict) -> dict:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            item_id = item_data.get("id")
            if not item_id:
                import uuid
                item_id = f"item-{uuid.uuid4().hex[:8]}"

            name_val = item_data.get("name")
            if isinstance(name_val, dict):
                name_en = item_data.get("name_en") or name_val.get("en", "New Dish")
                name_fr = item_data.get("name_fr") or name_val.get("fr", "")
                name_ar = item_data.get("name_ar") or name_val.get("ar", "")
            else:
                name_en = item_data.get("name_en") or (str(name_val) if name_val else "New Dish")
                name_fr = item_data.get("name_fr", "")
                name_ar = item_data.get("name_ar", "")

            desc_val = item_data.get("description")
            if isinstance(desc_val, dict):
                desc_en = item_data.get("desc_en") or desc_val.get("en", "")
                desc_fr = item_data.get("desc_fr") or desc_val.get("fr", "")
                desc_ar = item_data.get("desc_ar") or desc_val.get("ar", "")
            else:
                desc_en = item_data.get("desc_en") or (str(desc_val) if desc_val else "")
                desc_fr = item_data.get("desc_fr", "")
                desc_ar = item_data.get("desc_ar", "")

            price = float(item_data.get("price", 9.99))
            category = item_data.get("category", "Mains")
            upsell_ids = json.dumps(item_data.get("upsell_ids", []))
            stock_qty = int(item_data.get("stock_qty", 30))
            allergens_json = json.dumps(item_data.get("allergens", []))
            dietary_json = json.dumps(item_data.get("dietary", []))
            kcal = int(item_data.get("kcal", 0))
            serves = str(item_data.get("serves", ""))
            is_featured = 1 if item_data.get("is_featured") else 0
            is_new = 1 if item_data.get("is_new") else 0
            image_url = str(item_data.get("image_url", ""))
            modifiers_json = json.dumps(item_data.get("modifiers", {}))
            price_from = 1 if item_data.get("price_from") else 0
            is_available = 0 if item_data.get("is_available") is False else 1

            cursor.execute("""
                INSERT OR REPLACE INTO menu_items (
                    id, name_en, name_fr, name_ar, desc_en, desc_fr, desc_ar,
                    price, category, upsell_ids, stock_qty, allergens_json, dietary_json,
                    kcal, serves, is_featured, is_new, image_url, modifiers_json, price_from, is_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id, name_en, name_fr, name_ar, desc_en, desc_fr, desc_ar,
                price, category, upsell_ids, stock_qty, allergens_json, dietary_json,
                kcal, serves, is_featured, is_new, image_url, modifiers_json, price_from, is_available
            ))
            conn.commit()
            return self.menu_items.get(item_id, {})

    def update_menu_item(self, item_id: str, item_data: dict) -> Optional[dict]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                return None

            name_val = item_data.get("name")
            if isinstance(name_val, dict):
                name_en = item_data.get("name_en") or name_val.get("en", row["name_en"])
                name_fr = item_data.get("name_fr") or name_val.get("fr", row["name_fr"])
                name_ar = item_data.get("name_ar") or name_val.get("ar", row["name_ar"])
            else:
                name_en = item_data.get("name_en") or (str(name_val) if name_val else row["name_en"])
                name_fr = item_data.get("name_fr", row["name_fr"])
                name_ar = item_data.get("name_ar", row["name_ar"])

            desc_val = item_data.get("description")
            if isinstance(desc_val, dict):
                desc_en = item_data.get("desc_en") or desc_val.get("en", row["desc_en"])
                desc_fr = item_data.get("desc_fr") or desc_val.get("fr", row["desc_fr"])
                desc_ar = item_data.get("desc_ar") or desc_val.get("ar", row["desc_ar"])
            else:
                desc_en = item_data.get("desc_en") or (str(desc_val) if desc_val else row["desc_en"])
                desc_fr = item_data.get("desc_fr", row["desc_fr"])
                desc_ar = item_data.get("desc_ar", row["desc_ar"])

            price = float(item_data.get("price", row["price"]))
            category = item_data.get("category", row["category"])
            stock_qty = int(item_data.get("stock_qty", row["stock_qty"] if "stock_qty" in row.keys() else 30))
            kcal = int(item_data.get("kcal", row["kcal"] if "kcal" in row.keys() else 0))
            image_url = item_data.get("image_url", row["image_url"] if "image_url" in row.keys() else "")

            allergens_json = json.dumps(item_data.get("allergens")) if "allergens" in item_data else (row["allergens_json"] if "allergens_json" in row.keys() else "[]")
            dietary_json = json.dumps(item_data.get("dietary")) if "dietary" in item_data else (row["dietary_json"] if "dietary_json" in row.keys() else "[]")

            if "is_available" in item_data:
                is_available = 0 if item_data["is_available"] is False else 1
            else:
                is_available = row["is_available"] if "is_available" in row.keys() else 1

            cursor.execute("""
                UPDATE menu_items SET
                    name_en = ?, name_fr = ?, name_ar = ?,
                    desc_en = ?, desc_fr = ?, desc_ar = ?,
                    price = ?, category = ?, stock_qty = ?, kcal = ?,
                    image_url = ?, allergens_json = ?, dietary_json = ?, is_available = ?
                WHERE id = ?
            """, (
                name_en, name_fr, name_ar, desc_en, desc_fr, desc_ar,
                price, category, stock_qty, kcal, image_url, allergens_json, dietary_json, is_available, item_id
            ))
            conn.commit()
            return self.menu_items.get(item_id)

    def delete_menu_item(self, item_id: str) -> bool:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_menu_item_86(self, item_id: str, is_available: Optional[bool] = None) -> Optional[dict]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                return None
            curr_avail = bool(row["is_available"]) if ("is_available" in row.keys() and row["is_available"] is not None) else (row["stock_qty"] > 0)
            new_avail = (not curr_avail) if is_available is None else is_available
            new_val = 1 if new_avail else 0
            cursor.execute("UPDATE menu_items SET is_available = ? WHERE id = ?", (new_val, item_id))
            conn.commit()
            return self.menu_items.get(item_id)

    def get_tables(self) -> List[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dining_tables ORDER BY table_number ASC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def add_or_update_table(self, table_number: int, capacity: int = 4, zone: str = "Main Dining Room", status: str = "AVAILABLE") -> dict:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            table_id = f"tbl-{table_number}"
            cursor.execute("""
                INSERT INTO dining_tables (id, table_number, capacity, zone, status)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(table_number) DO UPDATE SET
                    capacity = excluded.capacity,
                    zone = excluded.zone,
                    status = excluded.status
            """, (table_id, table_number, capacity, zone, status))
            conn.commit()
            return {"id": table_id, "table_number": table_number, "capacity": capacity, "zone": zone, "status": status}

    def delete_table(self, table_number: int) -> bool:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dining_tables WHERE table_number = ?", (table_number,))
            conn.commit()
            return cursor.rowcount > 0

    def update_table_status(self, table_number: int, status: str) -> bool:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE dining_tables SET status = ? WHERE table_number = ?", (status, table_number))
            conn.commit()
            return cursor.rowcount > 0

    def get_fridge_logs(self) -> List[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fridge_logs ORDER BY created_at DESC LIMIT 50")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def add_fridge_log(self, appliance: str, temperature: float, recorded_by: str = "Manager") -> dict:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            import uuid
            log_id = f"frg-{uuid.uuid4().hex[:8]}"
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            status = "ALERT (HIGH)" if temperature > 8.0 else ("ALERT (LOW)" if temperature < -25.0 else "NORMAL (PASS)")
            cursor.execute("""
                INSERT INTO fridge_logs (id, appliance, temperature, status, recorded_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (log_id, appliance, float(temperature), status, recorded_by, now_iso))
            conn.commit()
            return {"id": log_id, "appliance": appliance, "temperature": float(temperature), "status": status, "recorded_by": recorded_by, "created_at": now_iso}

    def get_challenge25_logs(self) -> List[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM challenge25_logs ORDER BY created_at DESC LIMIT 50")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def add_challenge25_log(self, item_name: str, reason: str, staff_member: str = "Server") -> dict:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            import uuid
            log_id = f"c25-{uuid.uuid4().hex[:8]}"
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                INSERT INTO challenge25_logs (id, item_name, reason, staff_member, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (log_id, item_name, reason, staff_member, now_iso))
            conn.commit()
            return {"id": log_id, "item_name": item_name, "reason": reason, "staff_member": staff_member, "created_at": now_iso}

db = DatabaseStore()
