from tests.conftest import login


def test_login_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Secure Login" in resp.data


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"


def test_login_success_redirects_to_dashboard(client):
    resp = login(client, "manager@test.et")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/dashboard"


def test_login_wrong_password_shows_error(client):
    resp = client.post("/", data={"email": "manager@test.et", "password": "wrong"})
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.data


def test_logout_clears_session(client):
    login(client, "manager@test.et")
    resp = client.get("/logout")
    assert resp.status_code == 302

    dashboard_resp = client.get("/dashboard")
    assert dashboard_resp.status_code == 302
