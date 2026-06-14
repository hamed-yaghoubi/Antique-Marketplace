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

let productId = getQueryParam("id");
let isEditMode = !!productId;

if (isEditMode) {
    document.getElementById("page-title").textContent = "ویرایش محصول | آنتیک مارکت";
    document.getElementById("form-title").textContent = "ویرایش محصول";
    document.getElementById("submit-btn").textContent = "ذخیره تغییرات";
    document.getElementById("images-section").classList.remove("d-none");
    loadProductData();
}

async function loadProductData() {
    try {
        const product = await apiRequest(`/products/${productId}`);

        document.getElementById("title").value = product.title;
        document.getElementById("description").value = product.description;
        document.getElementById("price").value = product.price;
        document.getElementById("quantity").value = product.quantity;
        document.getElementById("category").value = product.category;

        renderImages(product.images || []);

    } catch (err) {
        showAlert("alert-container", "خطا در بارگذاری اطلاعات محصول: " + err.message);
    }
}

function renderImages(images) {
    const gallery = document.getElementById("images-gallery");

    if (!images || images.length === 0) {
        gallery.innerHTML = `<div class="col-12 text-muted">هیچ عکسی برای این محصول ثبت نشده است.</div>`;
        return;
    }

    gallery.innerHTML = images.map(img => `
        <div class="col-4 col-md-3">
            <div class="position-relative">
                <img src="${API_BASE_URL}${img.image_url}" class="img-fluid rounded border" style="aspect-ratio: 1; object-fit: cover; width: 100%;">
                <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-1 delete-image-btn" data-image-id="${img.id}" title="حذف عکس">×</button>
            </div>
        </div>
    `).join("");

    document.querySelectorAll(".delete-image-btn").forEach(btn => {
        btn.addEventListener("click", () => deleteImage(btn.dataset.imageId));
    });
}

async function deleteImage(imageId) {
    if (!confirm("آیا از حذف این عکس مطمئن هستید؟")) return;

    try {
        await apiRequest(`/products/${productId}/images/${imageId}`, { method: "DELETE" });
        loadProductData();
    } catch (err) {
        showAlert("images-alert-container", "خطا در حذف عکس: " + err.message);
    }
}

document.getElementById("upload-image-btn")?.addEventListener("click", async () => {
    const input = document.getElementById("image-input");

    if (!input.files || input.files.length === 0) {
        showAlert("images-alert-container", "لطفاً یک عکس انتخاب کنید.");
        return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append("file", file);

    const btn = document.getElementById("upload-image-btn");
    btn.disabled = true;
    btn.textContent = "در حال آپلود...";

    try {
        // برای آپلود فایل نباید Content-Type دستی ست شود، مرورگر خودش boundary را تنظیم می‌کند
        const token = getToken();
        const response = await fetch(`${API_BASE_URL}/products/${productId}/images`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => null);
            const message = (errData && errData.detail) ? errData.detail : "خطا در آپلود عکس";
            throw new Error(typeof message === "string" ? message : JSON.stringify(message));
        }

        input.value = "";
        loadProductData();

    } catch (err) {
        showAlert("images-alert-container", "خطا در آپلود عکس: " + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = "آپلود عکس";
    }
});

document.getElementById("product-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        title: document.getElementById("title").value.trim(),
        description: document.getElementById("description").value.trim(),
        price: parseFloat(document.getElementById("price").value),
        quantity: parseInt(document.getElementById("quantity").value, 10),
        category: document.getElementById("category").value
    };

    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.textContent = "در حال ذخیره...";

    try {
        if (isEditMode) {
            await apiRequest(`/products/${productId}`, {
                method: "PATCH",
                body: JSON.stringify(data)
            });

            showAlert("alert-container", "تغییرات با موفقیت ذخیره شد.", "success");
            btn.disabled = false;
            btn.textContent = "ذخیره تغییرات";

        } else {
            // محصول جدید ساخته می‌شود، سپس کاربر به حالت ویرایش همین صفحه می‌رود تا بتواند عکس آپلود کند
            const product = await apiRequest("/products/", {
                method: "POST",
                body: JSON.stringify(data)
            });

            window.location.href = `add-product.html?id=${product.id}`;
        }

    } catch (err) {
        showAlert("alert-container", "خطا در ذخیره محصول: " + err.message);
        btn.disabled = false;
        btn.textContent = isEditMode ? "ذخیره تغییرات" : "ثبت محصول";
    }
});

