// Khareed AI - Pakistani Smart Shopping Agent Frontend Controller

const SESSION_ID = "session-fahad-" + Math.floor(Math.random() * 10000);
let currentApprovalToken = null;

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initHeroSearch();
    initWidgetChat();
    initFullChat();
    initCartDrawer();
    initCheckoutFlow();
    initAlertsForm();
    initBudgetForm();

    // Initial data loaders
    loadDashboardMetrics();
    loadActiveAlerts();
    loadOrdersDashboard();
    loadReviewSummary("daraz-shoe-01");
});

// 1. NAVIGATION & TAB SWITCHING
function initNavigation() {
    const navButtons = document.querySelectorAll(".sidebar-nav .nav-item");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            if (tabId === "cart") {
                openCartDrawer();
                return;
            }
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Update active nav button
    document.querySelectorAll(".sidebar-nav .nav-item").forEach(btn => {
        if (btn.getAttribute("data-tab") === tabId) {
            btn.classList.add("active");
        } else if (btn.getAttribute("data-tab") !== "cart") {
            btn.classList.remove("active");
        }
    });

    // Update active pane
    document.querySelectorAll(".tab-viewport .tab-pane").forEach(pane => {
        pane.classList.remove("active");
    });

    const targetPane = document.getElementById("pane-" + tabId);
    if (targetPane) {
        targetPane.classList.add("active");
    }

    if (tabId === "orders") loadOrdersDashboard();
    if (tabId === "alerts") loadActiveAlerts();
    if (tabId === "budget") loadBudgetStatus();
}

// 2. HERO SEARCH & TOP SEARCH
function initHeroSearch() {
    const tryChip = document.getElementById("tryPromptChip");
    const heroInput = document.getElementById("heroSearchInput");
    const heroBtn = document.getElementById("heroSearchBtn");
    const topInput = document.getElementById("topSearchInput");
    const cameraBtn = document.getElementById("uploadCameraBtn");
    const heroUploadBtn = document.getElementById("heroUploadBtn");
    const closeResultsBtn = document.getElementById("closeResultsBtn");

    if (tryChip) {
        tryChip.addEventListener("click", () => {
            const query = tryChip.getAttribute("data-query");
            executeSearch(query);
        });
    }

    if (heroBtn) {
        heroBtn.addEventListener("click", () => {
            const q = heroInput.value.trim();
            if (q) executeSearch(q);
        });
    }

    if (heroInput) {
        heroInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                const q = heroInput.value.trim();
                if (q) executeSearch(q);
            }
        });
    }

    if (topInput) {
        topInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                const q = topInput.value.trim();
                if (q) executeSearch(q);
            }
        });
    }

    if (closeResultsBtn) {
        closeResultsBtn.addEventListener("click", () => {
            const sec = document.getElementById("inPageSearchResults");
            if (sec) sec.style.display = "none";
        });
    }

    if (cameraBtn) cameraBtn.addEventListener("click", openImageModal);
    if (heroUploadBtn) heroUploadBtn.addEventListener("click", openImageModal);

    const viewAllRecsBtn = document.getElementById("viewAllRecsBtn");
    if (viewAllRecsBtn) {
        viewAllRecsBtn.addEventListener("click", () => {
            executeSearch("all deals");
        });
    }
}

