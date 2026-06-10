const apiBaseUrl = "";
const views = document.querySelectorAll(".view");
const tabs = document.querySelectorAll(".tab");
const messageBox = document.getElementById("message");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const logoutBtn = document.getElementById("logout-btn");
const profileSection = document.getElementById("profile");
const profileUsername = document.getElementById("profile-username");
const profileId = document.getElementById("profile-id");
const profileCreated = document.getElementById("profile-created");
const productsList = document.getElementById("products-list");
const cartList = document.getElementById("cart-list");
const ordersList = document.getElementById("orders-list");

function showMessage(text, isError = false) {
  messageBox.textContent = text;
  messageBox.className = isError ? "message" : "message";
  messageBox.classList.remove("hidden");
}

function hideMessage() {
  messageBox.classList.add("hidden");
}

function showView(viewId) {
  views.forEach(view => view.id === viewId ? view.classList.remove("hidden") : view.classList.add("hidden"));
  tabs.forEach(tab => tab.classList.toggle("active", tab.dataset.view === viewId));
  if (viewId === "products") loadProducts();
  if (viewId === "cart") loadCart();
  if (viewId === "orders") loadOrders();
}

tabs.forEach(tab => tab.addEventListener("click", () => showView(tab.dataset.view)));

function getToken() {
  return localStorage.getItem("authToken");
}

function setToken(token) {
  if (token) {
    localStorage.setItem("authToken", token);
  } else {
    localStorage.removeItem("authToken");
  }
}

async function request(path, options = {}) {
  const headers = options.headers || {};
  headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers,
  });

  const text = await response.text();
  let data = text;
  try {
    data = JSON.parse(text);
  } catch {
    // keep raw text if invalid JSON
  }

  if (!response.ok) {
    throw new Error(data.detail || data.message || data || "خطا در ارتباط با سرور");
  }

  return data;
}

loginForm.addEventListener("submit", async event => {
  event.preventDefault();
  hideMessage();
  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const result = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setToken(result.access_token);
    showMessage("ورود با موفقیت انجام شد.");
    await loadProfile();
    showView("profile");
  } catch (error) {
    showMessage(error.message, true);
  }
});

registerForm.addEventListener("submit", async event => {
  event.preventDefault();
  hideMessage();
  const formData = new FormData(registerForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const result = await request("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setToken(getToken());
    showMessage("ثبت نام انجام شد. اکنون می‌توانید وارد شوید.");
    showView("login");
  } catch (error) {
    showMessage(error.message, true);
  }
});

logoutBtn?.addEventListener("click", () => {
  setToken(null);
  profileUsername.textContent = "-";
  profileId.textContent = "-";
  profileCreated.textContent = "-";
  showMessage("شما از سیستم خارج شدید.");
  showView("login");
});

async function loadProfile() {
  const token = getToken();
  if (!token) {
    return;
  }

  try {
    const user = await request("/auth/me");
    profileUsername.textContent = user.username || "-";
    profileId.textContent = user.id || "-";
    profileCreated.textContent = user.created_at ? new Date(user.created_at).toLocaleString("fa-IR") : "-";
  } catch (error) {
    setToken(null);
    showMessage("برای مشاهده پروفایل نیاز به ورود مجدد دارید.", true);
    showView("login");
  }
}

async function loadProducts() {
  productsList.textContent = "در حال بارگذاری محصولات...";
  try {
    const products = await request("/products");
    if (!Array.isArray(products) || products.length === 0) {
      productsList.textContent = "هیچ محصولی یافت نشد یا مسیر /products پیاده نشده است.";
      return;
    }
    productsList.innerHTML = products.map(product => `
      <div class="data-item">
        <strong>${product.name || "نام نامشخص"}</strong>
        <p>قیمت: ${product.price ?? "نامشخص"}</p>
        <p>موجودی: ${product.stock ?? "نامشخص"}</p>
      </div>
    `).join("");
  } catch (error) {
    productsList.textContent = error.message;
  }
}

async function loadCart() {
  cartList.textContent = "در حال بارگذاری سبد خرید...";
  try {
    const cart = await request("/cart");
    if (!Array.isArray(cart) || cart.length === 0) {
      cartList.textContent = "سبد خرید خالی است یا مسیر /cart پیاده نشده است.";
      return;
    }
    cartList.innerHTML = cart.map(item => `
      <div class="data-item">
        <strong>${item.product_name || "محصول"}</strong>
        <p>تعداد: ${item.quantity}</p>
        <p>قیمت واحد: ${item.unit_price}</p>
      </div>
    `).join("");
  } catch (error) {
    cartList.textContent = error.message;
  }
}

async function loadOrders() {
  ordersList.textContent = "در حال بارگذاری سفارش‌ها...";
  try {
    const orders = await request("/orders");
    if (!Array.isArray(orders) || orders.length === 0) {
      ordersList.textContent = "هیچ سفارشی یافت نشد یا مسیر /orders پیاده نشده است.";
      return;
    }
    ordersList.innerHTML = orders.map(order => `
      <div class="data-item">
        <strong>سفارش #${order.id}</strong>
        <p>وضعیت: ${order.status || "نامشخص"}</p>
        <p>مجموع: ${order.total ?? "نامشخص"}</p>
      </div>
    `).join("");
  } catch (error) {
    ordersList.textContent = error.message;
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  const token = getToken();
  if (token) {
    await loadProfile();
    showView("profile");
  } else {
    showView("login");
  }
});
