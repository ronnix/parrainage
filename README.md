# Outil de suivi des parrainages

## Sources de données

- [Répertoire national des élus](https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/)
- [Annuaire de l’administration](https://www.data.gouv.fr/fr/datasets/service-public-fr-annuaire-de-l-administration-base-de-donnees-locales/)


## Installation locale

### Pré-requis

- Python 3.7.x


### Installer

Créer un virtualenv :
```
python3.7 -m venv venv
source venv/bin/activate
```

Installer les dépendances Python :
```
pip install -r requirements.txt -r requirements-dev.txt
```


### Configurer la base de données

Par défaut, l’application utilisera une base de données SQLite (dans `parrainage/db.sqlite3`).

Pour créer les tables, il faut appliquer les migrations :
```
python manage.py migrate
```


### Charger les données

#### Liste des maires

- Récupérer `rne-maires.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/2876a346-d50c-4911-934e-19ee07b0e503
```

- Récupérer `mairies.csv` depuis https://www.data.gouv.fr/fr/datasets/service-public-fr-annuaire-de-l-administration-base-de-donnees-locales/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/953465b8-35a3-4e54-89cd-0b9766503ff9
```

- Récupérer et dézipper `ensemble.zip` depuis https://www.insee.fr/fr/statistiques/6011070?sommaire=6011075
```
wget https://www.insee.fr/fr/statistiques/fichier/6011070/ensemble.zip
unzip ensemble.zip
```

- Lancer la commande :
```
python manage.py import_maires rne-maires.csv mairies.csv donnees_communes.csv
```

#### Liste des maires délégués

- Récupérer `rne-cm.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/d5f400de-ae3f-4966-8cb6-a85c70c6c24a
```

- Lancer la commande :
```
python manage.py import_elus --mandat=MD rne-cm.csv
```


#### Liste des présidents de communautés de communes

- Récupérer `rne-epci.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/41d95d7d-b172-4636-ac44-32656367cdc7
```

- Lancer la commande :
```
python manage.py import_elus --mandat=CC rne-epci.csv
```


#### Liste des conseillers départementaux

- Récupérer `rne-cd.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/601ef073-d986-4582-8e1a-ed14dc857fba
```

- Lancer la commande :
```
python manage.py import_elus --mandat=CD rne-cd.csv
```

#### Liste des conseillers de Paris

- Récupérer (si ce n’est déjà fait) `rne-cm.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/d5f400de-ae3f-4966-8cb6-a85c70c6c24a
```

- Lancer la commande :
```
python manage.py import_elus --mandat=CP rne-cm.csv
```

#### Liste des conseillers régionaux

- Récupérer `rne-cr.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/430e13f9-834b-4411-a1a8-da0b4b6e715c
```

- Lancer la commande :
```
python manage.py import_elus --mandat=CR rne-cr.csv
```

#### Liste des élus des collectivités à statut particulier

- Récupérer `rne-ma.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/a595be27-cfab-4810-b9d4-22e193bffe35
```

- Lancer la commande :
```
python manage.py import_elus --mandat=SP rne-ma.csv
```

#### Liste des sénateurs

- Récupérer `rne-sen.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/b78f8945-509f-4609-a4a7-3048b8370479
```

- Lancer la commande :
```
python manage.py import_elus --mandat=S rne-sen.csv
```


#### Liste des députés

- Récupérer `rne-dep.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/1ac42ff4-1336-44f8-a221-832039dbc142
```

- Lancer la commande :
```
python manage.py import_elus --mandat=D rne-dep.csv
```


#### Liste des représentants au parlement européen

- Récupérer `rne-rpe.csv` depuis https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/
```
wget --content-disposition https://www.data.gouv.fr/fr/datasets/r/70957bb0-f19f-40c5-b97b-90b3d4d71f9e
```

- Lancer la commande :
```
python manage.py import_elus --mandat=DE rne-rpe.csv
```



#### Parrainages déjà validés

- Télécharger le CSV depuis https://presidentielle2022.conseil-constitutionnel.fr/les-parrainages/tous-les-parrainages-valides.html
```
wget https://presidentielle2022.conseil-constitutionnel.fr/telechargement/parrainagestotal.csv
```

- Lancer la commande :
```
python manage.py import_parrainages parrainagestotal.csv --candidate="TAUBIRA Christiane"
```

La correspondance entre la liste du CC et celle du RNE n’est pas robuste (par manque d’un identifiant unique), donc 100% des parrainages ne pourront pas attribués, et quelques mises à jour manuelles pourront être requises.


### Créer un super-utilisateur

```
python manage.py createsuperuser
```


### Lancer un serveur local

```
python manage.py collectstatic
ALLOWED_HOSTS=127.0.0.1 python manage.py runserver
```


### Lancer les tests

```
pytest
```

ou, pour les lancer en continu :

```
ptw
```
