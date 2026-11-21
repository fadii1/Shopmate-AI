from typing import List, Optional, Dict, Any
from app.adapters.base import BaseStoreAdapter
from app.schemas.product import Product, ProductFilter
from app.schemas.reviews import ReviewItem
from app.services.fx_service import fx_service


class AmazonAdapter(BaseStoreAdapter):
    """Adapter for Amazon Global Store (with USD to PKR live conversion & delivery fees)."""

    def __init__(self):
        self._raw_products = self._init_raw_amazon_items()
        self._reviews_db = self._init_mock_reviews()
        self._history_db = self._init_mock_history()

    @property
    def store_name(self) -> str:
        return "Amazon"

    async def search(self, query: str, filters: Optional[ProductFilter] = None) -> List[Product]:
        query_lower = query.lower()
        results: List[Product] = []

        for item in self._raw_products:
            title_match = any(word in item["title"].lower() for word in query_lower.split())
            spec_match = any(word in str(item.get("specs", {})).lower() for word in query_lower.split())

            if not (title_match or spec_match or query_lower in item["title"].lower()):
                continue

            # Convert prices from USD to PKR
            fx_info = fx_service.usd_to_pkr(item["price_usd"])
            fx_deliv = fx_service.usd_to_pkr(item["delivery_usd"])
            orig_fx = fx_service.usd_to_pkr(item["original_price_usd"]) if item.get("original_price_usd") else None

            product = Product(
                id=item["id"],
                title=item["title"],
                price_pkr=fx_info["amount_pkr"],
                original_price_pkr=orig_fx["amount_pkr"] if orig_fx else None,
                currency="PKR",
                store="Amazon",
                seller=item["seller"],
                seller_trust_score=item.get("seller_trust_score", 95),
                rating=item["rating"],
                review_count=item["review_count"],
                delivery_days=item["delivery_days"],
                delivery_fee_pkr=fx_deliv["amount_pkr"],
                payment_methods=["Card"],  # Amazon international requires online card payment
                url=item["url"],
                image=item.get("image"),
                in_stock=item.get("in_stock", True),
                specs=item.get("specs", {}),
                return_policy="30 days Amazon Global Return Policy",
                is_sponsored=item.get("is_sponsored", False)
            )

            # Apply filters
            if filters:
                if filters.min_price is not None and product.price_pkr < filters.min_price:
                    continue
                if filters.max_price is not None and product.price_pkr > filters.max_price:
                    continue
                if filters.brand and filters.brand.lower() not in product.title.lower() and filters.brand.lower() != str(product.specs.get("brand", "")).lower():
                    continue
                if filters.size:
                    available_sizes = [str(s) for s in product.specs.get("sizes", [])]
                    if available_sizes and str(filters.size) not in available_sizes:
                        continue
                if filters.min_rating is not None and product.rating < filters.min_rating:
                    continue
                if filters.max_delivery_days is not None and product.delivery_days > filters.max_delivery_days:
                    continue

            results.append(product)

        # Sorting
        if filters and filters.sort_by:
            if filters.sort_by == "price_asc":
                results.sort(key=lambda x: x.total_price_pkr)
            elif filters.sort_by == "price_desc":
                results.sort(key=lambda x: x.total_price_pkr, reverse=True)
            elif filters.sort_by == "rating":
                results.sort(key=lambda x: x.rating, reverse=True)
            elif filters.sort_by == "delivery":
                results.sort(key=lambda x: x.delivery_days)
            else:  # value
                results.sort(key=lambda x: (x.rating * 20 + x.seller_trust_score) / (x.total_price_pkr / 1000 + 1), reverse=True)

        return results

    async def get_product(self, product_id: str) -> Optional[Product]:
        for item in self._raw_products:
            if item["id"] == product_id:
                fx_info = fx_service.usd_to_pkr(item["price_usd"])
                fx_deliv = fx_service.usd_to_pkr(item["delivery_usd"])
                orig_fx = fx_service.usd_to_pkr(item["original_price_usd"]) if item.get("original_price_usd") else None

                return Product(
                    id=item["id"],
                    title=item["title"],
                    price_pkr=fx_info["amount_pkr"],
                    original_price_pkr=orig_fx["amount_pkr"] if orig_fx else None,
                    currency="PKR",
                    store="Amazon",
                    seller=item["seller"],
                    seller_trust_score=item.get("seller_trust_score", 95),
                    rating=item["rating"],
                    review_count=item["review_count"],
                    delivery_days=item["delivery_days"],
                    delivery_fee_pkr=fx_deliv["amount_pkr"],
                    payment_methods=["Card"],
                    url=item["url"],
                    image=item.get("image"),
                    in_stock=item.get("in_stock", True),
                    specs=item.get("specs", {}),
                    return_policy="30 days Amazon Global Return Policy",
                    is_sponsored=item.get("is_sponsored", False)
                )
        return None

    async def get_reviews(self, product_id: str) -> List[ReviewItem]:
        return self._reviews_db.get(product_id, [])

    async def get_price_history(self, product_id: str) -> List[Dict[str, Any]]:
        # Converts USD history to PKR
        usd_history = self._history_db.get(product_id, [])
        pkr_history = []
        for h in usd_history:
            pkr_entry = dict(h)
            fx = fx_service.usd_to_pkr(h["price_usd"])
            pkr_entry["price_pkr"] = fx["amount_pkr"]
            pkr_history.append(pkr_entry)
        return pkr_history

    def _init_raw_amazon_items(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "amz-shoe-01",
                "title": "Nike Air Zoom Pegasus 40 Mens Road Running Shoes",
                "price_usd": 99.95,  # ~ Rs. 27,836 PKR
                "original_price_usd": 130.00,
                "seller": "Nike Official Amazon Store",
                "seller_trust_score": 96,
                "rating": 4.7,
                "review_count": 2840,
                "delivery_days": 10,
                "delivery_usd": 15.00,  # ~ Rs. 4,177 PKR
                "url": "https://www.amazon.com/dp/B0BY3M9Z4K",
                "image": "https://m.media-amazon.com/images/I/71xyzPegasus40.jpg",
                "in_stock": True,
                "specs": {"brand": "Nike", "sizes": ["8", "9", "10", "11"], "colors": ["Black", "White", "Navy"], "category": "Shoes"}
            },
            {
                "id": "amz-audio-01",
                "title": "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones",
                "price_usd": 328.00,  # ~ Rs. 91,348 PKR
                "original_price_usd": 399.99,
                "seller": "Amazon.com Export Sales",
                "seller_trust_score": 98,
                "rating": 4.8,
                "review_count": 8920,
                "delivery_days": 8,
                "delivery_usd": 22.00,  # ~ Rs. 6,127 PKR
                "url": "https://www.amazon.com/dp/B09XS7JWHH",
                "image": "https://m.media-amazon.com/images/I/61vJ8qXM5.jpg",
                "in_stock": True,
                "specs": {"brand": "Sony", "anc": True, "battery": "30 hours"}
            },
            {
                "id": "amz-hoodie-01",
                "title": "Champion Mens Powerblend Fleece Pullover Hoodie Black",
                "price_usd": 24.50,  # ~ Rs. 6,823 PKR
                "original_price_usd": 50.00,
                "seller": "Champion Athletic",
                "seller_trust_score": 92,
                "rating": 4.6,
                "review_count": 14200,
                "delivery_days": 11,
                "delivery_usd": 12.00,
                "url": "https://www.amazon.com/dp/B01H2F3W9G",
                "image": "https://m.media-amazon.com/images/I/81xChampionHoodie.jpg",
                "in_stock": True,
                "specs": {"brand": "Champion", "color": "Black", "sizes": ["M", "L", "XL"]}
            }
        ]

    def _init_mock_reviews(self) -> Dict[str, List[ReviewItem]]:
        return {
            "amz-shoe-01": [
                ReviewItem(id="ar1", reviewer="David W.", rating=5.0, text="The Pegasus 40 is the gold standard for daily trainers. Soft responsive foam.", date="2026-11-12", reviewer_review_count=34),
                ReviewItem(id="ar2", reviewer="Michael B.", rating=4.5, text="Great running shoes, durable outsole that lasts 500+ miles. International shipping arrived fine.", date="2026-11-01", reviewer_review_count=19),
                ReviewItem(id="ar3", reviewer="Chris L.", rating=4.0, text="Runs slightly narrow in the forefoot, consider half size up if you have wide feet.", date="2026-10-18", reviewer_review_count=8),
            ],
            "amz-audio-01": [
                ReviewItem(id="ara1", reviewer="Sarah M.", rating=5.0, text="Best ANC in the market. Silences airplane engines and office chatter effortlessly.", date="2026-11-16", reviewer_review_count=42),
                ReviewItem(id="ara2", reviewer="Kenji T.", rating=5.0, text="Comfortable headband, multipoint Bluetooth connection switches flawlessly between laptop and phone.", date="2026-11-08", reviewer_review_count=27),
                ReviewItem(id="ara3", reviewer="Alex P.", rating=4.0, text="Case does not fold as compact as XM4, but audio profile is much cleaner.", date="2026-10-25", reviewer_review_count=14),
            ]
        }

    def _init_mock_history(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "amz-shoe-01": [
                {"date": "2026-09-01", "price_usd": 130.00, "is_sale": False},
                {"date": "2026-10-01", "price_usd": 120.00, "is_sale": False},
                {"date": "2026-11-01", "price_usd": 105.00, "is_sale": True},
                {"date": "2026-11-20", "price_usd": 99.95, "is_sale": True},
            ],
            "amz-audio-01": [
                {"date": "2026-09-01", "price_usd": 399.99, "is_sale": False},
                {"date": "2026-10-01", "price_usd": 380.00, "is_sale": False},
                {"date": "2026-11-01", "price_usd": 348.00, "is_sale": True},
                {"date": "2026-11-20", "price_usd": 328.00, "is_sale": True},
            ]
        }
