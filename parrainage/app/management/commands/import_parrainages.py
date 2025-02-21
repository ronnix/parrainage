import argparse
import csv
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from parrainage.app.models import Elu
from parrainage.app.management.commands.import_elus import MANDAT


DEPARTEMENTS = {
    "Ain": "01",
    "Aisne": "02",
    "Allier": "03",
    "Alpes-de-Haute-Provence": "04",
    "Hautes-Alpes": "05",
    "Alpes-Maritimes": "06",
    "Ardèche": "07",
    "Ardennes": "08",
    "Ariège": "09",
    "Aube": "10",
    "Aude": "11",
    "Aveyron": "12",
    "Bouches-du-Rhône": "13",
    "Calvados": "14",
    "Cantal": "15",
    "Charente": "16",
    "Charente-Maritime": "17",
    "Cher": "18",
    "Corrèze": "19",
    "Corse-du-sud": "2A",
    "Haute-corse": "2B",
    "Côte-d'Or": "21",
    "Côtes-d'Armor": "22",
    "Creuse": "23",
    "Dordogne": "24",
    "Doubs": "25",
    "Drôme": "26",
    "Eure": "27",
    "Eure-et-Loir": "28",
    "Finistère": "29",
    "Gard": "30",
    "Haute-Garonne": "31",
    "Gers": "32",
    "Gironde": "33",
    "Hérault": "34",
    "Ille-et-Vilaine": "35",
    "Indre": "36",
    "Indre-et-Loire": "37",
    "Isère": "38",
    "Jura": "39",
    "Landes": "40",
    "Loir-et-Cher": "41",
    "Loire": "42",
    "Haute-Loire": "43",
    "Loire-Atlantique": "44",
    "Loiret": "45",
    "Lot": "46",
    "Lot-et-Garonne": "47",
    "Lozère": "48",
    "Maine-et-Loire": "49",
    "Manche": "50",
    "Marne": "51",
    "Haute-Marne": "52",
    "Mayenne": "53",
    "Meurthe-et-Moselle": "54",
    "Meuse": "55",
    "Morbihan": "56",
    "Moselle": "57",
    "Nièvre": "58",
    "Nord": "59",
    "Oise": "60",
    "Orne": "61",
    "Pas-de-Calais": "62",
    "Puy-de-Dôme": "63",
    "Pyrénées-Atlantiques": "64",
    "Hautes-Pyrénées": "65",
    "Pyrénées-Orientales": "66",
    "Bas-Rhin": "67",
    "Haut-Rhin": "68",
    "Rhône": "69",
    "Haute-Saône": "70",
    "Saône-et-Loire": "71",
    "Sarthe": "72",
    "Savoie": "73",
    "Haute-Savoie": "74",
    "Paris": "75",
    "Seine-Maritime": "76",
    "Seine-et-Marne": "77",
    "Yvelines": "78",
    "Deux-Sèvres": "79",
    "Somme": "80",
    "Tarn": "81",
    "Tarn-et-Garonne": "82",
    "Var": "83",
    "Vaucluse": "84",
    "Vendée": "85",
    "Vienne": "86",
    "Haute-Vienne": "87",
    "Vosges": "88",
    "Yonne": "89",
    "Territoire de Belfort": "90",
    "Essonne": "91",
    "Hauts-de-Seine": "92",
    "Seine-Saint-Denis": "93",
    "Val-de-Marne": "94",
    "Val-d'Oise": "95",
    "Guadeloupe": "971",
    "Martinique": "972",
    "Guyane": "973",
    "La Réunion": "974",
    "Saint-Pierre-et-Miquelon": "975",
    "Mayotte": "976",
    "Saint-Barthélemy": "977",
    "Saint-Martin": "978",
}


