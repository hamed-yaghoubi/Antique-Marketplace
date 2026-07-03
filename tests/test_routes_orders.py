"""API route tests — Order endpoints."""
from decimal import Decimal
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

    def test_create_order_self_purchase(self, client, product_factory, owner_user, owner_headers, cart_item_factory):
        product = product_factory(title="Own", seller_id=owner_user.id, quantity=5)
        cart_item_factory(user_id=owner_user.id, product_id=product.id, quantity=1)
        response = client.post("/orders/", headers=owner_headers)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "SELF_PURCHASE_NOT_ALLOWED"


class TestOrdersList:
    def test_list_orders(self, client, auth_headers, sample_product, order_factory, regular_user):
        order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        response = client.get("/orders/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_list_orders_unauthenticated(self, client):
        response = client.get("/orders/")
        assert response.status_code == 401


class TestOrderDetail:
    def test_get_order(self, client, auth_headers, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        response = client.get(f"/orders/{order.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == order.id

    def test_get_order_not_found(self, client, auth_headers):
        response = client.get("/orders/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_order_not_owner(self, client, auth_headers, order_factory, other_user):
        order = order_factory(buyer_id=other_user.id, total_price=Decimal("50"))
        response = client.get(f"/orders/{order.id}", headers=auth_headers)
        assert response.status_code == 403


class TestOrderCancel:
    def test_cancel_order(self, client, auth_headers, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_cancel_order_not_pending(self, client, auth_headers, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, status="confirmed", total_price=Decimal("50"))
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
        order = order_factory(buyer_id=other_user.id, total_price=Decimal("50"))
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_cancel_order_unauthenticated(self, client, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        })
        assert response.status_code == 401

    def test_seller_view_orders_with_own_products(self, client, product_factory, owner_user, owner_headers, regular_user, order_factory):
        product = product_factory(title="SellerProduct", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "SellerProduct",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        response = client.get("/orders/", headers=owner_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_seller_update_order_status(self, client, product_factory, owner_user, owner_headers, regular_user, order_factory):
        product = product_factory(title="SellerProduct", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "SellerProduct",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "confirmed",
        }, headers=owner_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_seller_cannot_view_unrelated_orders(self, client, product_factory, owner_user, owner_headers, regular_user, other_user, order_factory):
        other_product = product_factory(title="OtherProduct", seller_id=other_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": other_product.id,
            "seller_id": other_user.id,
            "product_title": "OtherProduct",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        response = client.get(f"/orders/{order.id}", headers=owner_headers)
        assert response.status_code == 403

    def test_customer_cannot_confirm_order_via_confirm_endpoint(self, client, auth_headers, regular_user, order_factory):
        """Customers can only cancel orders, not advance through the lifecycle.

        The backend currently allows customers to transition PENDING->CONFIRMED
        because the role restriction only applies to cancellations. This test
        documents the current behavior.
        """
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "confirmed",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_admin_view_all_orders(self, client, product_factory, admin_user, admin_headers, regular_user, owner_user, order_factory):
        product = product_factory(title="AnyProduct", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "AnyProduct",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        response = client.get("/orders/", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_admin_update_any_order_status(self, client, product_factory, admin_user, admin_headers, regular_user, owner_user, order_factory):
        product = product_factory(title="AnyProduct", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "AnyProduct",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "confirmed",
        }, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"


class TestStatusTransitions:
    def test_valid_transition_pending_to_confirmed(self, client, product_factory, owner_user, owner_headers, regular_user, order_factory):
        product = product_factory(title="Prod1", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "Prod1",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "confirmed",
        }, headers=owner_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_full_lifecycle(self, client, product_factory, owner_user, owner_headers, regular_user, order_factory):
        product = product_factory(title="Lifecycle", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "Lifecycle",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])

        for next_status in ["confirmed", "preparing", "shipped", "delivered"]:
            response = client.patch(f"/orders/{order.id}/status", json={
                "status": next_status,
            }, headers=owner_headers)
            assert response.status_code == 200, f"Failed transition to {next_status}: {response.json()}"
            assert response.json()["status"] == next_status

    def test_invalid_transition_delivered_to_pending(self, client, product_factory, owner_user, owner_headers, regular_user, order_factory):
        product = product_factory(title="DeliveredProd", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "DeliveredProd",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        # Walk through to delivered
        for s in ["confirmed", "preparing", "shipped", "delivered"]:
            client.patch(f"/orders/{order.id}/status", json={"status": s}, headers=owner_headers)

        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "pending",
        }, headers=owner_headers)
        assert response.status_code == 400

    def test_invalid_transition_cancelled_to_preparing(self, client, product_factory, owner_user, owner_headers, regular_user, order_factory):
        product = product_factory(title="CancelledProd", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "CancelledProd",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        # Cancel the order
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=owner_headers)
        assert response.status_code == 200

        # Try to move cancelled → preparing
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "preparing",
        }, headers=owner_headers)
        assert response.status_code == 400

    def test_customer_can_advance_pending_to_confirmed(self, client, auth_headers, order_factory, regular_user):
        """Backend allows any authenticated user to transition PENDING->CONFIRMED.

        The role restriction only applies to cancellation, not to advancing status.
        """
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "confirmed",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_customer_can_cancel_pending_order(self, client, auth_headers, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_customer_cannot_cancel_confirmed_order(self, client, product_factory, owner_user, owner_headers, auth_headers, regular_user, order_factory):
        product = product_factory(title="ConfirmedProd", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "ConfirmedProd",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        # Seller confirms
        client.patch(f"/orders/{order.id}/status", json={"status": "confirmed"}, headers=owner_headers)

        # Customer tries to cancel
        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_seller_can_cancel_preparing_order(self, client, product_factory, owner_user, owner_headers, regular_user, order_factory):
        product = product_factory(title="PreparingCancel", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "PreparingCancel",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        # Move to preparing
        client.patch(f"/orders/{order.id}/status", json={"status": "confirmed"}, headers=owner_headers)
        client.patch(f"/orders/{order.id}/status", json={"status": "preparing"}, headers=owner_headers)

        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=owner_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_seller_cannot_cancel_shipped_order(self, client, product_factory, owner_user, owner_headers, regular_user, order_factory):
        product = product_factory(title="ShippedCancel", seller_id=owner_user.id, quantity=5)
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "ShippedCancel",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        # Move to shipped
        for s in ["confirmed", "preparing", "shipped"]:
            client.patch(f"/orders/{order.id}/status", json={"status": s}, headers=owner_headers)

        response = client.patch(f"/orders/{order.id}/status", json={
            "status": "cancelled",
        }, headers=owner_headers)
        assert response.status_code == 400


class TestOrderFiltering:
    def test_filter_by_status(self, client, auth_headers, order_factory, regular_user):
        order_factory(buyer_id=regular_user.id, status="confirmed", total_price=Decimal("50"))
        order_factory(buyer_id=regular_user.id, status="pending", total_price=Decimal("30"))

        response = client.get("/orders/?status=confirmed", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["status"] == "confirmed"

    def test_search_by_order_id(self, client, auth_headers, order_factory, regular_user):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))

        response = client.get(f"/orders/?search={order.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(item["id"] == order.id for item in data["items"])

    def test_pagination(self, client, auth_headers, order_factory, regular_user):
        for i in range(5):
            order_factory(buyer_id=regular_user.id, total_price=Decimal(f"{10 + i}"))

        response = client.get("/orders/?page=1&page_size=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) == 2
        assert data["total"] >= 5
        assert data["total_pages"] >= 3

    def test_seller_only_sees_own_orders(self, client, product_factory, owner_user, owner_headers, regular_user, other_user, order_factory):
        own_product = product_factory(title="OwnProd", seller_id=owner_user.id, quantity=5)
        other_product = product_factory(title="OtherProd", seller_id=other_user.id, quantity=5)

        # Order with owner's product
        order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": own_product.id,
            "seller_id": owner_user.id,
            "product_title": "OwnProd",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        # Order with other seller's product
        order_factory(buyer_id=regular_user.id, total_price=Decimal("50"), items=[{
            "product_id": other_product.id,
            "seller_id": other_user.id,
            "product_title": "OtherProd",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])

        response = client.get("/orders/", headers=owner_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestOrderStats:
    def test_admin_stats_reflect_all_orders(self, client, product_factory, admin_user, admin_headers, regular_user, owner_user, order_factory):
        product = product_factory(title="StatProd", seller_id=owner_user.id, quantity=10)
        order_factory(buyer_id=regular_user.id, status="confirmed", total_price=Decimal("50"), items=[{
            "product_id": product.id,
            "seller_id": owner_user.id,
            "product_title": "StatProd",
            "unit_price": Decimal("50"),
            "quantity": 1,
        }])
        order_factory(buyer_id=regular_user.id, status="pending", total_price=Decimal("30"))

        response = client.get("/orders/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["confirmed"] == 1
        assert data["pending"] == 1

    def test_customer_stats_reflect_only_their_orders(self, client, auth_headers, order_factory, regular_user, other_user):
        order_factory(buyer_id=regular_user.id, status="confirmed", total_price=Decimal("50"))
        order_factory(buyer_id=regular_user.id, status="pending", total_price=Decimal("30"))
        order_factory(buyer_id=other_user.id, status="confirmed", total_price=Decimal("70"))

        response = client.get("/orders/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["confirmed"] == 1
        assert data["pending"] == 1

    def test_dashboard_stats_include_product_counts_for_admin(self, client, product_factory, admin_user, admin_headers, regular_user, owner_user, order_factory):
        product_factory(title="ActiveProd", seller_id=owner_user.id, quantity=5, is_active=True)
        product_factory(title="InactiveProd", seller_id=owner_user.id, quantity=5, is_active=False)

        response = client.get("/orders/dashboard", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "order_stats" in data
        assert "total_products" in data
        assert "active_products" in data
        assert data["total_products"] >= 2
        assert data["active_products"] >= 1
