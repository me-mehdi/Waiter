import csv
import io
from src.core.db import db
from src.modules.inventory import inventory_service

class ExporterModule:
    """
    CSV Report Exporter Module
    Generates downloadable CSV reports for accounting, inventory audits, and customer feedback.
    """
    def export_orders_csv(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Order ID", "Table Number", "Item Count", "Items", "Subtotal (£)", "Discount (£)", "Total (£)", "Status", "Created At"])
        
        orders = list(db.orders.values())
        for order in orders:
            item_names = "; ".join([i["name"] for i in order["items"]])
            writer.writerow([
                order["id"],
                order["table_number"],
                len(order["items"]),
                item_names,
                f"{order['subtotal']:.2f}",
                f"{order['discount']:.2f}",
                f"{order['total']:.2f}",
                order["status"],
                order["created_at"]
            ])
            
        return output.getvalue()

    def export_inventory_csv(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Item ID", "Category", "Name (EN)", "Name (FR)", "Name (AR)", "Price (£)", "Stock Qty", "Stock Status"])
        
        items = inventory_service.get_inventory_status()
        for item in items:
            writer.writerow([
                item["id"],
                item["category"],
                item["name"]["en"],
                item["name"]["fr"],
                item["name"]["ar"],
                f"{item['price']:.2f}",
                item["stock_qty"],
                item["stock_status"]
            ])
            
        return output.getvalue()

    def export_reviews_csv(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Review ID", "Table Number", "Rating", "Comment", "Created At"])
        
        reviews = db.reviews
        for rev in reviews:
            writer.writerow([
                rev["id"],
                rev["table_number"],
                rev["rating"],
                rev["comment"],
                rev["created_at"]
            ])
            
        return output.getvalue()

exporter_service = ExporterModule()
