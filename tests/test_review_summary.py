import pytest
from app.services.review_service import review_service
from app.schemas.reviews import ReviewItem


def test_review_summary_structure():
    reviews = [
        ReviewItem(id="1", reviewer="Ali", rating=5.0, text="Very comfortable running shoes, lightweight and durable sole", date="2026-11-01", reviewer_review_count=10),
        ReviewItem(id="2", reviewer="Bilal", rating=4.5, text="Good fit for size 9, daily cushion is amazing", date="2026-11-03", reviewer_review_count=5),
        ReviewItem(id="3", reviewer="Hamza", rating=4.0, text="Courier crushed box but shoes are safe. Slightly stiff initially.", date="2026-11-05", reviewer_review_count=8),
    ]

    summary = review_service.summarize_reviews("p1", "Test Shoes", reviews)

    assert len(summary.pros) == 3
    assert len(summary.cons) == 3
    assert summary.average_rating > 4.0
    assert summary.verdict != ""
    assert summary.is_suspicious is False


def test_suspicious_review_detection():
    # Bursts of duplicate text on same day from single-review accounts
    fake_reviews = [
        ReviewItem(id="1", reviewer="Bot1", rating=5.0, text="Very good product thanks seller highly recommend best quality ever", date="2026-11-10", reviewer_review_count=1),
        ReviewItem(id="2", reviewer="Bot2", rating=5.0, text="Very good product thanks seller highly recommend best quality ever", date="2026-11-10", reviewer_review_count=1),
        ReviewItem(id="3", reviewer="Bot3", rating=5.0, text="Very good product thanks seller highly recommend best quality ever", date="2026-11-10", reviewer_review_count=1),
        ReviewItem(id="4", reviewer="RealBuyer", rating=2.0, text="Broke in two days, cheap plastic smell", date="2026-11-12", reviewer_review_count=4),
    ]

    summary = review_service.summarize_reviews("fake-p", "Fake Product", fake_reviews)

    assert summary.is_suspicious is True
    assert len(summary.suspicious_flags) >= 2
    assert "Ye review flag hai, koi pakka saboot nahi hai" in summary.disclaimer
