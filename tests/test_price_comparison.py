import pytest
from app.services.price_service import price_service
from app.schemas.product import Product


def test_price_comparison_best_pick():
    p1 = Product(
        id="p1",
        title="Nike Pegasus Option A",
        price_pkr=28000.0,
        currency="PKR",
        store="Daraz",
        seller="Daraz Mall Flagship",
        seller_trust_score=95,
        rating=4.8,
        delivery_days=3,
        delivery_fee_pkr=200.0,
        url="https://daraz.pk/p1"
    )
    p2 = Product(
        id="p2",
        title="Nike Pegasus Option B",
        price_pkr=35000.0,
        currency="PKR",
        store="Amazon",
        seller="Amazon Global",
        seller_trust_score=96,
        rating=4.7,
        delivery_days=10,
        delivery_fee_pkr=4000.0,
        url="https://amazon.com/p2"
    )

    comparison = price_service.compare_products([p1, p2])
    assert comparison["best_pick"]["product"].id == "p1"
    assert "Sab se behtareen price" in comparison["best_pick"]["reason"]


def test_real_deal_detection():
    product = Product(
        id="deal-01",
        title="Super Deal Shoes",
        price_pkr=4500.0,
        original_price_pkr=5500.0,
        currency="PKR",
        store="Daraz",
        seller="Official Store",
        seller_trust_score=90,
        rating=4.5,
        delivery_days=3,
        delivery_fee_pkr=200.0,
        url="https://daraz.pk/deal"
    )
    history = [
        {"price_pkr": 5500.0, "is_sale": False},
        {"price_pkr": 5400.0, "is_sale": False},
        {"price_pkr": 5500.0, "is_sale": False},
    ]

    result = price_service.evaluate_sale(product, history)
    assert result["verdict"] == "Real deal"
    assert result["savings_pkr"] > 0


def test_fake_sale_detection():
    product = Product(
        id="fake-01",
        title="Fake Sale Sneaker",
        price_pkr=4200.0,
        original_price_pkr=8999.0,  # Jacked up
        currency="PKR",
        store="Daraz",
        seller="Shady Seller",
        seller_trust_score=40,
        rating=3.0,
        delivery_days=5,
        delivery_fee_pkr=200.0,
        url="https://daraz.pk/fake"
    )
    history = [
        {"price_pkr": 4200.0, "fake_original": 8999.0, "is_sale": True},
        {"price_pkr": 4200.0, "is_sale": False},
    ]

    result = price_service.evaluate_sale(product, history)
    assert result["verdict"] == "Fake sale"
    assert "Original price ko barha kar" in result["details"]
