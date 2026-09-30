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

class TestWaiterModules(unittest.TestCase):
    def setUp(self):
        db.reset()

    def test_staff_pin_authentication(self):
        self.assertTrue(auth_service.verify_pin("1234"))
        self.assertFalse(auth_service.verify_pin("0000"))
        self.assertFalse(auth_service.verify_pin(""))

    def test_order_cancellation_and_refund(self):
        # 1. Place order
        stock_before = db.menu_items["item-1"]["stock_qty"]
        order = qr_ordering_service.submit_order(table_number=3, item_ids=["item-1"])
        order_id = order["id"]
        
        self.assertEqual(db.menu_items["item-1"]["stock_qty"], stock_before - 1)

        # 2. Cancel & Refund order
        cancelled_order = db.cancel_order(order_id)
        self.assertEqual(cancelled_order["status"], "CANCELLED")

        # 3. Stock should be returned to inventory
        self.assertEqual(db.menu_items["item-1"]["stock_qty"], stock_before)

        # 4. Analytics should exclude cancelled order
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

if __name__ == "__main__":
    unittest.main()
