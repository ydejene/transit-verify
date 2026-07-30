from tests.conftest import login


def test_supervisor_sees_updated_by_column(client):
    login(client, "supervisor@test.et")
    resp = client.get("/dashboard")
    assert b"Updated By" in resp.data


def test_terminal_manager_hides_updated_by_column(client):
    login(client, "manager@test.et")
    resp = client.get("/dashboard")
    assert b"Updated By" not in resp.data


def test_officer_hides_receipt_column(client):
    login(client, "officer@test.et")
    resp = client.get("/dashboard")
    assert b"Receipt Ref" not in resp.data


def test_terminal_manager_zone_filter_is_locked(client):
    login(client, "manager@test.et")
    resp = client.get("/dashboard?zone=Bole")
    assert b"Scoped to your assigned zone" in resp.data
    assert b"Megenagna" in resp.data


def test_status_update_forbidden_for_non_manager(client):
    login(client, "supervisor@test.et")
    resp = client.post("/dashboard/anomalies/1/status", json={"status": "Reviewed"})
    assert resp.status_code == 403
