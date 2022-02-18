# Copyright 2017 Raphaël Hertzog
#
# This file is subject to the license terms in the LICENSE file found in
# the top-level directory of this distribution.

import argparse

from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd

from parrainage.app.models import Elu
from parrainage.app.sources.annuaire import nettoie_mairies
from parrainage.app.sources.rne import parse_elu


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

    @transaction.atomic()
    def handle(self, *args, **kwargs):
        elus = Elu.objects.bulk_create(
            parse_elu(row, role="M")
            for row in merge_csv(kwargs["maires"], kwargs["mairies"])
        )
        print(f"Ajouté {len(elus)} maires avec leurs coordonnées")


def merge_csv(tsv_maires, csv_mairies):
    df = pd.merge(
        pd.read_csv(tsv_maires, sep="\t", dtype=str),
        nettoie_mairies(pd.read_csv(csv_mairies, sep=",", dtype=str)),
        left_on="Code de la commune",
        right_on="codeInsee",
        validate="one_to_one",
    )
    df.fillna("", inplace=True)
    for _, row in df.iterrows():
        yield dict(row)
