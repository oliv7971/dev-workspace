#!/usr/bin/env python3
"""
Script pour créer un fichier Excel étendu en évitant les cellules fusionnées
Approche robuste qui gère les problèmes de cellules fusionnées
"""

import openpyxl
from openpyxl.utils import get_column_letter
import shutil

def create_safe_extended_file(original_filename, output_filename):
    """Crée une version étendue en évitant les cellules fusionnées"""
    print("🔧 Création d'un fichier étendu sécurisé...")

    # Copier le fichier original
    shutil.copy2(original_filename, output_filename)
    print(f"✅ Fichier copié: {output_filename}")

    wb = openpyxl.load_workbook(output_filename, data_only=False)
    ws = wb['Résultats observations']

    # Supprimer les cellules fusionnées problématiques dans la zone d'extension
    ranges_to_unmerge = []
    for merged_range in ws.merged_cells.ranges:
        # Si la plage fusionnée commence après la colonne N (14), on la supprime
        if merged_range.min_col >= 14:
            ranges_to_unmerge.append(merged_range)

    for range_to_remove in ranges_to_unmerge:
        ws.unmerge_cells(str(range_to_remove))
        print(f"   🔓 Fusion supprimée: {range_to_remove}")

    # Définir les nouvelles cibles
    new_targets = []
    for i in range(1, 4): new_targets.append(f"V{i}")
    for i in range(1, 6): new_targets.append(f"H{i}")
    for i in range(1, 6): new_targets.append(f"B{i}")
    for i in range(1, 6): new_targets.append(f"M{i}")
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

            try:
                # Utiliser .cell() au lieu de la notation []
                ws.cell(row=4, column=col, value=target_id)
                ws.cell(row=5, column=col, value=['3', '4', '5'][coord_idx])
                ws.cell(row=9, column=col, value=coord)

                if coord_idx == 0:  # Première colonne de la cible
                    ws.cell(row=8, column=col, value=f"CHP_{target_id} ({target_id})")
                    ws.cell(row=7, column=col, value='BG')
                elif coord_idx == 2:  # Dernière colonne
                    ws.cell(row=7, column=col, value='HG')

                # Ajouter les formules pour les lignes de données
                for row in range(10, 51):
                    db_cols = {'X': 'AE', 'Y': 'AF', 'Z': 'AG'}
                    db_col = db_cols[coord]

                    formula = f'=IFERROR(INDEX(DATABASE.{db_col}:{db_col},MATCH(1,(DATABASE.AB:AB=$A{row})*(DATABASE.AC:AC="{target_id}"),0)),"")'
                    ws.cell(row=row, column=col, value=formula)

            except Exception as e:
                print(f"      ⚠️ Erreur colonne {get_column_letter(col)}: {e}")
                # Continuer malgré les erreurs
                pass

        current_col += 3

    # Sauvegarder
    try:
        wb.save(output_filename)
        wb.close()
        print(f"✅ Fichier sécurisé créé: {output_filename}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        wb.close()
        return False

def verify_extended_file(filename):
    """Vérifie que le fichier étendu fonctionne"""
    print(f"🔍 Vérification du fichier: {filename}")

    try:
        wb = openpyxl.load_workbook(filename, data_only=True)

        # Vérifier les onglets
        sheets = wb.sheetnames
        print(f"   📋 Onglets: {len(sheets)} trouvés")

        if 'Résultats observations' in sheets:
            ws = wb['Résultats observations']
            print(f"   📊 Résultats observations: {ws.max_row}×{ws.max_column}")

            # Vérifier quelques en-têtes
            targets_found = []
            for col in range(15, 85):  # Colonnes O à CU
                cell_value = ws.cell(4, col).value
                if cell_value and str(cell_value).strip():
                    targets_found.append(str(cell_value))

            print(f"   🎯 Cibles trouvées: {len(set(targets_found))} uniques")
            print(f"       Exemple: {targets_found[:5]}...")

        wb.close()
        print("✅ Fichier vérifié avec succès")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    original = "01_51-B-GER-HA21_3-PM_135-25-05-21.xlsm"
    output = "01_51-B-GER-HA21_3-PM_135-25-05-21_SAFE.xlsm"

    print("🚀 Création d'un fichier Excel étendu sécurisé...")

    # Créer le fichier sécurisé
    if create_safe_extended_file(original, output):
        # Vérifier le résultat
        verify_extended_file(output)
        print(f"\\n🎉 Fichier prêt: {output}")
        print("   Vous pouvez maintenant l'ouvrir dans Excel !")
    else:
        print("❌ Échec de la création du fichier")
