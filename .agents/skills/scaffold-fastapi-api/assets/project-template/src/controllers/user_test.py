from fastapi.testclient import TestClient

from db.engine import engine
from main import app
from tests.constants import test_user_email
from tests.constants import test_user_password
from tests.utils import delete_all_users_except_test_user

client = TestClient(app)
headers = None


def teardown_module():
    engine.dispose()


def setup_function():
    global headers

    delete_all_users_except_test_user()
    login_response = client.post(
        "/login",
        json={"email": test_user_email, "password": test_user_password},
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['token']}"}


def teardown_function():
    delete_all_users_except_test_user()


def test_login():
    response = client.post(
        "/login",
        json={"email": test_user_email, "password": test_user_password},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["user"]["email"] == test_user_email
    assert "password" not in body["user"]


def test_list_users():
    create_response = client.post(
        "/users",
        json={
            "name": "Second User",
            "email": "second-controller-test@example.com",
            "password": "second-password",
        },
        headers=headers,
    )
    assert create_response.status_code == 200

    response = client.get(
        "/users?page=0&page_size=1",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["pagination"]["total_pages"] == 2
    assert body["pagination"]["total_elements"] == 2
    assert body["pagination"]["page"] == 0
    assert body["pagination"]["size"] == 1


def test_create_user():
    payload = {
        "name": "Created User",
        "email": "created-controller-test@example.com",
        "password": "created-password",
    }

    response = client.post(
        "/users",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]
    assert "password" not in body

    login_response = client.post(
        "/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )
    assert login_response.status_code == 200


def test_update_user():
    create_response = client.post(
        "/users",
        json={
            "name": "User To Update",
            "email": "user-to-update@example.com",
            "password": "update-password",
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]
    payload = {
        "name": "Updated User",
        "email": "updated-controller-test@example.com",
    }

    response = client.put(
        f"/users/{user_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user_id
    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]
    assert "password" not in body


def test_remove_user():
    create_response = client.post(
        "/users",
        json={
            "name": "User To Remove",
            "email": "user-to-remove@example.com",
            "password": "remove-password",
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]

    response = client.delete(
        f"/users/{user_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["deleted_at"] is not None

    list_response = client.get("/users", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 1
    assert list_response.json()["data"][0]["email"] == test_user_email


def test_private_routes_require_authorization():
    response = client.get("/users")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authorization header is required"}
