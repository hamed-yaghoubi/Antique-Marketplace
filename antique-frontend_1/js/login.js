document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    const btn = document.getElementById("login-btn");
    btn.disabled = true;
    btn.textContent = "در حال ورود...";

    try {
        // OAuth2PasswordRequestForm نیاز به form-urlencoded دارد
        const params = new URLSearchParams();
        params.append("username", username);
        params.append("password", password);

        const data = await apiRequest("/auth/login", {
            method: "POST",
            body: params
        });

        saveToken(data.access_token);
        window.location.href = "index.html";

    } catch (err) {
        showAlert("alert-container", "خطا در ورود: " + err.message);
        btn.disabled = false;
        btn.textContent = "ورود";
    }
});
