import io
import json
from typing import List, Dict, Optional
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from src.core.db import db
from src.core.config import Config
from src.modules.venue import venue_service

VALID_TRANSFER_STATUSES = [
    "REQUESTED",
    "APPROVED",
    "DISPATCHED",
    "RECEIVED",
    "REJECTED"
]

class StoreTransfersModule:
    """
    Inter-Venue Inventory Stock Transfer & Central Kitchen Manifest Engine.
    Manages stock transfers between multi-venue locations (e.g. Covent Garden Central Kitchen to Soho Lounge/Paris),
    tracks approval/dispatch/receiving lifecycle, and exports ReportLab PDF Waybill Manifests.
    """

    def request_transfer(
        self,
        source_venue_id: str,
        target_venue_id: str,
        items: List[Dict],
        requested_by: str = "Central Kitchen Manager",
        notes: str = ""
    ) -> Dict:
        """
        Creates an inter-venue stock transfer request.
        `items`: list of {"item_id": "item-1", "quantity": 10}
        """
        if source_venue_id == target_venue_id:
            raise ValueError("Source venue and target venue must be different.")

        venues = venue_service.get_venues()
        v_ids = [v["id"] for v in venues]
        if source_venue_id not in v_ids:
            raise ValueError(f"Source venue '{source_venue_id}' invalid.")
        if target_venue_id not in v_ids:
            raise ValueError(f"Target venue '{target_venue_id}' invalid.")

        if not items:
            raise ValueError("Transfer items list cannot be empty.")

        formatted_items = []
        for it in items:
            iid = it.get("item_id")
            qty = int(it.get("quantity", 0))
            if qty <= 0:
                raise ValueError("Item quantity must be greater than zero.")
            
            menu_item = db.menu_items.get(iid)
            if not menu_item:
                raise ValueError(f"Menu item '{iid}' not found.")

            formatted_items.append({
                "item_id": iid,
                "name": menu_item["name"]["en"],
                "quantity": qty,
                "unit_price": menu_item["price"],
                "total_val": round(menu_item["price"] * qty, 2)
            })

        now_iso = datetime.now(timezone.utc).isoformat()

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM store_transfers")
            t_count = cursor.fetchone()[0] + 1001
            transfer_id = f"TRF-UK-{t_count}"

            cursor.execute("""
                INSERT INTO store_transfers (id, source_venue_id, target_venue_id, items_json, requested_by, notes, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transfer_id,
                source_venue_id,
                target_venue_id,
                json.dumps(formatted_items),
                requested_by,
                notes or "",
                "REQUESTED",
                now_iso,
                now_iso
            ))
            conn.commit()

        return {
            "id": transfer_id,
            "source_venue_id": source_venue_id,
            "target_venue_id": target_venue_id,
            "items": formatted_items,
            "requested_by": requested_by,
            "notes": notes or "",
            "status": "REQUESTED",
            "created_at": now_iso,
            "updated_at": now_iso
        }

    def get_transfers(self, venue_id: str = None, status: str = None) -> List[Dict]:
        """
        Retrieves store transfer records with optional venue or status filtering.
        """
        query = "SELECT * FROM store_transfers WHERE 1=1"
        params = []

        if venue_id:
            query += " AND (source_venue_id = ? OR target_venue_id = ?)"
            params.extend([venue_id, venue_id])
        if status:
            query += " AND status = ?"
            params.append(status.upper())

        query += " ORDER BY created_at DESC"

        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        transfers = []
        for r in rows:
            transfers.append({
                "id": r["id"],
                "source_venue_id": r["source_venue_id"],
                "target_venue_id": r["target_venue_id"],
                "items": json.loads(r["items_json"]),
                "requested_by": r["requested_by"],
                "notes": r["notes"],
                "status": r["status"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"]
            })
        return transfers

    def get_transfer_by_id(self, transfer_id: str) -> Optional[Dict]:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM store_transfers WHERE id = ?", (transfer_id,))
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id": row["id"],
                "source_venue_id": row["source_venue_id"],
                "target_venue_id": row["target_venue_id"],
                "items": json.loads(row["items_json"]),
                "requested_by": row["requested_by"],
                "notes": row["notes"],
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }

    def update_transfer_status(self, transfer_id: str, new_status: str) -> Dict:
        """
        Updates transfer status lifecycle and adjusts inventory stock levels on dispatch & receipt.
        """
        status_clean = new_status.upper()
        if status_clean not in VALID_TRANSFER_STATUSES:
            raise ValueError(f"Invalid transfer status '{new_status}'. Valid: {', '.join(VALID_TRANSFER_STATUSES)}")

        transfer = self.get_transfer_by_id(transfer_id)
        if not transfer:
            raise ValueError(f"Transfer ID {transfer_id} not found.")

        old_status = transfer["status"]
        if old_status == status_clean:
            return transfer

        now_iso = datetime.now(timezone.utc).isoformat()

        # Handle stock movements
        if status_clean == "DISPATCHED" and old_status in ["REQUESTED", "APPROVED"]:
            # Deduct items from inventory
            for it in transfer["items"]:
                db.deduct_stock(it["item_id"], it["quantity"])
        elif status_clean == "RECEIVED" and old_status == "DISPATCHED":
            # Add items to target inventory
            for it in transfer["items"]:
                db.restock_item(it["item_id"], it["quantity"])

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE store_transfers SET status = ?, updated_at = ? WHERE id = ?
            """, (status_clean, now_iso, transfer_id))
            conn.commit()

        return self.get_transfer_by_id(transfer_id)

    def generate_transfer_manifest_pdf(self, transfer_id: str) -> bytes:
        """
        Generates a ReportLab PDF Inter-Store Transfer Waybill & Dispatch Manifest.
        """
        transfer = self.get_transfer_by_id(transfer_id)
        if not transfer:
            raise ValueError(f"Transfer ID {transfer_id} not found.")

        src_venue = venue_service.get_venue(transfer["source_venue_id"]) or {"name": transfer["source_venue_id"], "address": "Central Kitchen"}
        tgt_venue = venue_service.get_venue(transfer["target_venue_id"]) or {"name": transfer["target_venue_id"], "address": "Destination Store"}

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TrfTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'TrfSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        bold_style = ParagraphStyle('TrfBold', parent=styles['Normal'], fontName='Helvetica-Bold')
        normal_style = styles['Normal']

        elements = []

        # Document Header
        elements.append(Paragraph("INTER-STORE STOCK TRANSFER MANIFEST", title_style))
        elements.append(Paragraph(f"Waybill Ref: {transfer['id']} | Status: {transfer['status']} | Date: {transfer['created_at'][:10]}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Source & Target Address Table
        route_data = [
            [
                Paragraph("<b>ORIGIN SOURCE STORE:</b>", bold_style),
                Paragraph("<b>DESTINATION TARGET STORE:</b>", bold_style)
            ],
            [
                Paragraph(
                    f"Store: <b>{src_venue['name']}</b><br/>"
                    f"Address: {src_venue.get('address', 'Central Hub')}<br/>"
                    f"Dispatched By: <b>{transfer['requested_by']}</b>",
                    normal_style
                ),
                Paragraph(
                    f"Store: <b>{tgt_venue['name']}</b><br/>"
                    f"Address: {tgt_venue.get('address', 'Branch Store')}<br/>"
                    f"Notes: <i>{transfer['notes'] or 'Standard Replenishment'}</i>",
                    normal_style
                )
            ]
        ]
        route_table = Table(route_data, colWidths=[260, 260])
        route_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#64748B')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(route_table)
        elements.append(Spacer(1, 15))

        # Items Grid
        items_data = [
            [
                Paragraph("<b>Item Name / SKU</b>", bold_style),
                Paragraph("<b>Quantity</b>", bold_style),
                Paragraph("<b>Unit Price (£)</b>", bold_style),
                Paragraph("<b>Total Value (£)</b>", bold_style)
            ]
        ]

        total_value = 0.0
        for it in transfer["items"]:
            total_value += it["total_val"]
            items_data.append([
                Paragraph(it["name"], normal_style),
                str(it["quantity"]),
                f"£{it['unit_price']:.2f}",
                f"£{it['total_val']:.2f}"
            ])

        items_data.append([
            Paragraph("<b>TOTAL MANIFEST STOCK VALUE</b>", bold_style),
            "", "",
            Paragraph(f"<b>£{total_value:.2f}</b>", bold_style)
        ])

        i_table = Table(items_data, colWidths=[240, 90, 95, 95])
        i_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F1F5F9')]),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E2E8F0')),
            ('SPAN', (0,-1), (2,-1)),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(i_table)
        elements.append(Spacer(1, 25))

        # Driver & Receiving Signatures
        sig_data = [
            [
                Paragraph("<b>Dispatch Driver Signature:</b><br/><br/>___________________________", normal_style),
                Paragraph("<b>Receiving Store Manager Signature:</b><br/><br/>___________________________", normal_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[260, 260])
        elements.append(sig_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

store_transfers_service = StoreTransfersModule()
