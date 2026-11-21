import pytest
from app.adapters.daraz import DarazAdapter
from app.adapters.amazon import AmazonAdapter
from app.adapters.registry import StoreAdapterRegistry
from app.schemas.product import ProductFilter


@pytest.mark.asyncio
async def test_daraz_search():
    adapter = DarazAdapter()
    filters = ProductFilter(query="running shoes", max_price=5000.0, size="9")
    products = await adapter.search("running shoes", filters)

    assert len(products) > 0
    for p in products:
        assert p.store == "Daraz"
        assert p.price_pkr <= 5000.0
        assert "9" in [str(s) for s in p.specs.get("sizes", [])]
        assert p.delivery_fee_pkr >= 0.0


@pytest.mark.asyncio
async def test_amazon_adapter_pkr_conversion():
    adapter = AmazonAdapter()
    filters = ProductFilter(query="Sony")
    products = await adapter.search("Sony", filters)

    assert len(products) > 0
    p = products[0]
    assert p.store == "Amazon"
    assert p.currency == "PKR"
    # Check that price is in PKR (Sony XM5 is ~ $328 * 278.50 > Rs. 80,000)
    assert p.price_pkr > 80000.0
    assert p.delivery_fee_pkr > 0.0
    assert p.delivery_days >= 7  # International delivery


@pytest.mark.asyncio
async def test_registry_parallel_search():
    reg = StoreAdapterRegistry()
    products, warnings = await reg.search_all(query="Pegasus")

    stores = set(p.store for p in products)
    assert "Daraz" in stores
    assert "Amazon" in stores
    assert len(warnings) == 0
