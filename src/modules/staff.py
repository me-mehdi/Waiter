from typing import List, Dict, Optional
from datetime import datetime, timezone
from src.core.db import db
from src.core.config import Config
from src.modules.finance import finance_service

class StaffModule:
    """
    Staff Shift & Time Clock Tracking Module
    PIN-based Clock-in/Clock-out logging, shift duration calculation, and labor cost analytics.
    """
    STAFF_ROSTER = {
        "1234": {"name": "Alice Vance (Manager)", "role": "MANAGER", "rate": 20.00},
        "5555": {"name": "Chef Gordon (Head Chef)", "role": "CHEF", "rate": 16.50},
        "7777": {"name": "Charlie Parker (Server)", "role": "SERVER", "rate": 14.50},
        "8888": {"name": "Diana Ross (Server)", "role": "SERVER", "rate": 14.50},
    }

    def get_staff_members(self) -> List[dict]:
        return [
            {"pin": pin, "name": info["name"], "role": info["role"], "rate": info["rate"]}
            for pin, info in self.STAFF_ROSTER.items()
        ]

    def get_shifts(self) -> List[dict]:
        return db.shifts


    def get_active_shifts(self) -> List[dict]:
        return [s for s in db.shifts if s["status"] == "ACTIVE"]

    def clock_in(self, pin: str) -> dict:
        staff_info = self.STAFF_ROSTER.get(pin)
        if not staff_info:
            return {"success": False, "error": "Invalid Staff PIN"}

        # Check for active shift
        active_shifts = [s for s in db.shifts if s["pin"] == pin and s["status"] == "ACTIVE"]
        if active_shifts:
            return {"success": True, "already_clocked_in": True, "shift": active_shifts[0]}

        now_iso = datetime.now(timezone.utc).isoformat()
        shift_id = f"SHIFT-{len(db.shifts) + 1:04d}"

        shift = {
            "id": shift_id,
            "staff_name": staff_info["name"],
            "role": staff_info["role"],
            "pin": pin,
            "hourly_rate": staff_info["rate"],
            "clock_in": now_iso,
            "clock_out": None,
            "total_hours": 0.0,
            "labor_cost": 0.0,
            "status": "ACTIVE"
        }

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO staff_shifts (id, staff_name, role, pin, hourly_rate, clock_in, clock_out, total_hours, labor_cost, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                shift["id"], shift["staff_name"], shift["role"], shift["pin"],
                shift["hourly_rate"], shift["clock_in"], None, 0.0, 0.0, "ACTIVE"
            ))
            conn.commit()

        return {"success": True, "already_clocked_in": False, "shift": shift}

    def clock_out(self, pin: str) -> dict:
        staff_info = self.STAFF_ROSTER.get(pin)
        if not staff_info:
            return {"success": False, "error": "Invalid Staff PIN"}

        active_shifts = [s for s in db.shifts if s["pin"] == pin and s["status"] == "ACTIVE"]
        if not active_shifts:
            return {"success": False, "error": "No active shift found for this staff member."}

        shift = active_shifts[0]
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()

        clock_in_dt = datetime.fromisoformat(shift["clock_in"])
        duration_seconds = max(0, (now_dt - clock_in_dt).total_seconds())
        total_hours = round(duration_seconds / 3600.0, 2)
        if total_hours == 0.0:
            total_hours = 0.01  # Minimum billable shift resolution

        labor_cost = round(total_hours * shift["hourly_rate"], 2)

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE staff_shifts
                SET clock_out = ?, total_hours = ?, labor_cost = ?, status = 'COMPLETED'
                WHERE id = ?
            """, (now_iso, total_hours, labor_cost, shift["id"]))
            conn.commit()

        shift["clock_out"] = now_iso
        shift["total_hours"] = total_hours
        shift["labor_cost"] = labor_cost
        shift["status"] = "COMPLETED"

        return {"success": True, "shift": shift}

    def get_labor_analytics(self, currency: str = "GBP") -> dict:
        shifts = db.shifts
        completed_shifts = [s for s in shifts if s["status"] == "COMPLETED"]
        active_shifts = [s for s in shifts if s["status"] == "ACTIVE"]

        total_labor_cost_gbp = sum(s["labor_cost"] for s in completed_shifts)
        total_hours = sum(s["total_hours"] for s in completed_shifts)

        analytics = finance_service.calculate_analytics(currency=currency)
        total_revenue = analytics.get("total_revenue", 0.0)

        curr = currency.upper()
        converted_labor = Config.convert_price(total_labor_cost_gbp, curr)
        symbol = Config.CURRENCY_SYMBOLS.get(curr, "£")

        labor_pct = round((converted_labor / total_revenue * 100), 1) if total_revenue > 0 else 0.0

        return {
            "active_staff_count": len(active_shifts),
            "completed_shifts_count": len(completed_shifts),
            "total_hours": round(total_hours, 2),
            "total_labor_cost": round(converted_labor, 2),
            "revenue": total_revenue,
            "labor_cost_percentage": labor_pct,
            "currency": curr,
            "currency_symbol": symbol
        }

staff_service = StaffModule()
