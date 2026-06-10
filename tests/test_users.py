from app.db import db
from app.models.user import User

# ──────────────────────────────────────────────
# POST /users/
# ──────────────────────────────────────────────


def test_create_user(client):
    response = client.post("/users/", json={
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
    })
    assert response.status_code == 201
    body = response.get_json()
    assert body["first_name"] == "Ada"
    assert body["last_name"] == "Lovelace"
    assert body["email"] == "ada@example.com"
    assert body["is_admin"] is False
    assert "id" in body


def test_create_user_sets_is_admin(client):
    response = client.post("/users/", json={
        "first_name": "Root",
        "last_name": "User",
        "email": "root@example.com",
        "is_admin": True,
    })
    assert response.status_code == 201
    assert response.get_json()["is_admin"] is True


def test_create_user_missing_required_field_returns_400(client):
    response = client.post("/users/", json={
        "last_name": "Lovelace",
        "email": "ada@example.com",
    })
    assert response.status_code == 400
    assert "Invalid" in response.get_json()["message"]


def test_create_user_duplicate_email_returns_409(client, one_user):
    response = client.post("/users/", json={
        "first_name": "Other",
        "last_name": "Person",
        "email": "ada@example.com",
    })
    assert response.status_code == 409
    assert "already exists" in response.get_json()["message"]


# ──────────────────────────────────────────────
# GET /users/
# ──────────────────────────────────────────────

def test_get_all_users_empty(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_all_users(client, three_users):
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.get_json()) == 3


def test_get_all_users_ordered_by_id(client, three_users):
    ids = [u["id"] for u in client.get("/users/").get_json()]
    assert ids == sorted(ids)


def test_get_all_users_filter_by_first_name(client, three_users):
    body = client.get("/users/?first_name=ada").get_json()
    assert len(body) == 1
    assert body[0]["first_name"] == "Ada"


def test_get_all_users_filter_no_match(client, three_users):
    assert client.get("/users/?first_name=Zzz").get_json() == []


def test_get_all_users_unknown_filter_ignored(client, three_users):
    response = client.get("/users/?nonexistent_field=value")
    assert response.status_code == 200
    assert len(response.get_json()) == 3


# ──────────────────────────────────────────────
# GET /users/email
# ──────────────────────────────────────────────

def test_get_single_user_by_email(client, one_user):
    response = client.get(f"/users/email?email={one_user.email}")
    response = client.get(f"/users/{one_user.id}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == one_user.id
    assert body["email"] == "ada@example.com"


def test_get_single_user_by_email_not_found_returns_404(client):
    response = client.get("/users/email?email=adminnotexist@example.com")
    assert response.status_code == 404
    assert "Could not find account." in response.get_json()["message"]
# ──────────────────────────────────────────────
# GET /users/<id>
# ──────────────────────────────────────────────


def test_get_single_user(client, one_user):
    response = client.get(f"/users/{one_user.id}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == one_user.id
    assert body["email"] == "ada@example.com"


def test_get_single_user_not_found_returns_404(client):
    response = client.get("/users/999")
    assert response.status_code == 404
    assert "not found" in response.get_json()["message"]


def test_get_single_user_invalid_id_returns_400(client):
    response = client.get("/users/abc")
    assert response.status_code == 400
    assert "invalid" in response.get_json()["message"]

# ──────────────────────────────────────────────
# PUT /users/<id>
# ──────────────────────────────────────────────


def test_update_user(client, one_user):
    response = client.put(
        f"/users/{one_user.id}", json={"first_name": "Augusta"})
    assert response.status_code == 204


def test_update_user_ignores_unknown_fields(client, one_user):
    response = client.put(
        f"/users/{one_user.id}", json={"unknown_field": "value"})
    assert response.status_code == 204


def test_update_user_not_found_returns_404(client):
    response = client.put("/users/999", json={"first_name": "Nobody"})
    assert response.status_code == 404
    assert "not found" in response.get_json()["message"]


def test_update_user_invalid_id_returns_400(client):
    response = client.put("/users/abc", json={"first_name": "Nobody"})
    assert response.status_code == 400
    assert "invalid" in response.get_json()["message"]

# ──────────────────────────────────────────────
# DELETE /users/<id>
# ──────────────────────────────────────────────


def test_delete_user(client, one_user):
    user_id = one_user.id
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    assert db.session.get(User, user_id) is None


def test_delete_user_not_found_returns_404(client):
    response = client.delete("/users/999")
    assert response.status_code == 404
    assert "not found" in response.get_json()["message"]


def test_delete_user_invalid_id_returns_400(client):
    response = client.delete("/users/abc")
    assert response.status_code == 400
    assert "invalid" in response.get_json()["message"]