// IN-PAGE SEARCH: Does NOT redirect away! Shows all store options with links right here.
async function executeSearch(query) {
    const resultsSec = document.getElementById("inPageSearchResults");
    const titleEl = document.getElementById("searchResultsTitle");
    const listEl = document.getElementById("searchResultsList");

    if (!resultsSec || !listEl) return;

    // Keep user on the current overview page without redirecting
    switchTab("overview");
    resultsSec.style.display = "block";
    titleEl.textContent = `All Options for: "${query}"`;
    listEl.innerHTML = `<div style="text-align: center; padding: 24px; color: #64748b;">Khareed AI is searching Daraz & Amazon...</div>`;

    // Smooth scroll into view
    resultsSec.scrollIntoView({ behavior: "smooth", block: "nearest" });

    // Send query to AI assistant widget alongside the list
    sendQuickMessage(query);

    try {
        const res = await fetch(`/api/products/search?query=${encodeURIComponent(query)}`);
        if (!res.ok) throw new Error("Search failed");
        const data = await res.json();

        if (!data.products || data.products.length === 0) {
            listEl.innerHTML = `
                <div style="text-align: center; padding: 30px; color: #64748b;">
                    Koi product nahi mila "${query}" ke liye. Thora broader search try karein.
                </div>
            `;
            return;
        }

        // Render each matched product with PKR price breakdown, best pick, Add to cart AND direct store link
        listEl.innerHTML = data.products.map((p, idx) => {
            const isBestPick = idx === 0;
            const evalBadge = p.price_evaluation ? p.price_evaluation.badge : (p.price_check_badge || "Normal price");
            const totPrice = (p.total_price_pkr || (p.price_pkr + p.delivery_fee_pkr)).toLocaleString();

            return `
                <div class="in-page-result-row ${isBestPick ? 'best-pick-border' : ''}">
                    <div class="res-item-left">
                        <div class="res-item-thumb">
                            ${p.store === 'Amazon' ? '📦' : '🛍️'}
                        </div>
                        <div class="res-item-info">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
                                <span class="store-tag ${p.store.toLowerCase()}">${p.store}</span>
                                ${isBestPick ? `<span style="background: #dcfce7; color: #15803d; font-size: 10.5px; font-weight: 700; padding: 2px 7px; border-radius: 4px;">BEST PICK</span>` : ''}
                                <span style="font-size: 11px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #475569;">${evalBadge}</span>
                            </div>
                            <strong>${p.title}</strong>
                            <div class="res-meta-line">
                                <span>Seller: <strong>${p.seller}</strong> (Trust: ${p.seller_trust_score}/100)</span>
                                <span>•</span>
                                <span style="color: #f59e0b; font-weight: 600;">★ ${p.rating}</span>
                                <span>(${p.review_count} reviews)</span>
                                <span>•</span>
                                <span>Est. Delivery: ${p.delivery_days} days</span>
                            </div>
                        </div>
                    </div>

                    <div class="res-item-price-col">
                        <div class="res-total-price">Rs. ${totPrice}</div>
                        <div class="res-delivery-note">Item: Rs. ${p.price_pkr.toLocaleString()} + Del: Rs. ${p.delivery_fee_pkr.toLocaleString()}</div>
                    </div>

                    <div class="res-actions-col">
                        <button class="add-cart-btn" style="width: 100%; padding: 8px 12px;" onclick="quickAddToCart('${p.id}')">Add to Cart +</button>
                        <a href="${p.url}" target="_blank" rel="noopener noreferrer" class="visit-store-btn" title="Open external product page in a new tab">
                            <span>Open on ${p.store}</span>
                            <span>↗</span>
                        </a>
                    </div>
                </div>
            `;
        }).join("");

    } catch (err) {
        listEl.innerHTML = `<div style="color: #ef4444; padding: 20px; text-align: center;">Error loading search results: ${err.message}</div>`;
    }
}

// 3. AI SHOPPING ASSISTANT WIDGET
function initWidgetChat() {
    const form = document.getElementById("widgetChatForm");
    const input = document.getElementById("widgetChatInput");
    const history = document.getElementById("widgetChatHistory");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;

            appendWidgetMessage("user", text);
            input.value = "";
            input.disabled = true;

            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text, session_id: SESSION_ID })
                });
                const data = await res.json();
                appendWidgetMessage("assistant", data.response);
            } catch (err) {
                appendWidgetMessage("assistant", "Server connection error. Please try again.");
            } finally {
                input.disabled = false;
                input.focus();
            }
        });
    }
}

