document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const confirm_password = document.getElementById("confirm_password").value;

    if (password !== confirm_password) {
        showAlert("alert-container", "رمز عبور و تکرار آن مطابقت ندارند.");
        return;
    }

    const btn = document.getElementById("register-btn");
    btn.disabled = true;
    btn.textContent = "در حال ثبت‌نام...";

    try {
        await apiRequest("/auth/register", {
            method: "POST",
            body: JSON.stringify({ username, password, confirm_password })
        });

        showAlert("alert-container", "ثبت‌نام با موفقیت انجام شد. در حال انتقال به صفحه ورود...", "success");

        setTimeout(() => {
            window.location.href = "login.html";
        }, 1500);

    } catch (err) {
        showAlert("alert-container", "خطا در ثبت‌نام: " + err.message);
        btn.disabled = false;
        btn.textContent = "ثبت‌نام";
    }
});
