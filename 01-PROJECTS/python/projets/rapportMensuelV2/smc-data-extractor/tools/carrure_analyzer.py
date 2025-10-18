#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur de fichiers Excel d'auscultation de carrure
Compare avec la structure SMC pour identifier les différences
"""

import openpyxl
from pathlib import Path
import pandas as pd
from datetime import datetime

class CarrureAnalyzer:
    """Analyse les fichiers Excel d'auscultation de carrure"""

    def __init__(self):
        self.carrure_file = Path(r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\1-tableaux\GGS\03_100-GGS-GRD-double carrure-XYZ-tableau Jour-25-09-10.xlsm")
        self.smc_file = Path(r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250901-rapport mensuel aout\1-tableaux\GGS\03_104-GGS_SMC_C003_PM001_25_08-25.xlsm")

    def analyze_workbook_structure(self, file_path, file_type):
        """Analyse la structure générale d'un fichier Excel"""

        print(f"\n📊 ANALYSE {file_type.upper()}: {file_path.name}")
        print("=" * 70)

        if not file_path.exists():
            print(f"❌ Fichier non trouvé: {file_path}")
            return None

        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)

            print(f"📋 ONGLETS DISPONIBLES ({len(wb.sheetnames)}) :")
            for i, sheet_name in enumerate(wb.sheetnames, 1):
                print(f"   {i}. '{sheet_name}'")

            # Analyser chaque onglet
            for sheet_name in wb.sheetnames:
                self.analyze_sheet_content(wb[sheet_name], sheet_name, file_type)

            wb.close()
            return wb.sheetnames

        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")
            return None

    def analyze_sheet_content(self, worksheet, sheet_name, file_type):
        """Analyse le contenu d'un onglet spécifique"""

        print(f"\n🔍 ONGLET: '{sheet_name}'")
        print("-" * 50)

        # Dimensions de l'onglet
        max_row = worksheet.max_row
        max_col = worksheet.max_column
        print(f"   📏 Dimensions: {max_row} lignes × {max_col} colonnes")

        # Rechercher les en-têtes potentiels
        headers_found = []
        for row in range(1, min(15, max_row + 1)):  # Chercher dans les 15 premières lignes
            row_content = []
            for col in range(1, min(20, max_col + 1)):  # Chercher dans les 20 premières colonnes
                cell_value = worksheet.cell(row, col).value
                if cell_value:
                    row_content.append(str(cell_value).strip())

            if row_content and len(row_content) > 2:  # Si la ligne a du contenu substantiel
                headers_found.append((row, row_content))

        # Afficher les en-têtes trouvés
        if headers_found:
            print(f"   📋 EN-TÊTES POTENTIELS:")
            for row_num, content in headers_found[:5]:  # Afficher les 5 premiers
                print(f"      Ligne {row_num}: {content[:5]}")  # Afficher les 5 premières colonnes

        # Rechercher des données numériques (potentielles mesures)
        numeric_data_rows = 0
        for row in range(10, min(50, max_row + 1)):  # Vérifier les lignes 10-50
            numeric_count = 0
            for col in range(1, min(10, max_col + 1)):
                cell_value = worksheet.cell(row, col).value
                if isinstance(cell_value, (int, float)) and cell_value != 0:
                    numeric_count += 1
            if numeric_count > 3:  # Si plus de 3 valeurs numériques
                numeric_data_rows += 1

        print(f"   🔢 Lignes avec données numériques: ~{numeric_data_rows}")

        return {
            'sheet_name': sheet_name,
            'dimensions': (max_row, max_col),
            'headers': headers_found,
            'numeric_rows': numeric_data_rows
        }

    def compare_structures(self):
        """Compare les structures SMC vs Carrure"""

        print("\n🔄 COMPARAISON SMC vs CARRURE")
        print("=" * 70)

        # Analyser le fichier de carrure
        carrure_sheets = self.analyze_workbook_structure(self.carrure_file, "CARRURE")

        # Analyser le fichier SMC si disponible
        if self.smc_file.exists():
            smc_sheets = self.analyze_workbook_structure(self.smc_file, "SMC")

            # Comparaison
            print(f"\n🔍 COMPARAISON DES ONGLETS:")
            print(f"   SMC: {smc_sheets}")
            print(f"   CARRURE: {carrure_sheets}")

            # Onglets communs
            if smc_sheets and carrure_sheets:
                common_sheets = set(smc_sheets) & set(carrure_sheets)
                unique_smc = set(smc_sheets) - set(carrure_sheets)
                unique_carrure = set(carrure_sheets) - set(smc_sheets)

                print(f"\n   🤝 ONGLETS COMMUNS: {list(common_sheets)}")
                print(f"   🔵 UNIQUEMENT SMC: {list(unique_smc)}")
                print(f"   🟡 UNIQUEMENT CARRURE: {list(unique_carrure)}")
        else:
            print(f"⚠️  Fichier SMC non trouvé: {self.smc_file}")

    def detailed_carrure_analysis(self):
        """Analyse détaillée spécifique au fichier de carrure"""

        print(f"\n🎯 ANALYSE DÉTAILLÉE CARRURE")
        print("=" * 70)

        if not self.carrure_file.exists():
            print(f"❌ Fichier carrure non trouvé")
            return

        try:
            wb = openpyxl.load_workbook(self.carrure_file, data_only=True)

            # Analyser chaque onglet en détail
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                print(f"\n📊 ANALYSE DÉTAILLÉE: '{sheet_name}'")

                # Chercher spécifiquement des colonnes de coordonnées X, Y, Z
                xyz_columns = []
                for row in range(1, 20):
                    for col in range(1, 15):
                        cell_value = ws.cell(row, col).value
                        if cell_value and isinstance(cell_value, str):
                            cell_lower = cell_value.lower().strip()
                            if any(coord in cell_lower for coord in ['x', 'y', 'z', 'coord', 'point']):
                                xyz_columns.append((row, col, cell_value))

                if xyz_columns:
                    print(f"   📍 COLONNES COORDONNÉES TROUVÉES:")
                    for row, col, value in xyz_columns:
                        print(f"      Ligne {row}, Col {col}: '{value}'")

                # Chercher des colonnes de dates
                date_columns = []
                for row in range(1, 20):
                    for col in range(1, 15):
                        cell_value = ws.cell(row, col).value
                        if cell_value and isinstance(cell_value, str):
                            cell_lower = cell_value.lower().strip()
                            if any(date_word in cell_lower for date_word in ['date', 'jour', 'temps', 'time']):
                                date_columns.append((row, col, cell_value))

                if date_columns:
                    print(f"   📅 COLONNES DATES TROUVÉES:")
                    for row, col, value in date_columns:
                        print(f"      Ligne {row}, Col {col}: '{value}'")

            wb.close()

        except Exception as e:
            print(f"❌ Erreur lors de l'analyse détaillée: {e}")

def main():
    """Fonction principale d'analyse"""
    analyzer = CarrureAnalyzer()

    print("🔍 ANALYSEUR FICHIERS AUSCULTATION DE CARRURE")
    print("=" * 70)

    # 1. Comparaison générale des structures
    analyzer.compare_structures()

    # 2. Analyse détaillée spécifique carrure
    analyzer.detailed_carrure_analysis()

    print(f"\n✅ ANALYSE TERMINÉE")
    print("📋 Consultez les résultats ci-dessus pour adapter l'extracteur")

if __name__ == "__main__":
    main()
