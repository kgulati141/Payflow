from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# =========================================================
# Helper Function
# =========================================================

def create_test_order():
    response = client.post(
        "/orders",
        json={
            "customer_name": "Test User",
            "product_name": "Test Laptop",
            "amount": 50000,
            "coupon_code": "TEST10"
        }
    )

    assert response.status_code == 200

    return response.json()


# =========================================================
# TEST HOME
# =========================================================

def test_home():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["message"] == "PayFlow API is running"


# =========================================================
# TEST DATABASE
# =========================================================

def test_database():
    response = client.get("/test-db")

    assert response.status_code == 200

    assert (
        response.json()["message"]
        == "Database session created successfully"
    )


# =========================================================
# TEST CREATE ORDER - POST
# =========================================================

def test_create_order():

    order = create_test_order()

    assert "order_id" in order
    assert order["customer_name"] == "Test User"
    assert order["product_name"] == "Test Laptop"
    assert order["amount"] == 50000
    assert order["status"] == "created"

    # Cleanup
    client.delete(f"/orders/{order['order_id']}")


# =========================================================
# TEST GET ALL ORDERS
# =========================================================

def test_get_all_orders():

    response = client.get("/orders")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


# =========================================================
# TEST GET ORDER BY ID
# =========================================================

def test_get_order_by_id():

    order = create_test_order()

    order_id = order["order_id"]

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["customer_name"] == "Test User"

    # Cleanup
    client.delete(f"/orders/{order_id}")


# =========================================================
# TEST QUERY PARAMETER
# =========================================================

def test_get_orders_by_status():

    order = create_test_order()

    response = client.get(
        "/orders",
        params={
            "status": "created"
        }
    )

    assert response.status_code == 200

    orders = response.json()

    assert isinstance(orders, list)

    for item in orders:
        assert item["status"] == "created"

    # Cleanup
    client.delete(f"/orders/{order['order_id']}")


# =========================================================
# TEST UPDATE ORDER - PUT
# =========================================================

def test_update_order():

    order = create_test_order()

    order_id = order["order_id"]

    response = client.put(
        f"/orders/{order_id}",
        json={
            "customer_name": "Updated User",
            "product_name": "Updated Laptop",
            "amount": 75000,
            "coupon_code": "UPDATED20"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["customer_name"] == "Updated User"
    assert data["product_name"] == "Updated Laptop"
    assert data["amount"] == 75000

    # Cleanup
    client.delete(f"/orders/{order_id}")


# =========================================================
# TEST DELETE ORDER
# =========================================================

def test_delete_order():

    order = create_test_order()

    order_id = order["order_id"]

    response = client.delete(
        f"/orders/{order_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["message"] == "Order deleted successfully"

    # Verify order is actually deleted
    response = client.get(
        f"/orders/{order_id}"
    )

    assert response.status_code == 404


# =========================================================
# TEST ORDER NOT FOUND
# =========================================================

def test_order_not_found():

    response = client.get("/orders/999999999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Order not found"


# =========================================================
# TEST INVALID ORDER DATA
# =========================================================

def test_invalid_order():

    response = client.post(
        "/orders",
        json={
            "customer_name": "K",
            "product_name": "Laptop",
            "amount": -500
        }
    )

    assert response.status_code == 422