from typing import List, Dict
from src.core.db import db

class ReviewModule:
    """
    Private Customer Reviews ("Avis clients") Module
    Captures guest feedback internally before it reaches public review platforms.
    """
    def submit_review(self, table_number: int, rating: int, comment: str = "") -> dict:
        payload = {
            "table_number": table_number,
            "rating": max(1, min(5, rating)),
            "comment": comment
        }
        return db.add_review(payload)

    def get_all_reviews(self) -> List[dict]:
        return db.reviews

    def get_average_rating(self) -> float:
        if not db.reviews:
            return 0.0
        total_rating = sum(r["rating"] for r in db.reviews)
        return round(total_rating / len(db.reviews), 2)

review_service = ReviewModule()
