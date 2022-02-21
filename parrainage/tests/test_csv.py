import csv

import pytest


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
        "Célina de la Bonneau (Maire de Delorme-les-Bains)",
        "Charlie Martin (Maire de Ailleurs)",
        "Diane Lecoq (Maire de Guillou-la-Forêt)",
        "Doriane Grès (Maire de Quelque part)",
        "Marcel Martel (Maire de Brunelnec)",
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
