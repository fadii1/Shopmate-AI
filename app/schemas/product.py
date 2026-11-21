from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str = Field(..., description="Unique product identifier (e.g. 'daraz-101')")
    title: str = Field(..., description="Product title/name")
    price_pkr: float = Field(..., description="Base product price in Pakistani Rupees")
    original_price_pkr: Optional[float] = Field(None, description="Original price before discount if on sale")
    currency: str = Field("PKR", description="Currency code (always PKR for display)")
    store: str = Field(..., description="Origin store (e.g., 'Daraz', 'Amazon')")
    seller: str = Field(..., description="Seller or brand store name")
    seller_trust_score: int = Field(..., ge=0, le=100, description="Trust score out of 100")
    rating: float = Field(..., ge=0.0, le=5.0, description="Customer rating out of 5.0")
    review_count: int = Field(0, description="Total number of reviews")
    delivery_days: int = Field(..., description="Estimated delivery time in days")
    delivery_fee_pkr: float = Field(0.0, description="Delivery fee in PKR")
    payment_methods: List[str] = Field(
        default_factory=lambda: ["COD", "JazzCash", "Easypaisa", "Card"],
        description="Supported payment methods"
    )
    url: str = Field(..., description="Direct link to product on the store")
    image: Optional[str] = Field(None, description="Product image URL")
    in_stock: bool = Field(True, description="Stock status")
    specs: Dict[str, Any] = Field(default_factory=dict, description="Product specs (size, color, etc.)")
    return_policy: str = Field("7 days return policy", description="Store return policy")
    is_sponsored: bool = Field(False, description="Whether this is a sponsored result")

    @property
    def total_price_pkr(self) -> float:
        """Total customer cost including delivery fee."""
        return self.price_pkr + self.delivery_fee_pkr


class ProductFilter(BaseModel):
    query: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    min_rating: Optional[float] = None
    max_delivery_days: Optional[int] = None
    stores: Optional[List[str]] = None
    sort_by: Optional[str] = "value"  # value, price_asc, price_desc, rating, delivery
