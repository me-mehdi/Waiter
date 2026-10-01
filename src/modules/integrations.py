import json
from typing import List, Dict, Optional
from datetime import datetime, timezone

from src.core.db import db
from src.core.config import Config
from src.modules.qr_ordering import qr_ordering_service
from src.modules.kds import kds_service
from src.modules.venue import venue_service

SUPPORTED_PLATFORMS = [
    "DELIVEROO",
    "UBEREATS",
    "DELIVERECT",
    "TOAST"
]

class IntegrationsModule:
    """
    Third-Party Delivery Aggregator & Enterprise POS Integration Simulator.
    Supports Deliveroo, UberEats, Deliverect, and Toast POS inbound order webhooks,
    menu/stock sync, and real-time KDS ticket injection with channel badges.
    """

    def process_inbound_webhook(
        self,
        platform: str,
        external_order_ref: str,
        customer_name: str,
        items: List[Dict],
        delivery_address: str = "London Central Delivery",
        table_number: int = 99
    ) -> Dict:
        """
        Processes an inbound delivery order webhook from Deliveroo, UberEats, or Deliverect.
        Injects ticket into KDS and updates stock.
        """
        plat_clean = platform.upper()
        if plat_clean not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported delivery platform '{platform}'. Supported: {', '.join(SUPPORTED_PLATFORMS)}")

        if not items:
            raise ValueError("Order items list cannot be empty.")

        item_ids = []
        for it in items:
            iid = it.get("item_id") or it.get("id")
            if iid and iid in db.menu_items:
                item_ids.append(iid)
            else:
                # Default fallback item if external item ID is simulated
                item_ids.append("item-1")

        venue_id = venue_service.get_active_venue()["id"]
        order = qr_ordering_service.submit_order(
            table_number=table_number,
            item_ids=item_ids,
            venue_id=venue_id
        )

        # Annotate order record with integration metadata
        now_iso = datetime.now(timezone.utc).isoformat()
        order_id = order["id"]

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT items_json FROM orders WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            current_items = json.loads(row["items_json"]) if row else order["items"]

            # Add channel metadata to items_json
            annotated_data = {
                "channel": plat_clean,
                "external_ref": external_order_ref,
                "customer_name": customer_name,
                "delivery_address": delivery_address,
                "items": current_items
            }

            cursor.execute("UPDATE orders SET items_json = ? WHERE id = ?", (json.dumps(annotated_data), order_id))
            conn.commit()

        # Fetch updated order and publish KDS live SSE event
        updated_order = db.orders.get(order_id)
        kds_service.publish_event("kds_update", {
            "type": "NEW_DELIVERY_ORDER",
            "channel": plat_clean,
            "order": updated_order
        })

        return {
            "order_id": order_id,
            "channel": plat_clean,
            "external_ref": external_order_ref,
            "customer_name": customer_name,
            "table_number": table_number,
            "total": updated_order["total"],
            "status": updated_order["status"],
            "created_at": now_iso
        }

    def sync_menu_to_aggregator(self, platform: str) -> Dict:
        """
        Serializes menu catalog and stock levels into Deliverect / Deliveroo JSON sync format.
        """
        plat_clean = platform.upper()
        if plat_clean not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported delivery platform '{platform}'.")

        menu_items = list(db.menu_items.values())
        formatted_catalog = []

        for item in menu_items:
            formatted_catalog.append({
                "external_sku": item["id"],
                "name": item["name"]["en"],
                "price_gbp": item["price"],
                "category": item["category"],
                "available": item["stock_qty"] > 0,
                "stock_quantity": item["stock_qty"],
                "allergens": item.get("allergens", []),
                "dietary": item.get("dietary", [])
            })

        now_iso = datetime.now(timezone.utc).isoformat()

        return {
            "channel": plat_clean,
            "status": "SYNCED",
            "synced_items_count": len(formatted_catalog),
            "catalog": formatted_catalog,
            "synced_at": now_iso
        }

    def get_integration_channels(self) -> List[Dict]:
        """
        Returns status, order volume, and revenue breakdown per integration channel.
        """
        all_orders = list(db.orders.values())
        now_iso = datetime.now(timezone.utc).isoformat()

        channels = []
        for p in SUPPORTED_PLATFORMS:
            # Match orders tagged with this channel
            channel_orders = []
            for o in all_orders:
                items_data = o.get("items", {})
                if isinstance(items_data, dict) and items_data.get("channel") == p:
                    channel_orders.append(o)

            vol = len(channel_orders)
            rev = sum(o["total"] for o in channel_orders)

            channels.append({
                "channel": p,
                "status": "ONLINE",
                "processed_orders_count": vol,
                "total_revenue_processed": round(rev, 2),
                "last_heartbeat": now_iso
            })

        return channels

integrations_service = IntegrationsModule()
