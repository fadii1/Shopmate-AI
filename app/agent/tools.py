from typing import List, Dict, Any, Optional
from app.adapters.registry import registry
from app.services.price_service import price_service
from app.services.review_service import review_service
from app.services.alert_service import alert_service
from app.services.cart_service import cart_service
from app.services.order_service import order_service
from app.services.budget_service import budget_service
from app.services.security_service import security_service
from app.schemas.product import ProductFilter
from app.schemas.alert import AlertCreate

TOOL_DEFINITIONS = [
    {
        "name": "search_products",
        "description": "Search products across multiple Pakistani and international stores (Daraz, Amazon) in parallel with structured filters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords (e.g. 'running shoes', 'Samsung Galaxy A15')"},
                "min_price": {"type": "number", "description": "Minimum price in PKR"},
                "max_price": {"type": "number", "description": "Maximum price in PKR"},
                "brand": {"type": "string", "description": "Brand filter (e.g. 'Service', 'Nike', 'Samsung')"},
                "size": {"type": "string", "description": "Size filter (e.g. '9', '10', 'M', 'L')"},
                "color": {"type": "string", "description": "Color filter (e.g. 'Black', 'Blue')"},
                "stores": {"type": "array", "items": {"type": "string"}, "description": "Stores to search ('daraz', 'amazon')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "compare_prices",
        "description": "Compare products across stores (Daraz vs Amazon), evaluating base price, delivery fees, seller trust, and identifying the best pick.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_ids": {"type": "array", "items": {"type": "string"}, "description": "List of product IDs to compare"},
                "query": {"type": "string", "description": "Optional search query to fetch and compare products"}
            }
        }
    },
    {
        "name": "analyze_reviews",
        "description": "Analyze customer reviews for a product, generating 3 pros, 3 cons, one-line verdict, and flagging suspicious/fake review patterns.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Product identifier"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "get_price_history",
        "description": "Retrieve 30/90-day price history and check if a current sale is a 'Real deal', 'Normal price', or 'Fake sale'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Product identifier"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "set_alert",
        "description": "Set a price-drop or back-in-stock alert for a product.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Product ID"},
                "alert_type": {"type": "string", "enum": ["price_drop", "back_in_stock"], "description": "Alert type"},
                "threshold_pkr": {"type": "number", "description": "Target price threshold in PKR for price drop alert"},
                "contact": {"type": "string", "description": "User notification destination (console, email, or phone)"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "cart_add",
        "description": "Add an item to the unified multi-store cart.",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "product_id": {"type": "string"},
                "quantity": {"type": "integer", "default": 1}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "cart_view",
        "description": "View current unified cart items, totals in PKR, and delivery fees.",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"}
            }
        }
    },
    {
        "name": "request_checkout_approval",
        "description": "Generate an approval-gated checkout summary. Does NOT complete order without user confirmation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "payment_method": {"type": "string", "default": "COD"},
                "delivery_address": {"type": "string", "default": "Lahore, Pakistan"},
                "coupon_code": {"type": "string"}
            }
        }
    },
    {
        "name": "place_order",
        "description": "Confirm and place the order using a validated approval token.",
        "input_schema": {
            "type": "object",
            "properties": {
                "approval_token": {"type": "string"},
                "approved": {"type": "boolean"}
            },
            "required": ["approval_token", "approved"]
        }
    },
    {
        "name": "track_order",
        "description": "Track courier delivery (TCS, Leopard, Trax) with live ETA and checkpoints.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "budget_status",
        "description": "Check current monthly spending vs budget limit with 80% warnings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"}
            }
        }
    },
    {
        "name": "check_link_safety",
        "description": "Check if a shopping URL is safe or a scam/phishing lookalike domain.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            },
            "required": ["url"]
        }
    }
]


