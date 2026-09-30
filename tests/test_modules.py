import unittest
import os
import sys

# Ensure src path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.db import db
from src.core.config import Config
from src.core.auth import auth_service
from src.core.translation import translator
from src.modules.qr_ordering import qr_ordering_service
from src.modules.kds import kds_service
from src.modules.promos import promo_service
from src.modules.reviews import review_service
from src.modules.finance import finance_service
from src.modules.inventory import inventory_service
from src.modules.exporter import exporter_service

class TestWaiterModules(unittest.TestCase):
    def setUp(self):
        db.reset()

    def test_csv_exporter_reports(self):
        # Place order & review
        order = qr_ordering_service.submit_order(table_number=3, item_ids=["item-1"])
        review_service.submit_review(table_number=3, rating=5, comment="Awesome Fish & Chips!")

        orders_csv = exporter_service.export_orders_csv()
        self.assertIn("Order ID", orders_csv)
        self.assertIn(order["id"], orders_csv)

        inventory_csv = exporter_service.export_inventory_csv()
        self.assertIn("Fish & Chips", inventory_csv)
        self.assertIn("IN_STOCK", inventory_csv)

        reviews_csv = exporter_service.export_reviews_csv()
        self.assertIn("Awesome Fish & Chips!", reviews_csv)

    def test_staff_pin_authentication(self):
        self.assertTrue(auth_service.verify_pin("1234"))
        self.assertFalse(auth_service.verify_pin("0000"))
        self.assertFalse(auth_service.verify_pin(""))

    def test_order_cancellation_and_refund(self):
        stock_before = db.menu_items["item-1"]["stock_qty"]
        order = qr_ordering_service.submit_order(table_number=3, item_ids=["item-1"])
        order_id = order["id"]
        
        self.assertEqual(db.menu_items["item-1"]["stock_qty"], stock_before - 1)

        cancelled_order = db.cancel_order(order_id)
        self.assertEqual(cancelled_order["status"], "CANCELLED")

        self.assertEqual(db.menu_items["item-1"]["stock_qty"], stock_before)

        analytics = finance_service.calculate_analytics()
        self.assertEqual(analytics["total_orders"], 0)
        self.assertEqual(analytics["total_revenue"], 0.0)

    def test_qr_menu_translation_and_currency(self):
        menu_en = qr_ordering_service.get_menu("en", "GBP")
        self.assertGreater(len(menu_en), 0)
        self.assertEqual(menu_en[0]["name_translated"], "Fish & Chips")
        self.assertEqual(menu_en[0]["currency"], "GBP")

        menu_eur = qr_ordering_service.get_menu("fr", "EUR")
        self.assertEqual(menu_eur[0]["name_translated"], "Poisson & Frites")
        self.assertEqual(menu_eur[0]["currency"], "EUR")
        self.assertIn("€", menu_eur[0]["price_formatted"])

        menu_usd = qr_ordering_service.get_menu("en", "USD")
        self.assertEqual(menu_usd[0]["currency"], "USD")
        self.assertIn("$", menu_usd[0]["price_formatted"])

    def test_order_submission_and_upsell(self):
        upsells = qr_ordering_service.get_upsells_for_cart(["item-1"], "en", "GBP")
        self.assertTrue(any(u["id"] == "item-4" for u in upsells))

        order = qr_ordering_service.submit_order(
            table_number=5,
            item_ids=["item-1", "item-3"],
            promo_code="WELCOME10"
        )
        self.assertTrue(order["id"].startswith("ORD-"))
        self.assertEqual(order["table_number"], 5)
        self.assertGreater(order["discount"], 0.0)

    def test_inventory_auto_deduction_and_restock(self):
        initial_stock = db.menu_items["item-1"]["stock_qty"]
        order = qr_ordering_service.submit_order(table_number=1, item_ids=["item-1"])
        
        updated_stock = db.menu_items["item-1"]["stock_qty"]
        self.assertEqual(updated_stock, initial_stock - 1)

        restock_res = inventory_service.restock("item-1", 10)
        self.assertEqual(restock_res["new_stock_qty"], updated_stock + 10)

        inventory = inventory_service.get_inventory_status()
        self.assertTrue(any(i["id"] == "item-1" for i in inventory))

    def test_kds_order_lifecycle(self):
        order = qr_ordering_service.submit_order(table_number=2, item_ids=["item-2"])
        order_id = order["id"]

        self.assertEqual(db.orders[order_id]["status"], "New")

        kds_service.advance_order_status(order_id)
        self.assertEqual(db.orders[order_id]["status"], "Preparing")

        kds_service.advance_order_status(order_id)
        self.assertEqual(db.orders[order_id]["status"], "Ready")

        tv_status = kds_service.get_tv_display_status()
        self.assertIn(order_id, tv_status["ready"])

    def test_private_reviews(self):
        review_service.submit_review(table_number=4, rating=5, comment="Excellent meal")
        review_service.submit_review(table_number=4, rating=3, comment="A bit noisy")

        avg = review_service.get_average_rating()
        self.assertEqual(avg, 4.0)

    def test_finance_invoice_and_multi_currency(self):
        order = qr_ordering_service.submit_order(table_number=1, item_ids=["item-1", "item-4"])
        
        inv_gbp = finance_service.generate_invoice(order["id"], "GBP")
        self.assertIsNotNone(inv_gbp)
        self.assertEqual(inv_gbp["currency"], "GBP")
        self.assertEqual(inv_gbp["currency_symbol"], "£")

        pdf_eur = finance_service.generate_pdf_invoice(order["id"], "EUR")
        self.assertIsNotNone(pdf_eur)
        self.assertTrue(pdf_eur.startswith(b"%PDF"))

        analytics = finance_service.calculate_analytics(total_seats=50, operating_hours=12, currency="USD")
        self.assertIn("rev_pash", analytics)
        self.assertEqual(analytics["currency"], "USD")

    def test_thermal_receipt_printing(self):
        from src.modules.thermal_print import thermal_printer_service
        order = qr_ordering_service.submit_order(table_number=3, item_ids=["item-1", "item-3"])
        
        text_receipt = thermal_printer_service.format_receipt_text(order["id"], width=32)
        self.assertIsNotNone(text_receipt)
        self.assertIn("THE WAITER UK", text_receipt)

        escpos_bytes = thermal_printer_service.generate_escpos_bytes(order["id"])
        self.assertIsNotNone(escpos_bytes)
        self.assertTrue(escpos_bytes.startswith(b"\x1b@"))

    def test_qr_code_and_table_tent_pdf(self):
        from src.modules.qr_generator import qr_generator_service
        
        png_bytes = qr_generator_service.generate_table_qr_png(table_number=4)
        self.assertIsNotNone(png_bytes)
        self.assertTrue(png_bytes.startswith(b"\x89PNG"))

        pdf_bytes = qr_generator_service.generate_pdf_table_tents(total_tables=3)
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_finance_z_report(self):
        order1 = qr_ordering_service.submit_order(table_number=1, item_ids=["item-1", "item-3"])
        order2 = qr_ordering_service.submit_order(table_number=2, item_ids=["item-2"])
        order3 = qr_ordering_service.submit_order(table_number=3, item_ids=["item-4"])
        db.cancel_order(order3["id"])

        report = finance_service.generate_z_report(currency="GBP")
        self.assertIsNotNone(report)
        self.assertEqual(report["total_tickets"], 3)
        self.assertEqual(report["completed_tickets"], 2)
        self.assertEqual(report["cancelled_tickets"], 1)
        self.assertGreater(report["total_revenue"], 0.0)

        pdf_bytes = finance_service.generate_pdf_z_report(currency="GBP")
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_multi_venue_management(self):
        from src.modules.venue import venue_service

        venues = venue_service.get_venues()
        self.assertGreaterEqual(len(venues), 4)

        active = venue_service.get_active_venue()
        self.assertEqual(active["id"], "venue-1")

        self.assertTrue(venue_service.set_active_venue("venue-3"))
        active_fr = venue_service.get_active_venue()
        self.assertEqual(active_fr["id"], "venue-3")
        self.assertEqual(active_fr["currency"], "EUR")

        order = qr_ordering_service.submit_order(table_number=2, item_ids=["item-1"])
        self.assertEqual(order["venue_id"], "venue-3")

        venue_service.set_active_venue("venue-1")

    def test_sse_kds_events(self):
        q = kds_service.subscribe()
        try:
            self.assertTrue(q.empty())

            order = qr_ordering_service.submit_order(table_number=5, item_ids=["item-2"])
            self.assertFalse(q.empty())

            event_msg = q.get_nowait()
            self.assertIn("event: kds_update", event_msg)
            self.assertIn(order["id"], event_msg)

            kds_service.advance_order_status(order["id"])
            event_msg2 = q.get_nowait()
            self.assertIn("STATUS_ADVANCED", event_msg2)
        finally:
            kds_service.unsubscribe(q)

    def test_staff_shift_clock_in_out(self):
        from src.modules.staff import staff_service

        roster = staff_service.get_staff_members()
        self.assertGreaterEqual(len(roster), 4)

        # Clock-in Charlie (7777)
        res_in = staff_service.clock_in("7777")
        self.assertTrue(res_in["success"])
        self.assertFalse(res_in["already_clocked_in"])
        self.assertEqual(res_in["shift"]["staff_name"], "Charlie Parker (Server)")

        # Repeated clock in returns existing shift
        res_repeat = staff_service.clock_in("7777")
        self.assertTrue(res_repeat["already_clocked_in"])

        active_shifts = staff_service.get_active_shifts()
        self.assertEqual(len(active_shifts), 1)

        # Clock-out Charlie
        res_out = staff_service.clock_out("7777")
        self.assertTrue(res_out["success"])
        self.assertEqual(res_out["shift"]["status"], "COMPLETED")
        self.assertGreater(res_out["shift"]["total_hours"], 0.0)

        analytics = staff_service.get_labor_analytics(currency="GBP")
        self.assertIn("labor_cost_percentage", analytics)
        self.assertGreater(analytics["total_labor_cost"], 0.0)

    def test_floor_plan_and_reservations(self):
        from src.modules.floor_plan import floor_plan_service

        tables = floor_plan_service.get_floor_plan()
        self.assertEqual(len(tables), 12)

        # Place an order on Table #3
        order = qr_ordering_service.submit_order(table_number=3, item_ids=["item-1"])

        # Reserve Table #5
        res = floor_plan_service.reserve_table(table_number=5, guest_name="Mr. Smith", time_slot="20:00")
        self.assertTrue(res["success"])

        updated_tables = floor_plan_service.get_floor_plan()
        t3 = next(t for t in updated_tables if t["table_number"] == 3)
        t5 = next(t for t in updated_tables if t["table_number"] == 5)
        t1 = next(t for t in updated_tables if t["table_number"] == 1)

        self.assertEqual(t3["status"], "OCCUPIED")
        self.assertEqual(t5["status"], "RESERVED")
        self.assertEqual(t1["status"], "AVAILABLE")

        # Release Table #5
        rel = floor_plan_service.release_table(5)
        self.assertTrue(rel["success"])

    def test_customer_loyalty_and_rewards(self):
        from src.modules.loyalty import loyalty_service

        phone = "+447700900077"
        reg = loyalty_service.register_account(phone, "James Bond")
        self.assertTrue(reg["success"])
        self.assertEqual(reg["account"]["points_balance"], 50)

        order = qr_ordering_service.submit_order(table_number=1, item_ids=["item-1", "item-2"])
        earn = loyalty_service.earn_points(phone, order["id"])
        self.assertTrue(earn["success"])
        self.assertGreater(earn["new_balance"], 50)

        if earn["new_balance"] >= 100:
            red = loyalty_service.redeem_reward(phone, "REWARD5")
            self.assertTrue(red["success"])
            voucher_code = red["voucher_code"]
            self.assertTrue(voucher_code.startswith("LOYAL5-"))

            discounted_order = qr_ordering_service.submit_order(
                table_number=2,
                item_ids=["item-1"],
                promo_code=voucher_code
            )
            self.assertGreater(discounted_order["discount"], 0.0)

    def test_allergen_and_dietary_filtering(self):
        from src.modules.allergens import allergen_service

        all_menu = allergen_service.get_filtered_menu()
        self.assertGreaterEqual(len(all_menu), 5)

        vegan_menu = allergen_service.get_filtered_menu(dietary_filter="vegan")
        self.assertTrue(all(any(d in ["vegan"] for d in item["dietary"]) for item in vegan_menu))

        no_gluten_menu = allergen_service.get_filtered_menu(exclude_allergens=["gluten"])
        self.assertTrue(all("gluten" not in item["allergens"] for item in no_gluten_menu))

    def test_kitchen_prep_time_and_station_routing(self):
        from src.modules.prep_routing import prep_routing_service

        order = qr_ordering_service.submit_order(table_number=2, item_ids=["item-1", "item-3"])
        order_id = order["id"]

        eta = prep_routing_service.calculate_order_eta(order_id)
        self.assertIsNotNone(eta)
        self.assertEqual(eta["max_prep_mins"], 12)
        self.assertEqual(len(eta["items"]), 2)

        stations = prep_routing_service.get_station_queues()
        self.assertIn("FRYER", stations)
        self.assertIn("BAR", stations)
        self.assertTrue(any(t["order_id"] == order_id for t in stations["FRYER"]))
        self.assertTrue(any(t["order_id"] == order_id for t in stations["BAR"]))

if __name__ == "__main__":
    unittest.main()








