import asyncio
from typing import List, Dict, Optional, Tuple
from app.adapters.base import BaseStoreAdapter
from app.adapters.daraz import DarazAdapter
from app.adapters.amazon import AmazonAdapter
from app.schemas.product import Product, ProductFilter
from app.schemas.reviews import ReviewItem


class StoreAdapterRegistry:
    """Orchestrates multi-store queries in parallel with fault-isolation and fallback handling."""

    def __init__(self):
        self._adapters: Dict[str, BaseStoreAdapter] = {
            "daraz": DarazAdapter(),
            "amazon": AmazonAdapter(),
        }

    def register(self, key: str, adapter: BaseStoreAdapter):
        self._adapters[key.lower()] = adapter

    def get_adapter(self, key: str) -> Optional[BaseStoreAdapter]:
        return self._adapters.get(key.lower())

    @property
    def available_stores(self) -> List[str]:
        return [adapter.store_name for adapter in self._adapters.values()]

    async def search_all(
        self,
        query: str,
        filters: Optional[ProductFilter] = None,
        stores: Optional[List[str]] = None
    ) -> Tuple[List[Product], List[str]]:
        """Search across target stores in parallel.
        
        Returns:
            Tuple of (merged_and_ranked_products, errors_or_warnings)
        """
        target_stores = stores or list(self._adapters.keys())
        target_adapters = []
        for s in target_stores:
            adapter = self.get_adapter(s)
            if adapter:
                target_adapters.append(adapter)

        if not target_adapters:
            return [], [f"No valid store adapter found for {target_stores}"]

        # Execute searches in parallel with error isolation
        async def safe_search(adapter: BaseStoreAdapter) -> Tuple[str, List[Product], Optional[str]]:
            try:
                prods = await adapter.search(query, filters)
                return adapter.store_name, prods, None
            except Exception as e:
                return adapter.store_name, [], f"Store '{adapter.store_name}' error: {str(e)}"

        tasks = [safe_search(a) for a in target_adapters]
        results = await asyncio.gather(*tasks)

        all_products: List[Product] = []
        warnings: List[str] = []

        for store_name, products, error in results:
            if error:
                warnings.append(error)
            else:
                all_products.extend(products)

        # Merge and rank by user value: (rating * 20 + trust) / (cost_factor)
        all_products.sort(
            key=lambda x: (x.rating * 20.0 + x.seller_trust_score) / (x.total_price_pkr / 5000.0 + 1.0),
            reverse=True
        )

        return all_products, warnings

    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        for adapter in self._adapters.values():
            prod = await adapter.get_product(product_id)
            if prod:
                return prod
        return None

    async def get_reviews(self, product_id: str) -> List[ReviewItem]:
        for adapter in self._adapters.values():
            reviews = await adapter.get_reviews(product_id)
            if reviews:
                return reviews
        return []

    async def get_price_history(self, product_id: str) -> List[Dict]:
        for adapter in self._adapters.values():
            history = await adapter.get_price_history(product_id)
            if history:
                return history
        return []


registry = StoreAdapterRegistry()
