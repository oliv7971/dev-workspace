#!/usr/bin/env python3
"""
Corriger les formules pour tenir compte des 8 lignes d'en-tête
"""

import openpyxl
from openpyxl.utils import get_column_letter

def fix_formulas_for_headers():
    """Corrige les formules pour tenir compte des 8 lignes d'en-tête"""

    input_file = "AUSCULTATION_AVEC_FORMULES.xlsx"
    output_file = "AUSCULTATION_FORMULES_CORRIGEES.xlsx"

    print(f"🔧 Correction des formules pour 8 lignes d'en-tête...")
    print(f"📂 Entrée: {input_file}")
    print(f"📁 Sortie: {output_file}")

    # Ouvrir le fichier
    wb = openpyxl.load_workbook(input_file)
    ws_obs = wb['Observations']

    print("📊 Analyse des colonnes existantes...")

    # Identifier les colonnes des cibles
    target_columns = {}
    header_row = 1  # Ligne actuelle des en-têtes

    for col in range(1, ws_obs.max_column + 1):
        header = ws_obs.cell(header_row, col).value
        if header and '_' in str(header):  # Colonnes type "V1_X", "V2_Y", etc.
            target_columns[col] = str(header)

    print(f"🎯 {len(target_columns)} colonnes de cibles trouvées")

    # Déplacer les en-têtes à la ligne 9
    print("📝 Déplacement des en-têtes vers la ligne 9...")

    new_header_row = 9
    new_data_start_row = 10

    # Copier les en-têtes vers la ligne 9
    for col in range(1, ws_obs.max_column + 1):
        old_header = ws_obs.cell(header_row, col).value
        ws_obs.cell(new_header_row, col).value = old_header
        # Effacer l'ancienne ligne
        ws_obs.cell(header_row, col).value = None

    # Effacer les anciennes données (lignes 2-8)
    for row in range(2, 9):
        for col in range(1, ws_obs.max_column + 1):
            ws_obs.cell(row, col).value = None

    print("⚡ Recréation des formules avec les bonnes références...")

    # Recréer les formules avec les bonnes références de ligne
    for col, col_name in target_columns.items():
        parts = col_name.split('_')
        if len(parts) == 2:
            target_code, coord_type = parts
            db_coord_col = coord_type

            print(f"   🔗 {get_column_letter(col)} ({col_name}) -> lignes {new_data_start_row}+")

            # Ajouter les formules pour les lignes de données (à partir de la ligne 10)
            for row in range(new_data_start_row, new_data_start_row + 15):
                try:
                    # Formule corrigée avec les bonnes références de ligne
                    formula = f'=IFERROR(INDEX(DATABASE.{db_coord_col}:{db_coord_col},MATCH(1,(DATABASE.DATE:DATE=$A{row})*(DATABASE.NO:NO="{target_code}"),0)),"")'

                    ws_obs.cell(row, col).value = formula

                except Exception as e:
                    print(f"      ⚠️ Erreur {get_column_letter(col)}{row}: {e}")

    print("📅 Ajout des dates d'exemple à partir de la ligne 10...")

    # Ajouter les dates d'exemple à partir de la ligne 10
    sample_dates = [
        '2024-08-28', '2024-09-05', '2024-09-09',
        '2024-09-13', '2024-09-17', '2024-09-18'
    ]

    for i, date in enumerate(sample_dates):
        row = new_data_start_row + i  # Ligne 10, 11, 12, etc.
        ws_obs.cell(row, 1).value = date  # Colonne A = Date

        # Colonne B = Jours écoulés
        if i == 0:
            ws_obs.cell(row, 2).value = 0
        else:
            ws_obs.cell(row, 2).value = f"=A{row}-A${new_data_start_row}"

    # Ajouter des en-têtes explicatifs
    ws_obs.cell(7, 1).value = "Date point 0"
    ws_obs.cell(8, 1).value = "Date"
    ws_obs.cell(8, 2).value = "Jours"

    # Sauvegarder
    wb.save(output_file)
    wb.close()

    print(f"✅ Fichier corrigé sauvé: {output_file}")
    return output_file

def create_layout_info():
    """Crée un fichier avec la disposition finale"""

    layout_info = """
📋 DISPOSITION FINALE DU FICHIER CORRIGÉ

ONGLET "Observations":

Ligne 7: "Date point 0" (information)
Ligne 8: "Date" | "Jours" | (en-têtes des colonnes)
Ligne 9: "Date" | "Jours" | "V1_X" | "V1_Y" | "V1_Z" | "V2_X" | ... (en-têtes des cibles)
Ligne 10: 2024-08-28 | 0 | [formule] | [formule] | [formule] | ... (première ligne de données)
Ligne 11: 2024-09-05 | 8 | [formule] | [formule] | [formule] | ... (deuxième ligne de données)
...

COLONNES DES CIBLES (à partir de la colonne C):
C: V1_X    D: V1_Y    E: V1_Z
F: V2_X    G: V2_Y    H: V2_Z
I: V3_X    J: V3_Y    K: V3_Z
L: H1_X    M: H1_Y    N: H1_Z
O: H2_X    P: H2_Y    Q: H2_Z
R: H3_X    S: H3_Y    T: H3_Z
U: H4_X    V: H4_Y    W: H4_Z
X: H5_X    Y: H5_Y    Z: H5_Z
AA: B1_X   AB: B1_Y   AC: B1_Z
AD: B2_X   AE: B2_Y   AF: B2_Z
AG: B3_X   AH: B3_Y   AI: B3_Z
AJ: B4_X   AK: B4_Y   AL: B4_Z
AM: B5_X   AN: B5_Y   AO: B5_Z
AP: M1_X   AQ: M1_Y   AR: M1_Z
AS: M2_X   AT: M2_Y   AU: M2_Z
AV: M3_X   AW: M3_Y   AX: M3_Z
AY: M4_X   AZ: M4_Y   BA: M4_Z
BB: M5_X   BC: M5_Y   BD: M5_Z
BE: REF1_X BF: REF1_Y BG: REF1_Z
BH: REF2_X BI: REF2_Y BJ: REF2_Z

FORMULES:
Chaque cellule de données contient:
=IFERROR(INDEX(DATABASE.X:X,MATCH(1,(DATABASE.DATE:DATE=$A10)*(DATABASE.NO:NO="V1"),0)),"")

Les références de ligne commencent à A10, A11, A12, etc.
"""

    with open("DISPOSITION_FINALE.txt", "w", encoding="utf-8") as f:
        f.write(layout_info)

    print("📝 Disposition sauvée: DISPOSITION_FINALE.txt")

if __name__ == "__main__":
    print("🚀 Correction des formules pour les 8 lignes d'en-tête...")

    try:
        corrected_file = fix_formulas_for_headers()
        create_layout_info()

        print(f"\\n🎉 FORMULES CORRIGÉES!")
        print(f"📁 Fichier prêt: {corrected_file}")
        print(f"📝 Disposition: DISPOSITION_FINALE.txt")

        print(f"\\n💡 MAINTENANT:")
        print(f"1. Ouvrez {corrected_file}")
        print(f"2. Les en-têtes sont en ligne 9")
        print(f"3. Les données commencent en ligne 10")
        print(f"4. Les formules pointent vers $A10, $A11, etc.")
        print(f"5. Vous pouvez copier-coller sans décalage!")

    except Exception as e:
        print(f"❌ Erreur: {e}")
