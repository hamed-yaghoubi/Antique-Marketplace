requireAuth();

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function loadCart() {
    try {
        const cart = await apiRequest("/cart/");
        renderCart(cart);
    } catch (err) {
        showAlert("alert-container", "خطا در بارگذاری سبد خرید: " + err.message);
        document.getElementById("cart-container").innerHTML = "";
    }
}

function renderCart(cart) {
    const container = document.getElementById("cart-container");

    if (!cart.items || cart.items.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5 text-muted">
                <p class="fs-5">سبد خرید شما خالی است.</p>
                <a href="index.html" class="btn btn-antique">مشاهده محصولات</a>
            </div>`;
        return;
    }

    const rows = cart.items.map(item => {
        const hasImage = item.product.images && item.product.images.length > 0;
        const imgHtml = hasImage
            ? `<img src="${API_BASE_URL}${item.product.images[0].image_url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 6px;" class="me-2">`
            : `<span style="font-size: 1.8rem;" class="me-2">🏺</span>`;

        return `
        <tr data-item-id="${item.id}">
            <td>
                <div class="d-flex align-items-center">
                    ${imgHtml}
                    <div>
                        <strong>${escapeHtml(item.product.title)}</strong><br>
                        <span class="badge badge-category">${categoryLabel(item.product.category)}</span>
                    </div>
                </div>
            </td>
            <td>${formatPrice(item.product.price)}</td>
            <td style="width: 130px;">
                <input type="number" class="form-control form-control-sm qty-input" value="${item.quantity}" min="1">
            </td>
            <td class="fw-bold">${formatPrice(item.product.price * item.quantity)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary update-btn">به‌روزرسانی</button>
                <button class="btn btn-sm btn-outline-danger remove-btn">حذف</button>
            </td>
        </tr>
    `;
    }).join("");

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table align-middle bg-white">
                <thead>
                    <tr>
                        <th>محصول</th>
                        <th>قیمت واحد</th>
                        <th>تعداد</th>
                        <th>جمع</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>

        <div class="d-flex justify-content-between align-items-center mt-4 flex-wrap gap-2">
            <button class="btn btn-outline-danger" id="clear-cart-btn">خالی کردن سبد خرید</button>
            <div class="text-end">
                <h4>جمع کل: <span class="price-tag">${formatPrice(cart.total_price)}</span></h4>
                <button class="btn btn-antique btn-lg mt-2" id="checkout-btn">ثبت سفارش</button>
            </div>
        </div>
    `;

    attachEventListeners();
}

function attachEventListeners() {
    document.querySelectorAll(".update-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const row = e.target.closest("tr");
            const itemId = row.dataset.itemId;
            const qty = parseInt(row.querySelector(".qty-input").value, 10);
            updateCartItem(itemId, qty);
        });
    });

    document.querySelectorAll(".remove-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const row = e.target.closest("tr");
            removeCartItem(row.dataset.itemId);
        });
    });

    document.getElementById("clear-cart-btn")?.addEventListener("click", clearCart);
    document.getElementById("checkout-btn")?.addEventListener("click", checkout);
}

async function updateCartItem(itemId, quantity) {
    if (!quantity || quantity < 1) {
        showAlert("alert-container", "تعداد وارد شده معتبر نیست.");
        return;
    }

    try {
        await apiRequest(`/cart/items/${itemId}`, {
            method: "PATCH",
            body: JSON.stringify({ quantity })
        });
        loadCart();
    } catch (err) {
        showAlert("alert-container", "خطا در به‌روزرسانی: " + err.message);
    }
}

async function removeCartItem(itemId) {
    try {
        await apiRequest(`/cart/items/${itemId}`, { method: "DELETE" });
        loadCart();
    } catch (err) {
        showAlert("alert-container", "خطا در حذف آیتم: " + err.message);
    }
}

async function clearCart() {
    if (!confirm("آیا از خالی کردن سبد خرید مطمئن هستید؟")) return;

    try {
        await apiRequest("/cart/", { method: "DELETE" });
        loadCart();
    } catch (err) {
        showAlert("alert-container", "خطا در خالی کردن سبد خرید: " + err.message);
    }
}

async function checkout() {
    if (!confirm("آیا از ثبت سفارش مطمئن هستید؟")) return;

    const btn = document.getElementById("checkout-btn");
    btn.disabled = true;
    btn.textContent = "در حال ثبت...";

    try {
        const order = await apiRequest("/orders/", { method: "POST" });
        window.location.href = `order-detail.html?id=${order.id}`;
    } catch (err) {
        showAlert("alert-container", "خطا در ثبت سفارش: " + err.message);
        btn.disabled = false;
        btn.textContent = "ثبت سفارش";
    }
}

loadCart();
