from datetime import date
from io import StringIO

import pytest


TSV_RNE_MAIRES = """\
Code du département\tLibellé du département\tCode de la collectivité à statut particulier\tLibellé de la collectivité à statut particulier\tCode de la commune\tLibellé de la commune\tNom de l'élu\tPrénom de l'élu\tCode sexe\tDate de naissance\tCode de la catégorie socio-professionnelle\tLibellé de la catégorie socio-professionnelle\tDate de début du mandat\tDate de début de la fonction
01\tAin\t\t\t01001\tL'Abergement-Clémenciat\tBOULON\tDaniel\tM\t04/03/1951\t74\tAncien cadre\t18/05/2020\t26/05/2020
"""


@pytest.fixture
def row_rne_maires():
    from parrainage.app.sources.rne import charge_rne

    return dict(next(charge_rne(StringIO(TSV_RNE_MAIRES)).iterrows())[1])


def test_tsv_rne_maires(row_rne_maires):
    assert row_rne_maires == {
        "Code de la collectivité à statut particulier": "",
        "Code de la commune": "01001",
        "Code du département": "01",
        "Code sexe": "M",
        "Date de début de la fonction": "26/05/2020",
        "Date de début du mandat": "18/05/2020",
        "Date de naissance": "04/03/1951",
        "Libellé de la catégorie socio-professionnelle": "Ancien cadre",
        "Libellé de la collectivité à statut particulier": "",
        "Libellé de la commune": "L'Abergement-Clémenciat",
        "Libellé du département": "Ain",
        "Nom de l'élu": "BOULON",
        "Prénom de l'élu": "Daniel",
    }


CSV_ANNUAIRE = """\
codeInsee,CodePostal,NomOrganisme,NomCommune,Email,Téléphone,Url,Adresse,Latitude,Longitude,dateMiseAJour
01001,01400,Mairie de L'Abergement-Clémenciat,L'Abergement-Clémenciat,mairieabergementclemenciat@wanadoo.fr,+33 4 74 24 03 08,http://example.org,Le Village,46.151676178,4.92007112503,2014-12-04
"""


CSV_POPULATION = """\
CODREG;REG;CODDEP;CODARR;CODCAN;CODCOM;COM;PMUN;PCAP;PTOT
84;Auvergne-Rhône-Alpes;01;2;08;001;L'Abergement-Clémenciat;779;19;798
"""


@pytest.fixture
def row_merged_maires():
    from parrainage.app.management.commands.import_maires import merge_csv

    rows = merge_csv(
        StringIO(TSV_RNE_MAIRES), StringIO(CSV_ANNUAIRE), StringIO(CSV_POPULATION)
    )
    return list(rows)[0]


def test_merged_maires(row_merged_maires):
    assert row_merged_maires == {
        "Adresse": "Le Village",
        "Code de la collectivité à statut particulier": "",
        "Code de la commune": "01001",
        "Code du département": "01",
        "Code sexe": "M",
        "CodePostal": "01400",
        "Date de début de la fonction": "26/05/2020",
        "Date de début du mandat": "18/05/2020",
        "Date de naissance": "04/03/1951",
        "Email": "mairieabergementclemenciat@wanadoo.fr",
        "Latitude": "46.151676178",
        "Libellé de la catégorie socio-professionnelle": "Ancien cadre",
        "Libellé de la collectivité à statut particulier": "",
        "Libellé de la commune": "L'Abergement-Clémenciat",
        "Libellé du département": "Ain",
        "Longitude": "4.92007112503",
        "Nom de l'élu": "BOULON",
        "NomOrganisme": "Mairie de L'Abergement-Clémenciat",
        "PMUN": "779",
        "Prénom de l'élu": "Daniel",
        "Téléphone": "+33 4 74 24 03 08",
        "Url": "http://example.org",
    }


TSV_RNE_CD = """\
Code du département\tLibellé du département\tCode du canton\tLibellé du canton\tNom de l'élu\tPrénom de l'élu\tCode sexe\tDate de naissance\tCode de la catégorie socio-professionnelle\tLibellé de la catégorie socio-professionnelle\tDate de début du mandat\tLibellé de la fonction\tDate de début de la fonction
01\tAin\t0101\tAmbérieu-En-Bugey\tPETIT\tAurélie\tF\t29/08/1982\t38\tIngénieur et cadre technique d'entreprise\t01/07/2021\t\t
"""


@pytest.fixture
def row_rne_cd():
    from parrainage.app.sources.rne import charge_rne

    return dict(next(charge_rne(StringIO(TSV_RNE_CD)).iterrows())[1])


def test_tsv_rne_cd(row_rne_cd):
    assert row_rne_cd == {
        "Code du canton": "0101",
        "Code du département": "01",
        "Code sexe": "F",
        "Date de début de la fonction": "",
        "Date de début du mandat": "01/07/2021",
        "Date de naissance": "29/08/1982",
        "Libellé de la catégorie socio-professionnelle": "Ingénieur et cadre technique d'entreprise",
        "Libellé de la fonction": "",
        "Libellé du canton": "Ambérieu-En-Bugey",
        "Libellé du département": "Ain",
        "Nom de l'élu": "PETIT",
        "Prénom de l'élu": "Aurélie",
    }


