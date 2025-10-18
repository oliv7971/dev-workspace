# Récupération des Dernières Auscultations GHA

Ce programme récupère automatiquement les dernières mesures d'auscultation depuis les fichiers Excel des différents secteurs GHA.

## Prérequis

Installer les dépendances Python :
`
pip install pandas openpyxl
`

## Utilisation

### Utilisation basique
`
py recupDernieresAuscultations_GHA.py
`
Récupère les 10 dernières lignes de chaque fichier et génère dernieres_auscultations_GHA.csv

### Options disponibles

- -o, --output : Nom du fichier CSV de sortie
- -n, --lignes : Nombre de lignes à récupérer (défaut: 10)
- -v, --verbose : Mode verbeux (affiche plus d'informations)
- --base : Répertoire de base (si différent du défaut)

### Exemples

`
# Récupérer les 5 dernières lignes avec logs détaillés
py recupDernieresAuscultations_GHA.py -n 5 -v

# Spécifier un fichier de sortie personnalisé
py recupDernieresAuscultations_GHA.py -o "auscultations_20250902.csv"

# Mode très verbeux pour déboguer
py recupDernieresAuscultations_GHA.py -vv
`

## Structure des données

Le programme traite les répertoires suivants :
- 01-GVA105-106
- 02-GHA-04-05
- 03-GHA-T15
- 04-GHA-T28
- 05-GHA-T41

Pour chaque répertoire, il :
1. Cherche le fichier .xlsm
2. Lit l'onglet 'DATABASE'
3. Récupère les colonnes AD, AE, AF, AG
4. Exporte les dernières lignes en CSV

## Format du CSV de sortie

Le fichier CSV généré contient :
- Colonne 1 : Nom du répertoire
- Colonne 2 : Index de ligne Excel
- Colonnes 3-6 : Valeurs des colonnes AD, AE, AF, AG

Séparateur : point-virgule (;)
Encodage : UTF-8
