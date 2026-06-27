let allProducts = [];

function renderProducts(products) {
    const container = document.getElementById("products-container");

    if (products.length === 0) {
        container.innerHTML = `<div class="col-12 text-center py-5 text-muted">
            هیچ محصولی در این دسته‌بندی یافت نشد.
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
                    <a href="product-detail.html?id=${p.id}" class="btn btn-antique w-100">مشاهده جزئیات</a>
                </div>
            </div>
        </div>
    `;
    }).join("");
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function loadProducts() {
    try {
        allProducts = await apiRequest("/products/");
        renderProducts(allProducts);
    } catch (err) {
        showAlert("alert-container", "خطا در بارگذاری محصولات: " + err.message);
        document.getElementById("products-container").innerHTML = "";
    }
}

// فیلتر دسته‌بندی
document.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        const category = btn.dataset.category;

        if (category === "all") {
            renderProducts(allProducts);
        } else {
            renderProducts(allProducts.filter(p => p.category === category));
        }
    });
});

loadProducts();
