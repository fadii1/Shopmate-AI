import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_api_chat_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat", json={
            "message": "5000 se kam ke running shoes size 9"
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "Rs." in data["response"]
        assert data["language"] == "roman_urdu"


@pytest.mark.asyncio
async def test_api_search_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/products/search?query=shoes&max_price=5000")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        assert data["products"][0]["price_pkr"] <= 5000.0


@pytest.mark.asyncio
async def test_api_compare_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/products/compare", json=["daraz-shoe-01", "daraz-shoe-02"])
        assert response.status_code == 200
        data = response.json()
        assert "best_pick" in data
        assert data["total_options"] == 2


@pytest.mark.asyncio
async def test_api_alert_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create alert
        create_res = await client.post("/api/alerts", json={
            "product_id": "daraz-shoe-01",
            "product_title": "Service Cheetah",
            "store": "Daraz",
            "target_price": 4000.0,
            "user_contact": "test@user.pk"
        })
        assert create_res.status_code == 200
        alert_data = create_res.json()
        assert alert_data["status"] == "active"

        # Check alert trigger
        check_res = await client.post("/api/alerts/check?product_id=daraz-shoe-01&new_price=3900")
        assert check_res.status_code == 200
        check_data = check_res.json()
        assert check_data["triggered_count"] >= 1
