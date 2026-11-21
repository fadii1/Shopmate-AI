from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.schemas.product import Product, ProductFilter
from app.schemas.reviews import ReviewItem


class BaseStoreAdapter(ABC):
    """Abstract base adapter for online stores (Daraz, Amazon, etc.)"""

    @property
    @abstractmethod
    def store_name(self) -> str:
        """Name of the store (e.g., 'Daraz', 'Amazon')"""
        pass

    @abstractmethod
    async def search(self, query: str, filters: Optional[ProductFilter] = None) -> List[Product]:
        """Search products given a query and structured filters."""
        pass

    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Retrieve single product by ID."""
        pass

    @abstractmethod
    async def get_reviews(self, product_id: str) -> List[ReviewItem]:
        """Retrieve customer reviews for a product."""
        pass

    @abstractmethod
    async def get_price_history(self, product_id: str) -> List[Dict[str, Any]]:
        """Retrieve 30/90-day price history snapshots for a product."""
        pass
