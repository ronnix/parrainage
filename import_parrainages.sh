#!/bin/bash
set -o errexit
set -o verbose
wget https://presidentielle2022.conseil-constitutionnel.fr/telechargement/parrainagestotal.csv
python manage.py import_parrainages parrainagestotal.csv --candidate="TAUBIRA Christiane"
