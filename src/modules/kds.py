import queue
import threading
import json
from typing import List, Dict, Optional
from src.core.db import db
from src.core.config import Config
from src.modules.prep_routing import prep_routing_service

class KDSModule:
    """
    Kitchen Display System (KDS) & Guest TV Display Module with SSE Event Broadcasting
    Digitalizes production workflows: New -> Preparing -> Ready -> Served.
    Supports station-specific routing (GRILL, FRYER, BAR, LARDER, HOT_LINE).
    """
    VALID_STATUSES = ["New", "Preparing", "Ready", "Served"]

    def __init__(self):
        self._listeners: List[queue.Queue] = []
        self._lock = threading.Lock()

    def subscribe(self) -> queue.Queue:
        q = queue.Queue(maxsize=15)
        with self._lock:
            self._listeners.append(q)
        return q

    def unsubscribe(self, q: queue.Queue):
        with self._lock:
            if q in self._listeners:
                self._listeners.remove(q)

    def publish_event(self, event_type: str, data: dict):
        event_payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        with self._lock:
            dead_listeners = []
            for q in self._listeners:
                try:
                    q.put_nowait(event_payload)
                except queue.Full:
                    dead_listeners.append(q)
            for q in dead_listeners:
                if q in self._listeners:
                    self._listeners.remove(q)

    def get_active_kitchen_orders(self, station: Optional[str] = None) -> List[dict]:
        """Returns all orders currently in kitchen (New, Preparing, Ready), optionally filtered by prep station."""
        menu = db.menu_items
        active_orders = []
        for order in db.orders.values():
            if order["status"] not in ["New", "Preparing", "Ready"]:
                continue
            o = dict(order)
            item_ids = [i.get("item_id") for i in o["items"] if isinstance(i, dict)]
            allergens = set()
            for iid in item_ids:
                allergens.update(menu.get(iid, {}).get("allergens", []))
            o["allergens"] = sorted(allergens)
            o["requires_challenge25"] = any(iid in Config.ALCOHOL_ITEM_IDS for iid in item_ids)
            o["channel"] = o.get("channel") or "DINE_IN"
            active_orders.append(o)
        
        # Sort by creation time (FIFO)
        sorted_orders = sorted(active_orders, key=lambda x: x["created_at"])

        if not station or station.upper() == "ALL":
            return sorted_orders

        # Filter items matching station
        filtered = []
        for o in sorted_orders:
            station_items = []
            for item in o["items"]:
                if not isinstance(item, dict):
                    continue
                item_id = item.get("item_id")
                routing = prep_routing_service.get_item_routing(item_id)
                if routing["station"].upper() == station.upper():
                    item_copy = dict(item)
                    item_copy["station"] = routing["station"]
                    item_copy["prep_mins"] = routing["prep_mins"]
                    station_items.append(item_copy)
            if station_items:
                o_copy = dict(o)
                o_copy["items"] = station_items
                filtered.append(o_copy)

        return filtered

    def get_station_counts(self) -> Dict[str, int]:
        all_orders = self.get_active_kitchen_orders(station=None)
        counts = {"ALL": len(all_orders), "GRILL": 0, "FRYER": 0, "BAR": 0, "LARDER": 0, "HOT_LINE": 0}
        for st in ["GRILL", "FRYER", "BAR", "LARDER", "HOT_LINE"]:
            counts[st] = len(self.get_active_kitchen_orders(station=st))
        return counts

    def get_tv_display_status(self) -> dict:
        """Returns orders categorized for guest-facing TV screens."""
        preparing = [o["id"] for o in db.orders.values() if o["status"] == "Preparing"]
        ready = [o["id"] for o in db.orders.values() if o["status"] == "Ready"]
        return {
            "preparing": preparing,
            "ready": ready
        }

    def advance_order_status(self, order_id: str) -> Optional[dict]:
        """Advances order status through the KDS lifecycle."""
        order = db.orders.get(order_id)
        if not order:
            return None
            
        current_idx = self.VALID_STATUSES.index(order["status"])
        if current_idx < len(self.VALID_STATUSES) - 1:
            next_status = self.VALID_STATUSES[current_idx + 1]
            updated = db.update_order_status(order_id, next_status)
            self.publish_event("kds_update", {
                "action": "STATUS_ADVANCED",
                "order_id": order_id,
                "new_status": next_status,
                "tv": self.get_tv_display_status()
            })
            return updated
        return order

kds_service = KDSModule()
