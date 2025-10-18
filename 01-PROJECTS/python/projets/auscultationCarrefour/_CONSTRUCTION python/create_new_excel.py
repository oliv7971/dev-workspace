#!/usr/bin/env python3
"""
Création d'un fichier Excel complètement nouveau et propre
Évite tous les problèmes de corruption en repartant de zéro
"""

import openpyxl
from openpyxl.utils import get_column_letter
import pandas as pd

def create_fresh_excel_file():
    """Crée un fichier Excel complètement nouveau avec la structure d'auscultation"""

    print("🆕 Création d'un fichier Excel complètement nouveau...")

    # Créer un nouveau classeur
    wb = openpyxl.Workbook()

    # Supprimer la feuille par défaut
    wb.remove(wb.active)

    # Créer les onglets nécessaires
    ws_database = wb.create_sheet("DATABASE")
    ws_observations = wb.create_sheet("Résultats observations")

    print("📋 Onglets créés: DATABASE, Résultats observations")

    # === ONGLET DATABASE ===
    print("💾 Configuration de l'onglet DATABASE...")

    # En-têtes DATABASE (colonnes AB-AG comme dans l'original)
    db_headers = ['DATE', 'NO', 'NO', 'X', 'Y', 'Z']
    for i, header in enumerate(db_headers):
        ws_database.cell(12, 28 + i).value = header  # AB=28, AC=29, etc.

    # Ajouter quelques exemples de données
    sample_data = [
        ['2024-08-28', 'V1', 'V1.Test', 823147.6488, 1091710.0857, -121.5674],
        ['2024-08-28', 'V2', 'V2.Test', 823147.5852, 1091710.2506, -121.9302],
        ['2024-09-05', 'V1', 'V1.Test', 823147.6490, 1091710.0850, -121.5690],
    ]

    for row_idx, data_row in enumerate(sample_data):
        for col_idx, value in enumerate(data_row):
            ws_database.cell(14 + row_idx, 28 + col_idx).value = value

    # === ONGLET RÉSULTATS OBSERVATIONS ===
    print("📊 Configuration de l'onglet Résultats observations...")

    # En-têtes fixes
    ws_observations.cell(1, 4).value = "AUSCULTATION AUTOMATISÉE - 20 CIBLES"
    ws_observations.cell(6, 1).value = "Date point 0"
    ws_observations.cell(8, 1).value = "Date"
    ws_observations.cell(8, 2).value = "Jours"

    # Dates d'exemple
    dates = [
        '2024-08-28', '2024-09-05', '2024-09-09', '2024-09-13',
        '2024-09-17', '2024-09-18', '2024-09-19', '2024-09-22'
    ]

    for i, date in enumerate(dates):
        ws_observations.cell(10 + i, 1).value = date
        if i == 0:
            ws_observations.cell(10 + i, 2).value = 0
        else:
            ws_observations.cell(10 + i, 2).value = f"=A{10+i}-A$10"

    # === AJOUTER LES 20 CIBLES ===
    print("🎯 Ajout des 20 cibles avec formules...")

    # Définir les cibles
    targets = []
    for i in range(1, 4): targets.append(f"V{i}")
    for i in range(1, 6): targets.append(f"H{i}")
    for i in range(1, 6): targets.append(f"B{i}")
    for i in range(1, 6): targets.append(f"M{i}")
    targets.extend(["REF1", "REF2"])

    start_col = 3  # Colonne C
    current_col = start_col

    for target_id in targets:
        print(f"   📍 {target_id} -> {get_column_letter(current_col)}-{get_column_letter(current_col+2)}")

        # Ajouter X, Y, Z pour chaque cible
        for coord_idx, coord in enumerate(['X', 'Y', 'Z']):
            col = current_col + coord_idx

            # En-têtes
            ws_observations.cell(4, col).value = target_id
            ws_observations.cell(5, col).value = ['3', '4', '5'][coord_idx]
            ws_observations.cell(9, col).value = coord

            if coord_idx == 0:
                ws_observations.cell(8, col).value = f"CHP_{target_id} ({target_id})"
                ws_observations.cell(7, col).value = 'BG'
            elif coord_idx == 2:
                ws_observations.cell(7, col).value = 'HG'

            # Formules pour récupérer les données
            db_cols = {'X': 'AE', 'Y': 'AF', 'Z': 'AG'}
            db_col = db_cols[coord]

            for row in range(10, 25):  # Lignes de données
                formula = f'=IFERROR(INDEX(DATABASE.{db_col}:{db_col},MATCH(1,(DATABASE.AB:AB=$A{row})*(DATABASE.AC:AC="{target_id}"),0)),"")'
                ws_observations.cell(row, col).value = formula

        current_col += 3

    # Sauvegarder le nouveau fichier
    output_file = "AUSCULTATION_20_CIBLES_NOUVEAU.xlsm"
    wb.save(output_file)
    wb.close()

    print(f"✅ Nouveau fichier créé: {output_file}")
    return output_file

def test_new_file(filename):
    """Teste le nouveau fichier"""
    print(f"\\n🔍 Test du nouveau fichier: {filename}")

    try:
        wb = openpyxl.load_workbook(filename)

        print(f"📋 Onglets: {wb.sheetnames}")

        # Tester l'onglet observations
        ws = wb['Résultats observations']
        print(f"📊 Dimensions: {ws.max_row}×{ws.max_column}")

        # Compter les cibles
        targets = set()
        for col in range(3, 65):
            value = ws.cell(4, col).value
            if value and len(str(value)) <= 10:
                targets.add(str(value))

        print(f"🎯 Cibles: {len(targets)} -> {sorted(list(targets))}")

        wb.close()
        print("✅ Nouveau fichier fonctionne!")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Création d'un fichier Excel complètement nouveau...")

    new_file = create_fresh_excel_file()
    test_new_file(new_file)

    print(f"\\n🎉 TERMINÉ!")
    print(f"📁 Nouveau fichier: {new_file}")
    print(f"\\n💡 Ce fichier contient:")
    print(f"   - Structure DATABASE propre (colonnes AB-AG)")
    print(f"   - 20 cibles avec formules automatiques")
    print(f"   - Aucun problème de cellules fusionnées")
    print(f"   - Prêt à recevoir vos données!")

    print(f"\\n📝 UTILISATION:")
    print(f"   1. Ouvrez {new_file} dans Excel")
    print(f"   2. Ajoutez vos mesures dans DATABASE (colonnes AB-AG)")
    print(f"   3. Utilisez les codes: V1,V2,V3,H1-H5,B1-B5,M1-M5,REF1,REF2")
    print(f"   4. Les calculs apparaîtront automatiquement!")
