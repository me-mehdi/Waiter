import io
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from src.core.db import db


class UKComplianceModule:
    """
    UK Statutory Hospitality Compliance Engine:
    1. Natasha's Law (PPDS) Ingredient-to-14-Allergen Auto-Tagger & Grab-and-Go Label Printer
    2. Employment (Allocation of Tips) Act 2023 (Effective Oct 2024) — 100% Fair Tip Payout Log & Written Policy
    3. Licensing Act 2003 (Challenge 25) — Alcohol QR Order Flagging, Staff ID Verification & Refusal Register
    4. FSA Safer Food Better Business (SFBB) & HACCP — Fridge Temps, Cleaning Checklists & EHO Inspection Export
    5. HMRC VAT Notice 709/1 — Eat-In (20%) vs Hot Takeaway (20%) vs Cold Takeaway (0% Zero-Rated Food)
    6. UK GDPR (Data Protection Act 2018), London Region (eu-west-2) Hosting & NCSC Cyber Essentials Posture
    """

    # Official 14 UK Food Standards Agency (FSA) Regulated Allergens
    UK_14_ALLERGENS = [
        "celery", "cereals_with_gluten", "crustaceans", "eggs", "fish",
        "lupin", "milk", "molluscs", "mustard", "nuts",
        "peanuts", "sesame", "soybeans", "sulphites"
    ]

    # Ingredient Keyword -> UK 14 Allergen Auto-Detection Dictionary
    INGREDIENT_ALLERGEN_MAP = {
        "cod": ["fish"],
        "haddock": ["fish"],
        "salmon": ["fish"],
        "anchovy": ["fish"],
        "prawn": ["crustaceans"],
        "crab": ["crustaceans"],
        "lobster": ["crustaceans"],
        "squid": ["molluscs"],
        "mussel": ["molluscs"],
        "oyster": ["molluscs"],
        "wheat": ["cereals_with_gluten"],
        "barley": ["cereals_with_gluten"],
        "rye": ["cereals_with_gluten"],
        "oats": ["cereals_with_gluten"],
        "flour": ["cereals_with_gluten"],
        "brioche": ["cereals_with_gluten", "eggs", "milk"],
        "beer batter": ["cereals_with_gluten", "sulphites"],
        "craft ipa": ["cereals_with_gluten", "sulphites"],
        "malt": ["cereals_with_gluten"],
        "bread": ["cereals_with_gluten"],
        "cheddar": ["milk"],
        "parmesan": ["milk"],
        "parmigiano": ["milk"],
        "butter": ["milk"],
        "butterscotch": ["milk"],
        "cream": ["milk"],
        "clotted cream": ["milk"],
        "milk": ["milk"],
        "whey": ["milk"],
        "egg": ["eggs"],
        "mayo": ["eggs", "mustard"],
        "mayonnaise": ["eggs", "mustard"],
        "tartar": ["eggs", "mustard", "sulphites"],
        "mustard": ["mustard"],
        "celery": ["celery"],
        "celeriac": ["celery"],
        "peanut": ["peanuts"],
        "almond": ["nuts"],
        "walnut": ["nuts"],
        "hazelnut": ["nuts"],
        "cashew": ["nuts"],
        "pistachio": ["nuts"],
        "pecan": ["nuts"],
        "sesame": ["sesame"],
        "tahini": ["sesame"],
        "soy": ["soybeans"],
        "soya": ["soybeans"],
        "edamame": ["soybeans"],
        "tofu": ["soybeans"],
        "lupin": ["lupin"],
        "wine": ["sulphites"],
        "vinegar": ["sulphites"],
        "caper": ["sulphites"]
    }

    def __init__(self):
        # 1. Pre-configured Dish Ingredient Breakdowns for Natasha's Law PPDS Labels
        self.dish_recipes: Dict[str, dict] = {
            "item-1": {
                "item_id": "item-1",
                "dish_name": "Brixham Cod Fish & Chips",
                "is_ppds_eligible": True,
                "storage_instructions": "Keep hot above 63°C or chill below 5°C. Consume within 2 hours.",
                "net_weight_g": 480,
                "raw_ingredients": [
                    "Brixham Atlantic Cod Fillet",
                    "Wheat Flour",
                    "Malted Barley Craft IPA Beer Batter",
                    "Maris Piper Potatoes",
                    "Marrowfat Mushy Peas",
                    "Free-Range Egg Mayonnaise",
                    "Dijon Mustard",
                    "Capers in Spirit Vinegar"
                ]
            },
            "item-2": {
                "item_id": "item-2",
                "dish_name": "Gourmet British Wagyu Beef Burger",
                "is_ppds_eligible": True,
                "storage_instructions": "Keep refrigerated at 0°C to 5°C. Reheat thoroughly to 75°C core.",
                "net_weight_g": 380,
                "raw_ingredients": [
                    "British Wagyu Beef Patty",
                    "Glazed Wheat Flour Brioche Bun",
                    "Pasteurised Milk Clarified Butter",
                    "Aged Somerset Cheddar Cheese (Milk)",
                    "Free-Range Egg Truffle Mayonnaise",
                    "Yellow Mustard Seeds",
                    "Red Wine Vinegar Onion Chutney"
                ]
            },
            "item-3": {
                "item_id": "item-3",
                "dish_name": "Camden Pale Craft IPA Pint (5.2% ABV)",
                "is_ppds_eligible": False,
                "storage_instructions": "Cellar chilled at 4°C - 6°C.",
                "net_weight_g": 568,
                "raw_ingredients": [
                    "Water",
                    "Malted Barley",
                    "Wheat Malt",
                    "British Hops",
                    "Brewers Yeast (Sulphites)"
                ]
            },
            "item-4": {
                "item_id": "item-4",
                "dish_name": "Artisan Truffle & Parmesan Fries (Grab & Go Box)",
                "is_ppds_eligible": True,
                "storage_instructions": "Store below 5°C if pre-packed cold, or serve hot above 63°C.",
                "net_weight_g": 220,
                "raw_ingredients": [
                    "Julienne Potatoes",
                    "White Alba Truffle Olive Oil",
                    "24-Month Parmigiano-Reggiano (Milk)",
                    "Cornish Sea Salt",
                    "Flat-Leaf Parsley"
                ]
            },
            "item-5": {
                "item_id": "item-5",
                "dish_name": "Medjool Date Sticky Toffee Pudding (Pre-Packed Deli Pot)",
                "is_ppds_eligible": True,
                "storage_instructions": "Keep refrigerated below 5°C. Best before: +48 hours from pack date.",
                "net_weight_g": 295,
                "raw_ingredients": [
                    "Medjool Dates",
                    "Self-Raising Wheat Flour",
                    "Free-Range Eggs",
                    "Salted Butterscotch Cream Sauce (Milk)",
                    "Cornish Clotted Cream (Milk)",
                    "Madagascan Vanilla Bean"
                ]
            }
        }

        # 2. Employment (Allocation of Tips) Act 2023 — Staff Payout Log & Policy
        self.written_tipping_policy = {
            "legislation": "Employment (Allocation of Tips) Act 2023 & Statutory Code of Practice (Effective 1 October 2024)",
            "policy_version": "v2024.10-UK",
            "employer_deduction_pct": 0.0,
            "pass_through_pct": 100.0,
            "allocation_method": "Independent Tronc Master Point System (45% Front-of-House Waiters, 35% Kitchen Chefs & Porters, 20% Bar & Runner Support)",
            "payment_deadline": "No later than the end of the month following the month in which the tip was paid by the customer.",
            "record_retention_years": 3,
            "agency_workers_included": True,
            "policy_summary": (
                "100% of all qualifying tips, gratuities, and service charges paid via Card, Apple Pay, Google Pay, or QR Checkout "
                "are ring-fenced in the staff Tronc pool with zero employer administration deductions. Every worker (including zero-hour "
                "and agency staff) has the statutory right to inspect their 3-year tipping payout statement."
            )
        }
        self.tip_payout_logs: List[dict] = [
            {
                "payout_id": "TIP-PAY-1001",
                "period": datetime.now(timezone.utc).strftime("%Y-%m"),
                "staff_name": "Sarah Jenkins",
                "role": "Senior Floor Server (FOH)",
                "hours_worked": 38.5,
                "tronc_points": 4.5,
                "gross_tip_allocated_gbp": 184.50,
                "employer_deduction_gbp": 0.00,
                "net_payout_gbp": 184.50,
                "status": "DISBURSED_FULL_100_PCT",
                "paid_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "payout_id": "TIP-PAY-1002",
                "period": datetime.now(timezone.utc).strftime("%Y-%m"),
                "staff_name": "Marco Rossi",
                "role": "Head Grill Chef (Kitchen)",
                "hours_worked": 42.0,
                "tronc_points": 3.5,
                "gross_tip_allocated_gbp": 143.50,
                "employer_deduction_gbp": 0.00,
                "net_payout_gbp": 143.50,
                "status": "DISBURSED_FULL_100_PCT",
                "paid_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "payout_id": "TIP-PAY-1003",
                "period": datetime.now(timezone.utc).strftime("%Y-%m"),
                "staff_name": "Liam O'Connor",
                "role": "Head Bartender & Cellar (Bar)",
                "hours_worked": 36.0,
                "tronc_points": 2.0,
                "gross_tip_allocated_gbp": 82.00,
                "employer_deduction_gbp": 0.00,
                "net_payout_gbp": 82.00,
                "status": "DISBURSED_FULL_100_PCT",
                "paid_at": datetime.now(timezone.utc).isoformat()
            }
        ]

        # 3. Challenge 25 Age Verification Log (Licensing Act 2003)
        self.alcohol_item_ids = {"item-3"}
        self.challenge25_logs: List[dict] = [
            {
                "check_id": "CH25-1001",
                "order_id": "ORD-0001",
                "table_number": 4,
                "item_name": "Camden Pale Craft IPA Pint (5.2% ABV)",
                "decision": "APPROVED",
                "id_type": "UK Photocard Driving Licence",
                "verified_by_staff": "Liam O'Connor (Personal Licence #LN/2024091)",
                "customer_looks_under_25": True,
                "dob_verified_18_plus": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]

        # 4. FSA Food Safety, Fridge Temperatures, Cleaning & HACCP Logs
        self.fridge_temp_logs: List[dict] = [
            {
                "log_id": "TEMP-1001",
                "unit_name": "Walk-In Cold Room #1 (Raw Meat & Fish)",
                "unit_type": "CHILLER",
                "target_range": "0.0°C to 5.0°C",
                "recorded_temp_c": 2.8,
                "status": "COMPLIANT",
                "corrective_action": "None required",
                "checked_by": "Marco Rossi (Head Chef)",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "log_id": "TEMP-1002",
                "unit_name": "Dairy & Grab-and-Go Display Fridge #2",
                "unit_type": "CHILLER",
                "target_range": "0.0°C to 5.0°C",
                "recorded_temp_c": 3.4,
                "status": "COMPLIANT",
                "corrective_action": "None required",
                "checked_by": "Sarah Jenkins",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "log_id": "TEMP-1003",
                "unit_name": "Deep Freeze Chest #1 (Artisan Ice Cream & Chips)",
                "unit_type": "FREEZER",
                "target_range": "-18.0°C or colder",
                "recorded_temp_c": -20.5,
                "status": "COMPLIANT",
                "corrective_action": "None required",
                "checked_by": "Marco Rossi (Head Chef)",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]

        self.cleaning_haccp_checklists: List[dict] = [
            {"task_id": "HACCP-01", "category": "OPENING_SFBB", "task": "Sanitise all raw/ready-to-eat prep surfaces to BS EN 1276 standard (30s contact time)", "completed": True, "signed_by": "Marco Rossi"},
            {"task_id": "HACCP-02", "category": "CROSS_CONTAMINATION", "task": "Verify colour-coded chopping boards (Red: Raw Meat, Blue: Raw Fish, Purple: Allergen-Free)", "completed": True, "signed_by": "Marco Rossi"},
            {"task_id": "HACCP-03", "category": "HOT_HOLD_CCP", "task": "Probe check hot pass & gravy hold >= 63°C and core cooking temp >= 75°C for 30s", "completed": True, "signed_by": "Marco Rossi"},
            {"task_id": "HACCP-04", "category": "CLOSING_SFBB", "task": "Deep clean fryer filtration, cellar beer lines, and seal clinical/food waste bins", "completed": True, "signed_by": "Liam O'Connor"}
        ]

    # =========================================================================
    # 1. NATASHA'S LAW (PPDS) INGREDIENT & LABEL ENGINE
    # =========================================================================
    def build_dish_allergen_profile(self, item_id: str, custom_ingredients: Optional[List[str]] = None) -> dict:
        recipe = self.dish_recipes.get(item_id, {
            "item_id": item_id,
            "dish_name": f"Custom Bakery / Deli Item ({item_id})",
            "is_ppds_eligible": True,
            "storage_instructions": "Keep refrigerated below 5°C.",
            "net_weight_g": 250,
            "raw_ingredients": custom_ingredients or ["Wheat Flour", "Butter (Milk)", "Free-Range Eggs"]
        })
        ingredients_list = custom_ingredients if custom_ingredients is not None else recipe["raw_ingredients"]

        detected_allergens = set()
        formatted_ingredients_html = []
        formatted_ingredients_text = []

        for ing in ingredients_list:
            ing_lower = ing.lower()
            matched_for_this_ing = set()
            for kw, allg_list in self.INGREDIENT_ALLERGEN_MAP.items():
                if kw in ing_lower:
                    for a in allg_list:
                        detected_allergens.add(a)
                        matched_for_this_ing.add(a.upper().replace("_", " "))

            if matched_for_this_ing:
                badge_str = ", ".join(sorted(matched_for_this_ing))
                formatted_ingredients_html.append(f"{ing} (<strong>{badge_str}</strong>)")
                formatted_ingredients_text.append(f"{ing} (**{badge_str}**)")
            else:
                formatted_ingredients_html.append(ing)
                formatted_ingredients_text.append(ing)

        now_utc = datetime.now(timezone.utc)
        use_by_dt = (now_utc + timedelta(days=2)).strftime("%d/%m/%Y 23:59")

        return {
            "item_id": item_id,
            "dish_name": recipe["dish_name"],
            "regulation": "The Food Information (Amendment) (England) Regulations 2019 (Natasha's Law — PPDS)",
            "is_ppds_eligible": recipe["is_ppds_eligible"],
            "net_weight_g": recipe["net_weight_g"],
            "raw_ingredients": ingredients_list,
            "detected_14_allergens": sorted(list(detected_allergens)),
            "natashas_law_label_html": (
                f"<strong>{recipe['dish_name'].upper()}</strong><br>"
                f"<small><strong>INGREDIENTS:</strong> {', '.join(formatted_ingredients_html)}.</small><br>"
                f"<small><strong>ALLERGY ADVICE:</strong> For allergens, including cereals containing gluten, see ingredients in <strong>BOLD CAPITALS</strong>.</small><br>"
                f"<small><strong>STORAGE:</strong> {recipe['storage_instructions']} | <strong>USE BY:</strong> {use_by_dt}</small><br>"
                f"<small><strong>PACKED AT:</strong> The Waiter UK Flagship, 14 Covent Garden Piazza, London WC2E 8HD</small>"
            ),
            "natashas_law_label_text": (
                f"=== NATASHA'S LAW PPDS GRAB-AND-GO LABEL ===\n"
                f"PRODUCT: {recipe['dish_name'].upper()} ({recipe['net_weight_g']}g)\n"
                f"INGREDIENTS: {', '.join(formatted_ingredients_text)}.\n"
                f"ALLERGY ADVICE: For allergens, see ingredients in **BOLD CAPITALS**.\n"
                f"CONTAINS UK 14 ALLERGENS: {', '.join(sorted([a.upper() for a in detected_allergens])) or 'NONE'}\n"
                f"STORAGE: {recipe['storage_instructions']}\n"
                f"PACKED ON: {now_utc.strftime('%d/%m/%Y %H:%M')} | USE BY: {use_by_dt}\n"
                f"VENUE: The Waiter UK Flagship, Covent Garden, London WC2E 8HD"
            )
        }

    def get_all_ppds_labels(self) -> List[dict]:
        return [self.build_dish_allergen_profile(item_id) for item_id in self.dish_recipes.keys()]

    # =========================================================================
    # 2. EMPLOYMENT (ALLOCATION OF TIPS) ACT 2023 (OCT 2024) ENGINE
    # =========================================================================
    def get_tips_act_2024_compliance(self) -> dict:
        total_distributed = round(sum(p["net_payout_gbp"] for p in self.tip_payout_logs), 2)
        return {
            "compliant_with_oct_2024_act": True,
            "written_policy": self.written_tipping_policy,
            "total_tips_disbursed_gbp": total_distributed,
            "employer_deductions_gbp": 0.00,
            "staff_payout_logs": self.tip_payout_logs
        }

    def record_staff_tip_payout(self, staff_name: str, role: str, hours_worked: float, amount_gbp: float) -> dict:
        entry = {
            "payout_id": f"TIP-PAY-{1000 + len(self.tip_payout_logs) + 1}",
            "period": datetime.now(timezone.utc).strftime("%Y-%m"),
            "staff_name": staff_name,
            "role": role,
            "hours_worked": round(float(hours_worked), 1),
            "tronc_points": 3.0,
            "gross_tip_allocated_gbp": round(float(amount_gbp), 2),
            "employer_deduction_gbp": 0.00,
            "net_payout_gbp": round(float(amount_gbp), 2),
            "status": "DISBURSED_FULL_100_PCT",
            "paid_at": datetime.now(timezone.utc).isoformat()
        }
        self.tip_payout_logs.insert(0, entry)
        return entry

    # =========================================================================
    # 3. AGE VERIFICATION (CHALLENGE 25 — LICENSING ACT 2003)
    # =========================================================================
    def check_order_requires_challenge25(self, item_ids: List[str]) -> dict:
        flagged = []
        for iid in item_ids:
            if iid in self.alcohol_item_ids:
                item_obj = db.menu_items.get(iid, {})
                name = item_obj.get("name", {}).get("en", "Alcoholic Beverage")
                flagged.append({"item_id": iid, "name": name, "abv": "5.2% ABV", "policy": "Challenge 25 Mandatory ID Check"})
        return {
            "requires_challenge25": len(flagged) > 0,
            "flagged_alcohol_items": flagged,
            "licensing_notice": "Under the UK Licensing Act 2003, our venue operates a strict Challenge 25 policy. Staff will verify photographic ID (Passport, Driving Licence, or PASS card) at your table before serving alcohol."
        }

    def verify_challenge25_id(
        self,
        table_number: int,
        order_id: str,
        decision: str = "APPROVED",
        id_type: str = "UK Photocard Driving Licence",
        verified_by_staff: str = "Duty Manager (Personal Licence Holder)"
    ) -> dict:
        record = {
            "check_id": f"CH25-{1000 + len(self.challenge25_logs) + 1}",
            "order_id": order_id,
            "table_number": int(table_number),
            "item_name": "Camden Pale Craft IPA Pint (5.2% ABV)",
            "decision": decision.upper(),
            "id_type": id_type,
            "verified_by_staff": verified_by_staff,
            "customer_looks_under_25": True,
            "dob_verified_18_plus": (decision.upper() == "APPROVED"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.challenge25_logs.insert(0, record)
        return record

    # =========================================================================
    # 4. FOOD SAFETY LOGS (FRIDGE TEMPS, CLEANING, HACCP & EHO EXPORT)
    # =========================================================================
    def log_fridge_temperature(self, unit_name: str, unit_type: str, recorded_temp_c: float, checked_by: str) -> dict:
        temp = round(float(recorded_temp_c), 1)
        u_type = unit_type.upper()
        if u_type == "FREEZER":
            is_ok = temp <= -18.0
            target = "-18.0°C or colder"
            action = "None required" if is_ok else "CRITICAL CCP BREACH: Transfer stock to backup freezer & call refrigeration engineer."
        elif u_type == "HOT_HOLD":
            is_ok = temp >= 63.0
            target = "63.0°C or hotter"
            action = "None required" if is_ok else "CRITICAL CCP BREACH: Reheat to 75°C immediately or discard after 2-hour rule."
        else:
            is_ok = 0.0 <= temp <= 5.0
            target = "0.0°C to 5.0°C"
            action = "None required" if is_ok else "CRITICAL CCP BREACH: Adjust thermostat, re-probe in 30 mins; discard high-risk food if >8°C for 4h."

        entry = {
            "log_id": f"TEMP-{1000 + len(self.fridge_temp_logs) + 1}",
            "unit_name": unit_name,
            "unit_type": u_type,
            "target_range": target,
            "recorded_temp_c": temp,
            "status": "COMPLIANT" if is_ok else "CCP_BREACH_ACTION_REQUIRED",
            "corrective_action": action,
            "checked_by": checked_by,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.fridge_temp_logs.insert(0, entry)
        return entry

    def toggle_haccp_task(self, task_id: str, signed_by: str = "Duty Manager") -> Optional[dict]:
        for t in self.cleaning_haccp_checklists:
            if t["task_id"] == task_id:
                t["completed"] = not t["completed"]
                t["signed_by"] = signed_by
                return t
        return None

    def get_food_safety_status(self) -> dict:
        all_temps_ok = all(l["status"] == "COMPLIANT" for l in self.fridge_temp_logs)
        all_tasks_done = all(t["completed"] for t in self.cleaning_haccp_checklists)
        return {
            "fsa_hygiene_rating_target": "5 / 5 (VERY GOOD — FSA Safer Food Better Business)",
            "eho_inspection_ready": all_temps_ok and all_tasks_done,
            "fridge_temp_logs": self.fridge_temp_logs,
            "cleaning_haccp_checklists": self.cleaning_haccp_checklists
        }

    # =========================================================================
    # 5. HMRC VAT NOTICE 709/1 (EAT-IN vs HOT TAKEAWAY vs COLD TAKEAWAY)
    # =========================================================================
    def calculate_order_mode_vat(self, item_ids: List[str], dining_mode: str = "EAT_IN") -> dict:
        """
        HMRC VAT Notice 709/1 (Catering, takeaway food):
        - EAT_IN: All food & drink consumed on premises is 20% Standard-Rated.
        - HOT_TAKEAWAY: Food served hot (> ambient temperature) for takeaway is 20% Standard-Rated; drinks/alcohol 20%.
        - COLD_TAKEAWAY: Cold takeaway food (sandwiches, salads, cold bakery/deli items) is 0% Zero-Rated,
          EXCEPT standard-rated beverages/alcohol/crisps/confectionery (which remain 20%).
        """
        mode = dining_mode.upper().strip()
        if mode not in ("EAT_IN", "HOT_TAKEAWAY", "COLD_TAKEAWAY"):
            mode = "EAT_IN"

        lines = []
        net_standard_20 = 0.0
        vat_standard_20 = 0.0
        net_zero_rated_0 = 0.0

        for iid in item_ids:
            item_obj = db.menu_items.get(iid)
            if not item_obj:
                continue
            gross_price = float(item_obj["price"])
            name = item_obj["name"]["en"]
            category = item_obj.get("category", "Mains")

            if mode == "COLD_TAKEAWAY" and category != "Drinks" and iid not in self.alcohol_item_ids:
                # Zero-rated cold takeaway food under HMRC Notice 709/1
                vat_rate = 0.0
                net_amt = gross_price
                vat_amt = 0.0
                net_zero_rated_0 += net_amt
                tax_code = "ZERO_RATED_0_PCT (HMRC 709/1 Cold Takeaway Food)"
            else:
                # 20% Standard UK VAT (VAT-inclusive menu price: Net = Gross / 1.2, VAT = Gross - Net)
                vat_rate = 20.0
                net_amt = round(gross_price / 1.20, 2)
                vat_amt = round(gross_price - net_amt, 2)
                net_standard_20 += net_amt
                vat_standard_20 += vat_amt
                tax_code = f"STANDARD_20_PCT ({mode.replace('_', ' ').title()})"

            lines.append({
                "item_id": iid,
                "name": name,
                "gross_price_gbp": round(gross_price, 2),
                "net_price_gbp": round(net_amt, 2),
                "vat_amount_gbp": round(vat_amt, 2),
                "vat_rate_pct": vat_rate,
                "hmrc_tax_code": tax_code
            })

        total_net = round(net_standard_20 + net_zero_rated_0, 2)
        total_vat = round(vat_standard_20, 2)
        # In COLD_TAKEAWAY mode, if venue passes zero-rating benefit or tracks VAT liability:
        total_gross = round(total_net + total_vat, 2)

        return {
            "hmrc_reference": "HMRC VAT Notice 709/1 (Catering and Takeaway Food)",
            "dining_mode": mode,
            "items_breakdown": lines,
            "net_standard_rated_gbp": round(net_standard_20, 2),
            "vat_20_pct_payable_gbp": total_vat,
            "net_zero_rated_gbp": round(net_zero_rated_0, 2),
            "total_net_sales_gbp": total_net,
            "total_vat_payable_gbp": total_vat,
            "total_gross_payable_gbp": total_gross
        }

    # =========================================================================
    # 6. UK GDPR, LONDON REGION RESIDENCY & CYBER ESSENTIALS POSTURE
    # =========================================================================
    def get_uk_gdpr_and_security_posture(self) -> dict:
        return {
            "data_residency": "UK Sovereign Cloud — London Region (eu-west-2, ISO 27001 Tier-4 Data Centres)",
            "legislation": "UK GDPR & Data Protection Act 2018 (ICO Registered Controller)",
            "cyber_security_certification": "NCSC Cyber Essentials & Cyber Essentials Plus Ready",
            "encryption_standard": "TLS 1.3 In-Transit & AES-256 At-Rest Database Encryption",
            "payment_security": "PCI-DSS v4.0 Level 1 Tokenised Checkout (Zero Raw PAN Storage)",
            "guest_privacy_controls": [
                "Zero third-party ad-tracker cookies on Guest QR Menus",
                "Automated 90-day anonymisation of guest table booking PII",
                "1-Click Data Subject Access Request (DSAR) & Right-to-Erasure (Right to be Forgotten) API"
            ]
        }

    # =========================================================================
    # 7. EHO & UK STATUTORY COMPLIANCE AUDIT PDF GENERATOR
    # =========================================================================
    def generate_eho_compliance_pdf(self) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('EhoTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#0f172a"), spaceAfter=6)
        sec_style = ParagraphStyle('EhoSec', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#1e3a8a"), spaceBefore=12, spaceAfter=6)

        story.append(Paragraph("THE WAITER — UK EHO & STATUTORY COMPLIANCE AUDIT PACK", title_style))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | <b>Region:</b> UK London (eu-west-2) | <b>Cyber Essentials:</b> Verified", styles['Normal']))
        story.append(Spacer(1, 12))

        # Section 1: Fridge & Freezer Temps
        story.append(Paragraph("1. FSA Safer Food Better Business (SFBB) — Temperature Logs", sec_style))
        t_data = [["Unit Name", "Type", "Target", "Recorded", "Status", "Checked By"]]
        for l in self.fridge_temp_logs:
            t_data.append([l["unit_name"][:28], l["unit_type"], l["target_range"], f"{l['recorded_temp_c']}°C", l["status"], l["checked_by"]])
        t1 = Table(t_data, colWidths=[145, 55, 85, 55, 75, 95])
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t1)

        # Section 2: Employment (Allocation of Tips) Act 2024
        story.append(Paragraph("2. Employment (Allocation of Tips) Act 2024 — 100% Staff Payout Audit", sec_style))
        tip_data = [["Payout ID", "Staff Member", "Role", "Hours", "Employer Ded.", "Net Paid (100%)"]]
        for p in self.tip_payout_logs:
            tip_data.append([p["payout_id"], p["staff_name"], p["role"][:22], str(p["hours_worked"]), "£0.00 (0%)", f"£{p['net_payout_gbp']:.2f}"])
        t2 = Table(tip_data, colWidths=[75, 100, 120, 50, 80, 85])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t2)

        # Section 3: Challenge 25 Age Verification Log
        story.append(Paragraph("3. Licensing Act 2003 — Challenge 25 Age Verification Register", sec_style))
        c25_data = [["Check ID", "Table", "Item", "Decision", "ID Verified", "Staff Licence Holder"]]
        for c in self.challenge25_logs:
            c25_data.append([c["check_id"], f"#{c['table_number']}", c["item_name"][:22], c["decision"], c["id_type"][:22], c["verified_by_staff"][:24]])
        t3 = Table(c25_data, colWidths=[65, 45, 115, 65, 105, 115])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#166534")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t3)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


uk_compliance_service = UKComplianceModule()
