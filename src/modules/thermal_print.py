from typing import Optional
import json
from src.core.db import db
from src.core.config import Config

class ThermalPrinterModule:
    """
    ESC/POS Thermal Receipt Printing Engine
    Generates monospaced formatted text and ESC/POS byte sequences for 80mm (42-col) and 58mm (32-col) thermal printers.
    """
    
    # ESC/POS Command Constants
    ESC = b'\x1b'
    GS = b'\x1d'
    INIT = ESC + b'@'
    ALIGN_LEFT = ESC + b'a\x00'
    ALIGN_CENTER = ESC + b'a\x01'
    ALIGN_RIGHT = ESC + b'a\x02'
    BOLD_ON = ESC + b'E\x01'
    BOLD_OFF = ESC + b'E\x00'
    DOUBLE_HEIGHT = ESC + b'!\x10'
    DOUBLE_WIDTH = ESC + b'!\x20'
    NORMAL_TEXT = ESC + b'!\x00'
    PAPER_CUT = GS + b'V\x41\x03'

    def format_receipt_text(self, order_id: str, width: int = 32) -> Optional[str]:
        """
        Formats order details into a clean monospaced string for thermal printers.
        `width` = 32 columns (58mm) or 42 columns (80mm).
        """
        order = db.orders.get(order_id)
        if not order:
            return None

        lines = []

        def center(text: str) -> str:
            return text.center(width)

        def left_right(left: str, right: str) -> str:
            space = width - len(left) - len(right)
            if space < 1:
                space = 1
            return left + (" " * space) + right

        # Header
        lines.append(center("THE WAITER UK"))
        lines.append(center("123 Oxford Street, London"))
        lines.append(center("Tel: +44 7594 560831"))
        lines.append("=" * width)
        
        # Order info
        lines.append(left_right(f"ORDER: {order['id']}", f"TABLE: #{order['table_number']}"))
        lines.append(left_right("DATE:", order['created_at'][:19].replace("T", " ")))
        lines.append("-" * width)

        # Items
        for item in order["items"]:
            lines.append(left_right(item["name"], f"£{item['price']:.2f}"))

        lines.append("-" * width)

        # Financial Breakdown
        subtotal = order["subtotal"]
        discount = order["discount"]
        total = order["total"]
        vat = round(total * 0.20 / 1.20, 2)  # VAT inclusive

        lines.append(left_right("Subtotal:", f"£{subtotal:.2f}"))
        if discount > 0:
            lines.append(left_right("Promo Discount:", f"-£{discount:.2f}"))
        lines.append(left_right("UK VAT (20% Inc):", f"£{vat:.2f}"))
        lines.append("=" * width)
        lines.append(left_right("TOTAL PAID:", f"£{total:.2f}"))
        lines.append("=" * width)

        # Footer
        lines.append(center("Thank you for visiting!"))
        lines.append(center("Scan to re-order: waiter.com"))
        lines.append("\n\n")

        return "\n".join(lines)

    def generate_escpos_bytes(self, order_id: str, width: int = 32) -> Optional[bytes]:
        """
        Generates raw ESC/POS command byte sequences ready to transmit via Raw Socket / Bluetooth / USB to thermal printer.
        """
        text_receipt = self.format_receipt_text(order_id, width)
        if not text_receipt:
            return None

        out = bytearray()
        out.extend(self.INIT)
        out.extend(self.ALIGN_CENTER)
        out.extend(self.BOLD_ON)
        out.extend(self.DOUBLE_HEIGHT)
        out.extend(b"THE WAITER UK\n")
        out.extend(self.NORMAL_TEXT)
        out.extend(self.BOLD_OFF)
        out.extend(self.ALIGN_LEFT)
        out.extend(text_receipt.encode("utf-8"))
        out.extend(self.PAPER_CUT)

        return bytes(out)

thermal_printer_service = ThermalPrinterModule()
