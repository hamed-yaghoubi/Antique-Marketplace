// به‌روزرسانی منوی ناوبری بر اساس وضعیت ورود کاربر
function initNavbar() {
    const guestLinks = document.getElementById("nav-guest-links");
    const userLinks = document.getElementById("nav-user-links");
    const usernameSpan = document.getElementById("nav-username");
    const logoutBtn = document.getElementById("nav-logout");

    if (isLoggedIn()) {
        if (guestLinks) guestLinks.classList.add("d-none");
        if (userLinks) userLinks.classList.remove("d-none");

        // گرفتن اطلاعات کاربر
        apiRequest("/auth/me")
            .then(user => {
                if (usernameSpan) usernameSpan.textContent = user.username;
            })
            .catch(() => {
                // توکن نامعتبر است
                removeToken();
                if (guestLinks) guestLinks.classList.remove("d-none");
                if (userLinks) userLinks.classList.add("d-none");
            });
    } else {
        if (guestLinks) guestLinks.classList.remove("d-none");
        if (userLinks) userLinks.classList.add("d-none");
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            removeToken();
            window.location.href = "index.html";
        });
    }
}

document.addEventListener("DOMContentLoaded", initNavbar);