function appendWidgetMessage(role, text) {
    const history = document.getElementById("widgetChatHistory");
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    div.innerHTML = marked.parse(text);
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
}

function sendQuickMessage(text) {
    const input = document.getElementById("widgetChatInput");
    if (input) {
        input.value = text;
        document.getElementById("widgetChatForm").dispatchEvent(new Event("submit"));
    }
}

// 4. FULL CHAT COPILOT
function initFullChat() {
    const form = document.getElementById("mainChatForm");
    const input = document.getElementById("mainChatInput");
    const history = document.getElementById("mainChatHistory");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;

            appendMainChatMessage("user", text);
            input.value = "";
            input.disabled = true;

            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text, session_id: SESSION_ID })
                });
                const data = await res.json();
                appendMainChatMessage("assistant", data.response);

                // If alert set or cart modified, refresh stats
                loadDashboardMetrics();
            } catch (err) {
                appendMainChatMessage("assistant", "Khareed server error. Please verify backend is running.");
            } finally {
                input.disabled = false;
                input.focus();
            }
        });
    }
}

function appendMainChatMessage(role, text) {
    const history = document.getElementById("mainChatHistory");
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    div.innerHTML = marked.parse(text);
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
}

// 5. UNIFIED CART SYSTEM
function initCartDrawer() {
    const overlay = document.getElementById("cartOverlay");
    const closeBtn = document.getElementById("closeCartBtn");
    const applyCouponBtn = document.getElementById("applyCouponBtn");

    if (overlay) overlay.addEventListener("click", closeCartDrawer);
    if (closeBtn) closeBtn.addEventListener("click", closeCartDrawer);

    if (applyCouponBtn) {
        applyCouponBtn.addEventListener("click", () => {
            const code = document.getElementById("couponInput").value.trim();
            if (code) {
                alert(`Coupon '${code}' applied! You will see the discount at checkout.`);
                loadCart();
            }
        });
    }
}

function openCartDrawer() {
    document.getElementById("cartOverlay").classList.add("open");
    document.getElementById("cartDrawer").classList.add("open");
    loadCart();
}

function closeCartDrawer() {
    document.getElementById("cartOverlay").classList.remove("open");
    document.getElementById("cartDrawer").classList.remove("open");
}

async function quickAddToCart(productId) {
    try {
        const res = await fetch("/api/cart/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: SESSION_ID, product_id: productId, quantity: 1 })
        });
        if (res.ok) {
            const cart = await res.json();
            updateCartBadge(cart.total_items);
            openCartDrawer();
        }
    } catch (e) {
        alert("Cart error: " + e.message);
    }
}

async function loadCart() {
    const list = document.getElementById("cartItemsList");
    const totalsBox = document.getElementById("cartTotalsBox");

    try {
        const res = await fetch(`/api/cart?session_id=${SESSION_ID}`);
        if (!res.ok) return;
        const cart = await res.json();
        updateCartBadge(cart.total_items);

        if (!cart.items || cart.items.length === 0) {
            list.innerHTML = `<div style="text-align: center; padding: 40px 0; color: #94a3b8;">Aapka cart khali hai.<br>Explore deals & add items!</div>`;
            totalsBox.innerHTML = "";
            return;
        }

        list.innerHTML = cart.items.map(item => `
            <div class="cart-item-card">
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 13px; color: #0f172a;">${item.title}</div>
                    <div style="font-size: 11px; color: #64748b;">Store: ${item.store} • Trust: ${item.seller_trust_score}/100</div>
                    <div style="font-size: 11px; color: #059669; font-weight: 600; margin-top: 2px;">Rec: ${item.payment_recommendation}</div>
                    <div style="font-weight: 700; color: #059669; margin-top: 4px;">Rs. ${item.price_pkr.toLocaleString()} (Qty: ${item.quantity})</div>
                </div>
                <button onclick="removeCartItem('${item.product_id}')" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 12px;">Remove</button>
            </div>
        `).join("");

        totalsBox.innerHTML = `
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                <span>Items Subtotal:</span> <strong>Rs. ${cart.items_total_pkr.toLocaleString()}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                <span>Estimated Delivery:</span> <strong>Rs. ${cart.delivery_total_pkr.toLocaleString()}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 15px; font-weight: 700; color: #059669; margin-top: 8px; border-top: 1px solid #e2e8f0; padding-top: 6px;">
                <span>Grand Total:</span> <span>Rs. ${cart.grand_total_pkr.toLocaleString()}</span>
            </div>
        `;
    } catch (e) {
        console.error("Cart load error", e);
    }
}

