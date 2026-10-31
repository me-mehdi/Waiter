import json
import sqlite3
from typing import List, Dict, Optional, Union
from datetime import datetime, timezone
from src.core.db import db
from src.core.config import Config

class BillSplittingModule:
    """
    Table Bill Splitting & Group Payment Module for The Waiter.
    Supports:
      1. Equal Bill Splitting (dividing bill total & 12.5% service charge evenly across N guests)
      2. Itemized Bill Splitting (assigning specific order items to individual guests)
      3. Partial & Full Group Settlement Tracking
      4. Individual Monospaced Guest Sub-Receipt Generation (ESC/POS compatible)
    """
    DEFAULT_SERVICE_CHARGE_RATE = 0.125

    def split_evenly(self, order_id: str, num_guests: int, include_service_charge: bool = True) -> Dict:
        """
        Splits an order bill evenly among N guests.
        """
        if num_guests < 2:
            raise ValueError("Number of guests for splitting must be at least 2.")

        order = db.orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found.")

        subtotal = float(order["subtotal"])
        discount = float(order["discount"])
        net_subtotal = max(0.0, subtotal - discount)
        service_charge = round(net_subtotal * self.DEFAULT_SERVICE_CHARGE_RATE, 2) if include_service_charge else 0.0
        grand_total = round(net_subtotal + service_charge, 2)

        # Distribute base subtotal & service charge across guests
        base_subtotal_per_guest = round(net_subtotal / num_guests, 2)
        sc_per_guest = round(service_charge / num_guests, 2)
        total_per_guest = round(grand_total / num_guests, 2)

        # Calculate rounding remainders (allocated to last guest to ensure sum matches grand total)
        remainder_subtotal = round(net_subtotal - (base_subtotal_per_guest * num_guests), 2)
        remainder_sc = round(service_charge - (sc_per_guest * num_guests), 2)
        remainder_total = round(grand_total - (total_per_guest * num_guests), 2)

        splits = []
        now_iso = datetime.now(timezone.utc).isoformat()

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM order_splits WHERE order_id = ?", (order_id,))

            for i in range(1, num_guests + 1):
                is_last = (i == num_guests)
                guest_subtotal = base_subtotal_per_guest + (remainder_subtotal if is_last else 0.0)
                guest_sc = sc_per_guest + (remainder_sc if is_last else 0.0)
                guest_total = total_per_guest + (remainder_total if is_last else 0.0)

                split_id = f"SPLIT-{order_id}-{i}"
                guest_name = f"Guest {i}"
                items_summary = [{"description": f"1/{num_guests} Equal Share of Table Bill", "price": guest_subtotal}]

                split_record = {
                    "id": split_id,
                    "order_id": order_id,
                    "split_type": "EVEN",
                    "guest_name": guest_name,
                    "guest_index": i,
                    "items": items_summary,
                    "subtotal": round(guest_subtotal, 2),
                    "service_charge": round(guest_sc, 2),
                    "total": round(guest_total, 2),
                    "status": "UNPAID",
                    "payment_method": None,
                    "paid_at": None,
                    "created_at": now_iso
                }

                cursor.execute("""
                    INSERT INTO order_splits (id, order_id, split_type, guest_name, guest_index, items_json, subtotal, service_charge, total, status, payment_method, paid_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    split_record["id"],
                    split_record["order_id"],
                    split_record["split_type"],
                    split_record["guest_name"],
                    split_record["guest_index"],
                    json.dumps(split_record["items"]),
                    split_record["subtotal"],
                    split_record["service_charge"],
                    split_record["total"],
                    split_record["status"],
                    split_record["payment_method"],
                    split_record["paid_at"],
                    split_record["created_at"]
                ))
                splits.append(split_record)

            conn.commit()

        return {
            "order_id": order_id,
            "split_type": "EVEN",
            "total_guests": num_guests,
            "order_total": grand_total,
            "total_service_charge": service_charge,
            "splits": splits
        }

    def split_itemized(self, order_id: str, guest_assignments: List[Dict], include_service_charge: bool = True) -> Dict:
        """
        Splits an order bill by item assignment per guest.
        Each element in guest_assignments:
          {
            "guest_name": "Guest 1",
            "items": [{"name": "Fish & Chips", "price": 14.50}, ...]
          }
        """
        order = db.orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found.")

        if not guest_assignments:
            raise ValueError("Guest assignments list cannot be empty.")

        order_items = order["items"]
        order_subtotal = float(order["subtotal"])
        order_discount = float(order["discount"])
        order_net_subtotal = max(0.001, order_subtotal - order_discount)
        total_service_charge = round(order_net_subtotal * self.DEFAULT_SERVICE_CHARGE_RATE, 2) if include_service_charge else 0.0

        now_iso = datetime.now(timezone.utc).isoformat()
        splits = []
        num_guests = len(guest_assignments)

        # Compute guest subtotal, service charge ratio, and totals
        running_sc = 0.0
        running_total = 0.0
        grand_total = round(order_net_subtotal + total_service_charge, 2)

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM order_splits WHERE order_id = ?", (order_id,))

            for idx, g in enumerate(guest_assignments, start=1):
                guest_name = g.get("guest_name", f"Guest {idx}")
                items = g.get("items", [])
                guest_items_subtotal = sum(float(item.get("price", 0.0)) for item in items)
                
                # Pro-rate discount if any
                discount_ratio = (order_discount / order_subtotal) if order_subtotal > 0 else 0.0
                guest_net_subtotal = max(0.0, guest_items_subtotal * (1.0 - discount_ratio))

                if idx == num_guests:
                    # Last guest gets remaining balance to resolve rounding precision
                    guest_sc = round(total_service_charge - running_sc, 2)
                    guest_total = round(grand_total - running_total, 2)
                else:
                    sc_ratio = (guest_net_subtotal / order_net_subtotal) if order_net_subtotal > 0 else (1.0 / num_guests)
                    guest_sc = round(total_service_charge * sc_ratio, 2)
                    guest_total = round(guest_net_subtotal + guest_sc, 2)
                    running_sc += guest_sc
                    running_total += guest_total

                split_id = f"SPLIT-{order_id}-{idx}"
                split_record = {
                    "id": split_id,
                    "order_id": order_id,
                    "split_type": "ITEMIZED",
                    "guest_name": guest_name,
                    "guest_index": idx,
                    "items": items,
                    "subtotal": round(guest_net_subtotal, 2),
                    "service_charge": round(guest_sc, 2),
                    "total": round(guest_total, 2),
                    "status": "UNPAID",
                    "payment_method": None,
                    "paid_at": None,
                    "created_at": now_iso
                }

                cursor.execute("""
                    INSERT INTO order_splits (id, order_id, split_type, guest_name, guest_index, items_json, subtotal, service_charge, total, status, payment_method, paid_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    split_record["id"],
                    split_record["order_id"],
                    split_record["split_type"],
                    split_record["guest_name"],
                    split_record["guest_index"],
                    json.dumps(split_record["items"]),
                    split_record["subtotal"],
                    split_record["service_charge"],
                    split_record["total"],
                    split_record["status"],
                    split_record["payment_method"],
                    split_record["paid_at"],
                    split_record["created_at"]
                ))
                splits.append(split_record)

            conn.commit()

        return {
            "order_id": order_id,
            "split_type": "ITEMIZED",
            "total_guests": num_guests,
            "order_total": grand_total,
            "total_service_charge": total_service_charge,
            "splits": splits
        }

    def pay_split_share(self, order_id: str, split_id_or_index: Union[str, int], payment_method: str = "CARD") -> Dict:
        """
        Processes payment for a guest's split share.
        Updates order status to PAID if all shares are settled.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            
            if isinstance(split_id_or_index, int) or (isinstance(split_id_or_index, str) and split_id_or_index.isdigit()):
                guest_idx = int(split_id_or_index)
                cursor.execute("SELECT * FROM order_splits WHERE order_id = ? AND guest_index = ?", (order_id, guest_idx))
            else:
                cursor.execute("SELECT * FROM order_splits WHERE id = ? OR (order_id = ? AND id = ?)", (split_id_or_index, order_id, split_id_or_index))

            split_row = cursor.fetchone()
            if not split_row:
                raise ValueError(f"Split share '{split_id_or_index}' for order {order_id} not found.")

            target_id = split_row["id"]
            cursor.execute("""
                UPDATE order_splits SET status = 'PAID', payment_method = ?, paid_at = ? WHERE id = ?
            """, (payment_method.upper(), now_iso, target_id))
            conn.commit()

        # Check overall order settlement status
        status_info = self.get_split_status(order_id)
        if status_info["settlement_status"] == "SETTLED":
            db.update_order_status(order_id, "PAID")
            db.mark_order_paid(order_id, "SPLIT")

        return status_info

    def get_split_status(self, order_id: str) -> Dict:
        """
        Retrieves live split status, amounts paid, remaining balance, and list of guest splits.
        """
        order = db.orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found.")

        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM order_splits WHERE order_id = ? ORDER BY guest_index ASC", (order_id,))
            rows = cursor.fetchall()

        splits = []
        total_paid = 0.0
        total_split_amount = 0.0

        for r in rows:
            items = json.loads(r["items_json"]) if r["items_json"] else []
            s_dict = {
                "id": r["id"],
                "order_id": r["order_id"],
                "split_type": r["split_type"],
                "guest_name": r["guest_name"],
                "guest_index": r["guest_index"],
                "items": items,
                "subtotal": float(r["subtotal"]),
                "service_charge": float(r["service_charge"]),
                "total": float(r["total"]),
                "status": r["status"],
                "payment_method": r["payment_method"],
                "paid_at": r["paid_at"]
            }
            splits.append(s_dict)
            total_split_amount += s_dict["total"]
            if s_dict["status"] == "PAID":
                total_paid += s_dict["total"]

        total_split_amount = round(total_split_amount, 2)
        total_paid = round(total_paid, 2)
        remaining_balance = max(0.0, round(total_split_amount - total_paid, 2))
        
        is_settled = (len(splits) > 0 and remaining_balance == 0.0)
        settlement_status = "SETTLED" if is_settled else ("PARTIAL" if total_paid > 0 else "UNSPLIT")

        return {
            "order_id": order_id,
            "table_number": order["table_number"],
            "settlement_status": settlement_status,
            "order_total": total_split_amount if total_split_amount > 0 else order["total"],
            "total_paid": total_paid,
            "remaining_balance": remaining_balance,
            "total_guests": len(splits),
            "splits": splits
        }

    def generate_sub_receipt(self, order_id: str, split_id_or_index: Union[str, int], width: int = 32) -> str:
        """
        Formats a monospaced receipt string (ESC/POS thermal printable) for an individual guest split.
        """
        status_info = self.get_split_status(order_id)
        target_split = None
        for s in status_info["splits"]:
            if str(s["id"]) == str(split_id_or_index) or str(s["guest_index"]) == str(split_id_or_index):
                target_split = s
                break

        if not target_split:
            raise ValueError(f"Guest split share '{split_id_or_index}' for order {order_id} not found.")

        lines = []

        def center(text: str) -> str:
            return text.center(width)

        def left_right(left: str, right: str) -> str:
            space = width - len(left) - len(right)
            if space < 1:
                space = 1
            return left + (" " * space) + right

        lines.append(center("THE WAITER UK"))
        lines.append(center("123 Oxford Street, London"))
        lines.append(center("Tel: +44 7594 560831"))
        lines.append("=" * width)
        lines.append(left_right(f"ORDER: {order_id}", f"TABLE: #{status_info['table_number']}"))
        lines.append(left_right(f"GUEST: {target_split['guest_name']}", f"({target_split['guest_index']}/{status_info['total_guests']})"))
        lines.append("=" * width)

        lines.append("GUEST SHARE ITEMS:")
        for item in target_split["items"]:
            name = item.get("name") or item.get("description", "Item Share")
            price = float(item.get("price", 0.0))
            lines.append(left_right(f"- {name[:18]}", f"£{price:.2f}"))

        lines.append("-" * width)
        lines.append(left_right("Subtotal:", f"£{target_split['subtotal']:.2f}"))
        if target_split["service_charge"] > 0:
            lines.append(left_right("Service Charge (12.5%):", f"£{target_split['service_charge']:.2f}"))

        lines.append("=" * width)
        lines.append(left_right("GUEST TOTAL:", f"£{target_split['total']:.2f}"))
        lines.append("=" * width)

        pm = target_split.get("payment_method") or "UNPAID"
        status_line = f"STATUS: {target_split['status']} ({pm})" if target_split['status'] == "PAID" else "STATUS: UNPAID"
        lines.append(center(status_line))
        lines.append(center("Thank you for dining with us!"))
        lines.append("\n\n")

        return "\n".join(lines)

bill_splitting_service = BillSplittingModule()
