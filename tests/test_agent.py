import pytest
from app.agent.core import khareed_agent
from app.schemas.agent import ChatRequest


@pytest.mark.asyncio
async def test_agent_clarification_on_missing_size():
    req = ChatRequest(message="mujhe running shoes chahiye")
    res = await khareed_agent.chat(req)

    assert "shoe size" in res.response.lower() or "size" in res.response.lower()
    assert res.products == []


@pytest.mark.asyncio
async def test_agent_roman_urdu_search_flow():
    req = ChatRequest(message="5000 se kam ke running shoes size 9")
    res = await khareed_agent.chat(req)

    assert res.language == "roman_urdu"
    assert "Rs." in res.response
    assert "Best pick:" in res.response
    assert "Cart mein add karun?" in res.response
    assert len(res.tool_calls) > 0
    assert res.tool_calls[0].tool == "search_products"


@pytest.mark.asyncio
async def test_agent_set_alert_flow():
    req = ChatRequest(message="Service Cheetah shoes pe price drop alert lagao 4000 tak")
    res = await khareed_agent.chat(req)

    assert "alert" in res.response.lower()
    assert any(tc.tool == "set_alert" for tc in res.tool_calls)
