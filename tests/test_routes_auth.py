"""API route tests — Auth endpoints."""
import pytest


class TestAuthRegister:
    def test_register_success(self, client):
        response = client.post("/auth/register", json={
            "username": "newuser",
            "password": "StrongPass1!",
            "confirm_password": "StrongPass1!",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] in ("user", "owner")  # First user gets owner, subsequent get user
        assert data["is_active"] is True

    def test_register_first_user_gets_owner(self, client):
        response = client.post("/auth/register", json={
            "username": "firstowner",
            "password": "StrongPass1!",
            "confirm_password": "StrongPass1!",
        })
        assert response.status_code == 201
        assert response.json()["role"] == "owner"

    def test_register_duplicate_username(self, client, regular_user):
        response = client.post("/auth/register", json={
            "username": regular_user.username,
            "password": "StrongPass1!",
            "confirm_password": "StrongPass1!",
        })
        assert response.status_code == 409

    def test_register_passwords_mismatch(self, client):
        response = client.post("/auth/register", json={
            "username": "mismatch",
            "password": "Pass1!",
            "confirm_password": "Different1!",
        })
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        response = client.post("/auth/register", json={
            "username": "incomplete",
        })
        assert response.status_code == 422


class TestAuthLogin:
    def test_login_success(self, client, regular_user):
        response = client.post("/auth/login", json={
            "username": regular_user.username,
            "password": "TestPass123!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, regular_user):
        response = client.post("/auth/login", json={
            "username": regular_user.username,
            "password": "WrongPass!",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/auth/login", json={
            "username": "ghost",
            "password": "Pass!",
        })
        assert response.status_code == 401

    def test_login_sets_refresh_cookie(self, client, regular_user):
        response = client.post("/auth/login", json={
            "username": regular_user.username,
            "password": "TestPass123!",
        })
        assert response.status_code == 200
        assert "refresh_token" in response.cookies


class TestAuthRefresh:
    def test_refresh_no_cookie(self, client):
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_refresh_invalid_token(self, client):
        client.cookies.set("refresh_token", "invalid.token.here")
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_refresh_valid_token(self, client, regular_user):
        login_response = client.post("/auth/login", json={
            "username": regular_user.username,
            "password": "TestPass123!",
        })
        refresh_token = login_response.json()["refresh_token"]
        client.cookies.set("refresh_token", refresh_token)
        response = client.post("/auth/refresh")
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestAuthMe:
    def test_me_authenticated(self, client, regular_user):
        login = client.post("/auth/login", json={
            "username": regular_user.username,
            "password": "TestPass123!",
        })
        token = login.json()["access_token"]
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["username"] == regular_user.username

    def test_me_unauthenticated(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_me_invalid_token(self, client):
        response = client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
        assert response.status_code == 401


class TestAuthChangePassword:
    def test_change_password_success(self, client, regular_user):
        login = client.post("/auth/login", json={
            "username": regular_user.username,
            "password": "TestPass123!",
        })
        token = login.json()["access_token"]
        response = client.patch("/auth/change-password", json={
            "current_password": "TestPass123!",
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!",
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "message" in response.json()

    def test_change_password_wrong_current(self, client, regular_user):
        login = client.post("/auth/login", json={
            "username": regular_user.username,
            "password": "TestPass123!",
        })
        token = login.json()["access_token"]
        response = client.patch("/auth/change-password", json={
            "current_password": "WrongPass!",
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!",
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401

    def test_change_password_unauthenticated(self, client):
        response = client.patch("/auth/change-password", json={
            "current_password": "old",
            "new_password": "new",
            "confirm_password": "new",
        })
        assert response.status_code == 401


class TestAuthLogout:
    def test_logout_clears_cookie(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 204
