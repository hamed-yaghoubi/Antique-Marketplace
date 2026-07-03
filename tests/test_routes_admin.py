"""API route tests — Admin endpoints."""
import pytest


class TestAdminListUsers:
    def test_list_users(self, client, admin_headers, regular_user):
        response = client.get("/admin/users", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_list_users_unauthenticated(self, client):
        response = client.get("/admin/users")
        assert response.status_code == 401

    def test_list_users_forbidden_for_regular_user(self, client, auth_headers):
        response = client.get("/admin/users", headers=auth_headers)
        assert response.status_code == 403


class TestAdminGetUser:
    def test_get_user(self, client, admin_headers, regular_user):
        response = client.get(f"/admin/users/{regular_user.id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["username"] == regular_user.username

    def test_get_user_not_found(self, client, admin_headers):
        response = client.get("/admin/users/99999", headers=admin_headers)
        assert response.status_code == 404


class TestAdminBanUser:
    def test_ban_user(self, client, admin_headers, regular_user):
        response = client.patch(f"/admin/users/{regular_user.id}/ban", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_ban_self(self, client, admin_headers, admin_user):
        response = client.patch(f"/admin/users/{admin_user.id}/ban", headers=admin_headers)
        assert response.status_code == 400

    def test_ban_user_not_found(self, client, admin_headers):
        response = client.patch("/admin/users/99999/ban", headers=admin_headers)
        assert response.status_code == 404

    def test_ban_admin_by_admin(self, client, admin_headers, user_factory):
        other_admin = user_factory(username="banadmin", role="admin")
        response = client.patch(f"/admin/users/{other_admin.id}/ban", headers=admin_headers)
        assert response.status_code == 403

    def test_ban_owner_by_admin(self, client, admin_headers, owner_user):
        response = client.patch(f"/admin/users/{owner_user.id}/ban", headers=admin_headers)
        assert response.status_code == 403


class TestAdminUnbanUser:
    def test_unban_user(self, client, admin_headers, user_factory):
        target = user_factory(username="tounban", is_active=False)
        response = client.patch(f"/admin/users/{target.id}/unban", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["is_active"] is True

    def test_unban_admin_by_admin(self, client, admin_headers, user_factory):
        other_admin = user_factory(username="unbanadmin", role="admin", is_active=False)
        response = client.patch(f"/admin/users/{other_admin.id}/unban", headers=admin_headers)
        assert response.status_code == 403


class TestOwnerPromote:
    def test_promote_user(self, client, owner_headers, user_factory):
        target = user_factory(username="topromote")
        response = client.post(f"/owner/promote/{target.id}", headers=owner_headers)
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    def test_promote_already_admin(self, client, owner_headers, user_factory):
        target = user_factory(username="alreadyadmin", role="admin")
        response = client.post(f"/owner/promote/{target.id}", headers=owner_headers)
        assert response.status_code == 400

    def test_promote_forbidden_for_admin(self, client, admin_headers, user_factory):
        target = user_factory(username="notallowed")
        response = client.post(f"/owner/promote/{target.id}", headers=admin_headers)
        assert response.status_code == 403


class TestOwnerDemote:
    def test_demote_admin(self, client, owner_headers, user_factory):
        target = user_factory(username="todemote", role="admin")
        response = client.post(f"/owner/demote/{target.id}", headers=owner_headers)
        assert response.status_code == 200
        assert response.json()["role"] == "user"

    def test_demote_self(self, client, owner_headers, owner_user):
        response = client.post(f"/owner/demote/{owner_user.id}", headers=owner_headers)
        assert response.status_code == 400

    def test_demote_non_admin(self, client, owner_headers, user_factory):
        target = user_factory(username="regularuser")
        response = client.post(f"/owner/demote/{target.id}", headers=owner_headers)
        assert response.status_code == 403

    def test_demote_forbidden_for_admin(self, client, admin_headers, user_factory):
        target = user_factory(username="someadmin", role="admin")
        response = client.post(f"/owner/demote/{target.id}", headers=admin_headers)
        assert response.status_code == 403

    def test_demote_unauthenticated(self, client, user_factory):
        target = user_factory(username="unauthadmin", role="admin")
        response = client.post(f"/owner/demote/{target.id}")
        assert response.status_code == 401

    def test_demote_nonexistent_user(self, client, owner_headers):
        response = client.post("/owner/demote/99999", headers=owner_headers)
        assert response.status_code == 404
