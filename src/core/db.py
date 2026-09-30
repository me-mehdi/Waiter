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
                    updated_at TEXT NOT NULL
                )
            """)

            # 3. Promos Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS promos (
                    code TEXT PRIMARY KEY,
                    discount_pct REAL NOT NULL,
                    max_uses INTEGER NOT NULL,
                    current_uses INTEGER NOT NULL,
                    active INTEGER NOT NULL
                )
            """)

            # 4. Reviews Table
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

            # 5. Invoices Table
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

            conn.commit()
            self._seed_default_data(cursor, conn)

    def _seed_default_data(self, cursor, conn):
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

        conn.commit()

    def reset(self):
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders")
            cursor.execute("DELETE FROM reviews")
            cursor.execute("DELETE FROM invoices")
            cursor.execute("DELETE FROM menu_items")
            cursor.execute("DELETE FROM promos")
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
                    "stock_qty": row["stock_qty"] if "stock_qty" in row.keys() else 30
                }
            return items

    @property
    def orders(self) -> Dict[str, dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            rows = cursor.fetchall()
            orders_dict = {}
            for row in rows:
                orders_dict[row["id"]] = {
                    "id": row["id"],
                    "table_number": row["table_number"],
                    "items": json.loads(row["items_json"]),
                    "status": row["status"],
                    "subtotal": row["subtotal"],
                    "discount": row["discount"],
                    "total": row["total"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
            return orders_dict

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
                "updated_at": now_iso
            }

            cursor.execute("""
                INSERT INTO orders (id, table_number, items_json, status, subtotal, discount, total, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order["id"],
                order["table_number"],
                json.dumps(order["items"]),
                order["status"],
                order["subtotal"],
                order["discount"],
                order["total"],
                order["created_at"],
                order["updated_at"]
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

            # Return stock back to inventory
            items = json.loads(order_row["items_json"])
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

db = DatabaseStore()
