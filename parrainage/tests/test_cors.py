import pytest


@pytest.fixture(autouse=True)
def custom_settings(settings):
    settings.CORS_ORIGIN_WHITELIST = ["https://example.org"]


def test_allowed_origin(client):
    resp = client.get("/", HTTP_ORIGIN="https://example.org/toto")
    assert resp.status_code == 200
    assert "Access-Control-Allow-Origin" in resp
    assert resp["Access-Control-Allow-Origin"] == "https://example.org/toto"


def test_not_allowed_origin(client):
    resp = client.get("/", HTTP_ORIGIN="https://example.net/toto")
    assert resp.status_code == 200
    assert "Access-Control-Allow-Origin" not in resp


def test_no_origin(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Access-Control-Allow-Origin" not in resp