async function removeCartItem(productId) {
    await fetch("/api/cart/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: SESSION_ID, product_id: productId })
    });
    loadCart();
}

function updateCartBadge(count) {
    const badge = document.getElementById("cartBadgeCount");
    if (badge) badge.textContent = count;
}

// 6. APPROVAL-GATED CHECKOUT FLOW
function initCheckoutFlow() {
    const initBtn = document.getElementById("initCheckoutBtn");
    const haanBtn = document.getElementById("approveOrderHaanBtn");
    const nahiBtn = document.getElementById("rejectOrderNahiBtn");

    if (initBtn) {
        initBtn.addEventListener("click", async () => {
            const coupon = document.getElementById("couponInput")?.value.trim() || null;
            try {
                // Step 1: Request Checkout Summary (Generates approval token)
                const res = await fetch("/api/cart/checkout", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: SESSION_ID,
                        payment_method: "COD",
                        delivery_address: "House 12, Main Boulevard, Gulberg, Lahore",
                        coupon_code: coupon
                    })
                });

                if (!res.ok) {
                    const err = await res.json();
                    alert(err.detail || "Checkout error");
                    return;
                }

                const summary = await res.json();
                currentApprovalToken = summary.approval_token;

                // Render modal summary
                const modalBody = document.getElementById("checkoutModalBody");
                modalBody.innerHTML = `
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-bottom: 14px;">
                        <div style="font-weight: 700; font-size: 14px; color: #0f172a; margin-bottom: 8px;">Order Details (${summary.items.length} items)</div>
                        ${summary.items.map(i => `<div style="font-size: 12px; display: flex; justify-content: space-between; margin-bottom: 4px;"><span>${i.title} (x${i.quantity})</span><strong>Rs. ${i.price_pkr.toLocaleString()}</strong></div>`).join("")}
                        <div style="border-top: 1px dashed #cbd5e1; margin: 8px 0;"></div>
                        <div style="font-size: 12px; display: flex; justify-content: space-between;"><span>Delivery Fee:</span><strong>Rs. ${summary.delivery_total_pkr.toLocaleString()}</strong></div>
                        ${summary.discount_pkr > 0 ? `<div style="font-size: 12px; color: #059669; display: flex; justify-content: space-between;"><span>Coupon Discount:</span><strong>-Rs. ${summary.discount_pkr.toLocaleString()}</strong></div>` : ''}
                        <div style="font-size: 15px; font-weight: 700; color: #059669; display: flex; justify-content: space-between; margin-top: 6px;"><span>Total to Pay:</span><strong>Rs. ${summary.final_total_pkr.toLocaleString()}</strong></div>
                    </div>
                    <div style="font-size: 12px; color: #475569; line-height: 1.5;">
                        <div>📍 <strong>Address:</strong> ${summary.delivery_address}</div>
                        <div>💳 <strong>Payment:</strong> ${summary.payment_method} (Cash on Delivery)</div>
                    </div>
                `;

                closeCartDrawer();
                document.getElementById("checkoutModal").classList.add("open");
            } catch (err) {
                alert("Checkout request failed: " + err.message);
            }
        });
    }

    // User confirms "Haan"
    if (haanBtn) {
        haanBtn.addEventListener("click", async () => {
            if (!currentApprovalToken) return;
            try {
                const res = await fetch("/api/cart/approve", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ approval_token: currentApprovalToken, approved: true })
                });
                const confirmation = await res.json();
                closeCheckoutModal();
                alert(`🎉 ${confirmation.message}\nOrder ID: ${confirmation.order_id}\nTracking: ${confirmation.tracking_id}`);
                loadCart();
                loadOrdersDashboard();
                loadDashboardMetrics();
            } catch (e) {
                alert("Order approval error: " + e.message);
            }
        });
    }

    // User rejects "Nahi"
    if (nahiBtn) {
        nahiBtn.addEventListener("click", () => {
            closeCheckoutModal();
            alert("Order cancel kar diya gaya hai. Koi amount charge nahi hui.");
        });
    }
}

