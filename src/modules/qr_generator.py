import io
import qrcode
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class QRGeneratorModule:
    """
    Table QR Code & PDF Tent Card Generator Module
    Generates scannable QR codes encoding table ordering URLs and printable PDF Table Tent cards.
    """
    
    def generate_table_qr_png(self, table_number: int, base_url: str = "http://127.0.0.1:5050") -> bytes:
        """Generates a PNG image byte stream for a table's QR code."""
        table_url = f"{base_url}/?table={table_number}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2
        )
        qr.add_data(table_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#0f2027", back_color="#ffffff")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

    def generate_pdf_table_tents(self, total_tables: int = 12, base_url: str = "http://127.0.0.1:5050") -> bytes:
        """
        Generates a printable PDF containing foldable Table Tent Cards for tables 1 to total_tables.
        Each page contains a card formatted for instant guest table-side ordering.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TentTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor("#0f2027"),
            alignment=1, # Center
            spaceAfter=6
        )

        table_num_style = ParagraphStyle(
            'TableNumStyle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=colors.HexColor("#00b4db"),
            alignment=1,
            spaceAfter=12
        )

        instruction_style = ParagraphStyle(
            'InstructionStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor("#333333"),
            alignment=1,
            spaceAfter=6
        )

        sub_instruction = ParagraphStyle(
            'SubInstruction',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=1
        )

        for t_num in range(1, total_tables + 1):
            # Header
            story.append(Paragraph("THE WAITER UK", title_style))
            story.append(Paragraph(f"TABLE #{t_num}", table_num_style))
            story.append(Spacer(1, 10))

            # QR Code Image
            png_bytes = self.generate_table_qr_png(t_num, base_url)
            qr_img_stream = io.BytesIO(png_bytes)
            rl_img = RLImage(qr_img_stream, width=180, height=180)
            rl_img.hAlign = 'CENTER'
            story.append(rl_img)

            story.append(Spacer(1, 16))
            story.append(Paragraph("<b>SCAN TO VIEW MENU & ORDER</b>", instruction_style))
            story.append(Paragraph("Point your smartphone camera at the QR code above.<br/>No app download required.", sub_instruction))
            story.append(Spacer(1, 20))
            story.append(Paragraph("<i>Powered by The Waiter (waiter.com)</i>", sub_instruction))

            # Page break for next table tent except for the last one
            if t_num < total_tables:
                from reportlab.platypus import PageBreak
                story.append(PageBreak())

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

qr_generator_service = QRGeneratorModule()
