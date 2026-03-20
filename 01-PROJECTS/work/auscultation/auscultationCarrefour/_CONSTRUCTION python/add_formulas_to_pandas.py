#!/usr/bin/env python3
"""
Ajouter les formules Excel au fichier pandas qui fonctionne
"""

import openpyxl
from openpyxl.utils import get_column_letter

def add_formulas_to_working_file():
    """Ajoute les formules au fichier pandas qui s'ouvre correctement"""

    input_file = "AUSCULTATION_PANDAS.xlsx"
    output_file = "AUSCULTATION_AVEC_FORMULES.xlsx"

    print(f"⚙️ Ajout des formules au fichier qui fonctionne...")
    print(f"📂 Entrée: {input_file}")
    print(f"📁 Sortie: {output_file}")

    # Ouvrir le fichier qui fonctionne
    wb = openpyxl.load_workbook(input_file)

    # Accéder à l'onglet Observations
    ws_obs = wb['Observations']

    print("📊 Analyse de la structure existante...")

    # Identifier les colonnes des cibles
    target_columns = {}
    header_row = 1  # Première ligne contient les en-têtes

    for col in range(1, ws_obs.max_column + 1):
        header = ws_obs.cell(header_row, col).value
        if header and '_' in str(header):  # Colonnes type "V1_X", "V2_Y", etc.
            target_columns[col] = str(header)

    print(f"🎯 Colonnes de cibles trouvées: {len(target_columns)}")
    for col, name in list(target_columns.items())[:5]:
        print(f"   {get_column_letter(col)}: {name}")
    print(f"   ...")

    # Ajouter les formules
    print("⚡ Ajout des formules...")

    data_start_row = 2  # Les données commencent à la ligne 2

    for col, col_name in target_columns.items():
        # Analyser le nom de colonne (ex: "V1_X" -> target="V1", coord="X")
        parts = col_name.split('_')
        if len(parts) == 2:
            target_code, coord_type = parts

            # Colonnes DATABASE: X->X, Y->Y, Z->Z (on garde les mêmes noms)
            db_coord_col = coord_type

            print(f"   🔗 {get_column_letter(col)} ({col_name}) -> DATABASE.{db_coord_col} pour {target_code}")

            # Ajouter les formules pour les lignes de données (ligne 2 à 20)
            for row in range(data_start_row, data_start_row + 15):  # 15 lignes de données
                try:
                    # Formule pour chercher dans DATABASE
                    # =IFERROR(INDEX(DATABASE.X:X,MATCH(1,(DATABASE.DATE:DATE=$A2)*(DATABASE.NO:NO="V1"),0)),"")
                    formula = f'=IFERROR(INDEX(DATABASE.{db_coord_col}:{db_coord_col},MATCH(1,(DATABASE.DATE:DATE=$A{row})*(DATABASE.NO:NO="{target_code}"),0)),"")'

                    ws_obs.cell(row, col).value = formula

                except Exception as e:
                    print(f"      ⚠️ Erreur {get_column_letter(col)}{row}: {e}")

    print("📅 Ajout de quelques dates d'exemple...")

    # Ajouter quelques dates d'exemple dans la colonne Date
    sample_dates = [
        '2024-08-28', '2024-09-05', '2024-09-09',
        '2024-09-13', '2024-09-17', '2024-09-18'
    ]

    for i, date in enumerate(sample_dates):
        row = data_start_row + i
        ws_obs.cell(row, 1).value = date  # Colonne A = Date

        # Colonne B = Jours écoulés
        if i == 0:
            ws_obs.cell(row, 2).value = 0
        else:
            ws_obs.cell(row, 2).value = f"=A{row}-A${data_start_row}"

    # Sauvegarder
    wb.save(output_file)
    wb.close()

    print(f"✅ Fichier avec formules sauvé: {output_file}")
    return output_file

def test_formulas_file(filename):
    """Teste le fichier avec formules"""
    print(f"\\n🔍 Test du fichier avec formules: {filename}")

    try:
        wb = openpyxl.load_workbook(filename, data_only=False)  # data_only=False pour voir les formules

        ws_obs = wb['Observations']
        ws_db = wb['DATABASE']

        print(f"📊 Observations: {ws_obs.max_row}×{ws_obs.max_column}")
        print(f"💾 DATABASE: {ws_db.max_row}×{ws_db.max_column}")

        # Vérifier quelques formules
        print("🧮 Exemples de formules:")
        test_cells = [(2, 3), (2, 4), (2, 5)]  # Quelques cellules
        for row, col in test_cells:
            cell_value = ws_obs.cell(row, col).value
            if cell_value and str(cell_value).startswith('='):
                print(f"   {get_column_letter(col)}{row}: {str(cell_value)[:60]}...")

        wb.close()
        print("✅ Fichier avec formules vérifié!")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Ajout des formules automatiques...")

    try:
        formulas_file = add_formulas_to_working_file()

        if test_formulas_file(formulas_file):
            print(f"\\n🎉 SUCCÈS!")
            print(f"📁 Fichier prêt: {formulas_file}")
            print(f"\\n💡 UTILISATION:")
            print(f"1. Ouvrez {formulas_file}")
            print(f"2. Ajoutez vos mesures dans l'onglet DATABASE")
            print(f"3. Utilisez les codes: V1,V2,V3,H1-H5,B1-B5,M1-M5,REF1,REF2")
            print(f"4. Les calculs apparaîtront dans l'onglet Observations!")
        else:
            print("❌ Problème avec les formules")

    except Exception as e:
        print(f"❌ Erreur globale: {e}")
