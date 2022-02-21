import csv

from parrainage.app.models import Elu

import pytest


@pytest.fixture
def logged_in_user(client):
    from django.contrib.auth.models import User

    user = User.objects.create_user(
        username="test", email="test@example.com", password="secret"
    )
    client.login(username="test", password="secret")


@pytest.fixture
def elus():
    return [
        make_elu(
            first_name="Alice",
            family_name="Dupont",
            city="Ici",
            status=Elu.STATUS_ACCEPTED,
        ),
        make_elu(
            first_name="Bob",
            family_name="Durand",
            city="Là-bas",
            status=Elu.STATUS_REFUSED,
        ),
        make_elu(
            first_name="Charlie",
            family_name="Martin",
            city="Ailleurs",
            status=Elu.STATUS_RECEIVED,
        ),
        make_elu(
            first_name="Doriane",
            family_name="Grès",
            city="Quelque part",
            status=Elu.STATUS_CONTACTED,
        ),
    ]


def make_elu(**kwargs):
    elu = Elu(
        role="M",
        city_latitude=42,
        city_longitude=8,
        **kwargs,
    )
    elu.save()
    return elu


@pytest.mark.django_db
def test_csv_forbidden(client):
    resp = client.get("/csv/")
    assert resp.status_code == 302
    assert resp["Location"] == "/login/?next=/csv/"


@pytest.mark.django_db
def test_csv_empty(client, logged_in_user):
    resp = client.get("/csv/")
    assert resp.status_code == 200
    rows = list(csv.DictReader(resp.content.decode("utf-8").splitlines()))
    assert len(rows) == 0


@pytest.mark.django_db
def test_csv_all(client, logged_in_user, elus):
    resp = client.get("/csv/")
    assert resp.status_code == 200
    rows = list(csv.DictReader(resp.content.decode("utf-8").splitlines()))
    names = {row["name"] for row in rows}
    assert names == {
        "Alice Dupont (Maire de Ici)",
        "Bob Durand (Maire de Là-bas)",
        "Charlie Martin (Maire de Ailleurs)",
        "Doriane Grès (Maire de Quelque part)",
    }


@pytest.mark.django_db
def test_csv_done(client, logged_in_user, elus):
    resp = client.get("/csv/?status=done")
    assert resp.status_code == 200
    rows = list(csv.DictReader(resp.content.decode("utf-8").splitlines()))
    names = {row["name"] for row in rows}
    assert names == {
        "Alice Dupont (Maire de Ici)",
        "Bob Durand (Maire de Là-bas)",
        "Charlie Martin (Maire de Ailleurs)",
    }


@pytest.mark.django_db
def test_csv_accepted(client, logged_in_user, elus):
    resp = client.get("/csv/?status=accepted")
    assert resp.status_code == 200
    rows = list(csv.DictReader(resp.content.decode("utf-8").splitlines()))
    names = {row["name"] for row in rows}
    assert names == {
        "Alice Dupont (Maire de Ici)",
        "Charlie Martin (Maire de Ailleurs)",
    }
