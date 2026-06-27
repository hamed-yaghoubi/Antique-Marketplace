requireAuth();

async function loadOrders() {
    try {
        const orders = await apiRequest("/orders/");
        renderOrders(orders);
    } catch (err) {
        showAlert("alert-container", "خطا در بارگذاری سفارش‌ها: " + err.message);
        document.getElementById("orders-container").innerHTML = "";
    }
}

function renderOrders(orders) {
    const container = document.getElementById("orders-container");

    if (orders.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5 text-muted">
                <p class="fs-5">شما هنوز هیچ سفارشی ثبت نکرده‌اید.</p>
                <a href="index.html" class="btn btn-antique">مشاهده محصولات</a>
            </div>`;
        return;
    }

    const rows = orders.map(order => `
        <tr>
            <td>#${order.id}</td>
            <td>${new Date(order.created_at).toLocaleDateString("fa-IR")}</td>
            <td><span class="badge ${orderStatusClass(order.status)}">${orderStatusLabel(order.status)}</span></td>
            <td class="fw-bold">${formatPrice(order.total_price)}</td>
            <td><a href="order-detail.html?id=${order.id}" class="btn btn-sm btn-outline-secondary">مشاهده</a></td>
        </tr>
    `).join("");

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table align-middle bg-white">
                <thead>
                    <tr>
                        <th>شماره سفارش</th>
                        <th>تاریخ</th>
                        <th>وضعیت</th>
                        <th>جمع کل</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;
}

loadOrders();
