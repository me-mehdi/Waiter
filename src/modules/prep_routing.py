from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from src.core.db import db

class PrepRoutingModule:
    """
    Kitchen Prep Time Estimator & Station Routing Module
    Routes menu items to specialized kitchen prep stations (GRILL, FRYER, BAR, LARDER) and calculates ticket ETAs.
    """
    STATION_MAPPING = {
        "item-1": {"station": "FRYER", "prep_mins": 12},
        "item-2": {"station": "GRILL", "prep_mins": 10},
        "item-3": {"station": "BAR", "prep_mins": 2},
        "item-4": {"station": "LARDER", "prep_mins": 3},
        "item-5": {"station": "BAR", "prep_mins": 2},
    }

    DEFAULT_STATION = {"station": "HOT_LINE", "prep_mins": 8}

    def get_item_routing(self, item_id: str) -> dict:
        return self.STATION_MAPPING.get(item_id, self.DEFAULT_STATION)

    def calculate_order_eta(self, order_id: str) -> Optional[dict]:
        order = db.orders.get(order_id)
        if not order:
            return None

        max_prep = 0
        items_with_stations = []

        for item in order["items"]:
            item_id = item.get("item_id")
            routing = self.get_item_routing(item_id)
            prep_mins = routing["prep_mins"]
            if prep_mins > max_prep:
                max_prep = prep_mins

            item_copy = dict(item)
            item_copy["station"] = routing["station"]
            item_copy["prep_mins"] = prep_mins
            items_with_stations.append(item_copy)

        created_dt = datetime.fromisoformat(order["created_at"])
        eta_dt = created_dt + timedelta(minutes=max_prep)
        now_dt = datetime.now(timezone.utc)
        remaining_seconds = max(0, int((eta_dt - now_dt).total_seconds()))
        remaining_mins = round(remaining_seconds / 60.0, 1)

        return {
            "order_id": order_id,
            "status": order["status"],
            "created_at": order["created_at"],
            "max_prep_mins": max_prep,
            "estimated_completion_at": eta_dt.isoformat(),
            "remaining_mins": remaining_mins,
            "items": items_with_stations
        }

    def get_station_queues(self) -> Dict[str, List[dict]]:
        active_orders = [
            o for o in db.orders.values()
            if o["status"] in ["New", "Preparing"]
        ]

        stations = {"GRILL": [], "FRYER": [], "BAR": [], "LARDER": [], "HOT_LINE": []}

        for order in active_orders:
            for item in order["items"]:
                item_id = item.get("item_id")
                routing = self.get_item_routing(item_id)
                st_name = routing["station"]

                ticket_snippet = {
                    "order_id": order["id"],
                    "table_number": order["table_number"],
                    "item_name": item["name"],
                    "status": order["status"],
                    "prep_mins": routing["prep_mins"],
                    "created_at": order["created_at"]
                }
                stations[st_name].append(ticket_snippet)

        return stations

prep_routing_service = PrepRoutingModule()
