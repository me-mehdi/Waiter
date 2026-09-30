from typing import List, Dict, Optional
from src.core.db import db

class VenueModule:
    """
    Multi-Venue / Multi-Store Location Management Module
    Supports venue switching, per-location order tracking, and store configuration.
    """
    def __init__(self):
        self._active_venue_id = "venue-1"

    def get_venues(self) -> List[dict]:
        return list(db.venues.values())

    def get_venue(self, venue_id: str) -> Optional[dict]:
        return db.venues.get(venue_id)

    def get_active_venue(self) -> dict:
        venue = db.venues.get(self._active_venue_id)
        if not venue:
            venues = self.get_venues()
            return venues[0] if venues else {
                "id": "venue-1",
                "name": "Covent Garden Flagship",
                "address": "12 Floral St, London WC2E 9DH",
                "currency": "GBP",
                "tables_count": 12,
                "market": "UK"
            }
        return venue

    def set_active_venue(self, venue_id: str) -> bool:
        if venue_id in db.venues:
            self._active_venue_id = venue_id
            return True
        return False

venue_service = VenueModule()
