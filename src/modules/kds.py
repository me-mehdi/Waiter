import queue
import threading
import json
from typing import List, Dict, Optional
from src.core.db import db

class KDSModule:
    """
    Kitchen Display System (KDS) & Guest TV Display Module with SSE Event Broadcasting
    Digitalizes production workflows: New -> Preparing -> Ready -> Served.
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

    def get_active_kitchen_orders(self) -> List[dict]:
        """Returns all orders currently in kitchen (New, Preparing, Ready)."""
        active_orders = [
            order for order in db.orders.values()
            if order["status"] in ["New", "Preparing", "Ready"]
        ]
        # Sort by creation time (FIFO)
        return sorted(active_orders, key=lambda x: x["created_at"])

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

