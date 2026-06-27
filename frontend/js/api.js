// ====== مدیریت توکن ======
function saveToken(token) {
    localStorage.setItem("access_token", token);
}

function getToken() {
    return localStorage.getItem("access_token");
}

function removeToken() {
    localStorage.removeItem("access_token");
}

function isLoggedIn() {
    return !!getToken();
}

// ====== درخواست‌های API ======
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers = {
        ...(options.headers || {})
    };

    // اگر body از نوع form-urlencoded نباشد، Content-Type را JSON بگذار
    if (!(options.body instanceof URLSearchParams) && options.body) {
        headers["Content-Type"] = "application/json";
    }

    // افزودن توکن در صورت وجود
    const token = getToken();
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    // پاسخ بدون محتوا (204)
    if (response.status === 204) {
        return null;
    }

    let data = null;
    try {
        data = await response.json();
    } catch (e) {
        data = null;
    }

    if (!response.ok) {
        const message = (data && data.detail) ? data.detail : "خطایی رخ داده است";
        throw new Error(typeof message === "string" ? message : JSON.stringify(message));
    }

    return data;
}

// ====== هدایت کاربر اگر لاگین نباشد ======
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = "login.html";
    }
}

// ====== نمایش پیام خطا/موفقیت ======
function showAlert(containerId, message, type = "danger") {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;
}

// ====== فرمت قیمت ======
function formatPrice(price) {
    return Number(price).toLocaleString("fa-IR") + " تومان";
}

// ====== نام فارسی دسته‌بندی ======
const CATEGORY_LABELS = {
    coin: "سکه",
    clock: "ساعت",
    painting: "تابلو نقاشی",
    book: "کتاب",
    statue: "مجسمه"
};

function categoryLabel(cat) {
    return CATEGORY_LABELS[cat] || cat;
}

// ====== نام فارسی وضعیت سفارش ======
const ORDER_STATUS_LABELS = {
    pending: "در انتظار",
    paid: "پرداخت شده",
    shipped: "ارسال شده",
    delivered: "تحویل شده",
    cancelled: "لغو شده"
};

const ORDER_STATUS_CLASSES = {
    pending: "bg-warning text-dark",
    paid: "bg-info text-dark",
    shipped: "bg-primary",
    delivered: "bg-success",
    cancelled: "bg-danger"
};

function orderStatusLabel(status) {
    return ORDER_STATUS_LABELS[status] || status;
}

function orderStatusClass(status) {
    return ORDER_STATUS_CLASSES[status] || "bg-secondary";
}
