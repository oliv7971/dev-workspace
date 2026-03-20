#!/usr/bin/env python3
"""
Script pour étendre l'onglet 'Résultats observations' de 4 à 20 cibles
Analyse la structure existante et insère automatiquement les colonnes nécessaires
"""

import openpyxl
from openpyxl.utils import get_column_letter
import copy

def analyze_current_structure(filename):
    """Analyse la structure actuelle de l'onglet Résultats observations"""
    print("🔍 Analyse de la structure actuelle...")

    wb = openpyxl.load_workbook(filename, data_only=False)
    ws = wb['Résultats observations']

    # Identifier les cibles existantes
    current_targets = []

    # Lignes 4-5 contiennent les identifiants des cibles
    for col in range(3, 20):  # C à S environ
        cell_4 = ws.cell(4, col).value
        cell_5 = ws.cell(5, col).value
        cell_8 = ws.cell(8, col).value  # Description

        if cell_4 is not None and str(cell_4).strip():
            current_targets.append({
                'column': col,
                'letter': get_column_letter(col),
                'target_id': cell_4,
                'coord_type': cell_5,
                'description': cell_8
            })

    wb.close()

    print(f"📊 Cibles actuelles trouvées: {len(current_targets)}")
    for target in current_targets:
        print(f"   {target['letter']}: {target['target_id']} ({target['coord_type']}) - {target['description']}")

    return current_targets

def define_new_targets():
    """Définit les 20 nouvelles cibles à créer"""
    targets = []

    # 3 Voûtes
    for i in range(1, 4):
        targets.append(f"V{i}")

    # 5 Haut
    for i in range(1, 6):
        targets.append(f"H{i}")

    # 5 Bas
    for i in range(1, 6):
        targets.append(f"B{i}")

    # 5 Milieu
    for i in range(1, 6):
        targets.append(f"M{i}")

    # 2 Références
    targets.extend(["REF1", "REF2"])

    print(f"🎯 Nouvelles cibles définies: {targets}")
    return targets

def insert_columns_for_targets(filename, output_filename, new_targets):
    """Insère les colonnes pour les nouvelles cibles"""
    print("📝 Insertion des colonnes pour les nouvelles cibles...")

    wb = openpyxl.load_workbook(filename, data_only=False)
    ws = wb['Résultats observations']

    # Position d'insertion (après les colonnes existantes)
    insert_start_col = 15  # Après les cibles existantes A,B,C,D

    current_col = insert_start_col

    for target_id in new_targets:
        print(f"   Ajout cible {target_id} à partir de la colonne {get_column_letter(current_col)}")

        # Insérer 3 colonnes pour X, Y, Z
        for coord_idx, coord in enumerate(['X', 'Y', 'Z']):
            col_letter = get_column_letter(current_col + coord_idx)

            try:
                # Méthode plus simple : écraser directement
                # Ligne 4: Identifiant de la cible
                ws.cell(4, current_col + coord_idx).value = target_id

                # Ligne 5: Type de coordonnée
                coord_types = ['3', '4', '5']  # Pattern observé dans l'existant
                ws.cell(5, current_col + coord_idx).value = coord_types[coord_idx]

                # Ligne 7: BG/IG/HG pattern
                patterns = ['BG', '', 'HG'] if coord_idx == 0 else ['', '', '']
                if patterns[coord_idx]:
                    ws.cell(7, current_col + coord_idx).value = patterns[coord_idx]

                # Ligne 8: Description avec nom de cible
                if coord_idx == 0:  # Seulement sur la première colonne
                    ws.cell(8, current_col + coord_idx).value = f"CHP_{target_id} ({target_id})"

                # Ligne 9: Type de coordonnée
                ws.cell(9, current_col + coord_idx).value = coord

            except Exception as e:
                print(f"      ⚠️ Erreur sur {col_letter}: {e}")
                # Ignorer les erreurs et continuer
                pass

        current_col += 3  # Passer aux 3 colonnes suivantes

    # Sauvegarder
    wb.save(output_filename)
    wb.close()

    print(f"✅ Colonnes insérées. Fichier sauvé: {output_filename}")

def generate_formulas_for_targets(filename, output_filename, new_targets):
    """Génère les formules pour les nouvelles cibles"""
    print("⚙️ Génération des formules pour les nouvelles cibles...")

    wb = openpyxl.load_workbook(output_filename, data_only=False)
    ws = wb['Résultats observations']

    # Commencer les formules à la colonne O (15)
    insert_start_col = 15
    current_col = insert_start_col

    for target_id in new_targets:
        print(f"   Génération formules pour {target_id} (colonnes {get_column_letter(current_col)}-{get_column_letter(current_col+2)})")

        # Pour chaque cible, générer les formules pour X, Y, Z
        for coord_idx, coord in enumerate(['X', 'Y', 'Z']):
            col_letter = get_column_letter(current_col + coord_idx)

            # Générer les formules pour les lignes de données (10 à 50)
            for row in range(10, 51):  # Lignes de données
                try:
                    # La formule doit chercher dans DATABASE (onglet DATABASE, colonnes AB-AG)
                    # Formule type: =INDEX(DATABASE.AE:AE,MATCH(1,(DATABASE.AB:AB=A10)*(DATABASE.AC:AC="V1"),0))

                    # Colonnes DATABASE: AB=Date, AC=NO, AD=Matricule, AE=X, AF=Y, AG=Z
                    db_col_map = {'X': 'AE', 'Y': 'AF', 'Z': 'AG'}
                    db_col = db_col_map[coord]

                    # Formule pour trouver la valeur correspondante
                    formula = f'=IFERROR(INDEX(DATABASE.{db_col}:{db_col},MATCH(1,(DATABASE.AB:AB=$A{row})*(DATABASE.AC:AC="{target_id}"),0)),"")'

                    ws.cell(row, current_col + coord_idx).value = formula

                except Exception as e:
                    print(f"      ⚠️ Erreur formule {col_letter}{row}: {e}")
                    pass

        current_col += 3

    # Sauvegarder
    wb.save(output_filename)
    wb.close()

    print(f"✅ Formules générées et sauvées dans: {output_filename}")

if __name__ == "__main__":
    filename = "01_51-B-GER-HA21_3-PM_135-25-05-21.xlsm"
    output_filename = "01_51-B-GER-HA21_3-PM_135-25-05-21_EXTENDED.xlsm"

    # 1. Analyser l'existant
    current_structure = analyze_current_structure(filename)

    # 2. Définir les nouvelles cibles
    new_targets = define_new_targets()

    # 3. Insérer les colonnes
    insert_columns_for_targets(filename, output_filename, new_targets)

    # 4. Générer les formules
    generate_formulas_for_targets(filename, output_filename, new_targets)

    print("🎉 Extension terminée !")
