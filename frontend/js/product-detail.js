function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

const productId = getQueryParam("id");

async function loadProduct() {
    if (!productId) {
        showAlert("alert-container", "شناسه محصول مشخص نشده است.");
        document.getElementById("product-container").innerHTML = "";
        return;
    }

    try {
        const product = await apiRequest(`/products/${productId}`);
        renderProduct(product);
    } catch (err) {
        showAlert("alert-container", "خطا در بارگذاری محصول: " + err.message);
        document.getElementById("product-container").innerHTML = "";
    }
}

function renderProduct(product) {
    const container = document.getElementById("product-container");

    const stockBadge = product.quantity > 0
        ? `<span class="badge bg-success">موجود (${product.quantity} عدد)</span>`
        : `<span class="badge bg-danger">ناموجود</span>`;

    const images = product.images || [];

    let imageSection;
    if (images.length === 0) {
        imageSection = `<div class="card-img-placeholder" style="height: 350px; border-radius: 12px; font-size: 5rem;">🏺</div>`;
    } else {
        const mainImg = `<img id="main-product-image" src="${API_BASE_URL}${images[0].image_url}" class="img-fluid rounded border w-100" style="height: 350px; object-fit: cover;">`;

        const thumbs = images.map((img, idx) => `
            <img src="${API_BASE_URL}${img.image_url}" class="img-thumbnail thumb-img cursor-pointer ${idx === 0 ? "border-primary" : ""}" data-full="${API_BASE_URL}${img.image_url}" style="width: 70px; height: 70px; object-fit: cover;">
        `).join("");

        imageSection = `
            ${mainImg}
            <div class="d-flex gap-2 mt-2 flex-wrap" id="thumbs-container">${thumbs}</div>
        `;
    }

    container.innerHTML = `
        <div class="row g-4">
            <div class="col-md-5">
                ${imageSection}
            </div>
            <div class="col-md-7">
                <span class="badge badge-category mb-2">${categoryLabel(product.category)}</span>
                <h2>${escapeHtml(product.title)}</h2>
                <p class="text-muted">${escapeHtml(product.description)}</p>
                <h3 class="price-tag mb-3">${formatPrice(product.price)}</h3>
                <p class="mb-3">${stockBadge}</p>

                <div class="d-flex align-items-center gap-2 mb-3" id="add-to-cart-section">
                    <label for="qty-input" class="form-label mb-0">تعداد:</label>
                    <input type="number" id="qty-input" class="form-control" style="width: 100px;" value="1" min="1" max="${product.quantity}">
                    <button class="btn btn-antique" id="add-to-cart-btn" ${product.quantity === 0 ? "disabled" : ""}>
                        افزودن به سبد خرید
                    </button>
                </div>

                <a href="index.html" class="btn btn-outline-secondary">بازگشت به محصولات</a>
            </div>
        </div>
    `;

    document.getElementById("add-to-cart-btn")?.addEventListener("click", () => addToCart(product));

    document.querySelectorAll(".thumb-img").forEach(thumb => {
        thumb.addEventListener("click", () => {
            document.getElementById("main-product-image").src = thumb.dataset.full;
            document.querySelectorAll(".thumb-img").forEach(t => t.classList.remove("border-primary"));
            thumb.classList.add("border-primary");
        });
    });
}

async function addToCart(product) {
    if (!isLoggedIn()) {
        window.location.href = "login.html";
        return;
    }

    const qty = parseInt(document.getElementById("qty-input").value, 10);

    if (!qty || qty < 1) {
        showAlert("alert-container", "تعداد وارد شده معتبر نیست.");
        return;
    }

    try {
        await apiRequest("/cart/items", {
            method: "POST",
            body: JSON.stringify({ product_id: product.id, quantity: qty })
        });

        showAlert("alert-container", "محصول با موفقیت به سبد خرید اضافه شد.", "success");

    } catch (err) {
        showAlert("alert-container", "خطا: " + err.message);
    }
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

loadProduct();