function closeCheckoutModal() {
    document.getElementById("checkoutModal").classList.remove("open");
}

// 7. ORDERS DASHBOARD
async function loadOrdersDashboard() {
    const container = document.getElementById("ordersDashboardView");
    if (!container) return;

    try {
        const res = await fetch(`/api/orders?session_id=${SESSION_ID}`);
        if (!res.ok) return;
        const dashboard = await res.json();

        if (!dashboard.orders || dashboard.orders.length === 0) {
            container.innerHTML = `<p class="text-muted">No orders placed yet. Add items to cart and checkout to track live delivery.</p>`;
            return;
        }

        container.innerHTML = dashboard.orders.map(order => `
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong>Order #${order.order_id}</strong>
                    <span style="background: #dcfce7; color: #15803d; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px;">${order.status.toUpperCase()}</span>
                </div>
                <div style="font-size: 13px; color: #334155; margin-bottom: 6px;">Total: Rs. ${order.total_pkr.toLocaleString()} • ${order.payment_method}</div>
                <div style="font-size: 12px; color: #64748b; background: #f8fafc; padding: 10px; border-radius: 8px;">
                    <div>🚚 <strong>Courier:</strong> ${order.courier ? order.courier.courier_name : 'TCS'}</div>
                    <div>📦 <strong>Tracking ID:</strong> ${order.courier ? order.courier.tracking_id : 'N/A'}</div>
                    <div>📍 <strong>Status:</strong> ${order.courier ? order.courier.current_status : 'In transit'}</div>
                    <div>⏱️ <strong>Estimated Delivery:</strong> ${order.courier ? order.courier.estimated_delivery_date : '3 days'}</div>
                </div>
            </div>
        `).join("");
    } catch (e) {
        console.error("Orders fetch error", e);
    }
}

// 8. METRICS LOADER
async function loadDashboardMetrics() {
    try {
        const budgetRes = await fetch(`/api/budget/status?session_id=${SESSION_ID}`);
        if (budgetRes.ok) {
            const b = await budgetRes.json();
            const limitEl = document.getElementById("statBudgetLimit");
            const spentEl = document.getElementById("statBudgetSpent");
            const pctEl = document.getElementById("statBudgetPercent");
            const barEl = document.getElementById("statBudgetBar");

            if (limitEl && b.monthly_limit_pkr > 0) {
                limitEl.textContent = `Rs. ${b.monthly_limit_pkr.toLocaleString()}`;
                spentEl.textContent = `Rs. ${b.total_spent_pkr.toLocaleString()} spent`;
                pctEl.textContent = `${b.percentage_used}%`;
                barEl.style.width = `${Math.min(100, b.percentage_used)}%`;
            }
        }

        const alertsRes = await fetch("/api/alerts");
        if (alertsRes.ok) {
            const alerts = await alertsRes.json();
            const countEl = document.getElementById("statAlertsCount");
            if (countEl) countEl.textContent = alerts.length;
        }

        const cartRes = await fetch(`/api/cart?session_id=${SESSION_ID}`);
        if (cartRes.ok) {
            const c = await cartRes.json();
            updateCartBadge(c.total_items);
        }
    } catch (e) {
        console.error("Metrics load error", e);
    }
}

