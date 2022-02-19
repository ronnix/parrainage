# Copyright 2017 Raphaël Hertzog
#
# This file is subject to the license terms in the LICENSE file found in
# the top-level directory of this distribution.

import argparse

from django.core.management.base import BaseCommand
from django.db import transaction
from more_itertools import partition

from parrainage.app.models import Elu
from parrainage.app.sources.annuaire import charge_annuaire_mairies
from parrainage.app.sources.population import charge_population_communes
from parrainage.app.sources.rne import charge_rne, parse_elu


class Command(BaseCommand):
    help = "Importer les données sur les maires et les mairies"

    def add_arguments(self, parser):
        parser.add_argument(
            "maires",
            help="fichier rne-maires.csv du RNE",
            type=argparse.FileType(mode="rb"),
        )
        parser.add_argument(
            "mairies",
            help="chemin vers mairies.csv",
            type=argparse.FileType(mode="rb"),
        )
        parser.add_argument(
            "population",
            help="chemin vers donnees_communes.csv",
            type=argparse.FileType(mode="rb"),
        )

    @transaction.atomic()
    def handle(self, *args, **kwargs):
        existants = {
            tuple(d.values())
            for d in Elu.objects.filter(role="M").values(
                "first_name", "family_name", "birthdate", "city"
            )
        }
        print(f"Déja {len(existants)} maires dans la base.")
        importes = [
            parse_elu(row, role="M")
            for row in merge_csv(
                kwargs["maires"], kwargs["mairies"], kwargs["population"]
            )
        ]
        nouveaux, ignores = partition(
            (
                lambda elu: (
                    elu.first_name,
                    elu.family_name,
                    elu.birthdate,
                    elu.city,
                )
                in existants
            ),
            importes,
        )
        print(f"Ignoré {len(list(ignores))}/{len(importes)} maires déjà importés.")
        ajoutes = Elu.objects.bulk_create(nouveaux)
        print(f"Ajouté {len(ajoutes)} nouveaux maires avec leurs coordonnées.")


def merge_csv(tsv_maires, csv_mairies, csv_population):
    df = (
        charge_rne(tsv_maires)
        .merge(
            charge_annuaire_mairies(csv_mairies),
            how="left",
            left_on="Code de la commune",
            right_on="codeInsee",
            validate="one_to_one",
        )
        .drop(
            columns=[
                "codeInsee",
            ]
        )
        .merge(
            charge_population_communes(csv_population),
            how="left",
            left_on="Code de la commune",
            right_on="CODE",
            validate="one_to_one",
        )
        .drop(columns=["CODE"])
        .fillna("")
    )
    for _, row in df.iterrows():
        yield dict(row)
