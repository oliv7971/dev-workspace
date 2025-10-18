#!/usr/bin/env python3
"""
Script pour créer une version propre du fichier Excel étendu
Évite les problèmes de cellules fusionnées en recréant la structure
"""

import openpyxl
from openpyxl.utils import get_column_letter
import shutil

def create_clean_extended_file(original_filename, output_filename):
    """Crée une version propre du fichier étendu"""
    print("🔧 Création d'une version propre du fichier étendu...")

    # Copier le fichier original
    shutil.copy2(original_filename, output_filename)
    print(f"✅ Fichier copié: {output_filename}")

    # Ouvrir et nettoyer
    wb = openpyxl.load_workbook(output_filename, data_only=False)
    ws = wb['Résultats observations']

    # Définir les nouvelles cibles
    new_targets = []
    # 3 Voûtes
    for i in range(1, 4):
        new_targets.append(f"V{i}")
    # 5 Haut
    for i in range(1, 6):
        new_targets.append(f"H{i}")
    # 5 Bas
    for i in range(1, 6):
        new_targets.append(f"B{i}")
    # 5 Milieu
    for i in range(1, 6):
        new_targets.append(f"M{i}")
    # 2 Références
    new_targets.extend(["REF1", "REF2"])

    print(f"🎯 Ajout de {len(new_targets)} nouvelles cibles...")

    # Commencer à partir de la colonne O (15)
    start_col = 15
    current_col = start_col

    for target_id in new_targets:
        print(f"   📍 {target_id} -> colonnes {get_column_letter(current_col)}-{get_column_letter(current_col+2)}")

        # Ajouter les en-têtes pour X, Y, Z
        for coord_idx, coord in enumerate(['X', 'Y', 'Z']):
            col = current_col + coord_idx
            col_letter = get_column_letter(col)

            # En-têtes
            ws[f'{col_letter}4'] = target_id
            ws[f'{col_letter}5'] = ['3', '4', '5'][coord_idx]
            ws[f'{col_letter}9'] = coord

            if coord_idx == 0:  # Première colonne de la cible
                ws[f'{col_letter}8'] = f"CHP_{target_id} ({target_id})"
                ws[f'{col_letter}7'] = 'BG'
            elif coord_idx == 2:  # Dernière colonne
                ws[f'{col_letter}7'] = 'HG'

            # Ajouter les formules pour les lignes de données
            for row in range(10, 51):
                # Colonnes DATABASE: AB=Date, AC=NO, AD=Matricule, AE=X, AF=Y, AG=Z
                db_cols = {'X': 'AE', 'Y': 'AF', 'Z': 'AG'}
                db_col = db_cols[coord]

                formula = f'=IFERROR(INDEX(DATABASE.{db_col}:{db_col},MATCH(1,(DATABASE.AB:AB=$A{row})*(DATABASE.AC:AC="{target_id}"),0)),"")'
                ws[f'{col_letter}{row}'] = formula

        current_col += 3

    # Sauvegarder
    wb.save(output_filename)
    wb.close()

    print(f"✅ Fichier propre créé: {output_filename}")

def test_file_integrity(filename):
    """Teste l'intégrité du fichier créé"""
    print(f"🔍 Test d'intégrité du fichier: {filename}")

    try:
        wb = openpyxl.load_workbook(filename, data_only=False)

        # Tester l'accès aux onglets
        sheets = wb.sheetnames
        print(f"   📋 Onglets trouvés: {sheets}")

        # Tester l'onglet Résultats observations
        if 'Résultats observations' in sheets:
            ws = wb['Résultats observations']
            print(f"   📊 Dimensions: {ws.max_row} lignes × {ws.max_column} colonnes")

            # Tester quelques cellules
            test_cells = ['O4', 'O10', 'P10', 'BT4']
            for cell_ref in test_cells:
                value = ws[cell_ref].value
                print(f"   🔗 {cell_ref}: {str(value)[:50]}...")

        # Tester l'onglet DATABASE
        if 'DATABASE' in sheets:
            ws_db = wb['DATABASE']
            print(f"   💾 DATABASE dimensions: {ws_db.max_row} lignes × {ws_db.max_column} colonnes")

        wb.close()
        print("✅ Fichier intègre et lisible")
        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    original = "01_51-B-GER-HA21_3-PM_135-25-05-21.xlsm"
    output = "01_51-B-GER-HA21_3-PM_135-25-05-21_CLEAN.xlsm"

    # Créer le fichier propre
    create_clean_extended_file(original, output)

    # Tester l'intégrité
    test_file_integrity(output)

    print("🎉 Terminé !")
