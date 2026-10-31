import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from src.core.db import db


class UKPubFeaturesModule:
    """
    British Pub & Gastropub Specialized Engine ('The Waiter'):
    1. Bar Tabs: Card Pre-Authorisation (£50 hold), Round Ordering & 1-Tap 'Same Again!'
    2. Cellar & Keg Management: 11-Gallon/50L (88-Pint) Keg Tracking, 7-Day Line-Cleaning Logs, Pour-Cost & Ullage Wastage
    3. Pub Extras: Sunday Roast Pre-Orders with Live Sold-Out Counters, Pub Quiz & Event Ticketing, Happy-Hour Scheduler
    4. Beer Garden Zones: Numbered Garden Benches/Pods (#G1-#G6, #P1-#P4) with Weather-Triggered 'Garden Open' Toggle
    """

    def __init__(self):
        # 1. Active Bar Tabs with Card Pre-Authorisation & Rounds History
        self.bar_tabs: Dict[str, dict] = {
            "TAB-101": {
                "tab_id": "TAB-101",
                "customer_name": "Dave & Mates (Table #4 / Bar Stool S2)",
                "table_or_zone": "Table #4",
                "pre_auth_token": "PREAUTH-STRIPE-99481A",
                "pre_auth_limit_gbp": 75.00,
                "current_balance_gbp": 18.60,
                "status": "OPEN_PRE_AUTHORISED",
                "rounds": [
                    {
                        "round_number": 1,
                        "items": [
                            {"item_id": "item-3", "name": "Camden Pale Craft IPA Pint", "price_gbp": 6.20},
                            {"item_id": "item-3", "name": "Camden Pale Craft IPA Pint", "price_gbp": 6.20},
                            {"item_id": "item-3", "name": "Camden Pale Craft IPA Pint", "price_gbp": 6.20}
                        ],
                        "round_total_gbp": 18.60,
                        "ordered_at": datetime.now(timezone.utc).isoformat()
                    }
                ],
                "opened_at": datetime.now(timezone.utc).isoformat()
            }
        }

        # 2. Cellar & Keg Management (11-Gallon / 50L Kegs = 88 Imperial Pints)
        now_utc = datetime.now(timezone.utc)
        self.kegs_and_taps: List[dict] = [
            {
                "tap_number": 1,
                "beer_name": "Camden Pale Craft IPA (5.2% ABV)",
                "keg_type": "50L Sankey Keg (88 Pints)",
                "total_pints_capacity": 88,
                "pints_poured": 62,
                "pints_ullage_waste": 2,
                "pints_remaining": 24,
                "pour_cost_gbp": 1.28,
                "sell_price_gbp": 6.20,
                "yield_efficiency_pct": 96.9,
                "last_line_cleaned_date": (now_utc - timedelta(days=2)).strftime("%Y-%m-%d"),
                "line_clean_status": "CLEAN_COMPLIANT",
                "cellar_temp_c": 11.2
            },
            {
                "tap_number": 2,
                "beer_name": "Guinness Draught Stout (4.1% ABV)",
                "keg_type": "50L Mixed-Gas Keg (88 Pints)",
                "total_pints_capacity": 88,
                "pints_poured": 74,
                "pints_ullage_waste": 1,
                "pints_remaining": 13,
                "pour_cost_gbp": 1.35,
                "sell_price_gbp": 6.50,
                "yield_efficiency_pct": 98.7,
                "last_line_cleaned_date": (now_utc - timedelta(days=3)).strftime("%Y-%m-%d"),
                "line_clean_status": "CLEAN_COMPLIANT",
                "cellar_temp_c": 11.2
            },
            {
                "tap_number": 3,
                "beer_name": "Timothy Taylor Landlord Cask Ale (4.3% ABV)",
                "keg_type": "9-Gallon Firkin Cask (72 Pints)",
                "total_pints_capacity": 72,
                "pints_poured": 58,
                "pints_ullage_waste": 4,
                "pints_remaining": 10,
                "pour_cost_gbp": 1.15,
                "sell_price_gbp": 5.80,
                "yield_efficiency_pct": 93.5,
                "last_line_cleaned_date": (now_utc - timedelta(days=7)).strftime("%Y-%m-%d"),
                "line_clean_status": "DUE_FOR_7_DAY_CAUSTIC_CLEAN",
                "cellar_temp_c": 12.0
            },
            {
                "tap_number": 4,
                "beer_name": "Beavertown Neck Oil Session IPA (4.3% ABV)",
                "keg_type": "50L Sankey Keg (88 Pints)",
                "total_pints_capacity": 88,
                "pints_poured": 41,
                "pints_ullage_waste": 1,
                "pints_remaining": 46,
                "pour_cost_gbp": 1.42,
                "sell_price_gbp": 6.80,
                "yield_efficiency_pct": 97.6,
                "last_line_cleaned_date": (now_utc - timedelta(days=1)).strftime("%Y-%m-%d"),
                "line_clean_status": "CLEAN_COMPLIANT",
                "cellar_temp_c": 11.2
            }
        ]

        # 3. Pub Extras: Sunday Roast Pre-Orders (with Sold-Out Counters), Quiz/Events & Happy-Hour Schedule
        self.sunday_roast_counter: List[dict] = [
            {
                "roast_id": "ROAST-BEEF",
                "name": "28-Day Dry-Aged Hereford Sirloin of Beef (with Yorkshire Pudding, Duck-Fat Roasties & Red Wine Jus)",
                "price_gbp": 21.50,
                "initial_allocated": 40,
                "remaining_portions": 9,
                "sold_out": False
            },
            {
                "roast_id": "ROAST-PORK",
                "name": "Slow-Roasted Dingley Dell Pork Belly (with Crackling, Bramley Apple Sauce & Roasties)",
                "price_gbp": 19.50,
                "initial_allocated": 30,
                "remaining_portions": 4,
                "sold_out": False
            },
            {
                "roast_id": "ROAST-CHICKEN",
                "name": "Half Corn-Fed Cotswold Roast Chicken (with Sage & Onion Stuffing & Pigs in Blankets)",
                "price_gbp": 18.90,
                "initial_allocated": 25,
                "remaining_portions": 1,
                "sold_out": False
            },
            {
                "roast_id": "ROAST-VEGAN",
                "name": "Wild Mushroom, Chestnut & Cranberry Wellington (Vegan Gravy & Maple Parsnips)",
                "price_gbp": 17.50,
                "initial_allocated": 15,
                "remaining_portions": 0,
                "sold_out": True
            }
        ]

        self.pub_events_and_quiz: List[dict] = [
            {
                "event_id": "QUIZ-WED",
                "title": "The Great British Wednesday Pub Quiz Night",
                "schedule": "Every Wednesday • 19:30 Start",
                "entry_fee_per_person_gbp": 3.00,
                "prize_pot": "£150 Bar Tab + Rollover Cash Jackpot",
                "max_teams": 16,
                "teams_booked": 13,
                "bookings": [
                    {"team_name": "Quizteam Aguilera", "team_size": 5, "table_assigned": 7, "paid_gbp": 15.00}
                ]
            },
            {
                "event_id": "RUGBY-LIVE",
                "title": "Six Nations & Premier League Live Big-Screen Booths",
                "schedule": "Saturday • 14:15 & 17:00 Kick-Off",
                "entry_fee_per_person_gbp": 10.00,
                "prize_pot": "Includes 1 Free Pint of Craft IPA on Arrival",
                "max_teams": 10,
                "teams_booked": 8,
                "bookings": []
            }
        ]

        self.happy_hour_schedule = {
            "active_rule": "WEEKDAY_AFTER_WORK_CLUB",
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "time_window": "16:00 - 19:00",
            "offers": [
                "£5.00 All Draught Craft Pints (Save up to £1.80/pint)",
                "2-for-£14 Artisan Spritz & Classic Pub Cocktails",
                "£10 Pint + Truffle Fries Combo"
            ],
            "auto_trigger_enabled": True
        }

        # 4. Beer Garden Zones & Weather-Triggered Open/Close Toggle
        self.beer_garden_state = {
            "garden_open": True,
            "weather_auto_trigger": True,
            "current_weather": {
                "condition": "SUNNY_INTERVALS",
                "temp_c": 19.5,
                "rain_probability_pct": 5,
                "wind_mph": 6,
                "summary": "19.5°C Sunny Intervals (London Met Office) — Ideal Beer Garden Trading"
            },
            "zones": [
                {"zone_id": "G1", "name": "Sunny Lawn Bench #G1", "capacity": 6, "covered_heated": False, "status": "OPEN", "active_orders": 1},
                {"zone_id": "G2", "name": "Sunny Lawn Bench #G2", "capacity": 6, "covered_heated": False, "status": "OPEN", "active_orders": 2},
                {"zone_id": "G3", "name": "Wisteria Pergola Table #G3", "capacity": 8, "covered_heated": True, "status": "OPEN", "active_orders": 1},
                {"zone_id": "P1", "name": "Heated Garden Cabana Pod #P1", "capacity": 8, "covered_heated": True, "status": "OPEN", "active_orders": 1},
                {"zone_id": "P2", "name": "Heated Garden Cabana Pod #P2", "capacity": 8, "covered_heated": True, "status": "OPEN", "active_orders": 0}
            ]
        }

    # =========================================================================
    # 1. BAR TABS, CARD PRE-AUTH & 1-TAP 'SAME AGAIN!' ROUND ORDERING
    # =========================================================================
    def get_bar_tabs(self) -> List[dict]:
        return list(self.bar_tabs.values())

    def open_bar_tab(self, customer_name: str, table_or_zone: str = "Bar Stool S1", pre_auth_limit_gbp: float = 50.0) -> dict:
        tab_id = f"TAB-{100 + len(self.bar_tabs) + 1}"
        initial_round = {
            "round_number": 1,
            "items": [
                {"item_id": "item-3", "name": "Camden Pale Craft IPA Pint", "price_gbp": 6.20},
                {"item_id": "item-3", "name": "Camden Pale Craft IPA Pint", "price_gbp": 6.20}
            ],
            "round_total_gbp": 12.40,
            "ordered_at": datetime.now(timezone.utc).isoformat()
        }
        tab = {
            "tab_id": tab_id,
            "customer_name": customer_name,
            "table_or_zone": table_or_zone,
            "pre_auth_token": f"PREAUTH-STRIPE-{uuid.uuid4().hex[:6].upper()}",
            "pre_auth_limit_gbp": round(float(pre_auth_limit_gbp), 2),
            "current_balance_gbp": 12.40,
            "status": "OPEN_PRE_AUTHORISED",
            "rounds": [initial_round],
            "opened_at": datetime.now(timezone.utc).isoformat()
        }
        self.bar_tabs[tab_id] = tab
        return tab

    def order_same_again_round(self, tab_id: str) -> dict:
        tab = self.bar_tabs.get(tab_id)
        if not tab:
            raise ValueError(f"Bar tab '{tab_id}' not found")
        if tab["status"] != "OPEN_PRE_AUTHORISED":
            raise ValueError(f"Bar tab '{tab_id}' is already closed")

        last_round = tab["rounds"][-1]
        next_round_num = len(tab["rounds"]) + 1
        round_cost = float(last_round["round_total_gbp"])

        if tab["current_balance_gbp"] + round_cost > tab["pre_auth_limit_gbp"]:
            # Automatically increment pre-auth hold by £50
            tab["pre_auth_limit_gbp"] = round(tab["pre_auth_limit_gbp"] + 50.0, 2)

        new_round = {
            "round_number": next_round_num,
            "items": list(last_round["items"]),
            "round_total_gbp": round_cost,
            "ordered_at": datetime.now(timezone.utc).isoformat()
        }
        tab["rounds"].append(new_round)
        tab["current_balance_gbp"] = round(tab["current_balance_gbp"] + round_cost, 2)

        # Deduct pints from Tap #1 in cellar
        self.kegs_and_taps[0]["pints_poured"] += len(new_round["items"])
        self.kegs_and_taps[0]["pints_remaining"] = max(0, self.kegs_and_taps[0]["pints_remaining"] - len(new_round["items"]))

        return {
            "success": True,
            "tab_id": tab_id,
            "customer_name": tab["customer_name"],
            "repeated_round_number": next_round_num,
            "round_total_gbp": round_cost,
            "new_tab_balance_gbp": tab["current_balance_gbp"],
            "pre_auth_limit_gbp": tab["pre_auth_limit_gbp"],
            "tab": tab
        }

    # =========================================================================
    # 2. CELLAR & KEG MANAGEMENT (LINE CLEANING, POUR COST & ULLAGE WASTAGE)
    # =========================================================================
    def get_cellar_status(self) -> dict:
        total_poured = sum(k["pints_poured"] for k in self.kegs_and_taps)
        total_waste = sum(k["pints_ullage_waste"] for k in self.kegs_and_taps)
        overall_yield = round((total_poured / (total_poured + total_waste)) * 100.0, 1) if (total_poured + total_waste) > 0 else 100.0
        waste_value_gbp = round(sum(k["pints_ullage_waste"] * k["sell_price_gbp"] for k in self.kegs_and_taps), 2)
        avg_pour_cost_pct = round(
            sum((k["pour_cost_gbp"] / (k["sell_price_gbp"] / 1.20)) * 100.0 for k in self.kegs_and_taps) / len(self.kegs_and_taps),
            1
        )
        return {
            "cellar_temperature_c": 11.4,
            "target_cellar_temp_range": "11.0°C - 13.0°C",
            "overall_keg_yield_pct": overall_yield,
            "average_draught_pour_cost_pct": avg_pour_cost_pct,
            "total_ullage_wastage_pints": total_waste,
            "total_ullage_lost_revenue_gbp": waste_value_gbp,
            "taps": self.kegs_and_taps
        }

    def log_beer_line_clean(self, tap_number: int, cleaned_by: str = "Liam O'Connor (Cellar Master)") -> dict:
        for tap in self.kegs_and_taps:
            if tap["tap_number"] == int(tap_number):
                tap["last_line_cleaned_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                tap["line_clean_status"] = "CLEAN_COMPLIANT"
                tap["cleaned_by"] = cleaned_by
                return tap
        raise ValueError(f"Tap #{tap_number} not found")

    # =========================================================================
    # 3. PUB EXTRAS: SUNDAY ROAST PRE-ORDERS, QUIZ TICKETING & HAPPY HOUR
    # =========================================================================
    def get_pub_extras_status(self) -> dict:
        return {
            "sunday_roasts": self.sunday_roast_counter,
            "quiz_and_events": self.pub_events_and_quiz,
            "happy_hour": self.happy_hour_schedule
        }

    def preorder_sunday_roast(self, roast_id: str, quantity: int = 1, guest_name: str = "Table Guest") -> dict:
        qty = max(1, int(quantity))
        for r in self.sunday_roast_counter:
            if r["roast_id"] == roast_id:
                if r["sold_out"] or r["remaining_portions"] < qty:
                    raise ValueError(f"Sorry, '{r['name']}' only has {r['remaining_portions']} portions left!")
                r["remaining_portions"] -= qty
                if r["remaining_portions"] <= 0:
                    r["remaining_portions"] = 0
                    r["sold_out"] = True
                return {
                    "success": True,
                    "roast_id": roast_id,
                    "roast_name": r["name"],
                    "quantity_reserved": qty,
                    "guest_name": guest_name,
                    "total_gbp": round(r["price_gbp"] * qty, 2),
                    "remaining_portions": r["remaining_portions"],
                    "sold_out": r["sold_out"]
                }
        raise ValueError(f"Sunday roast '{roast_id}' not found")

    def book_pub_quiz_team(self, event_id: str, team_name: str, team_size: int = 4) -> dict:
        size = max(1, min(6, int(team_size)))
        for ev in self.pub_events_and_quiz:
            if ev["event_id"] == event_id:
                if ev["teams_booked"] >= ev["max_teams"]:
                    raise ValueError(f"Event '{ev['title']}' is fully booked!")
                ev["teams_booked"] += 1
                fee = round(ev["entry_fee_per_person_gbp"] * size, 2)
                booking = {
                    "ticket_ref": f"TKT-{event_id[:4]}-{100 + ev['teams_booked']}",
                    "team_name": team_name,
                    "team_size": size,
                    "paid_gbp": fee
                }
                ev["bookings"].append(booking)
                return {
                    "success": True,
                    "event_title": ev["title"],
                    "booking": booking,
                    "teams_booked": ev["teams_booked"],
                    "spots_remaining": ev["max_teams"] - ev["teams_booked"]
                }
        raise ValueError(f"Event '{event_id}' not found")

    # =========================================================================
    # 4. BEER GARDEN ZONES & WEATHER-TRIGGERED OPEN/CLOSE TOGGLE
    # =========================================================================
    def get_beer_garden_status(self) -> dict:
        return self.beer_garden_state

    def update_beer_garden_weather_or_toggle(
        self,
        garden_open: Optional[bool] = None,
        simulate_weather: Optional[str] = None
    ) -> dict:
        if simulate_weather == "RAIN_STORM":
            self.beer_garden_state["current_weather"] = {
                "condition": "HEAVY_RAIN",
                "temp_c": 11.0,
                "rain_probability_pct": 92,
                "wind_mph": 24,
                "summary": "11.0°C Heavy Rain Alert — Uncovered Lawn Benches Auto-Closed; Heated Cabana Pods Open"
            }
            self.beer_garden_state["garden_open"] = False
            for z in self.beer_garden_state["zones"]:
                z["status"] = "OPEN_HEATED_ONLY" if z["covered_heated"] else "CLOSED_WEATHER"
        elif simulate_weather == "SUNNY":
            self.beer_garden_state["current_weather"] = {
                "condition": "SUNNY_INTERVALS",
                "temp_c": 21.0,
                "rain_probability_pct": 0,
                "wind_mph": 5,
                "summary": "21.0°C Warm Sunshine — All Beer Garden Benches & Cabana Pods Open!"
            }
            self.beer_garden_state["garden_open"] = True
            for z in self.beer_garden_state["zones"]:
                z["status"] = "OPEN"
        elif garden_open is not None:
            self.beer_garden_state["garden_open"] = bool(garden_open)
            for z in self.beer_garden_state["zones"]:
                z["status"] = "OPEN" if self.beer_garden_state["garden_open"] else "CLOSED_MANUAL"

        return self.beer_garden_state


pub_features_service = UKPubFeaturesModule()