class AgentToolExecutor:
    """Dispatches tool calls to underlying services and adapters."""

    @staticmethod
    async def execute_tool(name: str, args: Dict[str, Any]) -> Any:
        if name == "search_products":
            filters = ProductFilter(
                query=args.get("query", ""),
                min_price=args.get("min_price"),
                max_price=args.get("max_price"),
                brand=args.get("brand"),
                size=str(args.get("size")) if args.get("size") else None,
                color=args.get("color"),
                stores=args.get("stores")
            )
            products, warnings = await registry.search_all(
                query=filters.query,
                filters=filters,
                stores=args.get("stores")
            )
            product_cards = []
            for p in products:
                history = await registry.get_price_history(p.id)
                price_check = price_service.evaluate_sale(p, history)
                p_dict = p.model_dump()
                p_dict["price_check"] = price_check["verdict"]
                p_dict["price_check_badge"] = price_check.get("badge", "Normal price")
                product_cards.append(p_dict)

            return {
                "products": product_cards,
                "count": len(product_cards),
                "warnings": warnings
            }

        elif name == "compare_prices":
            product_ids = args.get("product_ids", [])
            query = args.get("query")
            products = []
            if product_ids:
                for pid in product_ids:
                    p = await registry.get_product_by_id(pid)
                    if p:
                        products.append(p)
            elif query:
                prods, _ = await registry.search_all(query=query)
                products = prods

            return price_service.compare_products(products)

        elif name == "analyze_reviews":
            pid = args.get("product_id")
            product = await registry.get_product_by_id(pid)
            title = product.title if product else f"Product {pid}"
            reviews = await registry.get_reviews(pid)
            summary = review_service.summarize_reviews(pid, title, reviews)
            return summary.model_dump()

        elif name == "get_price_history":
            pid = args.get("product_id")
            product = await registry.get_product_by_id(pid)
            if not product:
                return {"error": f"Product {pid} not found."}
            history = await registry.get_price_history(pid)
            sale_eval = price_service.evaluate_sale(product, history)
            return {
                "product_id": pid,
                "current_price_pkr": product.price_pkr,
                "history": history,
                "analysis": sale_eval
            }

        elif name == "set_alert":
            pid = args.get("product_id")
            product = await registry.get_product_by_id(pid)
            if not product:
                return {"error": f"Product {pid} not found."}

            alert_in = AlertCreate(
                product_id=pid,
                product_title=product.title,
                store=product.store,
                alert_type=args.get("alert_type", "price_drop"),
                target_price=args.get("threshold_pkr"),
                user_contact=args.get("contact", "console")
            )
            created = alert_service.create_alert(alert_in, current_price=product.price_pkr)
            return created.model_dump()

        elif name == "cart_add":
            sid = args.get("session_id", "default-session")
            pid = args.get("product_id")
            qty = args.get("quantity", 1)
            cart = await cart_service.add_item(sid, pid, qty)
            return cart.model_dump()

        elif name == "cart_view":
            sid = args.get("session_id", "default-session")
            return cart_service.get_cart(sid).model_dump()

        elif name == "request_checkout_approval":
            sid = args.get("session_id", "default-session")
            pm = args.get("payment_method", "COD")
            addr = args.get("delivery_address", "Lahore, Pakistan")
            coupon = args.get("coupon_code")
            summary = cart_service.request_checkout(sid, pm, addr, coupon)
            return summary.model_dump()

        elif name == "place_order":
            token = args.get("approval_token")
            approved = args.get("approved", True)
            confirmation = cart_service.approve_and_place_order(token, approved)
            return confirmation.model_dump()

        elif name == "track_order":
            oid = args.get("order_id")
            info = order_service.track_order(oid)
            return info.model_dump()

        elif name == "budget_status":
            sid = args.get("session_id", "default-session")
            return budget_service.get_status(sid).model_dump()

        elif name == "check_link_safety":
            url = args.get("url", "")
            return security_service.check_link_safety(url)

        return {"error": f"Unknown tool: {name}"}
