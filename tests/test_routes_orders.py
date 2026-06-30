"""API route tests — Order endpoints."""
import pytest


class TestOrdersCreate:
    def test_create_order(self, client, auth_headers, sample_product, cart_item_factory, regular_user):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=2)
        response = client.post("/orders/", headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert len(data["items"]) >= 1

    def test_create_order_empty_cart(self, client, auth_headers):
        response = client.post("/orders/", headers=auth_headers)
        assert response.status_code == 400

    def test_create_order_insufficient_stock(self, client, auth_headers, sample_product, cart_item_factory, regular_user):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=999)
        response = client.post("/orders/", headers=auth_headers)
        assert response.status_code == 400

    def test_create_order_unauthenticated(self, client):
        response = client.post("/orders/")
        assert response.status_code == 401


class TestOrdersList:
    def test_list_orders(self, client, auth_headers, sample_product, order_factory, regular_user, cart_item_factory):
        order_factory(buyer_id=regular_user.id, total_price=50)
        response = client.get("/orders/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_list_orders_unauthenticated(self, client):
        response = client.get("/orders/")
        assert response.status_code == 401


class TestOrderDetail:
    def test_get_order(self, client, auth_headers, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, total_price=50)
        response = client.get(f"/orders/{order.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == order.id

    def test_get_order_not_found(self, client, auth_headers):
        response = client.get("/orders/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_order_not_owner(self, client, auth_headers, order_factory, other_user):
        order = order_factory(buyer_id=other_user.id, total_price=50)
        response = client.get(f"/orders/{order.id}", headers=auth_headers)
        assert response.status_code == 403


class TestOrderCancel:
    def test_cancel_order(self, client, auth_headers, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, total_price=50)
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_cancel_order_not_pending(self, client, auth_headers, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, status="paid", total_price=50)
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_cancel_order_not_found(self, client, auth_headers):
        response = client.patch("/orders/99999/status", json={
            "status": "cancelled",
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_cancel_order_not_owner(self, client, auth_headers, order_factory, other_user):
        order = order_factory(buyer_id=other_user.id, total_price=50)
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_cancel_order_unauthenticated(self, client, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, total_price=50)
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        })
        assert response.status_code == 401
