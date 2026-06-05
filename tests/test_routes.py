def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_success(client, test_user):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert b"errati" in response.data


def test_404_page(client):
    response = client.get("/questa-pagina-non-esiste")
    assert response.status_code == 404
