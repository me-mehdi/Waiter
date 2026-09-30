import io
import re
from typing import List, Dict, Optional
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from src.core.db import db
from src.modules.reviews import review_service
from src.modules.venue import venue_service

POSITIVE_KEYWORDS = ["great", "excellent", "delicious", "amazing", "fast", "friendly", "fresh", "loved", "perfect", "tasty", "clean", "wonderful", "quick"]
NEGATIVE_KEYWORDS = ["slow", "cold", "salty", "dirty", "overpriced", "bad", "terrible", "late", "missing", "waiting", "bland", "rude", "disappointed"]

class FeedbackAnalyticsModule:
    """
    Guest Feedback, Sentiment & Net Promoter Score (NPS) Analytics Module.
    Computes venue NPS metrics, sentiment keyword frequency, urgent manager alerts,
    and exports ReportLab PDF Customer Sentiment Reports.
    """

    def calculate_nps(self) -> Dict:
        """
        Calculates Net Promoter Score (NPS) based on guest review ratings.
        Ratings: 5 = Promoter, 4 = Passive, 1-3 = Detractor.
        NPS = % Promoters - % Detractors (scale: -100 to +100).
        """
        reviews = db.reviews
        total_reviews = len(reviews)
        if total_reviews == 0:
            return {
                "nps_score": 0,
                "total_reviews": 0,
                "promoters_count": 0,
                "passives_count": 0,
                "detractors_count": 0,
                "promoters_pct": 0.0,
                "passives_pct": 0.0,
                "detractors_pct": 0.0,
                "sentiment_health": "NEUTRAL"
            }

        promoters = [r for r in reviews if r["rating"] == 5]
        passives = [r for r in reviews if r["rating"] == 4]
        detractors = [r for r in reviews if r["rating"] <= 3]

        p_cnt = len(promoters)
        pas_cnt = len(passives)
        d_cnt = len(detractors)

        p_pct = round((p_cnt / total_reviews) * 100, 1)
        pas_pct = round((pas_cnt / total_reviews) * 100, 1)
        d_pct = round((d_cnt / total_reviews) * 100, 1)

        nps_score = round(p_pct - d_pct, 1)

        if nps_score >= 50:
            health = "EXCELLENT"
        elif nps_score >= 20:
            health = "GOOD"
        elif nps_score >= 0:
            health = "AVERAGE"
        else:
            health = "NEEDS_IMPROVEMENT"

        return {
            "nps_score": nps_score,
            "total_reviews": total_reviews,
            "promoters_count": p_cnt,
            "passives_count": pas_cnt,
            "detractors_count": d_cnt,
            "promoters_pct": p_pct,
            "passives_pct": pas_pct,
            "detractors_pct": d_pct,
            "sentiment_health": health
        }

    def extract_sentiment(self) -> Dict:
        """
        Performs keyword sentiment frequency analysis on review comments.
        """
        reviews = db.reviews
        pos_hits: Dict[str, int] = {}
        neg_hits: Dict[str, int] = {}

        pos_comment_count = 0
        neg_comment_count = 0
        neu_comment_count = 0

        for r in reviews:
            comment = (r.get("comment") or "").lower()
            words = re.findall(r'\b\w+\b', comment)

            has_pos = False
            has_neg = False

            for w in words:
                if w in POSITIVE_KEYWORDS:
                    pos_hits[w] = pos_hits.get(w, 0) + 1
                    has_pos = True
                if w in NEGATIVE_KEYWORDS:
                    neg_hits[w] = neg_hits.get(w, 0) + 1
                    has_neg = True

            if r["rating"] >= 4 or (has_pos and not has_neg):
                pos_comment_count += 1
            elif r["rating"] <= 2 or (has_neg and not has_pos):
                neg_comment_count += 1
            else:
                neu_comment_count += 1

        total = len(reviews)
        return {
            "total_analyzed": total,
            "positive_reviews_count": pos_comment_count,
            "negative_reviews_count": neg_comment_count,
            "neutral_reviews_count": neu_comment_count,
            "positive_sentiment_pct": round((pos_comment_count / total * 100), 1) if total > 0 else 0.0,
            "negative_sentiment_pct": round((neg_comment_count / total * 100), 1) if total > 0 else 0.0,
            "top_positive_keywords": sorted([{"keyword": k, "count": v} for k, v in pos_hits.items()], key=lambda x: x["count"], reverse=True)[:5],
            "top_negative_keywords": sorted([{"keyword": k, "count": v} for k, v in neg_hits.items()], key=lambda x: x["count"], reverse=True)[:5]
        }

    def get_manager_alerts(self) -> List[Dict]:
        """
        Retrieves low-rating reviews (<= 3 stars) requiring urgent manager action.
        """
        reviews = db.reviews
        low_stars = [r for r in reviews if r["rating"] <= 3]
        alerts = []
        for r in low_stars:
            alerts.append({
                "review_id": r["id"],
                "table_number": r["table_number"],
                "rating": r["rating"],
                "comment": r["comment"],
                "created_at": r["created_at"],
                "urgency": "HIGH" if r["rating"] <= 2 else "MEDIUM",
                "status": "NEEDS_ACTION"
            })
        return alerts

    def generate_feedback_pdf_report(self) -> bytes:
        """
        Generates a formal ReportLab PDF Customer Sentiment & NPS Executive Report.
        """
        nps_info = self.calculate_nps()
        sentiment_info = self.extract_sentiment()
        alerts = self.get_manager_alerts()

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
            'NPSTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'NPSSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        bold_style = ParagraphStyle('NPSBold', parent=styles['Normal'], fontName='Helvetica-Bold')
        normal_style = styles['Normal']

        elements = []

        # Document Header
        elements.append(Paragraph("GUEST FEEDBACK & NPS SENTIMENT REPORT", title_style))
        elements.append(Paragraph(f"Venue: {venue_service.get_active_venue()['name']} | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", subtitle_style))
        elements.append(Spacer(1, 10))

        # NPS Executive Score Card
        score_color = colors.HexColor('#16A34A') if nps_info["nps_score"] >= 20 else colors.HexColor('#DC2626')
        nps_data = [
            [
                Paragraph("<b>Net Promoter Score (NPS)</b>", bold_style),
                Paragraph("<b>Total Reviews</b>", bold_style),
                Paragraph("<b>Sentiment Health</b>", bold_style)
            ],
            [
                Paragraph(f"<font size=16 color='{score_color.hexval()}'><b>+{nps_info['nps_score']}</b></font>", normal_style),
                Paragraph(str(nps_info["total_reviews"]), normal_style),
                Paragraph(f"<b>{nps_info['sentiment_health']}</b>", bold_style)
            ]
        ]
        nps_table = Table(nps_data, colWidths=[170, 170, 180])
        nps_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(nps_table)
        elements.append(Spacer(1, 15))

        # Promoters / Passives / Detractors Grid
        elements.append(Paragraph("<b>NPS RATINGS BREAKDOWN:</b>", bold_style))
        elements.append(Spacer(1, 5))

        breakdown_data = [
            [
                Paragraph("<b>Segment Category</b>", bold_style),
                Paragraph("<b>Star Rating</b>", bold_style),
                Paragraph("<b>Guest Count</b>", bold_style),
                Paragraph("<b>Percentage Ratio</b>", bold_style)
            ],
            [
                Paragraph("Promoters (Advocates)", bold_style),
                "5 Stars",
                str(nps_info["promoters_count"]),
                f"{nps_info['promoters_pct']}%"
            ],
            [
                Paragraph("Passives (Satisfied)", normal_style),
                "4 Stars",
                str(nps_info["passives_count"]),
                f"{nps_info['passives_pct']}%"
            ],
            [
                Paragraph("Detractors (Unhappy)", bold_style),
                "1-3 Stars",
                str(nps_info["detractors_count"]),
                f"{nps_info['detractors_pct']}%"
            ]
        ]
        b_table = Table(breakdown_data, colWidths=[180, 100, 110, 130])
        b_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F1F5F9')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(b_table)
        elements.append(Spacer(1, 15))

        # Urgent Manager Alerts Section
        elements.append(Paragraph("<b>URGENT MANAGER ACTION ALERTS:</b>", bold_style))
        elements.append(Spacer(1, 5))

        alert_table_data = [
            [
                Paragraph("<b>Table #</b>", bold_style),
                Paragraph("<b>Rating</b>", bold_style),
                Paragraph("<b>Guest Comment</b>", bold_style),
                Paragraph("<b>Urgency Level</b>", bold_style)
            ]
        ]

        for a in alerts:
            alert_table_data.append([
                f"#{a['table_number']}",
                f"{a['rating']} ★",
                Paragraph(a['comment'] or "No comment left", normal_style),
                Paragraph(f"<b>{a['urgency']}</b>", bold_style)
            ])

        if len(alerts) == 0:
            alert_table_data.append(["-", "-", "No urgent manager alerts logged.", "NORMAL"])

        a_table = Table(alert_table_data, colWidths=[65, 65, 290, 100])
        a_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#991B1B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#FEF2F2')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FCA5A5')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(a_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

feedback_analytics_service = FeedbackAnalyticsModule()