TSV_RNE_CR = """\
Code de la région\tLibellé de la région\tCode de la section départementale\tLibellé de la section départementale\tNom de l'élu\tPrénom de l'élu\tCode sexe\tDate de naissance\tCode de la catégorie socio-professionnelle\tLibellé de la catégorie socio-professionnelle\tDate de début du mandat\tLibellé de la fonction\tDate de début de la fonction
01\tGuadeloupe\t971\tGuadeloupe\tARMOUGOM\tBetty, Véronique\tF\t09/07/1965\t23\tChef d'entreprise de 10 salariés ou plus\t02/07/2021\t\t
"""


@pytest.fixture
def row_rne_cr():
    from parrainage.app.sources.rne import charge_rne

    return dict(next(charge_rne(StringIO(TSV_RNE_CR)).iterrows())[1])


def test_tsv_rne_cr(row_rne_cr):
    assert row_rne_cr == {
        "Code de la région": "01",
        "Code de la section départementale": "971",
        "Code sexe": "F",
        "Date de début de la fonction": "",
        "Date de début du mandat": "02/07/2021",
        "Date de naissance": "09/07/1965",
        "Libellé de la catégorie socio-professionnelle": "Chef d'entreprise de 10 "
        "salariés ou plus",
        "Libellé de la fonction": "",
        "Libellé de la région": "Guadeloupe",
        "Libellé de la section départementale": "Guadeloupe",
        "Nom de l'élu": "ARMOUGOM",
        "Prénom de l'élu": "Betty, Véronique",
    }


TSV_RNE_SEN = """\
Code du département\tLibellé du département\tCode de la collectivité à statut particulier\tLibellé de la collectivité à statut particulier\tNom de l'élu\tPrénom de l'élu\tCode sexe\tDate de naissance\tCode de la catégorie socio-professionnelle\tLibellé de la catégorie socio-professionnelle\tDate de début du mandat
01\tAin\t\t\tBLATRIX CONTAT\tFlorence\tF\t30/03/1966\t34\tProfesseur, profession scientifique\t01/10/2020
"""


@pytest.fixture
def row_rne_sen():
    from parrainage.app.sources.rne import charge_rne

    return dict(next(charge_rne(StringIO(TSV_RNE_SEN)).iterrows())[1])


def test_tsv_rne_sen(row_rne_sen):
    assert row_rne_sen == {
        "Code de la collectivité à statut particulier": "",
        "Code du département": "01",
        "Code sexe": "F",
        "Date de début du mandat": "01/10/2020",
        "Date de naissance": "30/03/1966",
        "Libellé de la catégorie socio-professionnelle": "Professeur, profession scientifique",
        "Libellé de la collectivité à statut particulier": "",
        "Libellé du département": "Ain",
        "Nom de l'élu": "BLATRIX CONTAT",
        "Prénom de l'élu": "Florence",
    }


class TestParseElu:
    def test_parse_maire(self, row_merged_maires):
        from parrainage.app.sources.rne import parse_elu

        elu = parse_elu(row_merged_maires, role="M")
        assert elu.first_name == "Daniel"
        assert elu.family_name == "BOULON"
        assert elu.gender == "H"
        assert elu.birthdate == date(1951, 3, 4)
        assert elu.role == "M"  # maire
        assert elu.comment == "Catégorie socio-professionnelle: Ancien cadre"
        assert elu.department == "01"
        assert elu.city == "L'Abergement-Clémenciat"
        assert elu.city_code == "01001"
        assert elu.public_email == "mairieabergementclemenciat@wanadoo.fr"
        assert elu.public_phone == "+33 4 74 24 03 08"
        assert elu.public_website == "http://example.org"
        assert elu.city_address == "Le Village"
        assert elu.city_zipcode == "01400"
        assert elu.city_latitude == "46.151676178"
        assert elu.city_longitude == "4.92007112503"

    def test_parse_cd(self, row_rne_cd):
        from parrainage.app.sources.rne import parse_elu

        elu = parse_elu(row_rne_cd, role="CD")
        assert elu.first_name == "Aurélie"
        assert elu.family_name == "PETIT"
        assert elu.gender == "F"
        assert elu.birthdate == date(1982, 8, 29)
        assert elu.role == "CD"  # conseillère départementale
        assert elu.comment == (
            "Catégorie socio-professionnelle: "
            "Ingénieur et cadre technique d'entreprise"
        )
        assert elu.department == "01"
        assert elu.city == ""
        assert elu.city_code == ""

    def test_parse_cr(self, row_rne_cr):
        from parrainage.app.sources.rne import parse_elu

        elu = parse_elu(row_rne_cr, role="CR")
        assert elu.first_name == "Betty, Véronique"
        assert elu.family_name == "ARMOUGOM"
        assert elu.gender == "F"
        assert elu.birthdate == date(1965, 7, 9)
        assert elu.role == "CR"  # conseillère régionale
        assert (
            elu.comment
            == "Catégorie socio-professionnelle: Chef d'entreprise de 10 salariés ou plus"
        )
        assert elu.department == ""
        assert elu.city == ""
        assert elu.city_code == ""

    def test_parse_sen(self, row_rne_sen):
        from parrainage.app.sources.rne import parse_elu

        elu = parse_elu(row_rne_sen, role="S")
        assert elu.first_name == "Florence"
        assert elu.family_name == "BLATRIX CONTAT"
        assert elu.gender == "F"
        assert elu.birthdate == date(1966, 3, 30)
        assert elu.role == "S"  # sénatrice
        assert (
            elu.comment
            == "Catégorie socio-professionnelle: Professeur, profession scientifique"
        )
        assert elu.department == "01"
        assert elu.city == ""
        assert elu.city_code == ""
