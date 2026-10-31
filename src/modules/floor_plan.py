from typing import List, Dict, Optional
from src.core.db import db

class FloorPlanModule:
    """
    Dynamic Table Layout & Interactive Floor Plan Module
    Manages restaurant dining zones (Main Hall, VIP Booth, Patio, Bar), table capacities, live occupancy state derived from orders, and table reservations.
    """
    TABLE_CONFIG = [
        {"table_number": 1, "capacity": 2, "zone": "Main Dining Room", "shape": "round"},
        {"table_number": 2, "capacity": 2, "zone": "Main Dining Room", "shape": "round"},
        {"table_number": 3, "capacity": 4, "zone": "Main Dining Room", "shape": "square"},
        {"table_number": 4, "capacity": 4, "zone": "Main Dining Room", "shape": "square"},
        {"table_number": 5, "capacity": 6, "zone": "VIP Booth", "shape": "booth"},
        {"table_number": 6, "capacity": 6, "zone": "VIP Booth", "shape": "booth"},
        {"table_number": 7, "capacity": 2, "zone": "Patio & Terrace", "shape": "round"},
        {"table_number": 8, "capacity": 2, "zone": "Patio & Terrace", "shape": "round"},
        {"table_number": 9, "capacity": 4, "zone": "Patio & Terrace", "shape": "square"},
        {"table_number": 10, "capacity": 4, "zone": "Bar Lounge", "shape": "high_top"},
        {"table_number": 11, "capacity": 4, "zone": "Bar Lounge", "shape": "high_top"},
        {"table_number": 12, "capacity": 8, "zone": "Banquet Table", "shape": "rectangle"},
    ]

    def __init__(self):
        self._reservations: Dict[int, dict] = {}

    # An unpaid table stays "occupied" through Served so the owner can see who is still eating or paying.
    OCCUPYING_STATUSES = ("New", "Preparing", "Ready", "Served")

    def get_floor_plan(self) -> List[dict]:
        active_orders_by_table = {}
        for order in db.orders.values():
            if order["status"] in self.OCCUPYING_STATUSES and order.get("payment_status") != "PAID":
                active_orders_by_table[order["table_number"]] = order

        floor_map = []
        for config in self.TABLE_CONFIG:
            table_num = config["table_number"]
            reservation = self._reservations.get(table_num)
            active_order = active_orders_by_table.get(table_num)

            if active_order:
                status = "OCCUPIED"
                phase = {"New": "ORDERED", "Preparing": "ORDERED", "Ready": "READY", "Served": "SEATED"}.get(active_order["status"], "ORDERED")
            elif reservation:
                status = reservation.get("status", "RESERVED")
                phase = "RESERVED"
            else:
                status = "AVAILABLE"
                phase = "FREE"

            table_info = dict(config)
            table_info["status"] = status
            table_info["phase"] = phase
            table_info["active_order"] = active_order
            table_info["reservation"] = reservation
            floor_map.append(table_info)

        return floor_map

    def reserve_table(self, table_number: int, guest_name: str, time_slot: str = "19:00") -> dict:
        if any(c["table_number"] == table_number for c in self.TABLE_CONFIG):
            reservation = {
                "table_number": table_number,
                "guest_name": guest_name,
                "time_slot": time_slot,
                "status": "RESERVED"
            }
            self._reservations[table_number] = reservation
            return {"success": True, "reservation": reservation}
        return {"success": False, "error": "Invalid table number"}

    def update_table_status(self, table_number: int, status: str, guest_name: str = "Reserved"):
        if status in ["RESERVED", "OCCUPIED"]:
            self._reservations[table_number] = {
                "table_number": table_number,
                "guest_name": guest_name,
                "status": status
            }
        else:
            self._reservations.pop(table_number, None)

    def release_table(self, table_number: int) -> dict:
        if table_number in self._reservations:
            del self._reservations[table_number]
            return {"success": True, "message": f"Table #{table_number} released"}
        return {"success": True, "message": f"Table #{table_number} is available"}

floor_plan_service = FloorPlanModule()
