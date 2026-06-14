requireAuth();

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function loadMyProducts() {
    try {
        const products = await apiRequest("/products/me");
        renderProducts(products);
    } catch (err) {
        showAlert("alert-container", "خطا در بارگذاری محصولات: " + err.message);
        document.getElementById("products-container").innerHTML = "";
    }
}

function renderProducts(products) {
    const container = document.getElementById("products-container");

    if (products.length === 0) {
        container.innerHTML = `<div class="col-12 text-center py-5 text-muted">
            شما هنوز هیچ محصولی ثبت نکرده‌اید.
        </div>`;
        return;
    }

    container.innerHTML = products.map(p => {
        const hasImage = p.images && p.images.length > 0;
        const imgHtml = hasImage
            ? `<img src="${API_BASE_URL}${p.images[0].image_url}" class="card-img-top" style="height: 180px; object-fit: cover; border-radius: 10px 10px 0 0;">`
            : `<div class="card-img-placeholder">🏺</div>`;

        return `
        <div class="col-sm-6 col-md-4 col-lg-3">
            <div class="card product-card">
                ${imgHtml}
                <div class="card-body">
                    <span class="badge badge-category mb-2">${categoryLabel(p.category)}</span>
                    <h5 class="card-title">${escapeHtml(p.title)}</h5>
                    <p class="price-tag mb-2">${formatPrice(p.price)}</p>
                    <div class="d-flex gap-2">
                        <a href="add-product.html?id=${p.id}" class="btn btn-sm btn-outline-secondary flex-fill">ویرایش</a>
                        <button class="btn btn-sm btn-outline-danger flex-fill delete-btn" data-id="${p.id}">حذف</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    }).join("");

    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", () => deleteProduct(btn.dataset.id));
    });
}

async function deleteProduct(id) {
    if (!confirm("آیا از حذف این محصول مطمئن هستید؟")) return;

    try {
        await apiRequest(`/products/${id}`, { method: "DELETE" });
        loadMyProducts();
    } catch (err) {
        showAlert("alert-container", "خطا در حذف محصول: " + err.message);
    }
}

loadMyProducts();
