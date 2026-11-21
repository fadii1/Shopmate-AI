from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from app.adapters.registry import registry
from app.schemas.product import ProductFilter
from app.services.price_service import price_service
from app.services.review_service import review_service

router = APIRouter(prefix="/products", tags=["Products & Price Comparison"])


@router.get("/search")
async def search_products(
    query: str = Query(..., description="Search query"),
    min_price: Optional[float] = Query(None, description="Minimum price in PKR"),
    max_price: Optional[float] = Query(None, description="Maximum price in PKR"),
    brand: Optional[str] = Query(None, description="Brand name"),
    size: Optional[str] = Query(None, description="Product size"),
    color: Optional[str] = Query(None, description="Color"),
    stores: Optional[List[str]] = Query(None, description="Stores to search (e.g. daraz, amazon)"),
    sort_by: Optional[str] = Query("value", description="Sort by: value, price_asc, price_desc, rating, delivery")
):
    filters = ProductFilter(
        query=query,
        min_price=min_price,
        max_price=max_price,
        brand=brand,
        size=size,
        color=color,
        stores=stores,
        sort_by=sort_by
    )
    products, warnings = await registry.search_all(query=query, filters=filters, stores=stores)

    # Attach sale evaluation
    decorated = []
    for p in products:
        history = await registry.get_price_history(p.id)
        evaluation = price_service.evaluate_sale(p, history)
        p_data = p.model_dump()
        p_data["total_price_pkr"] = p.total_price_pkr
        p_data["price_evaluation"] = evaluation
        decorated.append(p_data)

    return {
        "count": len(decorated),
        "products": decorated,
        "warnings": warnings
    }


@router.get("/{product_id}")
async def get_product_details(product_id: str):
    product = await registry.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
    history = await registry.get_price_history(product_id)
    evaluation = price_service.evaluate_sale(product, history)
    data = product.model_dump()
    data["total_price_pkr"] = product.total_price_pkr
    data["price_evaluation"] = evaluation
    return data


@router.get("/{product_id}/reviews")
async def get_product_reviews(product_id: str):
    product = await registry.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
    reviews = await registry.get_reviews(product_id)
    summary = review_service.summarize_reviews(product.id, product.title, reviews)
    return summary


@router.get("/{product_id}/history")
async def get_price_history(product_id: str):
    product = await registry.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
    history = await registry.get_price_history(product_id)
    evaluation = price_service.evaluate_sale(product, history)
    return {
        "product_id": product_id,
        "current_price_pkr": product.price_pkr,
        "history": history,
        "evaluation": evaluation
    }


@router.post("/compare")
async def compare_products(product_ids: List[str]):
    products = []
    for pid in product_ids:
        p = await registry.get_product_by_id(pid)
        if p:
            products.append(p)
    if not products:
        raise HTTPException(status_code=400, detail="No valid products found to compare")
    comparison = price_service.compare_products(products)
    return comparison
