requireAuth();

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

const orderId = getQueryParam("id");

async function loadOrder() {
    if (!orderId) {
        showAlert("alert-container", "شناسه سفارش مشخص نشده است.");
        document.getElementById("order-container").innerHTML = "";
        return;
    }

    try {
        const order = await apiRequest(`/orders/${orderId}`);
        renderOrder(order);
    } catch (err) {
        showAlert("alert-container", "خطا در بارگذاری سفارش: " + err.message);
        document.getElementById("order-container").innerHTML = "";
    }
}

function renderOrder(order) {
    const container = document.getElementById("order-container");

    const rows = order.items.map(item => `
        <tr>
            <td>${escapeHtml(item.product_title)}</td>
            <td>${formatPrice(item.unit_price)}</td>
            <td>${item.quantity}</td>
            <td class="fw-bold">${formatPrice(item.unit_price * item.quantity)}</td>
        </tr>
    `).join("");

    container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-4">
            <h3>سفارش #${order.id}</h3>
            <span class="badge ${orderStatusClass(order.status)} fs-6">${orderStatusLabel(order.status)}</span>
        </div>

        <p class="text-muted">تاریخ ثبت: ${new Date(order.created_at).toLocaleDateString("fa-IR")}</p>

        <div class="table-responsive mt-3">
            <table class="table align-middle bg-white">
                <thead>
                    <tr>
                        <th>محصول</th>
                        <th>قیمت واحد</th>
                        <th>تعداد</th>
                        <th>جمع</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>

        <div class="text-end mt-3">
            <h4>جمع کل: <span class="price-tag">${formatPrice(order.total_price)}</span></h4>
        </div>

        <a href="orders.html" class="btn btn-outline-secondary mt-3">بازگشت به لیست سفارش‌ها</a>
    `;
}

loadOrder();