// 9. ALERTS FORM
function initAlertsForm() {
    const form = document.getElementById("createAlertForm");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const pid = document.getElementById("alertProductSelect").value;
            const target = parseFloat(document.getElementById("alertTargetPrice").value);
            const contact = document.getElementById("alertContact").value.trim();

            await fetch("/api/alerts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    product_id: pid,
                    product_title: pid,
                    store: "Daraz",
                    target_price: target,
                    user_contact: contact
                })
            });

            alert("Price alert successfully set!");
            loadActiveAlerts();
            loadDashboardMetrics();
        });
    }
}

async function loadActiveAlerts() {
    const container = document.getElementById("alertsTableView");
    const countBadge = document.getElementById("activeAlertCount");
    if (!container) return;

    try {
        const res = await fetch("/api/alerts");
        if (res.ok) {
            const alerts = await res.json();
            if (countBadge) countBadge.textContent = alerts.length;

            if (alerts.length === 0) {
                container.innerHTML = `<p class="text-muted">No active price drop alerts right now.</p>`;
                return;
            }

            container.innerHTML = alerts.map(a => `
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>${a.product_title}</strong>
                        <div style="font-size: 11px; color: #64748b;">Target: Rs. ${a.target_price ? a.target_price.toLocaleString() : 'N/A'} • Status: ${a.status}</div>
                    </div>
                    <span style="font-size: 11px; background: #ecfdf5; color: #059669; padding: 2px 6px; border-radius: 4px; font-weight: 600;">ACTIVE</span>
                </div>
            `).join("");
        }
    } catch (e) {
        console.error("Alerts fetch error", e);
    }
}

// 10. REVIEWS & TRUST ANALYZER
async function loadReviewSummary(productId) {
    const details = document.getElementById("reviewSummaryDetails");
    const widget = document.getElementById("sellerTrustScoreWidget");
    if (!details) return;

    try {
        const res = await fetch(`/api/products/${productId}/reviews`);
        if (!res.ok) return;
        const data = await res.json();

        widget.innerHTML = `
            <div style="text-align: center; padding: 16px; background: #f8fafc; border-radius: 12px; margin-top: 14px;">
                <div style="font-size: 26px; font-weight: 800; color: #059669;">94/100</div>
                <div style="font-size: 12px; font-weight: 600; color: #334155;">Verified Seller Trust</div>
                <span style="font-size: 10px; color: #059669;">Aala rating & zero fraud reports</span>
            </div>
        `;

        details.innerHTML = `
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px;">
                <h4 style="margin-bottom: 6px; font-size: 16px;">${data.product_title}</h4>
                <div style="font-size: 12px; color: #64748b; margin-bottom: 12px;">★ ${data.average_rating}/5.0 (${data.total_reviews} verified customer reviews)</div>
                
                <div style="margin-bottom: 12px;">
                    <strong style="color: #059669; font-size: 13px;">Top 3 Pros:</strong>
                    <ul style="margin: 4px 0 0 18px; font-size: 12.5px; color: #334155; line-height: 1.5;">
                        ${data.pros.map(p => `<li>${p}</li>`).join("")}
                    </ul>
                </div>

                <div style="margin-bottom: 12px;">
                    <strong style="color: #d97706; font-size: 13px;">Top 3 Cons:</strong>
                    <ul style="margin: 4px 0 0 18px; font-size: 12.5px; color: #334155; line-height: 1.5;">
                        ${data.cons.map(c => `<li>${c}</li>`).join("")}
                    </ul>
                </div>

                <div style="background: #f1f5f9; padding: 10px; border-radius: 8px; font-size: 12.5px; line-height: 1.4;">
                    <strong>Verdict:</strong> ${data.verdict}
                </div>

                ${data.is_suspicious ? `
                    <div style="margin-top: 10px; background: #fff1eb; border: 1px solid #ffd8cc; padding: 10px; border-radius: 8px; font-size: 12px; color: #c2410c;">
                        <strong>⚠️ Suspicious Reviews Flag:</strong> ${data.disclaimer} (${data.suspicious_flags.join(" • ")})
                    </div>
                ` : ''}
            </div>
        `;
    } catch (e) {
        console.error("Reviews load error", e);
    }
}

