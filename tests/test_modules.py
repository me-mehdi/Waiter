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

    def test_tip_and_service_charge_tronc_distribution(self):
        from src.modules.tips_tronc import tips_tronc_service
        from src.modules.staff import staff_service

        staff_service.clock_in("1234")
        staff_service.clock_in("7777")

        order = qr_ordering_service.submit_order(table_number=1, item_ids=["item-1", "item-3"])

        sc_amount = tips_tronc_service.calculate_service_charge(order["subtotal"])
        self.assertEqual(sc_amount, round(order["subtotal"] * 0.125, 2))

        summary = tips_tronc_service.get_tronc_summary(currency="GBP")
        self.assertIsNotNone(summary)
        self.assertEqual(summary["service_charge_rate"], "12.5%")
        self.assertGreater(summary["total_tronc_pool"], 0.0)
        self.assertGreaterEqual(len(summary["payout_breakdown"]), 2)

    def test_equal_bill_splitting_and_group_payment(self):
        from src.modules.bill_splitting import bill_splitting_service

        order = qr_ordering_service.submit_order(table_number=4, item_ids=["item-1", "item-2"])
        order_id = order["id"]

        split_res = bill_splitting_service.split_evenly(order_id, num_guests=3, include_service_charge=True)
        self.assertEqual(split_res["total_guests"], 3)
        self.assertEqual(len(split_res["splits"]), 3)

        sum_splits = sum(s["total"] for s in split_res["splits"])
        self.assertEqual(round(sum_splits, 2), round(split_res["order_total"], 2))

        # Pay share for guest 1
        st1 = bill_splitting_service.pay_split_share(order_id, split_id_or_index=1, payment_method="CARD")
        self.assertEqual(st1["settlement_status"], "PARTIAL")

        # Pay share for guest 2 & 3
        bill_splitting_service.pay_split_share(order_id, split_id_or_index=2, payment_method="CASH")
        st3 = bill_splitting_service.pay_split_share(order_id, split_id_or_index=3, payment_method="APPLE_PAY")
        self.assertEqual(st3["settlement_status"], "SETTLED")

        # Check main order status updated to PAID
        updated_order = db.orders.get(order_id)
        self.assertEqual(updated_order["status"], "PAID")

        # Generate sub-receipt
        receipt_txt = bill_splitting_service.generate_sub_receipt(order_id, split_id_or_index=1)
        self.assertIn("THE WAITER UK", receipt_txt)
        self.assertIn("GUEST: Guest 1", receipt_txt)
        self.assertIn("STATUS: PAID (CARD)", receipt_txt)

    def test_itemized_bill_splitting(self):
        from src.modules.bill_splitting import bill_splitting_service

        order = qr_ordering_service.submit_order(table_number=6, item_ids=["item-1", "item-3"])
        order_id = order["id"]

        guest_assignments = [
            {"guest_name": "Alice", "items": [{"name": "Fish & Chips", "price": 14.50}]},
            {"guest_name": "Bob", "items": [{"name": "Craft IPA Pint", "price": 6.20}]}
        ]

        split_res = bill_splitting_service.split_itemized(order_id, guest_assignments, include_service_charge=True)
        self.assertEqual(split_res["split_type"], "ITEMIZED")
        self.assertEqual(len(split_res["splits"]), 2)
        self.assertEqual(split_res["splits"][0]["guest_name"], "Alice")
        self.assertEqual(split_res["splits"][1]["guest_name"], "Bob")

        sum_totals = sum(s["total"] for s in split_res["splits"])
        self.assertEqual(round(sum_totals, 2), round(split_res["order_total"], 2))

    def test_automated_purchase_order_generator(self):
        from src.modules.purchase_orders import purchase_order_service

        # Artificially set item stock to low stock level
        db.update_stock_qty("item-1", 3)
        db.update_stock_qty("item-3", 4)

        low_items = purchase_order_service.get_low_stock_items(threshold=10)
        self.assertGreaterEqual(len(low_items), 2)

        pos = purchase_order_service.generate_purchase_orders(threshold=10, reorder_qty=50)
        self.assertGreaterEqual(len(pos), 2)

        seafood_po = next(p for p in pos if p["supplier_category"] == "SEAFOOD")
        self.assertIn("PO-UK-", seafood_po["po_number"])
        self.assertEqual(seafood_po["supplier_name"], "Brixham Seafood Direct Ltd")
        self.assertGreater(seafood_po["total_estimated_cost"], 0.0)

        # Email text check
        email_text = purchase_order_service.generate_po_email_text(seafood_po)
        self.assertIn("Dear Dave Miller", email_text)
        self.assertIn("Brixham Seafood Direct Ltd", email_text)

        # PDF generation check
        pdf_bytes = purchase_order_service.generate_po_pdf(seafood_po)
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_kitchen_waste_tracker(self):
        from src.modules.waste_tracker import waste_tracker_service

        stock_before = db.menu_items["item-1"]["stock_qty"]
        log1 = waste_tracker_service.log_waste(item_id="item-1", quantity=2, reason="EXPIRED", staff_name="Head Chef Marco")
        self.assertEqual(log1["item_id"], "item-1")
        self.assertEqual(log1["quantity"], 2)
        self.assertEqual(log1["reason"], "EXPIRED")
        self.assertEqual(log1["remaining_stock"], max(0, stock_before - 2))

        log2 = waste_tracker_service.log_waste(item_id="item-2", quantity=1, reason="SPOILED", staff_name="Sous Chef Dave")
        self.assertEqual(log2["reason"], "SPOILED")

        logs = waste_tracker_service.get_waste_logs()
        self.assertGreaterEqual(len(logs), 2)

        analytics = waste_tracker_service.get_waste_analytics(currency="GBP")
        self.assertGreater(analytics["total_financial_loss"], 0.0)
        self.assertIn("EXPIRED", analytics["reason_breakdown"])

        pdf_bytes = waste_tracker_service.generate_waste_pdf_report(currency="GBP")
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_feedback_nps_sentiment_analytics(self):
        from src.modules.feedback_analytics import feedback_analytics_service
        from src.modules.reviews import review_service

        review_service.submit_review(table_number=1, rating=5, comment="Delicious fresh food and fast amazing service!")
        review_service.submit_review(table_number=2, rating=5, comment="Great craft beer and wonderful atmosphere!")
        review_service.submit_review(table_number=3, rating=1, comment="Slow service and cold food!")

        nps = feedback_analytics_service.calculate_nps()
        self.assertIn("nps_score", nps)
        self.assertGreater(nps["total_reviews"], 0)
        self.assertGreater(nps["promoters_count"], 0)

        sentiment = feedback_analytics_service.extract_sentiment()
        self.assertGreater(sentiment["positive_reviews_count"], 0)
        self.assertGreater(len(sentiment["top_positive_keywords"]), 0)

        alerts = feedback_analytics_service.get_manager_alerts()
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["urgency"], "HIGH")

        pdf_bytes = feedback_analytics_service.generate_feedback_pdf_report()
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_guest_table_reservation_booking_engine(self):
        from src.modules.table_booking import table_booking_service
        from src.modules.floor_plan import floor_plan_service

        booking = table_booking_service.create_booking(
            guest_name="Sarah Connor",
            guest_phone="+44 7911 123456",
            guest_email="sarah@sky.net",
            party_size=4,
            booking_date="2026-10-15",
            time_slot="20:00",
            special_requests="Celebrating anniversary, quiet booth"
        )

        self.assertIn("BKG-UK-", booking["id"])
        self.assertEqual(booking["guest_name"], "Sarah Connor")
        self.assertEqual(booking["party_size"], 4)
        self.assertEqual(booking["status"], "CONFIRMED")

        # Verify floor plan table is RESERVED
        tbl_num = booking["table_number"]
        fp_tables = floor_plan_service.get_floor_plan()
        target_tbl = next(t for t in fp_tables if t["table_number"] == tbl_num)
        self.assertEqual(target_tbl["status"], "RESERVED")

        # Update status to SEATED -> table becomes OCCUPIED
        updated = table_booking_service.update_booking_status(booking["id"], "SEATED")
        self.assertEqual(updated["status"], "SEATED")
        fp_tables_seated = floor_plan_service.get_floor_plan()
        seated_tbl = next(t for t in fp_tables_seated if t["table_number"] == tbl_num)
        self.assertEqual(seated_tbl["status"], "OCCUPIED")

        # Update status to COMPLETED -> table becomes AVAILABLE
        table_booking_service.update_booking_status(booking["id"], "COMPLETED")
        fp_tables_freed = floor_plan_service.get_floor_plan()
        freed_tbl = next(t for t in fp_tables_freed if t["table_number"] == tbl_num)
        self.assertEqual(freed_tbl["status"], "AVAILABLE")

        # Generate PDF confirmation pass
        pdf_bytes = table_booking_service.generate_booking_pdf(booking["id"])
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_inter_venue_stock_transfers_and_manifest_pdf(self):
        from src.modules.store_transfers import store_transfers_service

        transfer = store_transfers_service.request_transfer(
            source_venue_id="venue-1",
            target_venue_id="venue-2",
            items=[{"item_id": "item-1", "quantity": 10}, {"item_id": "item-3", "quantity": 5}],
            requested_by="Central Kitchen Manager Dave",
            notes="Urgent weekend replenishment for Soho Lounge"
        )

        self.assertIn("TRF-UK-", transfer["id"])
        self.assertEqual(transfer["status"], "REQUESTED")
        self.assertEqual(len(transfer["items"]), 2)

        # Update lifecycle to APPROVED -> DISPATCHED -> RECEIVED
        app_trf = store_transfers_service.update_transfer_status(transfer["id"], "APPROVED")
        self.assertEqual(app_trf["status"], "APPROVED")

        disp_trf = store_transfers_service.update_transfer_status(transfer["id"], "DISPATCHED")
        self.assertEqual(disp_trf["status"], "DISPATCHED")

        rec_trf = store_transfers_service.update_transfer_status(transfer["id"], "RECEIVED")
        self.assertEqual(rec_trf["status"], "RECEIVED")

        # Generate ReportLab PDF Waybill Manifest
        pdf_bytes = store_transfers_service.generate_transfer_manifest_pdf(transfer["id"])
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_multi_tax_compliance_and_hmrc_mtd_vat(self):
        from src.modules.tax_compliance import tax_compliance_service

        order = qr_ordering_service.submit_order(table_number=3, item_ids=["item-1", "item-2"])
        order_id = order["id"]

        tax_info = tax_compliance_service.calculate_tax_breakdown(order_id)
        self.assertEqual(tax_info["market"], "UK")
        self.assertEqual(tax_info["tax_rate_pct"], "20.00%")
        self.assertGreater(tax_info["tax_amount"], 0.0)

        ledger = tax_compliance_service.generate_vat_ledger(currency="GBP")
        self.assertIn("mtd_boxes", ledger)
        self.assertIn("box_1_vat_due", ledger["mtd_boxes"])
        self.assertIn("box_5_net_vat_payable", ledger["mtd_boxes"])

        pdf_bytes = tax_compliance_service.generate_vat_report_pdf(currency="GBP")
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

if __name__ == "__main__":
    unittest.main()









