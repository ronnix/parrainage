from datetime import datetime

import pandas as pd

from parrainage.app.models import Elu


def charge_rne(chemin):
    return (
        pd.read_csv(chemin, sep="\t", dtype=str)
        .drop(
            columns=[
                "Code de la catégorie socio-professionnelle",
            ]
        )
        .fillna("")
    )


def parse_elu(row, role):
    """
    Crée un élu à partir d'une ligne d’un fichier du Répertoire National des Élus

    https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
    """
    gender = "H" if row["Code sexe"] == "M" else "F"
    birthdate = datetime.strptime(row["Date de naissance"], "%d/%m/%Y").date()
    return Elu(
        first_name=row["Prénom de l'élu"],
        family_name=row["Nom de l'élu"],
        gender=gender,
        birthdate=birthdate,
        role=role,
        comment="Catégorie socio-professionnelle: {}".format(
            row["Libellé de la catégorie socio-professionnelle"]
        ),
        department=row.get("Code du département", ""),
        city=row.get(
            "Libellé de la commune",
            row.get("Libellé de la commune de rattachement", ""),
        ),
        city_code=row.get(
            "Code de la commune", row.get("Code de la commune de rattachement", "")
        ),
        city_zipcode=row.get("CodePostal", ""),
        city_latitude=row.get("Latitude", ""),
        city_longitude=row.get("Longitude", ""),
        city_address=row.get("Adresse", ""),
        city_size=int_or_none(row.get("PMUN", "")),
        public_email=row.get("Email", ""),
        public_phone=row.get("Téléphone", ""),
        public_website=row.get("Url", ""),
    )


def int_or_none(value):
    if not value:
        return None
    return int(value)
