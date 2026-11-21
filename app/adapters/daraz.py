from typing import List, Optional, Dict, Any
from app.adapters.base import BaseStoreAdapter
from app.schemas.product import Product, ProductFilter
from app.schemas.reviews import ReviewItem


class DarazAdapter(BaseStoreAdapter):
    """Adapter for Daraz Pakistan (daraz.pk)."""

    def __init__(self):
        self._products_db = self._init_mock_catalog()
        self._reviews_db = self._init_mock_reviews()
        self._history_db = self._init_mock_history()

    @property
    def store_name(self) -> str:
        return "Daraz"

    async def search(self, query: str, filters: Optional[ProductFilter] = None) -> List[Product]:
        query_lower = query.lower()
        results: List[Product] = []

        for p in self._products_db:
            # Query match across title, brand, category, tags
            title_match = any(word in p.title.lower() for word in query_lower.split())
            spec_match = any(word in str(p.specs).lower() for word in query_lower.split())

            if not (title_match or spec_match or query_lower in p.title.lower()):
                continue

            # Apply filters
            if filters:
                if filters.min_price is not None and p.price_pkr < filters.min_price:
                    continue
                if filters.max_price is not None and p.price_pkr > filters.max_price:
                    continue
                if filters.brand and filters.brand.lower() not in p.title.lower() and filters.brand.lower() != str(p.specs.get("brand", "")).lower():
                    continue
                if filters.size:
                    available_sizes = [str(s) for s in p.specs.get("sizes", [])]
                    if available_sizes and str(filters.size) not in available_sizes:
                        continue
                if filters.color:
                    available_colors = [str(c).lower() for c in p.specs.get("colors", [])]
                    if available_colors and filters.color.lower() not in available_colors:
                        continue
                if filters.min_rating is not None and p.rating < filters.min_rating:
                    continue
                if filters.max_delivery_days is not None and p.delivery_days > filters.max_delivery_days:
                    continue

            results.append(p)

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
            else:  # "value"
                results.sort(key=lambda x: (x.rating * 20 + x.seller_trust_score) / (x.total_price_pkr / 1000 + 1), reverse=True)

        return results

    async def get_product(self, product_id: str) -> Optional[Product]:
        for p in self._products_db:
            if p.id == product_id:
                return p
        return None

    async def get_reviews(self, product_id: str) -> List[ReviewItem]:
        return self._reviews_db.get(product_id, [])

    async def get_price_history(self, product_id: str) -> List[Dict[str, Any]]:
        return self._history_db.get(product_id, [])

    def _init_mock_catalog(self) -> List[Product]:
        return [
            Product(
                id="daraz-shoe-01",
                title="Service Cheetah Mens Lightweight Running Shoes Size 9",
                price_pkr=4499.0,
                original_price_pkr=5200.0,
                currency="PKR",
                store="Daraz",
                seller="Service Official Flagship",
                seller_trust_score=94,
                rating=4.6,
                review_count=328,
                delivery_days=3,
                delivery_fee_pkr=199.0,
                payment_methods=["COD", "JazzCash", "Easypaisa", "Card"],
                url="https://www.daraz.pk/products/service-cheetah-running-shoes-i1001.html",
                image="https://img.daraz.pk/p/service-cheetah-9.jpg",
                in_stock=True,
                specs={"brand": "Service", "sizes": ["7", "8", "9", "10"], "colors": ["Black", "Blue"], "category": "Shoes"},
                return_policy="14 days free return via Daraz Mall",
                is_sponsored=False
            ),
            Product(
                id="daraz-shoe-02",
                title="NDURE Sprint Men Athletic Running Shoes Size 9",
                price_pkr=3850.0,
                original_price_pkr=4500.0,
                currency="PKR",
                store="Daraz",
                seller="NDURE Official Store",
                seller_trust_score=89,
                rating=4.4,
                review_count=185,
                delivery_days=3,
                delivery_fee_pkr=199.0,
                payment_methods=["COD", "JazzCash", "Easypaisa", "Card"],
                url="https://www.daraz.pk/products/ndure-sprint-running-shoes-i1002.html",
                image="https://img.daraz.pk/p/ndure-sprint.jpg",
                in_stock=True,
                specs={"brand": "NDURE", "sizes": ["8", "9", "10", "11"], "colors": ["Grey", "Black"], "category": "Shoes"},
                return_policy="7 days easy return",
                is_sponsored=False
            ),
            Product(
                id="daraz-shoe-03",
                title="Nike Air Zoom Pegasus 40 Mens Running Shoes",
                price_pkr=29500.0,
                original_price_pkr=32000.0,
                currency="PKR",
                store="Daraz",
                seller="KicksPk Certified",
                seller_trust_score=88,
                rating=4.8,
                review_count=64,
                delivery_days=4,
                delivery_fee_pkr=250.0,
                payment_methods=["COD", "JazzCash", "Card"],
                url="https://www.daraz.pk/products/nike-air-zoom-pegasus-40-i1003.html",
                image="https://img.daraz.pk/p/nike-pegasus-40.jpg",
                in_stock=True,
                specs={"brand": "Nike", "sizes": ["8", "9", "10"], "colors": ["Black", "White"], "category": "Shoes"},
                return_policy="7 days return for defective items",
                is_sponsored=False
            ),
            Product(
                id="daraz-shoe-04",
                title="Generic Breathable Gym Mesh Sneakers - Fake Deal Item",
                price_pkr=4200.0,
                original_price_pkr=8999.0,  # Jacked up fake original price!
                currency="PKR",
                store="Daraz",
                seller="QuickShop Lahore",
                seller_trust_score=48,  # Low trust seller
                rating=3.2,
                review_count=18,
                delivery_days=5,
                delivery_fee_pkr=220.0,
                payment_methods=["COD"],
                url="https://www.daraz.pk/products/generic-gym-mesh-sneakers-i1004.html",
                image="https://img.daraz.pk/p/generic-sneakers.jpg",
                in_stock=True,
                specs={"brand": "Generic", "sizes": ["9"], "colors": ["Black"], "category": "Shoes"},
                return_policy="No returns accepted",
                is_sponsored=False
            ),
            Product(
                id="daraz-phone-01",
                title="Samsung Galaxy A15 (8GB RAM, 128GB ROM) PTA Approved",
                price_pkr=49999.0,
                original_price_pkr=54999.0,
                currency="PKR",
                store="Daraz",
                seller="Samsung Official Store",
                seller_trust_score=97,
                rating=4.7,
                review_count=412,
                delivery_days=2,
                delivery_fee_pkr=0.0,
                payment_methods=["COD", "JazzCash", "Easypaisa", "Card"],
                url="https://www.daraz.pk/products/samsung-galaxy-a15-i2001.html",
                image="https://img.daraz.pk/p/samsung-a15.jpg",
                in_stock=True,
                specs={"brand": "Samsung", "ram": "8GB", "storage": "128GB", "pta": "Approved"},
                return_policy="14 days official Samsung warranty",
                is_sponsored=False
            ),
            Product(
                id="daraz-audio-01",
                title="Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
                price_pkr=98500.0,
                original_price_pkr=108000.0,
                currency="PKR",
                store="Daraz",
                seller="Sony Authorized Dealer PK",
                seller_trust_score=95,
                rating=4.9,
                review_count=98,
                delivery_days=3,
                delivery_fee_pkr=0.0,
                payment_methods=["JazzCash", "Easypaisa", "Card"],
                url="https://www.daraz.pk/products/sony-wh-1000xm5-i3001.html",
                image="https://img.daraz.pk/p/sony-xm5.jpg",
                in_stock=True,
                specs={"brand": "Sony", "anc": True, "battery": "30 hours"},
                return_policy="7 days replacement warranty",
                is_sponsored=False
            ),
            Product(
                id="daraz-hoodie-01",
                title="Men Fleece Pullover Black Hoodie Warm Winter",
                price_pkr=1850.0,
                original_price_pkr=2400.0,
                currency="PKR",
                store="Daraz",
                seller="Outfitters PK Direct",
                seller_trust_score=90,
                rating=4.5,
                review_count=144,
                delivery_days=3,
                delivery_fee_pkr=180.0,
                payment_methods=["COD", "JazzCash", "Easypaisa", "Card"],
                url="https://www.daraz.pk/products/men-fleece-black-hoodie-i4001.html",
                image="https://img.daraz.pk/p/black-hoodie.jpg",
                in_stock=True,
                specs={"brand": "Outfitters", "color": "Black", "sizes": ["M", "L", "XL"]},
                return_policy="7 days return",
                is_sponsored=False
            )
        ]

    def _init_mock_reviews(self) -> Dict[str, List[ReviewItem]]:
        return {
            "daraz-shoe-01": [
                ReviewItem(id="r1", reviewer="Hamza K.", rating=5.0, text="Bohot zabardast joote hain! Daily jogging ke liye perfect cushion hai aur durability achi hai.", date="2026-11-10", reviewer_review_count=12),
                ReviewItem(id="r2", reviewer="Tariq M.", rating=4.5, text="Very comfortable running shoes, size 9 fits true to Pakistani foot sizing. Grip on asphalt road is excellent.", date="2026-11-05", reviewer_review_count=5),
                ReviewItem(id="r3", reviewer="Usman A.", rating=4.0, text="Good value for Rs 4500. Box was slightly crushed by TCS courier but shoes were safe.", date="2026-10-28", reviewer_review_count=8),
                ReviewItem(id="r4", reviewer="Ali R.", rating=5.0, text="Local brand Service has improved quality a lot. Lightweight, no heel pain after 5km run.", date="2026-10-20", reviewer_review_count=15),
                ReviewItem(id="r5", reviewer="Zeeshan P.", rating=3.5, text="Sole is slightly stiff in cold weather for first 10 minutes, but softens up after warm up.", date="2026-10-15", reviewer_review_count=3),
            ],
            "daraz-shoe-04": [
                # Suspicious reviews: burst on same date, single review count, generic repetitive praising
                ReviewItem(id="sr1", reviewer="User991", rating=5.0, text="Very good product thanks seller highly recommend best quality ever", date="2026-11-18", reviewer_review_count=1),
                ReviewItem(id="sr2", reviewer="User992", rating=5.0, text="Very good product thanks seller highly recommend best quality ever", date="2026-11-18", reviewer_review_count=1),
                ReviewItem(id="sr3", reviewer="User993", rating=5.0, text="Very good product thanks seller highly recommend best quality ever", date="2026-11-18", reviewer_review_count=1),
                ReviewItem(id="sr4", reviewer="User994", rating=5.0, text="Very good product thanks seller highly recommend best quality ever", date="2026-11-18", reviewer_review_count=1),
                ReviewItem(id="sr5", reviewer="GenuineBuyer", rating=1.5, text="Terrible smell, cheap plastic, broke within 2 days of jogging. Do not buy!", date="2026-11-12", reviewer_review_count=7),
            ],
            "daraz-audio-01": [
                ReviewItem(id="ra1", reviewer="Bilal S.", rating=5.0, text="Noise cancelling is unmatched. Karachi traffic noise completely disappears. Battery lasts forever.", date="2026-11-14", reviewer_review_count=21),
                ReviewItem(id="ra2", reviewer="Farhan T.", rating=5.0, text="Soundstage and mic quality during Zoom meetings are crisp. Very light on the head.", date="2026-11-02", reviewer_review_count=11),
                ReviewItem(id="ra3", reviewer="Saad N.", rating=4.5, text="High price in PKR due to import duties, but worth every rupee if you work in noisy areas.", date="2026-10-22", reviewer_review_count=9),
            ]
        }

    def _init_mock_history(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "daraz-shoe-01": [
                # Real sale: regular price was 5,200, dropped to 4,499
                {"date": "2026-09-01", "price_pkr": 5200.0, "is_sale": False},
                {"date": "2026-10-01", "price_pkr": 5200.0, "is_sale": False},
                {"date": "2026-11-01", "price_pkr": 4999.0, "is_sale": True},
                {"date": "2026-11-20", "price_pkr": 4499.0, "is_sale": True},
            ],
            "daraz-shoe-04": [
                # Fake sale: price was always 4,200, artificially jacked up original price to 8,999 to claim a 53% discount
                {"date": "2026-09-01", "price_pkr": 4200.0, "is_sale": False},
                {"date": "2026-10-01", "price_pkr": 4200.0, "is_sale": False},
                {"date": "2026-11-01", "price_pkr": 4200.0, "is_sale": False},
                {"date": "2026-11-20", "price_pkr": 4200.0, "is_sale": True, "fake_original": 8999.0},
            ]
        }
