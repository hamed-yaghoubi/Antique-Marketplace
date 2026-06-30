"""API route tests — Cart endpoints."""
import pytest


class TestCartRead:
    def test_get_cart_empty(self, client, auth_headers):
        response = client.get("/cart/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_price"] == "0"

    def test_get_cart_unauthenticated(self, client):
        response = client.get("/cart/")
        assert response.status_code == 401


class TestCartAddItem:
    def test_add_item(self, client, auth_headers, sample_product):
        response = client.post("/cart/items", json={
            "product_id": sample_product.id,
            "quantity": 2,
        }, headers=auth_headers)
        assert response.status_code == 201

    def test_add_item_product_not_found(self, client, auth_headers):
        response = client.post("/cart/items", json={
            "product_id": 99999,
            "quantity": 1,
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_add_item_insufficient_stock(self, client, auth_headers, sample_product):
        response = client.post("/cart/items", json={
            "product_id": sample_product.id,
            "quantity": 999,
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_add_item_merges_quantity(self, client, auth_headers, sample_product):
        client.post("/cart/items", json={
            "product_id": sample_product.id,
            "quantity": 2,
        }, headers=auth_headers)
        response = client.post("/cart/items", json={
            "product_id": sample_product.id,
            "quantity": 3,
        }, headers=auth_headers)
        assert response.status_code == 201

    def test_add_item_unauthenticated(self, client, sample_product):
        response = client.post("/cart/items", json={
            "product_id": sample_product.id,
            "quantity": 1,
        })
        assert response.status_code == 401


class TestCartUpdateItem:
    def test_update_quantity(self, client, auth_headers, sample_product, cart_item_factory, regular_user):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=1)
        response = client.patch(f"/cart/items/{item.id}", json={
            "quantity": 5,
        }, headers=auth_headers)
        assert response.status_code == 200

    def test_update_item_not_found(self, client, auth_headers):
        response = client.patch("/cart/items/99999", json={
            "quantity": 1,
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_update_item_not_owner(self, client, auth_headers, sample_product, cart_item_factory, other_user):
        item = cart_item_factory(user_id=other_user.id, product_id=sample_product.id, quantity=1)
        response = client.patch(f"/cart/items/{item.id}", json={
            "quantity": 1,
        }, headers=auth_headers)
        assert response.status_code == 403


class TestCartRemoveItem:
    def test_remove_item(self, client, auth_headers, sample_product, cart_item_factory, regular_user):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=1)
        response = client.delete(f"/cart/items/{item.id}", headers=auth_headers)
        assert response.status_code == 204

    def test_remove_item_not_found(self, client, auth_headers):
        response = client.delete("/cart/items/99999", headers=auth_headers)
        assert response.status_code == 404


class TestCartClear:
    def test_clear_cart(self, client, auth_headers, sample_product, cart_item_factory, regular_user):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=1)
        response = client.delete("/cart/", headers=auth_headers)
        assert response.status_code == 204
