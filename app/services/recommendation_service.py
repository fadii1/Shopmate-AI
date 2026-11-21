from typing import List, Dict, Any


class RecommendationService:
    """Handles personalized product recommendations and Pakistani gift suggestions."""

    def get_recommendations(self, category: str = "running shoes") -> List[Dict[str, Any]]:
        """Returns personalized suggestions based on category or recent user queries."""
        items = [
            {
                "id": "daraz-shoe-01",
                "title": "Nike Revolution 7 Running Shoes",
                "tag": "Best Value",
                "price_pkr": 4999.0,
                "original_price_pkr": 6999.0,
                "store": "Daraz",
                "seller": "Nike Authorized PK",
                "rating": 4.6,
                "review_count": "12k",
                "delivery_days": 3,
                "image": "https://img.daraz.pk/p/nike-rev-7.jpg"
            },
            {
                "id": "daraz-audio-01",
                "title": "Sony WH-CH520 Wireless Headphones",
                "tag": "Top Rated",
                "price_pkr": 7999.0,
                "original_price_pkr": 9999.0,
                "store": "PriceOye",
                "seller": "Sony Official",
                "rating": 4.7,
                "review_count": "8k",
                "delivery_days": 2,
                "image": "https://img.daraz.pk/p/sony-ch520.jpg"
            },
            {
                "id": "daraz-watch-01",
                "title": "boAt Wave Lite Smartwatch",
                "tag": "Trending",
                "price_pkr": 3499.0,
                "original_price_pkr": 5499.0,
                "store": "Daraz",
                "seller": "boAt Store PK",
                "rating": 4.5,
                "review_count": "15k",
                "delivery_days": 3,
                "image": "https://img.daraz.pk/p/boat-wave.jpg"
            }
        ]
        return items

    def get_price_drop_watch(self) -> List[Dict[str, Any]]:
        """Items currently experiencing significant price drops."""
        return [
            {
                "id": "watch-drop-01",
                "title": "Adidas Running Shoes",
                "current_price_pkr": 6999.0,
                "original_price_pkr": 8999.0,
                "drop_percentage": "22%",
                "store": "Daraz"
            },
            {
                "id": "watch-drop-02",
                "title": "OnePlus Buds 3",
                "current_price_pkr": 14999.0,
                "original_price_pkr": 19999.0,
                "drop_percentage": "25%",
                "store": "PriceOye"
            }
        ]

    def suggest_gifts(self, occasion: str, recipient: str, budget_pkr: float) -> List[Dict[str, Any]]:
        """Gift suggestions for Pakistani occasions (Eid, Weddings, Birthdays)."""
        gifts = []
        if "eid" in occasion.lower() or "birthday" in occasion.lower():
            gifts.append({
                "idea": "Premium Smartwatch with Fitness Tracker",
                "suggested_budget": "Rs. 3,500 - 6,000",
                "store": "Daraz / PriceOye",
                "why": "Har umar ke liye behtareen aur useful gift hai."
            })
            gifts.append({
                "idea": "Wireless Noise Cancelling Earbuds",
                "suggested_budget": "Rs. 4,500 - 8,000",
                "store": "Daraz Mall",
                "why": "Daily commute aur calls ke liye zabardast choice."
            })
        else:
            gifts.append({
                "idea": "Genuine Leather Wallet & Belt Gift Set",
                "suggested_budget": "Rs. 2,500 - 4,500",
                "store": "Outfitters / J.",
                "why": "Evergreen and elegant Pakistani gift choice."
            })
        return gifts


recommendation_service = RecommendationService()
