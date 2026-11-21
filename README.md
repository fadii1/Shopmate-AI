# Khareed AI (خرید) 🇵🇰 - Smart Online Shopping Agent for Pakistan

**Khareed AI** is a localized, full-stack agentic online shopping copilot engineered specifically for Pakistani shoppers. It connects multiple e-commerce destinations (**Daraz.pk, Amazon Global, PriceOye, and Telemart**) into a single, cohesive, clutter-free dashboard and conversational agent.

Khareed guarantees **zero-risk checkout**: it acts strictly on your behalf and **never completes any financial transaction or order without explicit, unambiguous user confirmation** (`"Confirm karun? (Haan/Nahi)"`).

---

## 🎨 Clean Dashboard Experience (Aligned with UI Reference)

- **Dark Emerald / Navy Sidebar**:
  - `Overview` — Unified summary dashboard
  - `Discover` — AI shopping copilot with Roman Urdu, Urdu script, and English parsing
  - `Price Compare` — Side-by-side comparative table with delivery fees & return policies
  - `Price Alerts` — Active price drop and stock alerts manager
  - `Reviews & Trust` — 3 pros, 3 cons, one-line verdict, and fake review heuristic scanner
  - `My Cart` — Unified multi-store cart with coupon support & approval-gated checkout
  - `Orders` — Live tracking dashboard (TCS, Leopard, Trax courier checkpoints)
  - `Budget` — Monthly budget tracking, 80% limit warnings, category reports, priority wishlist
  - `🇵🇰 Designed for Pakistan` badge with PKR normalization note
- **Top Greeting & Header**:
  - `"Good morning, Fahad 👋"`
  - Global natural language search with visual image search upload
  - Live notification bell & profile avatar
- **Hero Banner**:
  - `"Your shopping, made smarter"`
  - One-click prompt chip: `Try: "5000 se kam ke running shoes size 9"`
  - "Upload Image" visual search modal
- **4 Live Metric Stat Cards**:
  1. **Monthly Budget**: `Rs. 25,000` (live progress bar showing `57%` spent)
  2. **Saved this Month**: `Rs. 4,800` (savings calculated from real deals)
  3. **Active Price Alerts**: `3` (monitoring price drops)
  4. **Orders in Progress**: `2` (live courier parcels in transit)
- **Product Showcase & AI Copilot**:
  - **Recommended for you**: Cards tagged with `Best Value` and `Top Rated`, showing PKR prices, discounts, ratings, store badges, and direct `Add +` to cart.
  - **Price drop watch**: Live list of price reductions with percentage drops (`↓ 22%`, `↓ 25%`).
  - **AI Shopping Assistant Widget**: Interactive, instant conversational assistant supporting Roman Urdu (`"Best value options dikhao"`), Urdu, or English.
- **Security & Trust Strip**:
  - `Seller trust checked`: Verified seller scores (0-100)
  - `Track Your Orders`: Courier live tracking (TCS, Leopard, Trax)
  - `Flexible Payments`: Advice on COD vs. JazzCash vs. Easypaisa vs. Card

---

## ⚡ Core Rules & Pakistani Localization

1. **Currency**: All prices are displayed in **PKR (Rs.)** including courier delivery charges. Foreign prices from Amazon US are converted transparently at `$1 = Rs. 278.50` with rate and date cited.
2. **Payment Advice**: COD is automatically recommended for high-value items (`> Rs. 15,000`) or sellers with trust scores below 70.
3. **Hard Approval Checkout Gate**: The `approve_and_place_order` API endpoint strictly requires a cryptographically validated `approval_token`. It is programmatically impossible to place an order without the user clicking `"Haan (Confirm Order)"`.
4. **No Card Data Storage**: Card numbers, CVVs, and banking PINs are never requested or stored.

---

## 🧪 Comprehensive Test Suite (43 Tests Passed)

All 43 tests pass with 0 errors:

| Test Suite | Tests | Features Tested |
| :--- | :---: | :--- |
| `tests/test_adapters.py` | 3 | DarazAdapter, AmazonAdapter USD->PKR FX conversion, parallel multi-store search |
| `tests/test_agent.py` | 3 | Roman Urdu query resolution, size clarification, price-drop alert flow |
| `tests/test_alerts.py` | 1 | Price-drop threshold checks and notification dispatch |
| `tests/test_api.py` | 4 | Chat endpoint, search endpoint, price compare, alert trigger API |
| `tests/test_budget.py` | 6 | Budget limits, 80% threshold warnings, purchase blocking, category reports, priority wishlist |
| `tests/test_cart.py` | 5 | Multi-store cart, COD recommendation, approval-gated checkout token validation |
| `tests/test_nlp_parser.py` | 6 | Roman Urdu detection, Urdu script detection, English detection, `k` notation (`60k`), shoe size checks |
| `tests/test_orders.py` | 5 | Order creation, dashboard listing, TCS courier tracking, Leopard tracking, delay detection |
| `tests/test_price_comparison.py` | 3 | Cross-store best pick scoring, Real deal detection (>10% drop), Fake sale detection |
| `tests/test_review_summary.py` | 2 | 3 pros, 3 cons, verdict extraction, burst 5-star fake review heuristic detection |
| `tests/test_security.py` | 5 | Lookalike domain / scam URL detection, raw IP warning, 0-100 seller trust scoring, gift suggestions |
| **Total** | **43** | **All 43 Passed ✅** |

---

## 🚀 Running Khareed Locally

```bash
# 1. Activate virtual environment
.\.venv\Scripts\activate

# 2. Run test suite
pytest

# 3. Start Khareed web server
uvicorn app.main:app --reload --port 8000
```

Open **`http://localhost:8000`** in your browser to explore the dashboard.
