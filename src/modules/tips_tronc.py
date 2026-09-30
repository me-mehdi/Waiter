from typing import List, Dict, Optional
from datetime import datetime, timezone
from src.core.db import db
from src.core.config import Config

class TipsTroncModule:
    """
    Tip & Discretionary UK Service Charge (Tronc) Distribution Module
    Calculates 12.5% UK service charge, tip pool collection, and fair Tronc distribution among active shift staff.
    """
    DEFAULT_SERVICE_CHARGE_RATE = 0.125  # 12.5% UK Standard Discretionary Service Charge
    
    # Tronc Pool Distribution Ratios by Staff Role
    TRONC_SPLIT_RATIOS = {
        "SERVER": 0.60,   # 60% to Front of House Servers
        "CHEF": 0.30,     # 30% to Kitchen Chefs
        "MANAGER": 0.10   # 10% to Duty Manager/Supervisor
    }

    def calculate_service_charge(self, subtotal: float, rate: float = DEFAULT_SERVICE_CHARGE_RATE) -> float:
        return round(subtotal * rate, 2)

    def get_tronc_summary(self, currency: str = "GBP") -> dict:
        completed_orders = [o for o in db.orders.values() if o["status"] != "CANCELLED"]
        total_subtotal_gbp = sum(o["subtotal"] for o in completed_orders)
        total_service_charge_gbp = self.calculate_service_charge(total_subtotal_gbp)

        curr = currency.upper()
        symbol = Config.CURRENCY_SYMBOLS.get(curr, "£")
        converted_sc = Config.convert_price(total_service_charge_gbp, curr)
        converted_subtotal = Config.convert_price(total_subtotal_gbp, curr)

        # Get active shift staff
        active_shifts = [s for s in db.shifts if s["status"] in ["ACTIVE", "COMPLETED"]]
        role_counts = {}
        for s in active_shifts:
            role = s["role"]
            role_counts[role] = role_counts.get(role, 0) + 1

        payout_breakdown = []
        for s in active_shifts:
            role = s["role"]
            ratio = self.TRONC_SPLIT_RATIOS.get(role, 0.10)
            count = role_counts.get(role, 1)
            share_gbp = (total_service_charge_gbp * ratio) / count if count > 0 else 0.0
            share_converted = Config.convert_price(share_gbp, curr)

            payout_breakdown.append({
                "staff_name": s["staff_name"],
                "role": role,
                "tronc_share": round(share_converted, 2),
                "currency": curr,
                "currency_symbol": symbol
            })

        return {
            "subtotal": round(converted_subtotal, 2),
            "service_charge_rate": "12.5%",
            "total_tronc_pool": round(converted_sc, 2),
            "currency": curr,
            "currency_symbol": symbol,
            "eligible_staff_count": len(active_shifts),
            "payout_breakdown": payout_breakdown
        }

tips_tronc_service = TipsTroncModule()
