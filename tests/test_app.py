from datetime import date, timedelta

import pytest

from app import create_app, is_allowed_email

TOMORROW = (date.today() + timedelta(days=1)).isoformat()


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATA_FILE": str(tmp_path / "reservations.json")})
    return app.test_client()


def reserve(client, **overrides):
    form = {
        "name": "Ada Lovelace",
        "email": "ada@bilgi.edu.tr",
        "date": TOMORROW,
        "time": "10:00",
        "library": "ODTÜ Kütüphanesi",
    }
    form.update(overrides)
    return client.post("/reserve", data=form, follow_redirects=True)


@pytest.mark.parametrize(
    "email, allowed",
    [
        ("ada@bilgi.edu.tr", True),
        ("ada@metu.edu.tr", True),
        ("ADA@BILGI.EDU.TR", True),
        ("ada@edu.tr", True),
        ("ada@gmail.com", False),
        ("ada@notedu.tr", False),
        ("ada@bilgi.edu.tr.evil.com", False),
        ("not-an-email", False),
    ],
)
def test_university_emails(email, allowed):
    assert is_allowed_email(email) is allowed


def test_pages_load(client):
    assert client.get("/").status_code == 200
    assert client.get("/reserve").status_code == 200


def test_valid_reservation_is_listed(client):
    page = reserve(client).get_data(as_text=True)
    assert "Reservation successful" in page
    assert "Ada Lovelace" in page


def test_rejects_non_university_email(client):
    assert "university email" in reserve(client, email="ada@gmail.com").get_data(as_text=True)


def test_rejects_past_date(client):
    assert "past dates" in reserve(client, date="2020-01-01").get_data(as_text=True)


def test_rejects_double_booking(client):
    reserve(client)
    assert "already reserved" in reserve(client, name="Someone Else").get_data(as_text=True)


def test_rejects_missing_or_bad_date_and_time(client):
    for overrides in ({"date": ""}, {"date": "tomorrow"}, {"time": ""}, {"time": "25:00"}):
        response = reserve(client, **overrides)
        assert response.status_code == 200
        assert "valid date and time" in response.get_data(as_text=True)


def test_rejects_unknown_library(client):
    assert "Choose one of the listed libraries" in reserve(client, library="Nowhere").get_data(as_text=True)


def test_keeps_form_values_after_an_error(client):
    assert 'value="Ada Lovelace"' in reserve(client, email="ada@gmail.com").get_data(as_text=True)


def test_delete_needs_post(client):
    reserve(client)
    assert client.get("/delete/0").status_code == 405
    page = client.post("/delete/0", follow_redirects=True).get_data(as_text=True)
    assert "Reservation deleted" in page
    assert "Ada Lovelace" not in page


def test_reservations_survive_a_restart(tmp_path):
    config = {"TESTING": True, "DATA_FILE": str(tmp_path / "reservations.json")}
    reserve(create_app(config).test_client())
    assert "Ada Lovelace" in create_app(config).test_client().get("/").get_data(as_text=True)
