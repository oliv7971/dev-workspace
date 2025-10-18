#!/usr/bin/env python3
"""
Création d'un fichier Excel avec pandas/openpyxl en format .xlsx (plus simple)
"""

import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter

def create_simple_xlsx():
    """Crée un fichier .xlsx simple avec pandas"""

    print("📊 Création d'un fichier .xlsx simple avec pandas...")

    # Créer les données de base avec pandas

    # === Onglet DATABASE ===
    print("💾 Création des données DATABASE...")

    # Données d'exemple pour la DATABASE
    database_data = {
        'DATE': ['2024-08-28', '2024-08-28', '2024-09-05', '2024-09-05'],
        'NO': ['V1', 'V2', 'V1', 'V2'],
        'MATRICULE': ['V1.Test', 'V2.Test', 'V1.Test', 'V2.Test'],
        'X': [823147.6488, 823147.5852, 823147.6490, 823147.5860],
        'Y': [1091710.0857, 1091710.2506, 1091710.0850, 1091710.2510],
        'Z': [-121.5674, -121.9302, -121.5690, -121.9310]
    }

    df_database = pd.DataFrame(database_data)

    # === Onglet OBSERVATIONS ===
    print("📊 Création des données Observations...")

    # Dates pour l'observation
    dates = ['2024-08-28', '2024-09-05', '2024-09-09', '2024-09-13', '2024-09-17']

    # Créer le DataFrame de base pour les observations
    obs_data = {
        'Date': dates,
        'Jours': [0, 8, 12, 16, 20]
    }

    # Ajouter les colonnes pour les 20 cibles
    targets = []
    for i in range(1, 4): targets.append(f"V{i}")
    for i in range(1, 6): targets.append(f"H{i}")
    for i in range(1, 6): targets.append(f"B{i}")
    for i in range(1, 6): targets.append(f"M{i}")
    targets.extend(["REF1", "REF2"])

    print(f"🎯 Ajout des colonnes pour {len(targets)} cibles...")

    # Ajouter une colonne X, Y, Z pour chaque cible
    for target in targets:
        obs_data[f"{target}_X"] = [None] * len(dates)  # Vides pour l'instant
        obs_data[f"{target}_Y"] = [None] * len(dates)
        obs_data[f"{target}_Z"] = [None] * len(dates)

    df_observations = pd.DataFrame(obs_data)

    # === Sauvegarder avec pandas ===
    output_file = "AUSCULTATION_PANDAS.xlsx"

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_database.to_excel(writer, sheet_name='DATABASE', index=False)
        df_observations.to_excel(writer, sheet_name='Observations', index=False)

    print(f"✅ Fichier pandas créé: {output_file}")
    return output_file

def create_csv_alternative():
    """Crée des fichiers CSV comme alternative"""

    print("📄 Création d'une alternative CSV...")

    # DATABASE CSV
    database_data = {
        'DATE': ['2024-08-28', '2024-08-28', '2024-09-05', '2024-09-05'],
        'NO': ['V1', 'V2', 'V1', 'V2'],
        'MATRICULE': ['V1.Test', 'V2.Test', 'V1.Test', 'V2.Test'],
        'X': [823147.6488, 823147.5852, 823147.6490, 823147.5860],
        'Y': [1091710.0857, 1091710.2506, 1091710.0850, 1091710.2510],
        'Z': [-121.5674, -121.9302, -121.5690, -121.9310]
    }

    df_db = pd.DataFrame(database_data)
    df_db.to_csv("DATABASE_AUSCULTATION.csv", index=False, encoding='utf-8')

    # Structure pour les observations
    targets = []
    for i in range(1, 4): targets.append(f"V{i}")
    for i in range(1, 6): targets.append(f"H{i}")
    for i in range(1, 6): targets.append(f"B{i}")
    for i in range(1, 6): targets.append(f"M{i}")
    targets.extend(["REF1", "REF2"])

    # Créer les en-têtes pour CSV
    headers = ['Date', 'Jours']
    for target in targets:
        headers.extend([f"{target}_X", f"{target}_Y", f"{target}_Z"])

    # CSV vide prêt à remplir
    df_obs = pd.DataFrame(columns=headers)
    df_obs.to_csv("OBSERVATIONS_TEMPLATE.csv", index=False, encoding='utf-8')

    print("✅ Fichiers CSV créés:")
    print("   - DATABASE_AUSCULTATION.csv")
    print("   - OBSERVATIONS_TEMPLATE.csv")

    return ["DATABASE_AUSCULTATION.csv", "OBSERVATIONS_TEMPLATE.csv"]

