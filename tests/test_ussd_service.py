import pytest

from app.services.ussd_service import handle_ussd


@pytest.fixture(autouse=True)
def _ctx(app):
    with app.app_context():
        yield


def test_main_menu():
    assert handle_ussd("").startswith("CON Welcome to Transit Verify")


def test_asks_for_plate_after_selecting_report():
    assert handle_ussd("1").startswith("CON Enter the vehicle's license plate number")


def test_zone_menu_lists_seeded_zone():
    resp = handle_ussd("1*AA-9999")
    assert resp.startswith("CON Select the zone:")
    assert "Megenagna" in resp


def test_invalid_zone_choice_ends_session():
    assert handle_ussd("1*AA-9999*9") == "END Invalid zone selection."


def test_full_flow_creates_report():
    resp = handle_ussd("1*AA-9999*1*1*1*1")
    assert resp == "END Thank you. Your report has been submitted."


def test_cancel_at_confirmation():
    resp = handle_ussd("1*AA-9999*1*1*1*2")
    assert resp == "END Report cancelled."
