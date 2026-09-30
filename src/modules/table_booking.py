import io
import json
from typing import List, Dict, Optional
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from src.core.db import db
from src.core.config import Config
from src.modules.floor_plan import floor_plan_service
from src.modules.venue import venue_service
from src.modules.qr_generator import qr_generator_service

VALID_BOOKING_STATUSES = [
    "CONFIRMED",
    "SEATED",
    "COMPLETED",
    "CANCELLED",
    "NO_SHOW"
]

class TableBookingModule:
    """
    Guest Table Reservation & Booking Engine for The Waiter.
    Handles online table reservations, automatic table capacity allocation,
    status updates (Seated, Completed, Cancelled), and ReportLab PDF booking confirmation vouchers.
    """

    def create_booking(
        self,
        guest_name: str,
        guest_phone: str,
        guest_email: str,
        party_size: int,
        booking_date: str,
        time_slot: str,
        special_requests: str = "",
        venue_id: str = None
    ) -> Dict:
        """
        Creates a new table booking and allocates an optimal available table.
        """
        if party_size <= 0:
            raise ValueError("Party size must be at least 1 guest.")

        if not venue_id:
            venue_id = venue_service.get_active_venue()["id"]

        # Find best matching table based on capacity and availability
        tables = floor_plan_service.get_floor_plan()
        
        # Check existing bookings for that date & time to avoid double booking table
        existing_bookings = self.get_bookings(booking_date=booking_date, venue_id=venue_id)
        booked_table_nums = [b["table_number"] for b in existing_bookings if b["status"] in ["CONFIRMED", "SEATED"]]

        suitable_table = None
        for t in tables:
            t_num = t["table_number"]
            t_cap = t["capacity"]
            if t_cap >= party_size and t_num not in booked_table_nums:
                suitable_table = t
                break

        if not suitable_table:
            # Fallback to any table with enough capacity
            suitable_table = next((t for t in tables if t["capacity"] >= party_size), tables[0])

        allocated_table_num = suitable_table["table_number"]
        now_iso = datetime.now(timezone.utc).isoformat()

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM table_bookings")
            b_count = cursor.fetchone()[0] + 1001
            booking_id = f"BKG-UK-{b_count}"

            cursor.execute("""
                INSERT INTO table_bookings (id, guest_name, guest_phone, guest_email, party_size, table_number, booking_date, time_slot, special_requests, status, created_at, venue_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id,
                guest_name,
                guest_phone,
                guest_email,
                party_size,
                allocated_table_num,
                booking_date,
                time_slot,
                special_requests or "",
                "CONFIRMED",
                now_iso,
                venue_id
            ))
            conn.commit()

        # Update table status in floor plan
        floor_plan_service.update_table_status(allocated_table_num, "RESERVED")

        return {
            "id": booking_id,
            "guest_name": guest_name,
            "guest_phone": guest_phone,
            "guest_email": guest_email,
            "party_size": party_size,
            "table_number": allocated_table_num,
            "zone": suitable_table.get("zone", "Main Dining Room"),
            "booking_date": booking_date,
            "time_slot": time_slot,
            "special_requests": special_requests or "",
            "status": "CONFIRMED",
            "created_at": now_iso,
            "venue_id": venue_id
        }

    def get_bookings(self, booking_date: str = None, status: str = None, venue_id: str = None) -> List[Dict]:
        """
        Retrieves table bookings matching optional filters.
        """
        query = "SELECT * FROM table_bookings WHERE 1=1"
        params = []

        if booking_date:
            query += " AND booking_date = ?"
            params.append(booking_date)
        if status:
            query += " AND status = ?"
            params.append(status.upper())
        if venue_id:
            query += " AND venue_id = ?"
            params.append(venue_id)

        query += " ORDER BY booking_date ASC, time_slot ASC"

        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        bookings = []
        for r in rows:
            bookings.append({
                "id": r["id"],
                "guest_name": r["guest_name"],
                "guest_phone": r["guest_phone"],
                "guest_email": r["guest_email"],
                "party_size": r["party_size"],
                "table_number": r["table_number"],
                "booking_date": r["booking_date"],
                "time_slot": r["time_slot"],
                "special_requests": r["special_requests"],
                "status": r["status"],
                "created_at": r["created_at"],
                "venue_id": r["venue_id"]
            })
        return bookings

    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table_bookings WHERE id = ?", (booking_id,))
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id": row["id"],
                "guest_name": row["guest_name"],
                "guest_phone": row["guest_phone"],
                "guest_email": row["guest_email"],
                "party_size": row["party_size"],
                "table_number": row["table_number"],
                "booking_date": row["booking_date"],
                "time_slot": row["time_slot"],
                "special_requests": row["special_requests"],
                "status": row["status"],
                "created_at": row["created_at"],
                "venue_id": row["venue_id"]
            }

    def update_booking_status(self, booking_id: str, new_status: str) -> Dict:
        """
        Updates reservation status and synchronizes floor plan table state.
        """
        status_clean = new_status.upper()
        if status_clean not in VALID_BOOKING_STATUSES:
            raise ValueError(f"Invalid booking status '{new_status}'. Valid: {', '.join(VALID_BOOKING_STATUSES)}")

        booking = self.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking ID {booking_id} not found.")

        table_num = booking["table_number"]

        with db._lock, db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE table_bookings SET status = ? WHERE id = ?", (status_clean, booking_id))
            conn.commit()

        # Update floor plan layout table status accordingly
        if status_clean == "SEATED":
            floor_plan_service.update_table_status(table_num, "OCCUPIED")
        elif status_clean in ["COMPLETED", "CANCELLED", "NO_SHOW"]:
            floor_plan_service.update_table_status(table_num, "AVAILABLE")
        elif status_clean == "CONFIRMED":
            floor_plan_service.update_table_status(table_num, "RESERVED")

        updated = self.get_booking_by_id(booking_id)
        return updated

    def generate_booking_pdf(self, booking_id: str) -> bytes:
        """
        Generates a ReportLab PDF Table Reservation Confirmation Voucher with QR Code.
        """
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking ID {booking_id} not found.")

        venue = venue_service.get_active_venue()

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
            'BkgTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'BkgSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        bold_style = ParagraphStyle('BkgBold', parent=styles['Normal'], fontName='Helvetica-Bold')
        normal_style = styles['Normal']

        elements = []

        # Document Header
        elements.append(Paragraph("TABLE RESERVATION CONFIRMATION", title_style))
        elements.append(Paragraph(f"Ref: {booking['id']} | Venue: {venue['name']}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Booking Details Card
        bkg_data = [
            [
                Paragraph("<b>GUEST RESERVATION DETAILS:</b>", bold_style),
                Paragraph("<b>VENUE LOCATION:</b>", bold_style)
            ],
            [
                Paragraph(
                    f"Guest Name: <b>{booking['guest_name']}</b><br/>"
                    f"Party Size: <b>{booking['party_size']} Guests</b><br/>"
                    f"Date: <b>{booking['booking_date']}</b> | Time: <b>{booking['time_slot']}</b><br/>"
                    f"Allocated Table: <b>Table #{booking['table_number']}</b><br/>"
                    f"Status: <b>{booking['status']}</b>",
                    normal_style
                ),
                Paragraph(
                    f"Store: <b>{venue['name']}</b><br/>"
                    f"Address: {venue['address']}<br/>"
                    f"Contact: {booking['guest_phone']}<br/>"
                    f"Special Notes: <i>{booking['special_requests'] or 'None'}</i>",
                    normal_style
                )
            ]
        ]
        bkg_table = Table(bkg_data, colWidths=[260, 260])
        bkg_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#00B4DB')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(bkg_table)
        elements.append(Spacer(1, 15))

        # Embed QR Code for Check-in
        qr_png = qr_generator_service.generate_table_qr_png(booking['table_number'])
        qr_img = Image(io.BytesIO(qr_png), width=120, height=120)
        
        qr_data = [
            [
                qr_img,
                Paragraph(
                    "<b>FAST CHECK-IN QR CODE:</b><br/><br/>"
                    "Show this QR code voucher to your host upon arrival to automatically check-in and seat your party.<br/><br/>"
                    "<i>Please arrive 5 minutes before your time slot. Reservations are held for 15 minutes.</i>",
                    normal_style
                )
            ]
        ]
        qr_table = Table(qr_data, colWidths=[140, 380])
        qr_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(qr_table)
        elements.append(Spacer(1, 20))

        # Policies Footer
        policy_text = (
            "<b>Cancellation Policy:</b> Cancellations can be made up to 2 hours prior to reservation time.<br/>"
            "<b>Dietary & Allergies:</b> Please notify your server of any severe dietary requirements upon seating."
        )
        elements.append(Paragraph(policy_text, normal_style))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

table_booking_service = TableBookingModule()
