from typing import List, Optional
from pydantic import BaseModel, Field


class ReviewItem(BaseModel):
    id: str
    reviewer: str
    rating: float = Field(..., ge=1.0, le=5.0)
    text: str
    date: str
    is_verified_purchase: bool = True
    reviewer_review_count: int = 1


class ReviewSummary(BaseModel):
    product_id: str
    product_title: str
    average_rating: float
    total_reviews: int
    pros: List[str] = Field(..., min_length=1, max_length=5, description="Top positive points (3 preferred)")
    cons: List[str] = Field(..., min_length=1, max_length=5, description="Top negative points (3 preferred)")
    verdict: str = Field(..., description="One-line summary verdict")
    suspicious_flags: List[str] = Field(
        default_factory=list,
        description="Flags for potential fake reviews (e.g. repeated text, burst 5-stars)"
    )
    is_suspicious: bool = Field(
        False,
        description="Whether reviews exhibit signs of artificial manipulation"
    )
    disclaimer: str = Field(
        "Ye review flag hai, koi pakka saboot nahi hai.",
        description="User-facing note explaining flags are heuristic"
    )
