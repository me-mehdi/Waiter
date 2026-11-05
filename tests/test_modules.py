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

    def test_third_party_delivery_integrations(self):
        from src.modules.integrations import integrations_service

        delivery_res = integrations_service.process_inbound_webhook(
            platform="DELIVEROO",
            external_order_ref="DEL-UK-9912",
            customer_name="Gordon Ramsay",
            items=[{"item_id": "item-1"}, {"item_id": "item-3"}],
            delivery_address="10 Downing Street, London",
            table_number=99
        )

        self.assertIn("ORD-", delivery_res["order_id"])
        self.assertEqual(delivery_res["channel"], "DELIVEROO")
        self.assertEqual(delivery_res["external_ref"], "DEL-UK-9912")

        sync_res = integrations_service.sync_menu_to_aggregator(platform="UBEREATS")
        self.assertEqual(sync_res["channel"], "UBEREATS")
        self.assertEqual(sync_res["status"], "SYNCED")
        self.assertGreaterEqual(sync_res["synced_items_count"], 5)

        channels = integrations_service.get_integration_channels()
        self.assertEqual(len(channels), 4)
        ch_names = [c["channel"] for c in channels]
        self.assertIn("DELIVEROO", ch_names)
        self.assertIn("UBEREATS", ch_names)
        self.assertIn("DELIVERECT", ch_names)
        self.assertIn("TOAST", ch_names)

    def test_ai_menu_analytics_and_demand_forecasting(self):
        from src.modules.ai_forecasting import ai_forecasting_service

        forecasts = ai_forecasting_service.predict_prep_demand(target_day_of_week=5)
        self.assertGreaterEqual(len(forecasts), 5)
        self.assertGreater(forecasts[0]["predicted_prep_units"], 0)

        matrix = ai_forecasting_service.get_menu_engineering_matrix()
        self.assertIn("matrix", matrix)
        self.assertIn("STARS", matrix["matrix"])
        self.assertIn("DOGS", matrix["matrix"])

        pdf_bytes = ai_forecasting_service.generate_forecasting_pdf_report(currency="GBP")
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_white_label_brand_customizer(self):
        from src.modules.brand_customizer import brand_customizer_service

        config = brand_customizer_service.get_config()
        self.assertIn("brand_name", config)
        self.assertIn("primary_color", config)

        updated = brand_customizer_service.update_config({
            "brand_name": "Royal Bistro UK",
            "accent_color": "#10b981",
            "guest_welcome_message": "Welcome to Royal Bistro!"
        })
        self.assertEqual(updated["brand_name"], "Royal Bistro UK")
        self.assertEqual(updated["accent_color"], "#10b981")

        new_config = brand_customizer_service.get_config()
        self.assertEqual(new_config["brand_name"], "Royal Bistro UK")

    def test_online_table_payments(self):
        from src.modules.payments import payments_service
        order = qr_ordering_service.submit_order(table_number=4, item_ids=["item-1"])

        methods = payments_service.get_payment_methods()
        self.assertGreaterEqual(len(methods["methods"]), 3)

        res_apple = payments_service.process_checkout(
            order_id=order["id"],
            payment_method="APPLE_PAY",
            tip_percentage=12.5
        )
        self.assertEqual(res_apple["order_id"], order["id"])
        self.assertEqual(res_apple["payment_method"], "APPLE_PAY")
        self.assertEqual(res_apple["status"], "COMPLETED")
        self.assertGreater(res_apple["tip_amount"], 0.0)

        res_custom_tip = payments_service.process_checkout(
            order_id=order["id"],
            payment_method="CARD_STRIPE",
            custom_tip_amount=5.00
        )
        self.assertEqual(res_custom_tip["tip_amount"], 5.00)
        self.assertEqual(res_custom_tip["grand_total"], round(order["total"] + 5.00, 2))

    def test_ai_sommelier_and_review_auto_responder_endpoints(self):
        from src.app import app
        client = app.test_client()

        # 1. Test AI Sommelier Wine & Dish Pairing
        res_somm = client.post("/api/ai/sommelier", json={"prompt": "What wine pairs best with Fish & Chips?"})
        self.assertEqual(res_somm.status_code, 200)
        data_somm = res_somm.get_json()
        self.assertIn("Sauvignon Blanc", data_somm["response_text"])
        self.assertGreaterEqual(len(data_somm["recommendations"]), 2)

        # 2. Test AI Review Auto-Responder (5-Star Booster vs Low-Star Escalation)
        res_rev5 = client.post("/api/reviews/auto-respond", json={"rating": 5, "comment": "Amazing food!", "table_number": 4})
        self.assertEqual(res_rev5.status_code, 200)
        data_rev5 = res_rev5.get_json()
        self.assertTrue(data_rev5["success"])
        self.assertIn("5-star", data_rev5["response_draft"])

        res_rev2 = client.post("/api/reviews/auto-respond", json={"rating": 2, "comment": "Long wait", "table_number": 7})
        self.assertEqual(res_rev2.status_code, 200)
        data_rev2 = res_rev2.get_json()
        self.assertIn("apologize", data_rev2["response_draft"])

        # 3. Test PWA Manifest & Service Worker
        res_pwa = client.get("/manifest.json")
        self.assertEqual(res_pwa.status_code, 200)
        self.assertEqual(res_pwa.get_json()["short_name"], "The Waiter")

        res_sw = client.get("/sw.js")
        self.assertEqual(res_sw.status_code, 200)
        self.assertIn(b"waiter-pwa-cache-v1", res_sw.data)

    def test_sales_heatmap_and_kds_chef_recipes_endpoints(self):
        from src.app import app
        client = app.test_client()

        # 1. Test Executive Peak-Hour Sales Heatmap & Table Turnover Analytics
        res_hm = client.get("/api/analytics/heatmap")
        self.assertEqual(res_hm.status_code, 200)
        data_hm = res_hm.get_json()
        self.assertEqual(len(data_hm["hourly_heatmap"]), 7)
        self.assertEqual(len(data_hm["zone_turnover"]), 4)
        self.assertEqual(data_hm["avg_table_turn_mins"], 55)
        self.assertEqual(data_hm["peak_window"], "19:00 - 21:00")

        # 2. Test Digital Kitchen Recipe & Natasha's Law Allergen Matrix Cards
        res_rec = client.get("/api/kds/recipes")
        self.assertEqual(res_rec.status_code, 200)
        data_rec = res_rec.get_json()
        self.assertEqual(data_rec["count"], 5)
        self.assertEqual(len(data_rec["recipes"]), 5)
        first_recipe = data_rec["recipes"][0]
        self.assertIn("ingredients", first_recipe)
        self.assertIn("plating_guide", first_recipe)
        self.assertIn("cross_contamination_note", first_recipe)
        self.assertIn("fish", first_recipe["allergens"])

        # 3. Verify UI contains Delivery Hub tab, Heatmap, and Chef Recipe Modal
        res_index = client.get("/")
        self.assertEqual(res_index.status_code, 200)
        html = res_index.get_data(as_text=True)
        self.assertIn("deliveryChannelsGrid", html)
        self.assertIn("chefRecipeModal", html)
        self.assertIn("salesHeatmapGrid", html)

    def test_service_calls_and_dynamic_promo_studio_endpoints(self):
        from src.app import app
        client = app.test_client()

        # 1. Test Smart Table Service Call Bell & Staff Dispatch Queue
        res_call = client.post("/api/service-calls", json={
            "table_number": 5,
            "request_type": "WATER",
            "label": "💧 Free Tap Water"
        })
        self.assertEqual(res_call.status_code, 201)
        call_obj = res_call.get_json()
        self.assertEqual(call_obj["table_number"], 5)
        self.assertEqual(call_obj["status"], "PENDING")

        res_list = client.get("/api/service-calls")
        self.assertEqual(res_list.status_code, 200)
        self.assertGreaterEqual(res_list.get_json()["count"], 1)

        res_resolve = client.post(f"/api/service-calls/{call_obj['id']}/resolve")
        self.assertEqual(res_resolve.status_code, 200)
        self.assertEqual(res_resolve.get_json()["status"], "RESOLVED")

        # 2. Test Dynamic Happy Hour & Promo Code Campaign Studio
        res_promo = client.post("/api/promos", json={"code": "HAPPYHOUR25", "discount_pct": 25})
        self.assertEqual(res_promo.status_code, 201)
        self.assertEqual(res_promo.get_json()["discount_rate"], 0.25)

        res_del = client.delete("/api/promos/HAPPYHOUR25")
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.get_json()["deleted"], "HAPPYHOUR25")

        # 3. Verify UI contains Concierge Bar, Promo Flash Banner & Z-Report Interactive Ledger
        res_index = client.get("/")
        html = res_index.get_data(as_text=True)
        self.assertIn("guestPromoFlashBanner", html)
        self.assertIn("staffServiceCallsCard", html)
        self.assertIn("zReportInteractiveContainer", html)

    def test_blueprint_pdf_all_six_remaining_modules(self):
        from src.app import app
        client = app.test_client()

        # 1. Test Page 11 UK Consultation & 7-Day Free Trial Booking Endpoint
        res_consult = client.post("/api/blueprint/consultation", json={
            "venue_name": "The Crown & Anchor Covent Garden",
            "contact": "owner@crownanchor.co.uk"
        })
        self.assertEqual(res_consult.status_code, 201)
        data = res_consult.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["lead"]["trial_days"], 7)
        self.assertEqual(data["lead"]["setup_minutes"], 3)
        self.assertEqual(data["lead"]["uk_team_phone"], "+44 7594 560831")
        self.assertEqual(data["lead"]["uk_team_email"], "nidaazzielmehdi@gmail.com")
        self.assertEqual(data["lead"]["website"], "waiter.com")

        # 2. Verify all 6 Blueprint PDF visual & functional modules in GET /
        res_index = client.get("/")
        html = res_index.get_data(as_text=True)
        self.assertIn("barStoolsBlueprintRow", html)              # Page 1: 5 Bar Stools & Kitchen Pass
        self.assertIn("bpReservationsToday", html)                # Page 1: 4 Blueprint KPIs (120 Reservations, 18 Staff)
        self.assertIn("dishPhotos", html)                         # Page 6: Rich Dish Photography & Inline Allergen Badges
        self.assertIn("liveBlueprintInvoiceCard", html)           # Page 8: Auto-Generated Invoice #001024 & Horizon Toggle
        self.assertIn("The Waiter Cloud Sync — 6-Device Hub", html) # Page 9: 6-Device Zero Hardware Lock-In Hub
        self.assertIn("The Old Way vs. The Waiter Blueprint", html) # Pages 2, 3, 10: Operational Shift & ROI Calculator
        self.assertIn("nidaazzielmehdi@gmail.com", html)          # Page 11: UK Team Contact & 7-Day Free Trial
        self.assertIn("+44 7594 560831", html)

    def test_uk_statutory_compliance_all_six_pillars(self):
        from src.app import app
        client = app.test_client()

        # 1. Natasha's Law (PPDS) Ingredient-to-14-Allergen Auto-Tagger & Label Printer
        res_nl = client.post("/api/uk-compliance/natashas-law/build", json={
            "item_id": "custom-bakery",
            "ingredients": ["Wheat Flour", "Pasteurised Milk Butter", "Free-Range Egg", "Dijon Mustard", "Roasted Peanuts"]
        })
        self.assertEqual(res_nl.status_code, 200)
        data_nl = res_nl.get_json()
        self.assertIn("cereals_with_gluten", data_nl["detected_14_allergens"])
        self.assertIn("milk", data_nl["detected_14_allergens"])
        self.assertIn("eggs", data_nl["detected_14_allergens"])
        self.assertIn("mustard", data_nl["detected_14_allergens"])
        self.assertIn("peanuts", data_nl["detected_14_allergens"])
        self.assertIn("BOLD CAPITALS", data_nl["natashas_law_label_html"])

        # 2. Employment (Allocation of Tips) Act 2023 (Effective Oct 2024) — 100% Fair Payout Log
        res_tips = client.get("/api/uk-compliance/tips-act-2024")
        self.assertEqual(res_tips.status_code, 200)
        data_tips = res_tips.get_json()
        self.assertTrue(data_tips["compliant_with_oct_2024_act"])
        self.assertEqual(data_tips["written_policy"]["pass_through_pct"], 100.0)
        self.assertEqual(data_tips["employer_deductions_gbp"], 0.0)

        res_pay = client.post("/api/uk-compliance/tips-act-2024/payout", json={
            "staff_name": "Chloe Evans",
            "role": "FOH Server",
            "hours_worked": 40.0,
            "amount_gbp": 195.00
        })
        self.assertEqual(res_pay.status_code, 201)
        self.assertEqual(res_pay.get_json()["employer_deduction_gbp"], 0.0)
        self.assertEqual(res_pay.get_json()["net_payout_gbp"], 195.00)

        # 3. Challenge 25 Alcohol Age Verification (Licensing Act 2003)
        res_c25 = client.post("/api/uk-compliance/challenge25/verify", json={
            "table_number": 6,
            "order_id": "ORD-0001",
            "decision": "APPROVED",
            "id_type": "UK Photocard Driving Licence"
        })
        self.assertEqual(res_c25.status_code, 201)
        self.assertTrue(res_c25.get_json()["dob_verified_18_plus"])

        # 4. Food Safety Logs (Fridge Temps, HACCP & EHO Inspection PDF Export)
        res_temp = client.post("/api/uk-compliance/food-safety/temp", json={
            "unit_name": "Walk-In Chiller #1",
            "unit_type": "CHILLER",
            "recorded_temp_c": 3.1,
            "checked_by": "Marco Rossi"
        })
        self.assertEqual(res_temp.status_code, 201)
        self.assertEqual(res_temp.get_json()["status"], "COMPLIANT")

        res_eho_pdf = client.get("/api/uk-compliance/eho-report/pdf")
        self.assertEqual(res_eho_pdf.status_code, 200)
        self.assertTrue(res_eho_pdf.data.startswith(b"%PDF"))

        # 5. HMRC VAT Notice 709/1 (Eat-In 20% vs Cold Takeaway 0% Zero-Rated Food)
        res_vat_eat = client.post("/api/uk-compliance/vat-mode", json={
            "dining_mode": "EAT_IN",
            "items": ["item-1", "item-3"]
        })
        self.assertEqual(res_vat_eat.status_code, 200)
        self.assertEqual(res_vat_eat.get_json()["net_zero_rated_gbp"], 0.0)

        res_vat_cold = client.post("/api/uk-compliance/vat-mode", json={
            "dining_mode": "COLD_TAKEAWAY",
            "items": ["item-1", "item-3"]
        })
        self.assertEqual(res_vat_cold.status_code, 200)
        # item-1 (Food) is 0% Zero-Rated in Cold Takeaway, while item-3 (Alcohol Drink) remains 20% Standard-Rated!
        self.assertGreater(res_vat_cold.get_json()["net_zero_rated_gbp"], 0.0)
        self.assertGreater(res_vat_cold.get_json()["vat_20_pct_payable_gbp"], 0.0)

        # 6. UK GDPR, London Region (eu-west-2) Hosting & Cyber Essentials Posture
        res_gdpr = client.get("/api/uk-compliance/gdpr-security")
        self.assertEqual(res_gdpr.status_code, 200)
        data_gdpr = res_gdpr.get_json()
        self.assertIn("London Region (eu-west-2", data_gdpr["data_residency"])
        self.assertIn("Cyber Essentials", data_gdpr["cyber_security_certification"])

    def test_money_and_margins_all_five_pillars(self):
        from src.app import app
        from src.modules.qr_ordering import qr_ordering_service
        from src.modules.payments import payments_service
        client = app.test_client()

        # 1. Payment Options: Pay-by-Bank (0.2% Fee) & Split Bill by Percentage
        order = qr_ordering_service.submit_order(table_number=8, item_ids=["item-1", "item-2"])
        pay_res = payments_service.process_checkout(order["id"], payment_method="PAY_BY_BANK", tip_percentage=10.0)
        self.assertEqual(pay_res["processing_fee_pct"], 0.2)
        self.assertGreater(pay_res["fee_saved_vs_card_gbp"], 0.0)

        res_pct = client.post(f"/api/orders/{order['id']}/split/percentage", json={
            "percentages": [50, 25, 25],
            "include_service_charge": True
        })
        self.assertEqual(res_pct.status_code, 200)
        data_pct = res_pct.get_json()
        self.assertEqual(len(data_pct["shares"]), 3)
        self.assertEqual(data_pct["shares"][0]["percentage"], 50.0)

        # 2. UK Accounting Integrations (Xero, QuickBooks, Sage, FreeAgent — MTD Ready)
        for provider in ["XERO", "QUICKBOOKS", "SAGE", "FREEAGENT"]:
            res_sync = client.post(f"/api/margins/accounting/sync/{provider}")
            self.assertEqual(res_sync.status_code, 200)
            self.assertTrue(res_sync.get_json()["success"])

        # 3. Live Recipe Costing & Dish GP%
        res_gp = client.get("/api/margins/recipe-gp")
        self.assertEqual(res_gp.status_code, 200)
        data_gp = res_gp.get_json()
        self.assertGreater(data_gp["average_menu_gp_pct"], 60.0)
        self.assertEqual(len(data_gp["dishes_gp_matrix"]), 5)

        # 4. UK Wholesale Suppliers (Booker, Bidfood, Brakes) & AI Supplier Invoice Scanner
        for sup in ["BOOKER", "BIDFOOD", "BRAKES"]:
            res_po = client.post(f"/api/margins/suppliers/order/{sup}")
            self.assertEqual(res_po.status_code, 201)
            self.assertTrue(res_po.get_json()["success"])

        res_scan = client.post("/api/margins/suppliers/scan-invoice", json={
            "supplier_code": "BRAKES",
            "invoice_ref": "BRK-INV-2026-900",
            "cod_unit_cost_gbp": 2.80
        })
        self.assertEqual(res_scan.status_code, 201)
        self.assertIn("OCR Price Alert", res_scan.get_json()["price_variance_alerts"][0])

        # 5. Live Labour Cost % vs Sales, UK Statutory Holiday Accrual (12.07%) & Payroll CSV Export
        res_lab = client.get("/api/margins/labour-payroll")
        self.assertEqual(res_lab.status_code, 200)
        data_lab = res_lab.get_json()
        self.assertIn("12.07%", data_lab["uk_holiday_accrual_formula"])
        self.assertGreater(data_lab["total_holiday_accrual_gbp"], 0.0)

        res_csv = client.get("/api/margins/payroll/export/csv")
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn("Holiday Hours Accrued (12.07%)", res_csv.get_data(as_text=True))

    def test_british_pub_all_four_pillars(self):
        from src.app import app
        client = app.test_client()

        # 1. Bar Tabs: Card Pre-Authorisation & 1-Tap "Same Again!" Round Ordering
        res_open = client.post("/api/pub/tabs/open", json={
            "customer_name": "Alfie & Lads",
            "table_or_zone": "Garden Bench #G1",
            "pre_auth_limit_gbp": 60.00
        })
        self.assertEqual(res_open.status_code, 201)
        tab = res_open.get_json()
        self.assertEqual(tab["status"], "OPEN_PRE_AUTHORISED")
        self.assertTrue(tab["pre_auth_token"].startswith("PREAUTH-STRIPE-"))

        res_same = client.post(f"/api/pub/tabs/{tab['tab_id']}/same-again")
        self.assertEqual(res_same.status_code, 200)
        data_same = res_same.get_json()
        self.assertTrue(data_same["success"])
        self.assertEqual(data_same["repeated_round_number"], 2)
        self.assertEqual(data_same["new_tab_balance_gbp"], 24.80)

        # 2. Cellar & Keg Management: Keg Tracking, Line-Cleaning Logs & Ullage Wastage
        res_cellar = client.get("/api/pub/cellar")
        self.assertEqual(res_cellar.status_code, 200)
        data_cellar = res_cellar.get_json()
        self.assertGreater(data_cellar["overall_keg_yield_pct"], 90.0)
        self.assertEqual(len(data_cellar["taps"]), 4)

        res_clean = client.post("/api/pub/cellar/clean-line/3")
        self.assertEqual(res_clean.status_code, 200)
        self.assertEqual(res_clean.get_json()["line_clean_status"], "CLEAN_COMPLIANT")

        # 3. Pub Extras: Sunday Roast Pre-Orders with Sold-Out Counters & Quiz Ticketing
        res_roast = client.post("/api/pub/roast/preorder", json={
            "roast_id": "ROAST-CHICKEN",
            "quantity": 1,
            "guest_name": "Table #4"
        })
        self.assertEqual(res_roast.status_code, 201)
        self.assertTrue(res_roast.get_json()["sold_out"])  # Had 1 left, now 0 & sold_out=True!

        res_quiz = client.post("/api/pub/events/book", json={
            "event_id": "QUIZ-WED",
            "team_name": "Norfolk Enchants",
            "team_size": 5
        })
        self.assertEqual(res_quiz.status_code, 201)
        self.assertEqual(res_quiz.get_json()["booking"]["paid_gbp"], 15.00)

        # 4. Beer Garden Zones & Weather-Triggered "Garden Open" Toggle
        res_rain = client.post("/api/pub/garden/toggle", json={"simulate_weather": "RAIN_STORM"})
        self.assertEqual(res_rain.status_code, 200)
        self.assertFalse(res_rain.get_json()["garden_open"])

        res_sun = client.post("/api/pub/garden/toggle", json={"simulate_weather": "SUNNY"})
        self.assertEqual(res_sun.status_code, 200)
        self.assertTrue(res_sun.get_json()["garden_open"])

    def test_growth_and_customers_all_four_pillars(self):
        from src.app import app
        client = app.test_client()

        # 1. Delivery Aggregators (Deliveroo, Uber Eats, Just Eat) in Same KDS + 0% Commission Click & Collect
        res_je = client.post("/api/growth/aggregator-order", json={
            "platform": "JUSTEAT",
            "customer_name": "Tariq Mahmood",
            "item_ids": ["item-1", "item-4"]
        })
        self.assertEqual(res_je.status_code, 201)
        data_je = res_je.get_json()
        self.assertEqual(data_je["channel"], "JUSTEAT")
        self.assertTrue(data_je["kds_unified"])

        res_cnc = client.post("/api/growth/click-and-collect", json={
            "customer_name": "Zara Khan",
            "customer_phone": "+447700900456",
            "item_ids": ["item-1", "item-5"],
            "pickup_slot": "ASAP (15 mins)"
        })
        self.assertEqual(res_cnc.status_code, 201)
        data_cnc = res_cnc.get_json()
        self.assertEqual(data_cnc["channel"], "CLICK_AND_COLLECT")
        self.assertEqual(data_cnc["commission_fee_gbp"], 0.00)
        self.assertGreater(data_cnc["aggregator_commission_saved_gbp"], 0.00)
        self.assertTrue(data_cnc["collection_code"].startswith("CNC-"))

        # Verify both Just Eat and Click & Collect orders land in the unified KDS
        res_kds = client.get("/api/kds/active")
        kds_ids = [o["id"] for o in res_kds.get_json()["orders"]]
        self.assertIn(data_je["order_id"], kds_ids)
        self.assertIn(data_cnc["order_id"], kds_ids)

        # 2. Reservations with Card Pre-Auth Deposits + Google Business Profile Booking Link
        res_dep = client.post("/api/growth/reservations/deposit", json={
            "guest_name": "Dr. Priya Patel",
            "guest_phone": "+447700900888",
            "guest_email": "priya@example.co.uk",
            "party_size": 4,
            "table_number": 6,
            "booking_date": "2026-11-20",
            "time_slot": "19:30",
            "deposit_per_head_gbp": 10.0,
            "booking_source": "GOOGLE_BUSINESS_PROFILE"
        })
        self.assertEqual(res_dep.status_code, 201)
        data_dep = res_dep.get_json()
        self.assertEqual(data_dep["deposit_preauth"]["total_deposit_held_gbp"], 40.00)
        self.assertEqual(data_dep["deposit_preauth"]["status"], "PRE_AUTH_HELD")
        self.assertTrue(data_dep["google_business_profile_sync"])

        # 3. Loyalty: Apple & Google Wallet Stamp Cards + Post-Payment Google Review Prompt
        res_wal = client.post("/api/growth/wallet-stamp", json={
            "phone": "+447700900111",
            "guest_name": "Amelia Clarke",
            "stamps_to_add": 1
        })
        self.assertEqual(res_wal.status_code, 201)
        data_wal = res_wal.get_json()
        self.assertIn("APPLE_WALLET", data_wal["wallet_card"]["wallet_platforms"])
        self.assertIn("GOOGLE_WALLET", data_wal["wallet_card"]["wallet_platforms"])
        self.assertTrue(data_wal["google_review_prompt"]["triggered_after_payment"])
        self.assertIn("writereview", data_wal["google_review_prompt"]["google_review_url"])

        # 4. 10 UK Multicultural Languages (EN, FR, AR, PL, UR, BN, PA, ZH, ES, TR) + Halal/Vegan/Vegetarian
        res_langs = client.get("/api/growth/languages?lang=pl")
        self.assertEqual(res_langs.status_code, 200)
        data_langs = res_langs.get_json()
        self.assertEqual(data_langs["total_supported_languages"], 10)
        codes = [l["code"] for l in data_langs["supported_languages"]]
        for expected_code in ["en", "fr", "ar", "pl", "ur", "bn", "pa", "zh", "es", "tr"]:
            self.assertIn(expected_code, codes)

        # Verify filtered menu endpoint translates into Urdu (ur) with Halal filter
        res_urdu_halal = client.get("/api/menu/filtered?lang=ur&dietary=halal")
        self.assertEqual(res_urdu_halal.status_code, 200)
        urdu_items = res_urdu_halal.get_json()
        self.assertGreaterEqual(len(urdu_items), 2)
        self.assertEqual(urdu_items[0]["active_language"], "ur")
        self.assertTrue(urdu_items[0]["is_rtl"])

    def test_reliability_offline_queue_and_epson_star_printers(self):
        from src.app import app
        client = app.test_client()

        # 1. Switch to CELLAR_DEAD_ZONE offline mode & queue orders locally
        res_mode = client.post("/api/reliability/network-mode", json={"mode": "CELLAR_DEAD_ZONE"})
        self.assertEqual(res_mode.status_code, 200)
        self.assertTrue(res_mode.get_json()["is_offline_queuing"])

        res_q1 = client.post("/api/reliability/offline-queue", json={
            "table_number": 9,
            "item_ids": ["item-1", "item-3"],
            "scenario": "CELLAR_DEAD_ZONE",
            "location_note": "Underground Cellar Vault",
            "client_offline_id": "OFFLINE-Q-TEST99"
        })
        self.assertEqual(res_q1.status_code, 201)
        data_q1 = res_q1.get_json()
        self.assertEqual(data_q1["offline_id"], "OFFLINE-Q-TEST99")
        self.assertEqual(data_q1["status"], "QUEUED_LOCALLY")

        # Sync offline queue to live POS & Kitchen KDS
        res_sync = client.post("/api/reliability/offline-sync", json={
            "client_queued_orders": [{
                "offline_id": "OFFLINE-Q-SAT88",
                "table_number": 11,
                "item_ids": ["item-2"],
                "scenario": "SATURDAY_PEAK_CONGESTION",
                "location_note": "Rural Beer Garden Saturday Rush"
            }]
        })
        self.assertEqual(res_sync.status_code, 200)
        data_sync = res_sync.get_json()
        self.assertTrue(data_sync["success"])
        self.assertEqual(data_sync["synced_count"], 2)
        self.assertEqual(data_sync["remaining_queue_count"], 0)

        # Verify idempotency: re-syncing the exact same offline_id creates 0 duplicates
        res_dup = client.post("/api/reliability/offline-sync", json={
            "client_queued_orders": [{"offline_id": "OFFLINE-Q-SAT88", "table_number": 11, "item_ids": ["item-2"]}]
        })
        self.assertEqual(res_dup.get_json()["synced_count"], 0)

        # 2. Certified Epson & Star Micronics Thermal Printer Compatibility Matrix
        res_prn = client.get("/api/reliability/printers")
        self.assertEqual(res_prn.status_code, 200)
        data_prn = res_prn.get_json()
        self.assertIn("Epson", data_prn["supported_brands"])
        self.assertIn("Star Micronics", data_prn["supported_brands"])
        self.assertGreaterEqual(data_prn["total_certified_models"], 7)
        self.assertTrue(all(p["proprietary_lock_in"] is False for p in data_prn["printers"]))

        # Run live ESC/POS diagnostic test on Star TSP143IV & Epson TM-T88VII
        res_test = client.post("/api/reliability/printers/test", json={"model_id": "STAR-TSP143IV"})
        self.assertEqual(res_test.status_code, 200)
        data_test = res_test.get_json()
        self.assertTrue(data_test["success"])
        self.assertEqual(data_test["brand"], "Star Micronics")
        self.assertGreater(data_test["escpos_payload_size_bytes"], 50)

    def test_navy_and_brass_four_screen_uk_design_suite(self):
        from src.app import app
        client = app.test_client()

        for route in ["/", "/uk"]:
            res = client.get(route)
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            # Design system tokens (Fraunces + Inter, Navy #0f1520 & Brass #c8a86b)
            self.assertIn("Fraunces", html)
            self.assertIn("#0f1520", html)
            self.assertIn("#c8a86b", html)

            # Screen 1: Landing Page
            self.assertIn("One system for every table, ticket and till.", html)
            self.assertIn("Made for how the UK trades", html)
            self.assertIn("[£ PRICE] a month. No contract.", html)

            # Screen 2: Guest QR Menu (390x844)
            self.assertIn("TABLE 12", html)
            self.assertIn("[VENUE NAME]", html)
            self.assertIn("Gluten · Milk · Celery", html)
            self.assertIn("Challenge 25: ID may be checked", html)
            self.assertIn("View order · 2 items", html)

            # Screen 3: Kitchen Display
            self.assertIn("#1026 · Table 12", html)
            self.assertIn("#1024 · Delivery", html)
            self.assertIn("#1025 · Table 4", html)
            self.assertIn("Allergy: no gluten", html)

            # Screen 4: Owner Dashboard ("Today")
            self.assertIn("SALES TODAY", html)
            self.assertIn("£[X]", html)
            self.assertIn("Allergen labels: up to date", html)
            self.assertIn("Sales by hour", html)

    def test_all_dedicated_page_routes(self):
        from src.app import app
        client = app.test_client()

        routes = [
            ("/", "One system for every table, ticket and till."),
            ("/menu", "TABLE 12"),
            ("/guest", "TABLE 12"),
            ("/kitchen", "Kitchen"),
            ("/kds", "Kitchen"),
            ("/today", "SALES TODAY"),
            ("/owner", "SALES TODAY"),
            ("/till", "Till / POS"),
            ("/pos", "Till / POS"),
            ("/reservations", "Table Reservations"),
            ("/bookings", "Table Reservations"),
            ("/stock", "Stock, Cellar"),
            ("/cellar", "Stock, Cellar"),
            ("/staff", "Staff Rota"),
            ("/rota", "Staff Rota"),
            ("/settings", "System Reliability"),
            ("/printers", "System Reliability"),
            ("/tv", "Kitchen"),
            ("/terminal", "Till / POS"),
            ("/uk", "One system for every table, ticket and till."),
        ]

        for route, expected_text in routes:
            res = client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")
            html = res.get_data(as_text=True)
            self.assertIn(expected_text, html, f"Expected '{expected_text}' in route '{route}'")
            self.assertIn("Fraunces", html)
            self.assertIn("#0f1520", html)
            self.assertIn("#c8a86b", html)

    def test_admin_dashboard_page_and_crud_api_endpoints(self):
        """
        Verify the Admin Control Console page (/admin) and all CRUD API endpoints:
        Menu Items Add/Edit/Delete/86-Toggle, Orders pipeline, Tables QR studio,
        and UK statutory compliance logs.
        """
        from src.app import app
        client = app.test_client()

        # 1. Admin Page Route
        res = client.get("/admin")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("Admin Console", html)
        self.assertIn("Menu &amp; Dish Catalog Control", html)
        self.assertIn("Live Orders &amp; Kitchen Pipeline", html)
        self.assertIn("Dining Floor Plan &amp; QR Code Studio", html)
        self.assertIn("Fraunces", html)

        # 2. Get Menu
        res = client.get("/api/admin/menu")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("count", 0), 0)

        # 3. Add Menu Item (CRUD: Create)
        new_dish = {
            "name_en": "Truffle &amp; Rosemary Chips",
            "category": "Sides",
            "price": 5.95,
            "desc_en": "Triple cooked skin-on chips tossed in white truffle oil and rosemary sea salt.",
            "allergens": ["cereals_with_gluten"],
            "dietary": ["vegan", "vegetarian", "halal"],
            "stock_qty": 40
        }
        res = client.post("/api/admin/menu", json=new_dish)
        self.assertEqual(res.status_code, 201)
        created = res.get_json().get("item")
        item_id = created.get("id")
        self.assertTrue(item_id)
        self.assertEqual(created.get("category"), "Sides")

        # 4. Update Menu Item (CRUD: Update)
        res = client.put(f"/api/admin/menu/{item_id}", json={"price": 6.50, "category": "Sides"})
        self.assertEqual(res.status_code, 200)
        updated = res.get_json().get("item")
        self.assertEqual(updated.get("price"), 6.50)

        # 5. Toggle 86 / Out of Stock
        res = client.post(f"/api/admin/menu/{item_id}/toggle-86", json={"is_available": False})
        self.assertEqual(res.status_code, 200)
        toggled = res.get_json().get("item")
        self.assertFalse(toggled.get("is_available"))

        # 6. Delete Menu Item (CRUD: Delete)
        res = client.delete(f"/api/admin/menu/{item_id}")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json().get("success"))

        # 7. Tables Management
        res = client.get("/api/admin/tables")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json().get("success"))

        res = client.post("/api/admin/tables", json={"table_number": 99, "capacity": 6, "zone": "VIP Terrace"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["table"]["table_number"], 99)

        res = client.delete("/api/admin/tables/99")
        self.assertEqual(res.status_code, 200)

        # 8. Compliance Logs (Fridge & Challenge 25)
        res = client.post("/api/admin/compliance/fridge", json={"appliance": "Bar Keg Chiller", "temperature": 3.8, "recorded_by": "Duty Manager"})
        self.assertEqual(res.status_code, 201)

        res = client.post("/api/admin/compliance/c25", json={"item_name": "Craft Cider", "reason": "No photo ID produced", "staff_member": "Alice"})
        self.assertEqual(res.status_code, 201)

if __name__ == "__main__":
    unittest.main()