// 11. BUDGET MANAGEMENT
function initBudgetForm() {
    const form = document.getElementById("budgetSetForm");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const limit = parseFloat(document.getElementById("budgetLimitInput").value);
            await fetch("/api/budget/set", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: SESSION_ID, monthly_limit_pkr: limit })
            });
            alert("Monthly budget updated!");
            loadBudgetStatus();
            loadDashboardMetrics();
        });
    }
}

async function loadBudgetStatus() {
    const warnBox = document.getElementById("budgetWarningBox");
    try {
        const res = await fetch(`/api/budget/status?session_id=${SESSION_ID}`);
        if (!res.ok) return;
        const b = await res.json();
        if (warnBox) {
            if (b.warning) {
                warnBox.innerHTML = `<div style="background: #fffbeb; border: 1px solid #fde68a; color: #b45309; padding: 10px; border-radius: 8px; font-size: 12px; margin-top: 12px;">${b.warning}</div>`;
            } else {
                warnBox.innerHTML = `<div style="color: #059669; font-size: 12px; margin-top: 12px;">✅ You are well within your monthly budget.</div>`;
            }
        }
    } catch (e) {
        console.error("Budget status error", e);
    }
}

// 12. PRICE COMPARE DEMO
async function runCompareDemo() {
    const area = document.getElementById("compareResultsArea");
    area.innerHTML = `
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; text-align: left;">
            <thead>
                <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                    <th style="padding: 10px;">Product & Store</th>
                    <th style="padding: 10px;">Item Price</th>
                    <th style="padding: 10px;">Delivery Fee</th>
                    <th style="padding: 10px;">Total Price (PKR)</th>
                    <th style="padding: 10px;">Delivery Time</th>
                    <th style="padding: 10px;">Seller Trust</th>
                    <th style="padding: 10px;">Action</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #e2e8f0; background: #ecfdf5;">
                    <td style="padding: 10px;"><strong>Service Cheetah Running Shoes</strong><br><span style="color: #f85606; font-size: 11px;">Daraz Mall</span> • <span style="background: #dcfce7; color: #15803d; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 700;">BEST PICK</span></td>
                    <td style="padding: 10px;">Rs. 4,499</td>
                    <td style="padding: 10px;">Rs. 199 (TCS)</td>
                    <td style="padding: 10px; font-weight: 700; color: #059669;">Rs. 4,698</td>
                    <td style="padding: 10px;">3 days</td>
                    <td style="padding: 10px; font-weight: 600;">94/100</td>
                    <td style="padding: 10px;"><button class="add-cart-btn" onclick="quickAddToCart('daraz-shoe-01')">Add to Cart</button></td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px;"><strong>Nike Pegasus 40 Mens</strong><br><span style="color: #b45309; font-size: 11px;">Amazon Global (Converted from $99.95)</span></td>
                    <td style="padding: 10px;">Rs. 27,836</td>
                    <td style="padding: 10px;">Rs. 4,177 (Intl)</td>
                    <td style="padding: 10px; font-weight: 700;">Rs. 32,013</td>
                    <td style="padding: 10px;">10 days</td>
                    <td style="padding: 10px;">96/100</td>
                    <td style="padding: 10px;"><button class="add-cart-btn" onclick="quickAddToCart('amz-shoe-01')">Add to Cart</button></td>
                </tr>
            </tbody>
        </table>
    `;
}

