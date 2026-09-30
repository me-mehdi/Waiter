import unittest
import os
import sys

# Ensure src path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.db import db
from src.core.translation import translator
from src.modules.qr_ordering import qr_ordering_service
from src.modules.kds import kds_service
from src.modules.promos import promo_service
from src.modules.reviews import review_service
from src.modules.finance import finance_service

class TestWaiterModules(unittest.TestCase):
    def setUp(self):
        db.reset()

    def test_qr_menu_translation(self):
        menu_en = qr_ordering_service.get_menu("en")
        self.assertGreater(len(menu_en), 0)
        self.assertEqual(menu_en[0]["name_translated"], "Fish & Chips")

        menu_fr = qr_ordering_service.get_menu("fr")
        self.assertEqual(menu_fr[0]["name_translated"], "Poisson & Frites")

        menu_ar = qr_ordering_service.get_menu("ar")
        self.assertEqual(menu_ar[0]["name_translated"], "سمك وبطاطس")

    def test_order_submission_and_upsell(self):
        upsells = qr_ordering_service.get_upsells_for_cart(["item-1"], "en")
        self.assertTrue(any(u["id"] == "item-4" for u in upsells))

        order = qr_ordering_service.submit_order(
            table_number=5,
            item_ids=["item-1", "item-3"],
            promo_code="WELCOME10"
        )
        self.assertTrue(order["id"].startswith("ORD-"))
        self.assertEqual(order["table_number"], 5)
        self.assertGreater(order["discount"], 0.0)

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

    def test_finance_invoice_and_analytics(self):
        order = qr_ordering_service.submit_order(table_number=1, item_ids=["item-1", "item-4"])
        invoice = finance_service.generate_invoice(order["id"])

        self.assertIsNotNone(invoice)
        self.assertTrue(invoice["invoice_number"].startswith("INV-UK-"))
        self.assertEqual(invoice["currency"], "GBP")

        pdf_bytes = finance_service.generate_pdf_invoice(order["id"])
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

        analytics = finance_service.calculate_analytics(total_seats=50, operating_hours=12)
        self.assertIn("rev_pash", analytics)
        self.assertEqual(analytics["currency_symbol"], "£")

    def test_thermal_receipt_printing(self):
        from src.modules.thermal_print import thermal_printer_service
        order = qr_ordering_service.submit_order(table_number=3, item_ids=["item-1", "item-3"])
        
        text_receipt = thermal_printer_service.format_receipt_text(order["id"], width=32)
        self.assertIsNotNone(text_receipt)
        self.assertIn("THE WAITER UK", text_receipt)
        self.assertIn("Fish & Chips", text_receipt)

        escpos_bytes = thermal_printer_service.generate_escpos_bytes(order["id"])
        self.assertIsNotNone(escpos_bytes)
        self.assertTrue(escpos_bytes.startswith(b"\x1b@"))

if __name__ == "__main__":
    unittest.main()
