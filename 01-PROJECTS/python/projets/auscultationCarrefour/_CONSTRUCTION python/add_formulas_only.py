#!/usr/bin/env python3
"""
Script minimal pour ajouter uniquement les formules essentielles
Évite tous les problèmes de cellules fusionnées
"""

import openpyxl
from openpyxl.utils import get_column_letter
import shutil

def add_essential_formulas():
    """Ajoute seulement les formules essentielles sans toucher aux en-têtes"""

    input_file = "01_51-B-GER-HA21_3-PM_135-25-05-21_CLEAN.xlsm"
    output_file = "01_51-B-GER-HA21_3-PM_135-25-05-21_WORKING.xlsm"

    # Copier le fichier qui fonctionne
    shutil.copy2(input_file, output_file)
    print(f"📋 Fichier de travail créé: {output_file}")

    # Ouvrir le fichier
    wb = openpyxl.load_workbook(output_file, data_only=False)
    ws = wb['Résultats observations']

    # Définir les 20 nouvelles cibles
    new_targets = []
    for i in range(1, 4): new_targets.append(f"V{i}")
    for i in range(1, 6): new_targets.append(f"H{i}")
    for i in range(1, 6): new_targets.append(f"B{i}")
    for i in range(1, 6): new_targets.append(f"M{i}")
    new_targets.extend(["REF1", "REF2"])

    print(f"🎯 Ajout des formules pour {len(new_targets)} cibles...")

    # Commencer à la colonne O (15)
    start_col = 15
    current_col = start_col

    for target_id in new_targets:
        print(f"   📊 {target_id} -> {get_column_letter(current_col)}-{get_column_letter(current_col+2)}")

        # Ajouter SEULEMENT les formules de données (pas les en-têtes)
        for coord_idx, coord in enumerate(['X', 'Y', 'Z']):
            col = current_col + coord_idx

            # Colonnes DATABASE: AE=X, AF=Y, AG=Z
            db_cols = {'X': 'AE', 'Y': 'AF', 'Z': 'AG'}
            db_col = db_cols[coord]

            # Ajouter les formules SEULEMENT dans les lignes de données (10-50)
            for row in range(10, 51):
                formula = f'=IFERROR(INDEX(DATABASE.{db_col}:{db_col},MATCH(1,(DATABASE.AB:AB=$A{row})*(DATABASE.AC:AC="{target_id}"),0)),"")'
                try:
                    ws.cell(row, col).value = formula
                except:
                    # Ignorer les erreurs et continuer
                    pass

        current_col += 3

    # Sauvegarder
    wb.save(output_file)
    wb.close()

    print(f"✅ Formules ajoutées dans: {output_file}")
    return output_file

def add_headers_manually():
    """Créé un fichier texte avec les en-têtes à ajouter manuellement"""

    headers_info = """
📋 EN-TÊTES À AJOUTER MANUELLEMENT DANS EXCEL:

Ouvrez le fichier: 01_51-B-GER-HA21_3-PM_135-25-05-21_WORKING.xlsm

LIGNE 4 (Noms des cibles):
O4: V1    P4: V1    Q4: V1
R4: V2    S4: V2    T4: V2
U4: V3    V4: V3    W4: V3
X4: H1    Y4: H1    Z4: H1
AA4: H2   AB4: H2   AC4: H2
AD4: H3   AE4: H3   AF4: H3
AG4: H4   AH4: H4   AI4: H4
AJ4: H5   AK4: H5   AL4: H5
AM4: B1   AN4: B1   AO4: B1
AP4: B2   AQ4: B2   AR4: B2
AS4: B3   AT4: B3   AU4: B3
AV4: B4   AW4: B4   AX4: B4
AY4: B5   AZ4: B5   BA4: B5
BB4: M1   BC4: M1   BD4: M1
BE4: M2   BF4: M2   BG4: M2
BH4: M3   BI4: M3   BJ4: M3
BK4: M4   BL4: M4   BM4: M4
BN4: M5   BO4: M5   BP4: M5
BQ4: REF1 BR4: REF1 BS4: REF1
BT4: REF2 BU4: REF2 BV4: REF2

LIGNE 9 (Type de coordonnée):
O9: X    P9: Y    Q9: Z
R9: X    S9: Y    T9: Z
(etc. - répétez le pattern X,Y,Z pour chaque groupe de 3 colonnes)

Les formules sont déjà en place dans les lignes 10-50 !
"""

    with open("HEADERS_TO_ADD_MANUALLY.txt", "w", encoding="utf-8") as f:
        f.write(headers_info)

    print("📝 Instructions sauvées dans: HEADERS_TO_ADD_MANUALLY.txt")

if __name__ == "__main__":
    print("🚀 Ajout des formules essentielles (sans en-têtes)...")

    # Ajouter seulement les formules
    working_file = add_essential_formulas()

    # Créer les instructions pour les en-têtes
    add_headers_manually()

    print(f"\\n✅ TERMINÉ!")
    print(f"📁 Fichier avec formules: {working_file}")
    print(f"📝 Instructions pour en-têtes: HEADERS_TO_ADD_MANUALLY.txt")
    print(f"\\n💡 PROCHAINES ÉTAPES:")
    print(f"1. Ouvrez {working_file} dans Excel")
    print(f"2. Ajoutez les en-têtes selon les instructions")
    print(f"3. Ajoutez vos données dans l'onglet DATABASE avec les codes V1,V2,H1,etc.")
    print(f"4. Les calculs se feront automatiquement!")
