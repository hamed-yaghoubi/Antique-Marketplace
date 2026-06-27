requireAuth();

async function loadProfile() {
    try {
        const user = await apiRequest("/auth/me");

        document.getElementById("profile-info").innerHTML = `
            <p><strong>نام کاربری:</strong> ${escapeHtml(user.username)}</p>
            <p><strong>تاریخ عضویت:</strong> ${new Date(user.created_at).toLocaleDateString("fa-IR")}</p>
        `;
    } catch (err) {
        document.getElementById("profile-info").innerHTML =
            `<div class="alert alert-danger">خطا در بارگذاری اطلاعات کاربر: ${err.message}</div>`;
    }
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById("change-password-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const current_password = document.getElementById("current_password").value;
    const new_password = document.getElementById("new_password").value;
    const confirm_password = document.getElementById("confirm_password").value;

    if (new_password !== confirm_password) {
        showAlert("alert-container", "رمز عبور جدید و تکرار آن مطابقت ندارند.");
        return;
    }

    const btn = document.getElementById("change-pw-btn");
    btn.disabled = true;
    btn.textContent = "در حال ذخیره...";

    try {
        await apiRequest("/auth/change-password", {
            method: "PATCH",
            body: JSON.stringify({ current_password, new_password, confirm_password })
        });

        showAlert("alert-container", "رمز عبور با موفقیت تغییر یافت.", "success");
        document.getElementById("change-password-form").reset();

    } catch (err) {
        showAlert("alert-container", "خطا: " + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = "تغییر رمز عبور";
    }
});

loadProfile();