def create_instructions():
    """Crée un fichier d'instructions détaillées"""

    instructions = """
🎯 INSTRUCTIONS POUR VOTRE SYSTÈME D'AUSCULTATION 20 CIBLES

PROBLÈME RENCONTRÉ:
Les fichiers .xlsm générés par Python ne s'ouvrent pas correctement sur votre système.

SOLUTIONS ALTERNATIVES:

=== SOLUTION 1: Fichier .xlsx simple ===
Fichier créé: AUSCULTATION_PANDAS.xlsx
- Format .xlsx (plus compatible)
- Créé avec pandas (plus stable)
- Structure de base prête

=== SOLUTION 2: Fichiers CSV ===
Fichiers créés:
- DATABASE_AUSCULTATION.csv (données brutes)
- OBSERVATIONS_TEMPLATE.csv (template calculs)

Vous pouvez ouvrir ces CSV dans Excel et les convertir en .xlsx

=== SOLUTION 3: Créer manuellement dans Excel ===

1. STRUCTURE DATABASE (Onglet 1):
   Colonnes: DATE | NO | MATRICULE | X | Y | Z

2. STRUCTURE OBSERVATIONS (Onglet 2):
   Colonnes: Date | Jours | V1_X | V1_Y | V1_Z | V2_X | V2_Y | V2_Z | ...

   Pour chaque cible: V1,V2,V3,H1,H2,H3,H4,H5,B1,B2,B3,B4,B5,M1,M2,M3,M4,M5,REF1,REF2

3. FORMULES À AJOUTER:
   Dans chaque cellule de coordonnée (ex: V1_X):
   =IFERROR(INDEX(DATABASE.X:X,MATCH(1,(DATABASE.DATE:DATE=$A2)*(DATABASE.NO:NO="V1"),0)),"")

   Remplacez:
   - "V1" par le code de la cible
   - DATABASE.X:X par DATABASE.Y:Y ou DATABASE.Z:Z selon la coordonnée

=== VOS 20 CIBLES ===
V1, V2, V3 (Voûtes)
H1, H2, H3, H4, H5 (Haut)
B1, B2, B3, B4, B5 (Bas)
M1, M2, M3, M4, M5 (Milieu)
REF1, REF2 (Références)

UTILISATION:
1. Ajoutez vos mesures dans DATABASE avec les codes ci-dessus
2. Les calculs apparaîtront automatiquement dans OBSERVATIONS
3. Vous aurez vos déports et analyses pour les 20 cibles

Si aucune solution ne fonctionne, le problème peut être:
- Version d'Excel incompatible avec les fichiers générés
- Problème de permissions/sécurité
- Besoin d'une version plus récente d'openpyxl/pandas
"""

    with open("INSTRUCTIONS_AUSCULTATION.txt", "w", encoding="utf-8") as f:
        f.write(instructions)

    print("📝 Instructions détaillées sauvées: INSTRUCTIONS_AUSCULTATION.txt")

if __name__ == "__main__":
    print("🚀 Création de solutions alternatives...")

    # Essayer le format .xlsx avec pandas
    try:
        xlsx_file = create_simple_xlsx()
        print(f"✅ Fichier .xlsx créé: {xlsx_file}")
    except Exception as e:
        print(f"❌ Erreur .xlsx: {e}")

    # Créer les CSV de secours
    try:
        csv_files = create_csv_alternative()
        print(f"✅ Fichiers CSV créés")
    except Exception as e:
        print(f"❌ Erreur CSV: {e}")

    # Créer les instructions
    create_instructions()

    print(f"\n🎉 SOLUTIONS ALTERNATIVES CRÉÉES!")
    print(f"📁 Fichiers disponibles:")
    print(f"   - AUSCULTATION_PANDAS.xlsx (essayez celui-ci)")
    print(f"   - DATABASE_AUSCULTATION.csv")
    print(f"   - OBSERVATIONS_TEMPLATE.csv")
    print(f"   - INSTRUCTIONS_AUSCULTATION.txt")

    print(f"\n💡 ESSAYEZ D'ABORD: AUSCULTATION_PANDAS.xlsx")
    print(f"   Si ça ne marche pas, consultez INSTRUCTIONS_AUSCULTATION.txt")
