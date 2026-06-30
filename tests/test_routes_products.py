"""API route tests — Product endpoints."""
import pytest
from decimal import Decimal


class TestProductsList:
    def test_list_products_empty(self, client):
        response = client.get("/products/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 0

    def test_list_products_with_data(self, client, sample_product):
        response = client.get("/products/")
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_list_products_pagination(self, client, product_factory, owner_user):
        for i in range(25):
            product_factory(title=f"Item {i}", seller_id=owner_user.id, price=Decimal(str(i)))
        response = client.get("/products/?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] >= 25
        assert data["total_pages"] >= 3

    def test_list_products_search(self, client, product_factory, owner_user):
        product_factory(title="Unique Clock", seller_id=owner_user.id)
        response = client.get("/products/?search=Unique Clock")
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_list_products_filter_category(self, client, product_factory, owner_user):
        product_factory(title="Coin", category="coin", seller_id=owner_user.id)
        product_factory(title="Clock", category="clock", seller_id=owner_user.id)
        response = client.get("/products/?category=coin")
        assert response.status_code == 200
        data = response.json()
        assert all(item["category"] == "coin" for item in data["items"])


class TestProductDetail:
    def test_get_product(self, client, sample_product):
        response = client.get(f"/products/{sample_product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_product.title

    def test_get_product_not_found(self, client):
        response = client.get("/products/99999")
        assert response.status_code == 404


class TestProductCreate:
    def test_create_product(self, client, owner_headers):
        response = client.post("/products/", json={
            "title": "New Product",
            "description": "A new product",
            "price": "50.00",
            "quantity": 5,
            "category": "coin",
        }, headers=owner_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Product"
        assert data["price"] == "50.00"

    def test_create_product_unauthenticated(self, client):
        response = client.post("/products/", json={
            "title": "No Auth",
            "description": "Should fail",
            "price": "10.00",
            "quantity": 1,
            "category": "book",
        })
        assert response.status_code == 401

    def test_create_product_invalid_data(self, client, owner_headers):
        response = client.post("/products/", json={
            "title": "Missing fields",
        }, headers=owner_headers)
        assert response.status_code == 422


class TestProductUpdate:
    def test_update_product_owner(self, client, owner_headers, sample_product):
        response = client.patch(f"/products/{sample_product.id}", json={
            "title": "Updated Title",
        }, headers=owner_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_update_product_not_owner(self, client, auth_headers, sample_product):
        response = client.patch(f"/products/{sample_product.id}", json={
            "title": "Hacked",
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_update_product_not_found(self, client, owner_headers):
        response = client.patch("/products/99999", json={
            "title": "Ghost",
        }, headers=owner_headers)
        assert response.status_code == 404

    def test_update_product_unauthenticated(self, client, sample_product):
        response = client.patch(f"/products/{sample_product.id}", json={
            "title": "No Auth",
        })
        assert response.status_code == 401


class TestProductDelete:
    def test_delete_product_owner(self, client, owner_headers, sample_product):
        response = client.delete(f"/products/{sample_product.id}", headers=owner_headers)
        assert response.status_code == 204

    def test_delete_product_not_owner(self, client, auth_headers, sample_product):
        response = client.delete(f"/products/{sample_product.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_delete_product_not_found(self, client, owner_headers):
        response = client.delete("/products/99999", headers=owner_headers)
        assert response.status_code == 404

    def test_delete_product_unauthenticated(self, client, sample_product):
        response = client.delete(f"/products/{sample_product.id}")
        assert response.status_code == 401


class TestProductMyProducts:
    def test_my_products(self, client, owner_headers, sample_product):
        response = client.get("/products/me", headers=owner_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_my_products_unauthenticated(self, client):
        response = client.get("/products/me")
        assert response.status_code == 401
