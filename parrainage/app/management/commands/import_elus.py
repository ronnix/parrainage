# Copyright 2017 Raphaël Hertzog
#
# This file is subject to the license terms in the LICENSE file found in
# the top-level directory of this distribution.

import argparse
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from parrainage.app.models import Elu
from parrainage.app.sources.rne import charge_rne, parse_elu


MANDAT = {
    "CC": "Président de communauté de communes",
    "CD": "Conseiller départemental",
    "CP": "Conseiller de Paris",
    "CR": "Conseiller régional",
    "D": "Député",
    "DE": "Député européen",
    "S": "Sénateur",
    "SP": "Membre de l’assemblée d’une collectivité à statut particulier",
}


class Command(BaseCommand):
    help = "Importer les données du RNE sur des élus (hors maires)"

    def add_arguments(self, parser):
        parser.add_argument(
            "csvfile",
            help="fichier rne-xxx.csv du RNE",
            type=argparse.FileType(mode="r", encoding="utf-8"),
        )
        parser.add_argument(
            "--mandat",
            help="Type de mandat",
            choices=["CC", "CD", "CP", "CR", "D", "DE", "S", "SP"],
            required=True,
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        nouveaux_elus = []
        nb_elus_mis_a_jour = 0
        for _, row in charge_rne(kwargs["csvfile"]).iterrows():
            mandat = kwargs["mandat"]
            fonction = row.get("Libellé de la fonction", "")

            # Seulement les présidents pour les communautés de communes
            if mandat == "CC" and fonction != "Président du conseil communautaire":
                continue

            # Seulement Paris pour les conseillers municipaux
            if mandat == "CP" and row["Code du département"] != "75":
                continue

            # Pas de code rôle pour les présidents de communauté de communes, ni pour
            # les élus de collectivités à statut particulier
            if mandat in ("CC", "SP"):
                role = "A"
            # Le Conseil de Paris a les responsabilités d’un conseil départemental
            elif mandat == "CP":
                role = "CD"
            else:
                role = mandat

            elu = parse_elu(row, role)
            try:
                elu_existant = Elu.objects.get(
                    first_name=elu.first_name,
                    family_name=elu.family_name,
                    birthdate=elu.birthdate,
                )
                if elu_existant.role == elu.role:
                    continue
                else:
                    annotation = f"\nAutre mandat: {MANDAT[mandat]}"
                    if fonction:
                        annotation += f"({fonction})"
                    if annotation not in elu_existant.comment:
                        elu_existant.comment += annotation
                        elu_existant.save()
                        nb_elus_mis_a_jour += 1
            except Elu.DoesNotExist:
                if fonction:
                    elu.comment += f"\n{fonction}"
                nouveaux_elus.append(elu)
            except Elu.MultipleObjectsReturned:
                logging.error(
                    "Il y a plusieurs %s %s né(e)s le %s",
                    elu.first_name,
                    elu.family_name,
                    elu.birthdate,
                )
        Elu.objects.bulk_create(nouveaux_elus)
        print(
            f"Ajouté {len(nouveaux_elus)} élus et mis à jour {nb_elus_mis_a_jour} élus existants."
        )
