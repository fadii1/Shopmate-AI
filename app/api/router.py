from fastapi import APIRouter
from app.api.routes_chat import router as chat_router
from app.api.routes_products import router as products_router
from app.api.routes_alerts import router as alerts_router
from app.api.routes_cart import router as cart_router
from app.api.routes_orders import router as orders_router
from app.api.routes_budget import router as budget_router
from app.api.routes_extra import router as extra_router

api_router = APIRouter(prefix="/api")

api_router.include_router(chat_router)
api_router.include_router(products_router)
api_router.include_router(alerts_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(budget_router)
api_router.include_router(extra_router)
