from collections import Counter
from typing import List, Dict, Any
from app.schemas.reviews import ReviewItem, ReviewSummary


class ReviewService:
    """Extracts 3 pros, 3 cons, one-line verdict, and detects suspicious review patterns."""

    def summarize_reviews(self, product_id: str, product_title: str, reviews: List[ReviewItem]) -> ReviewSummary:
        if not reviews:
            return ReviewSummary(
                product_id=product_id,
                product_title=product_title,
                average_rating=0.0,
                total_reviews=0,
                pros=["Abhi customer reviews mojood nahi hain"],
                cons=["Koi negative report nahi"],
                verdict="Naya item hai, reviews abhi collect ho rahe hain.",
                suspicious_flags=[],
                is_suspicious=False
            )

        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

        # 1. Suspicious review heuristic checks
        suspicious_flags = []

        # Check A: Burst of 5-star reviews on the same date
        date_counts = Counter(r.date for r in reviews if r.rating >= 4.8)
        burst_dates = [d for d, c in date_counts.items() if c >= 3]
        if burst_dates:
            suspicious_flags.append(f"Ek hi din ({burst_dates[0]}) par achanak zyada 5-star reviews diye gaye")

        # Check B: Reviewers with only 1 total review count
        single_reviewers = [r for r in reviews if r.reviewer_review_count <= 1]
        if len(single_reviewers) >= 3 and len(single_reviewers) / len(reviews) > 0.5:
            suspicious_flags.append("Aksar reviews aise accounts se hain jinka ye pehla review hai")

        # Check C: Duplicate or verbatim repeated review texts
        text_counts = Counter(r.text.strip().lower() for r in reviews)
        duplicates = [t for t, c in text_counts.items() if c >= 2]
        if duplicates:
            suspicious_flags.append("Ek jaise lafz bar bar copy-paste kiye gaye hain")

        is_suspicious = len(suspicious_flags) >= 2

        # 2. Extract Pros and Cons
        pros = []
        cons = []

        pos_keywords = {
            "comfortable": "Zabardast comfort aur soft cushioning",
            "cushion": "Running aur jogging ke liye behtareen cushion",
            "durable": "Mazboot outsole aur lambi chalne wali quality",
            "lightweight": "Wazan mein bohot halka",
            "fit": "Pakistani standard foot size ke mutabiq perfect fit",
            "noise": "Industry-leading active noise cancelling",
            "battery": "Lambi battery life",
            "value": "Rs. ke hisab se bohot achi value",
            "sound": "Crisp clear sound aur mic quality",
            "warm": "Thand ke liye warm fleece fabric"
        }

        neg_keywords = {
            "crushed": "Courier delivery mein packaging dab sakti hai",
            "stiff": "Shuru ke kuch minute sole thora stiff rehta hai",
            "narrow": "Wide foot walon ke liye forefoot thora narrow ho sakta hai",
            "smell": "Kharab plastic smell ka report",
            "plastic": "Substandard material durability",
            "broke": "Jaldi tutne ki complaint",
            "duty": "Import taxes ki waja se foreign price zyada hai",
            "case": "Carrying case fold nahi hota"
        }

        all_text = " ".join(r.text.lower() for r in reviews)

        for kw, desc in pos_keywords.items():
            if kw in all_text and desc not in pros:
                pros.append(desc)
            if len(pros) == 3:
                break

        for kw, desc in neg_keywords.items():
            if kw in all_text and desc not in cons:
                cons.append(desc)
            if len(cons) == 3:
                break

        # Fallback pros/cons if specific keywords not triggered
        default_pros = [
            "Customer rating aur overall satisfaction aala hai",
            "Original brand aur authentic product",
            "Daily use ke liye reliable choice"
        ]
        default_cons = [
            "Sale khatam hone ke baad price barh sakti hai",
            "Peak delivery season mein 1 din delay ho sakta hai",
            "Limited color options"
        ]

        while len(pros) < 3:
            pros.append(default_pros[len(pros)])
        while len(cons) < 3:
            cons.append(default_cons[len(cons)])

        # 3. One-line Verdict
        if is_suspicious:
            verdict = "⚠️ Reviews mein mashkook patterns mile hain; khareedne se pehle seller trust aur COD ko tarjeeh dein."
        elif avg_rating >= 4.5:
            verdict = f"Overall {avg_rating}/5 rating ke sath ye ek top-rated aur qabil-e-itmad product hai."
        elif avg_rating >= 4.0:
            verdict = f"Achhi product hai ({avg_rating}/5), daily use ke liye budget-friendly hai."
        else:
            verdict = f"Miyanah darjay ki product hai ({avg_rating}/5); behtar alternatives check karein."

        return ReviewSummary(
            product_id=product_id,
            product_title=product_title,
            average_rating=avg_rating,
            total_reviews=len(reviews),
            pros=pros[:3],
            cons=cons[:3],
            verdict=verdict,
            suspicious_flags=suspicious_flags,
            is_suspicious=is_suspicious
        )


review_service = ReviewService()
