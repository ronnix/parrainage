# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-02-21 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_elu_public_assign_count"),
    ]

    operations = [
        migrations.AlterField(
            model_name="elu",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("H", "Homme"), ("F", "Femme"), ("", "Inconnu")],
                max_length=1,
                verbose_name="genre",
            ),
        ),
        migrations.AlterField(
            model_name="elu",
            name="status",
            field=models.IntegerField(
                choices=[
                    (1, "Rien n'a été fait"),
                    (2, "Démarches en cours"),
                    (3, "Christiane Taubira doit recontacter l'élu"),
                    (4, "L'élu souhaite être recontacté"),
                    (5, "Parrainage bloqué"),
                    (10, "Parrainage refusé"),
                    (20, "Parrainage accepté"),
                    (30, "Parrainage reçu par le conseil constitutionnel"),
                ],
                db_index=True,
                default=1,
                verbose_name="statut",
            ),
        ),
    ]
