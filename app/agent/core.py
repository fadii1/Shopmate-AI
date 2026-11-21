import json
from typing import Dict, Any, List, Optional
from app.config import settings
from app.agent.prompt import KHAREED_SYSTEM_PROMPT
from app.agent.tools import TOOL_DEFINITIONS, AgentToolExecutor
from app.services.nlp_parser import nlp_parser
from app.schemas.agent import ChatRequest, ChatResponse, ToolCallRecord

# Try importing Anthropic
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class KhareedAgent:
    """Khareed Core Agent: Handles natural language understanding, tool dispatching,
    and Pakistani e-commerce response formatting across English, Urdu, and Roman Urdu.
    """

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key) if (self.api_key and HAS_ANTHROPIC) else None

    async def chat(self, request: ChatRequest) -> ChatResponse:
        user_msg = request.message.strip()
        parsed = nlp_parser.parse_query(user_msg)
        lang = request.user_language or parsed["language"]

        # Check if clarification is needed for missing critical parameter (e.g. shoes without size)
        if parsed["needs_clarification"]:
            return ChatResponse(
                response=parsed["clarification_question"],
                language=lang,
                tool_calls=[],
                session_id=request.session_id or "default-session",
                products=[]
            )

        # If live Claude API is configured and key is present, run Claude tool-calling loop
        if self.client:
            try:
                return await self._run_claude_loop(user_msg, lang, request.session_id)
            except Exception as e:
                # Graceful fallback to deterministic engine
                print(f"[KhareedAgent] Claude API error ({e}), switching to local engine.")

        # Deterministic / offline engine with full tool execution & persona formatting
        return await self._run_local_agent_loop(user_msg, parsed, lang, request.session_id)

    async def _run_local_agent_loop(
        self,
        user_msg: str,
        parsed: Dict[str, Any],
        lang: str,
        session_id: str
    ) -> ChatResponse:
        """Runs the deterministic agent loop with full tool calling and Khareed formatting."""
        tool_records: List[ToolCallRecord] = []
        user_lower = user_msg.lower()

        # 1. Check for Alert commands
        if any(w in user_lower for w in ["alert", "notify", "khabar", "price drop alert"]):
            # Find matching product
            search_res = await AgentToolExecutor.execute_tool("search_products", {"query": parsed["clean_query"]})
            products = search_res.get("products", [])
            if products:
                target_p = products[0]
                target_threshold = parsed.get("max_price") or round(target_p["price_pkr"] * 0.9)
                alert_res = await AgentToolExecutor.execute_tool("set_alert", {
                    "product_id": target_p["id"],
                    "threshold_pkr": target_threshold,
                    "alert_type": "price_drop",
                    "contact": "console"
                })
                tool_records.append(ToolCallRecord(
                    tool="set_alert",
                    parameters={"product_id": target_p["id"], "threshold_pkr": target_threshold},
                    output=alert_res
                ))

                if lang == "roman_urdu":
                    resp_text = (
                        f"Done! **{target_p['title']}** ke liye price-drop alert set kar diya hai.\n"
                        f"Jaise hi price Rs. {target_threshold:,.0f} ya is se kam hogi, main aapko foran aagah kar dunga!"
                    )
                elif lang == "urdu":
                    resp_text = (
                        f"آپ کا پرائس ڈراپ الرٹ **{target_p['title']}** کے لیے سیٹ ہو چکا ہے۔\n"
                        f"جیسے ہی قیمت Rs. {target_threshold:,.0f} یا اس سے کم ہوگی، آپ کو مطلع کر دیا جائے گا۔"
                    )
                else:
                    resp_text = (
                        f"Price-drop alert successfully set for **{target_p['title']}** at Rs. {target_threshold:,.0f}.\n"
                        f"I'll notify you as soon as the price drops!"
                    )

                return ChatResponse(
                    response=resp_text,
                    language=lang,
                    tool_calls=tool_records,
                    session_id=session_id,
                    products=[target_p]
                )

        # 2. Check for Review analysis command
        if any(w in user_lower for w in ["review", "reviews", "kaisay hain", "kesa hai", "trust", "pros", "cons"]):
            search_res = await AgentToolExecutor.execute_tool("search_products", {"query": parsed["clean_query"]})
            products = search_res.get("products", [])
            if products:
                target_p = products[0]
                review_res = await AgentToolExecutor.execute_tool("analyze_reviews", {"product_id": target_p["id"]})
                tool_records.append(ToolCallRecord(
                    tool="analyze_reviews",
                    parameters={"product_id": target_p["id"]},
                    output=review_res
                ))

                pros_str = " • ".join(review_res.get("pros", []))
                cons_str = " • ".join(review_res.get("cons", []))
                verdict = review_res.get("verdict", "")

                if lang == "roman_urdu":
                    resp_text = (
                        f"### Review Summary: **{target_p['title']}**\n\n"
                        f"⭐ **Average Rating:** {review_res.get('average_rating')}/5.0 ({review_res.get('total_reviews')} reviews)\n\n"
                        f"**Pros:**\n{pros_str}\n\n"
                        f"**Cons:**\n{cons_str}\n\n"
                        f"**Verdict:** {verdict}\n\n"
                    )
                    if review_res.get("is_suspicious"):
                        resp_text += f"> ⚠️ **Flag:** {review_res.get('disclaimer')} ({' • '.join(review_res.get('suspicious_flags', []))})\n\n"
                    resp_text += "Cart mein add karun? (Haan/Nahi)"
                else:
                    resp_text = (
                        f"### Review Summary: **{target_p['title']}**\n\n"
                        f"⭐ **Average Rating:** {review_res.get('average_rating')}/5.0 ({review_res.get('total_reviews')} reviews)\n\n"
                        f"**Pros:**\n{pros_str}\n\n"
                        f"**Cons:**\n{cons_str}\n\n"
                        f"**Verdict:** {verdict}\n\n"
                    )
                    if review_res.get("is_suspicious"):
                        resp_text += f"> ⚠️ **Note:** {review_res.get('disclaimer')} ({' • '.join(review_res.get('suspicious_flags', []))})\n\n"
                    resp_text += "Should I add this to your cart? (Yes/No)"

                return ChatResponse(
                    response=resp_text,
                    language=lang,
                    tool_calls=tool_records,
                    session_id=session_id,
                    products=[target_p]
                )

        # 3. Default: Product Search & Multi-store Comparison
        search_params = {
            "query": parsed["clean_query"],
            "max_price": parsed.get("max_price"),
            "min_price": parsed.get("min_price"),
            "brand": parsed.get("brand"),
            "size": parsed.get("size"),
            "color": parsed.get("color"),
            "stores": parsed.get("stores")
        }
        search_res = await AgentToolExecutor.execute_tool("search_products", search_params)
        tool_records.append(ToolCallRecord(
            tool="search_products",
            parameters=search_params,
            output=search_res
        ))

        products = search_res.get("products", [])

        if not products:
            if lang == "roman_urdu":
                no_res = "Maaf kijiye ga, aapki filters ke mutabiq koi product nahi mila. Thora price ya brand filter change kar ke check karein?"
            elif lang == "urdu":
                no_res = "معذرت، آپ کے فلٹرز کے مطابق کوئی پراڈکٹ نہیں ملا۔ براہ کرم کچھ فلٹرز تبدیل کریں۔"
            else:
                no_res = "Sorry, no products matched your exact filters. Try broadening the price range or keywords."
            return ChatResponse(
                response=no_res,
                language=lang,
                tool_calls=tool_records,
                session_id=session_id,
                products=[]
            )

        # Format items according to Section 5: RESPONSE FORMAT
        # Structure for each item:
        # **[Product name]**: Rs. X (incl. delivery Rs. Y)
        # Store: __ | Seller: __ (Trust: __/100) | Rating: __ (__ reviews)
        # Delivery: __ days | Payment: COD/Online
        # Pros: __ | Cons: __
        # Price check: [Real deal / Normal price / Fake sale]
        # Then end with a "Best pick" line and one clear next step ("Cart mein add karun?").

        formatted_items = []
        top_items = products[:4]

        for p in top_items:
            # Get reviews summary
            rev_res = await AgentToolExecutor.execute_tool("analyze_reviews", {"product_id": p["id"]})
            pros_short = ", ".join(rev_res.get("pros", [])[:2])
            cons_short = ", ".join(rev_res.get("cons", [])[:2])

            pm_str = "COD / Online" if "COD" in p.get("payment_methods", []) else "Online (Card)"
            tot_price = p["price_pkr"] + p["delivery_fee_pkr"]
            pcheck = p.get("price_check_badge", "Normal price")

            item_block = (
                f"**{p['title']}**: Rs. {tot_price:,.0f} (incl. delivery Rs. {p['delivery_fee_pkr']:,.0f})\n"
                f"Store: {p['store']} | Seller: {p['seller']} (Trust: {p['seller_trust_score']}/100) | Rating: {p['rating']} ({p['review_count']} reviews)\n"
                f"Delivery: {p['delivery_days']} days | Payment: {pm_str}\n"
                f"Pros: {pros_short} | Cons: {cons_short}\n"
                f"Price check: {pcheck} | [View on {p['store']}]({p['url']})"
            )
            formatted_items.append(item_block)

        # Determine Best Pick
        best_item = top_items[0]
        for item in top_items:
            # If trusted seller and real deal, prefer
            if "Real deal" in item.get("price_check_badge", "") and item["seller_trust_score"] >= 80:
                best_item = item
                break

        if lang == "roman_urdu":
            best_pick_text = f"**Best pick:** **{best_item['title']}** (Store: {best_item['store']}, Total: Rs. {best_item['price_pkr'] + best_item['delivery_fee_pkr']:,.0f}) — Aala seller trust aur behtareen value!"
            next_step = "Cart mein add karun? (Haan/Nahi)"
            header = f"Aapki query ke mutabiq top options ye hain:\n\n"
        elif lang == "urdu":
            best_pick_text = f"**بہترین انتخاب:** **{best_item['title']}** (اسٹور: {best_item['store']}, ٹوٹل: Rs. {best_item['price_pkr'] + best_item['delivery_fee_pkr']:,.0f})"
            next_step = "کیا میں اسے آپ کے کارٹ میں شامل کروں؟ (ہاں/نہیں)"
            header = "آپ کے لیے بہترین اختیارات:\n\n"
        else:
            best_pick_text = f"**Best pick:** **{best_item['title']}** (Store: {best_item['store']}, Total: Rs. {best_item['price_pkr'] + best_item['delivery_fee_pkr']:,.0f}) — Best balance of price, seller trust and delivery!"
            next_step = "Should I add this to your cart? (Yes/No)"
            header = f"Here are the top options matching your search:\n\n"

        full_response = header + "\n\n".join(formatted_items) + "\n\n" + best_pick_text + "\n\n" + next_step

        return ChatResponse(
            response=full_response,
            language=lang,
            tool_calls=tool_records,
            session_id=session_id,
            products=top_items
        )

    async def _run_claude_loop(self, user_msg: str, lang: str, session_id: str) -> ChatResponse:
        """Executes Claude 3.5 Sonnet tool use loop."""
        messages = [{"role": "user", "content": user_msg}]
        tool_records: List[ToolCallRecord] = []

        response = await self.client.messages.create(
            model=settings.claude_model,
            max_tokens=2048,
            system=KHAREED_SYSTEM_PROMPT,
            messages=messages,
            tools=TOOL_DEFINITIONS
        )

        # Check if Claude called tools
        while response.stop_reason == "tool_use":
            tool_calls = [c for c in response.content if c.type == "tool_use"]
            tool_outputs = []
            for tc in tool_calls:
                out = await AgentToolExecutor.execute_tool(tc.name, tc.input)
                tool_records.append(ToolCallRecord(tool=tc.name, parameters=tc.input, output=out))
                tool_outputs.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": json.dumps(out)
                })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_outputs})

            response = await self.client.messages.create(
                model=settings.claude_model,
                max_tokens=2048,
                system=KHAREED_SYSTEM_PROMPT,
                messages=messages,
                tools=TOOL_DEFINITIONS
            )

        final_text = "".join([c.text for c in response.content if hasattr(c, "text")])
        return ChatResponse(
            response=final_text,
            language=lang,
            tool_calls=tool_records,
            session_id=session_id
        )


khareed_agent = KhareedAgent()