// 13. IMAGE SEARCH MODAL
function openImageModal() {
    document.getElementById("imageSearchModal").classList.add("open");
}
function closeImageModal() {
    document.getElementById("imageSearchModal").classList.remove("open");
}
function simulateImageSearch() {
    closeImageModal();
    executeSearch("Service Cheetah running shoes");
}

// 14. IN-PAGE COMPARISON (STAYS IN APP, SHOWS ALL DETAILS + LINKS)
async function quickCompare(productId) {
    const modal = document.getElementById("compareModal");
    const body = document.getElementById("compareModalBody");
    const title = document.getElementById("compareModalTitle");

    if (!modal || !body) return;

    modal.classList.add("open");
    body.innerHTML = `<div style="text-align: center; padding: 40px; color: #64748b;">Loading store options & price history...</div>`;

    try {
        // Fetch current product
        const res = await fetch(`/api/products/${productId}`);
        if (!res.ok) throw new Error("Could not load product details");
        const prod = await res.json();

        // Also fetch comparable items across Daraz and Amazon
        const queryTerm = prod.title.split(" ")[0] || "shoes";
        const searchRes = await fetch(`/api/products/search?query=${encodeURIComponent(queryTerm)}`);
        const searchData = await searchRes.json();
        const compareItems = searchData.products || [prod];

        title.textContent = `Comparing "${prod.title.substring(0, 35)}..."`;

        body.innerHTML = `
            <div style="margin-bottom: 16px; font-size: 13px; color: #475569;">
                Comparing prices, delivery charges & trust across stores in Pakistan. You can add directly to cart or open the verified store page.
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px;">
                ${compareItems.slice(0, 3).map((item, i) => `
                    <div style="background: ${i === 0 ? '#f0fdf4' : '#ffffff'}; border: 1.5px solid ${i === 0 ? '#059669' : '#e2e8f0'}; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span class="store-tag ${item.store.toLowerCase()}">${item.store}</span>
                                ${i === 0 ? `<span style="background: #dcfce7; color: #15803d; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px;">BEST VALUE</span>` : ''}
                            </div>
                            <h4 style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 6px; line-height: 1.35;">${item.title}</h4>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 10px;">
                                <div>Seller: <strong>${item.seller}</strong></div>
                                <div>Trust Score: <strong>${item.seller_trust_score}/100</strong></div>
                                <div>Rating: <span style="color: #f59e0b;">★ ${item.rating}</span> (${item.review_count} reviews)</div>
                                <div>Est. Delivery: <strong>${item.delivery_days} days</strong> (Rs. ${item.delivery_fee_pkr})</div>
                                <div>Return Policy: <em>${item.return_policy}</em></div>
                            </div>
                        </div>

                        <div style="border-top: 1px solid #e2e8f0; padding-top: 12px; margin-top: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px;">
                                <span style="font-size: 11px; color: #64748b;">Total in PKR:</span>
                                <span style="font-size: 18px; font-weight: 800; color: #059669;">Rs. ${(item.total_price_pkr || (item.price_pkr + item.delivery_fee_pkr)).toLocaleString()}</span>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 6px;">
                                <button class="add-cart-btn" style="width: 100%; padding: 8px;" onclick="quickAddToCart('${item.id}')">Add to Cart +</button>
                                <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="visit-store-btn">
                                    <span>Open on ${item.store}</span>
                                    <span>↗</span>
                                </a>
                            </div>
                        </div>
                    </div>
                `).join("")}
            </div>
        `;
    } catch (e) {
        body.innerHTML = `<div style="color: #ef4444; padding: 20px;">Could not load comparison: ${e.message}</div>`;
    }
}

function closeCompareModal() {
    const modal = document.getElementById("compareModal");
    if (modal) modal.classList.remove("open");
}
