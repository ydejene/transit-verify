import pytest

from app.services import anomaly_service


@pytest.fixture(autouse=True)
def _ctx(app):
    with app.app_context():
        yield


def test_no_anomaly_below_threshold():
    for _ in range(anomaly_service.ANOMALY_THRESHOLD - 1):
        anomaly_service.record_report(
            "AA-1111", "Megenagna", "Meg-Bole 01", "Route Chopping"
        )
    _, total, _, _ = anomaly_service.get_anomalies(status="All")
    assert total == 0


def test_anomaly_created_at_threshold():
    for _ in range(anomaly_service.ANOMALY_THRESHOLD):
        anomaly_service.record_report(
            "AA-2222", "Megenagna", "Meg-Bole 01", "Route Chopping"
        )
    anomalies, total, _, _ = anomaly_service.get_anomalies(status="All")
    assert total == 1
    assert anomalies[0]["reportCount"] == anomaly_service.ANOMALY_THRESHOLD
    assert anomalies[0]["status"] == "Pending"


def test_report_count_accumulates_after_anomaly_created():
    plate = "AA-3333"
    for _ in range(anomaly_service.ANOMALY_THRESHOLD + 1):
        anomaly_service.record_report(
            plate, "Megenagna", "Meg-Bole 01", "Route Chopping"
        )
    anomalies, _, _, _ = anomaly_service.get_anomalies(status="All", search=plate)
    assert anomalies[0]["reportCount"] == anomaly_service.ANOMALY_THRESHOLD + 1


def test_spam_filter_discards_over_ceiling():
    plate = "AA-4444"
    results = [
        anomaly_service.record_report(
            plate, "Megenagna", "Meg-Bole 01", "Fare Overcharge"
        )
        for _ in range(anomaly_service.SPAM_CEILING + 1)
    ]
    assert results.count(False) == 1
    assert results[-1] is False


def test_update_status_forward_only():
    plate = "AA-5555"
    for _ in range(anomaly_service.ANOMALY_THRESHOLD):
        anomaly_service.record_report(
            plate, "Megenagna", "Meg-Bole 01", "Route Chopping"
        )
    anomalies, _, _, _ = anomaly_service.get_anomalies(status="All", search=plate)
    anomaly_id = anomalies[0]["anomalyId"]

    success, _ = anomaly_service.update_status(
        anomaly_id, "Reviewed", "", updated_by_user_id=1
    )
    assert success is True

    success2, error2 = anomaly_service.update_status(
        anomaly_id, "Resolved", "RCP-2026-001", updated_by_user_id=1
    )
    assert success2 is False
    assert "forward-only" in error2


def test_update_status_rejects_bad_receipt_format():
    plate = "AA-6666"
    for _ in range(anomaly_service.ANOMALY_THRESHOLD):
        anomaly_service.record_report(
            plate, "Megenagna", "Meg-Bole 01", "Fare Overcharge"
        )
    anomalies, _, _, _ = anomaly_service.get_anomalies(status="All", search=plate)
    anomaly_id = anomalies[0]["anomalyId"]

    success, _ = anomaly_service.update_status(
        anomaly_id, "Resolved", "not-a-receipt", updated_by_user_id=1
    )
    assert success is False


def test_update_status_rejects_wrong_zone_manager():
    plate = "AA-7777"
    for _ in range(anomaly_service.ANOMALY_THRESHOLD):
        anomaly_service.record_report(
            plate, "Megenagna", "Meg-Bole 01", "Route Chopping"
        )
    anomalies, _, _, _ = anomaly_service.get_anomalies(status="All", search=plate)
    anomaly_id = anomalies[0]["anomalyId"]

    success, error = anomaly_service.update_status(
        anomaly_id, "Reviewed", "", updated_by_user_id=1, manager_zone="Bole"
    )
    assert success is False
    assert "zone" in error
