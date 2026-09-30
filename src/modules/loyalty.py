import json
import random
from typing import Optional, Dict, List
from datetime import datetime, timezone
from src.core.db import db

class LoyaltyModule:
    """
    Customer Loyalty & Digital Rewards Engine
    Points accumulation per £ spent, tier progression (Bronze, Silver, Gold), and reward voucher issuance.
    """
    REWARD_CATALOG = {
        "REWARD5": {"points_cost": 100, "description": "£5 Off Voucher Code", "discount_pct": 15.0, "prefix": "LOYAL5"},
        "REWARD15": {"points_cost": 250, "description": "£15 Off Voucher Code", "discount_pct": 30.0, "prefix": "LOYAL15"},
        "FREEMAIN": {"points_cost": 500, "description": "Free Main Dish Voucher", "discount_pct": 50.0, "prefix": "FREEMAIN"},
    }

    @staticmethod
    def _calculate_tier(points: int) -> str:
        if points >= 1000:
            return "GOLD"
        elif points >= 500:
            return "SILVER"
        return "BRONZE"

    def get_account(self, identifier: str) -> Optional[dict]:
        return db.loyalty_accounts.get(identifier)

    def register_account(self, phone_or_email: str, guest_name: str) -> dict:
        identifier = phone_or_email.strip()
        if not identifier or not guest_name.strip():
            return {"success": False, "error": "Phone/Email and Guest Name are required."}

        if identifier in db.loyalty_accounts:
            return {"success": True, "already_registered": True, "account": db.loyalty_accounts[identifier]}

        now_iso = datetime.now(timezone.utc).isoformat()
        account = {
            "phone_or_email": identifier,
            "guest_name": guest_name.strip(),
            "points_balance": 50,  # 50 Welcome bonus points
            "tier": "BRONZE",
            "total_spent": 0.0,
            "vouchers": [],
            "created_at": now_iso
        }

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO loyalty_accounts (phone_or_email, guest_name, points_balance, tier, total_spent, vouchers_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                account["phone_or_email"],
                account["guest_name"],
                account["points_balance"],
                account["tier"],
                account["total_spent"],
                json.dumps(account["vouchers"]),
                account["created_at"]
            ))
            conn.commit()

        return {"success": True, "already_registered": False, "account": account}

    def earn_points(self, phone_or_email: str, order_id: str) -> dict:
        account = self.get_account(phone_or_email)
        if not account:
            return {"success": False, "error": "Loyalty account not found."}

        order = db.orders.get(order_id)
        if not order:
            return {"success": False, "error": "Order not found."}

        order_total = order["total"]
        points_earned = int(order_total * 10)  # 10 points per £1

        new_points = account["points_balance"] + points_earned
        new_spent = round(account["total_spent"] + order_total, 2)
        new_tier = self._calculate_tier(new_points)

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE loyalty_accounts
                SET points_balance = ?, total_spent = ?, tier = ?
                WHERE phone_or_email = ?
            """, (new_points, new_spent, new_tier, phone_or_email))
            conn.commit()

        account["points_balance"] = new_points
        account["total_spent"] = new_spent
        account["tier"] = new_tier

        return {
            "success": True,
            "points_earned": points_earned,
            "new_balance": new_points,
            "tier": new_tier,
            "account": account
        }

    def redeem_reward(self, phone_or_email: str, reward_key: str) -> dict:
        account = self.get_account(phone_or_email)
        if not account:
            return {"success": False, "error": "Loyalty account not found."}

        reward_opt = self.REWARD_CATALOG.get(reward_key.upper())
        if not reward_opt:
            return {"success": False, "error": f"Invalid reward key. Choose from: {list(self.REWARD_CATALOG.keys())}"}

        cost = reward_opt["points_cost"]
        if account["points_balance"] < cost:
            return {
                "success": False,
                "error": f"Insufficient points. Required: {cost} pts, Available: {account['points_balance']} pts"
            }

        # Generate unique voucher code and register in db.promos
        rand_num = random.randint(1000, 9999)
        voucher_code = f"{reward_opt['prefix']}-{rand_num}"

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Insert into promos table
            cursor.execute("""
                INSERT INTO promos (code, discount_pct, max_uses, current_uses, active)
                VALUES (?, ?, ?, ?, ?)
            """, (voucher_code, reward_opt["discount_pct"], 1, 0, 1))

            # 2. Update loyalty account balance and vouchers list
            new_points = account["points_balance"] - cost
            vouchers = list(account.get("vouchers", []))
            vouchers.append({
                "code": voucher_code,
                "description": reward_opt["description"],
                "discount_pct": reward_opt["discount_pct"],
                "redeemed_at": datetime.now(timezone.utc).isoformat()
            })

            cursor.execute("""
                UPDATE loyalty_accounts
                SET points_balance = ?, vouchers_json = ?, tier = ?
                WHERE phone_or_email = ?
            """, (new_points, json.dumps(vouchers), self._calculate_tier(new_points), phone_or_email))

            conn.commit()

        account["points_balance"] = new_points
        account["vouchers"] = vouchers
        account["tier"] = self._calculate_tier(new_points)

        return {
            "success": True,
            "voucher_code": voucher_code,
            "reward_description": reward_opt["description"],
            "remaining_points": new_points,
            "account": account
        }

loyalty_service = LoyaltyModule()
