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
    from parrainage.app.models import Elu

    return [
        make_elu(
            first_name="Alice",
            family_name="Dupont",
            city="Ici",
            department="01",
            status=Elu.STATUS_ACCEPTED,
        ),
        make_elu(
            first_name="Bob",
            family_name="Durand",
            city="Là-bas",
            department="02",
            status=Elu.STATUS_REFUSED,
        ),
        make_elu(
            first_name="Charlie",
            family_name="Martin",
            city="Ailleurs",
            department="03",
            status=Elu.STATUS_RECEIVED,
        ),
        make_elu(
            first_name="Doriane",
            family_name="Grès",
            city="Quelque part",
            department="04",
            status=Elu.STATUS_CONTACTED,
        ),
        make_elu(
            first_name="Marcel",
            family_name="Martel",
            city="Brunelnec",
            department="05",
            status=Elu.STATUS_TO_CONTACT,
        ),
        make_elu(
            first_name="Célina",
            family_name="de la Bonneau",
            city="Delorme-les-Bains",
            department="06",
            status=Elu.STATUS_TO_CONTACT_TEAM,
        ),
        make_elu(
            first_name="Diane",
            family_name="Lecoq",
            city="Guillou-la-Forêt",
            department="",
            status=Elu.STATUS_NOTHING,
        ),
    ]


def make_elu(**kwargs):
    from parrainage.app.models import Elu

    elu = Elu(
        role="M",
        city_latitude=42,
        city_longitude=8,
        **kwargs,
    )
    elu.save()
    return elu