class Command(BaseCommand):
    help = "Importer les parrainages validés par le Conseil constitutionnel"

    def add_arguments(self, parser):
        parser.add_argument(
            "fichier",
            help="fichier parrainagestotal.csv",
            type=argparse.FileType(mode="r", encoding="utf-8"),
        )
        parser.add_argument(
            "--candidate",
            help="nom et prénom de la candidate",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        nb_elus_mis_a_jour = 0
        reader = csv.DictReader(kwargs["fichier"], delimiter=";")
        for row in reader:
            try:
                elu = trouve_elu(row)
                if row["Candidat"] == kwargs["candidate"]:
                    if elu.status != Elu.STATUS_RECEIVED:
                        elu.status = Elu.STATUS_RECEIVED
                        elu.comment += f"\nParrainage publié par le CC le {row['Date de publication']}"
                        elu.save()
                        nb_elus_mis_a_jour += 1
                else:
                    if elu.status != Elu.STATUS_REFUSED:
                        elu.status = Elu.STATUS_REFUSED
                        elu.comment += f"\nParrainage donné à {row['Candidat']}, publié par le CC le {row['Date de publication']}"
                        elu.save()
                        nb_elus_mis_a_jour += 1
            except Elu.DoesNotExist:
                logging.warning(
                    "Pas trouvé de %s %s (%s de %s)",
                    row["Prénom"],
                    row["Nom"],
                    row["Mandat"],
                    (
                        row["Département"]
                        if row["Mandat"]
                        in {"Conseiller départemental", "Conseillère départementale"}
                        else row["Circonscription"]
                    ),
                )
            except Elu.MultipleObjectsReturned:
                logging.error(
                    "Il y a plusieurs %s %s (%s de %s)",
                    row["Prénom"],
                    row["Nom"],
                    row["Mandat"],
                    (
                        row["Département"]
                        if row["Mandat"]
                        in {"Conseiller départemental", "Conseillère départementale"}
                        else row["Circonscription"]
                    ),
                )
        print(f"Mis à jour le statut de {nb_elus_mis_a_jour} élus.")


def trouve_elu(row):
    prenom = row["Prénom"]
    nom = row["Nom"]

    # On essaie d’abord juste avec le nom, si ce n’est pas ambigu
    try:
        return trouve_elu_par_nom(prenom=prenom, nom=nom)

    # Si c’est ambigu, on essaie d’affiner avec le mandat indiqué par le CC
    except Elu.MultipleObjectsReturned:
        if row["Mandat"] == "Maire":
            try:
                return trouve_maire_par_nom_et_ville(
                    prenom=prenom, nom=nom, ville=row["Circonscription"]
                )
            except Elu.DoesNotExist:
                # Sinon c’est un accent à enlever sur une capitale
                return trouve_maire_par_nom_et_ville(
                    prenom=prenom,
                    nom=nom,
                    ville=row["Circonscription"].replace("É", "E"),
                )

        elif row["Mandat"] in {
            "Conseiller départemental",
            "Conseillère départementale",
        }:
            return trouve_elu_par_mandat(
                prenom=prenom,
                nom=nom,
                role="CD",
                department=DEPARTEMENTS[row["Département"]],
            )

        elif row["Mandat"] in {"Conseiller régional", "Conseillère régionale"}:
            return trouve_elu_par_mandat(prenom=prenom, nom=nom, role="CR")

        elif row["Mandat"] in {"Sénateur", "Sénatrice"}:
            return trouve_elu_par_mandat(prenom=prenom, nom=nom, role="S")

        elif row["Mandat"] in {"Député", "Députée"}:
            return trouve_elu_par_mandat(prenom=prenom, nom=nom, role="D")

        elif row["Mandat"] in {
            "Représentant français au Parlement européen",
            "Représentante française au Parlement européen",
        }:
            return trouve_elu_par_mandat(prenom=prenom, nom=nom, role="DE")

        else:
            raise


def trouve_elu_par_nom(prenom, nom):
    try:
        return Elu.objects.get(first_name=prenom, family_name=nom)
    except Elu.DoesNotExist:
        # Sinon, des fois c’est la moitié d’un nom composé
        return Elu.objects.get(
            first_name=prenom,
            family_name__startswith=nom + "-",
        )


def trouve_maire_par_nom_et_ville(prenom, nom, ville):
    return Elu.objects.get(
        first_name=prenom,
        family_name=nom,
        role="M",
        city__iexact=ville,
    )


def trouve_elu_par_mandat(prenom, nom, role, **extra):
    try:
        # Recherche par mandat principal
        return Elu.objects.get(first_name=prenom, family_name=nom, role=role, **extra)
    except Elu.DoesNotExist:
        # Recherche par mandat additionnel
        mandat = "CC" if role == "A" else role
        autre_mandat = f"Autre mandat: {MANDAT[mandat]}"
        return Elu.objects.get(
            first_name=prenom, family_name=nom, comment__contains=autre_mandat, **extra
        )
