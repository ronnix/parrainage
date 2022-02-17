# Copyright 2017 Raphaël Hertzog
#
# This file is subject to the license terms in the LICENSE file found in
# the top-level directory of this distribution.

import argparse
import sys

from django.core.management.base import BaseCommand
from django.db import transaction
from more_itertools import ichunked

from parrainage.app.models import Elu
from parrainage.app.sources.rne import read_tsv, parse_elu
from parrainage.app.sources.annuaire import read_csv, met_a_jour_coordonnees_elus


class Command(BaseCommand):
    help = "Importer les données sur les maires et les mairies"

    def add_arguments(self, parser):
        parser.add_argument(
            "maires",
            help="fichier rne-maires.csv du RNE",
            type=argparse.FileType(mode="r", encoding="utf-8"),
        )
        parser.add_argument(
            "mairies",
            help="chemin vers mairies.csv",
            type=argparse.FileType(mode="r", encoding="utf-8"),
        )
        parser.add_argument(
            "--chunk-size", type=int, default=200
        )

    def handle(self, *args, **kwargs):
        print("Ajout des maires")
        for chunk in ichunked(read_tsv(kwargs["maires"]), kwargs["chunk_size"]):
            print(".", end="")
            with transaction.atomic():
                Elu.objects.bulk_create(parse_elu(row, role="M") for row in chunk)
        print()

        print(f"Mise à jour des coordonnées")
        csv_mairies = read_csv(kwargs["mairies"])
        for i, row in enumerate(csv_mairies):
            if i % 100 == 0:
                print(".", end="")
            met_a_jour_coordonnees_elus(row)
        print()
