#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug pour analyser la structure d'un fichier Excel SMC
"""

from openpyxl import load_workbook
import sys

def debug_excel_structure():
    # Chemin vers un fichier Excel (modifiez selon vos besoins)
    excel_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250901-rapport mensuel aout\1-tableaux\GGS\03_104-GGS_SMC_C003_PM001_25_08-25.xlsm"
    
    try:
        workbook = load_workbook(excel_path, data_only=True)
        
        # Analyser la feuille Convergences
        if 'Convergences' in workbook.sheetnames:
            sheet = workbook['Convergences']
            print("=== FEUILLE CONVERGENCES ===")
            print(f"Dimensions: {sheet.max_row} lignes x {sheet.max_column} colonnes")
            
            # Afficher les 15 premières lignes et colonnes
            print("\n=== CONTENU (15 premières lignes) ===")
            for row in range(1, min(16, sheet.max_row + 1)):
                row_data = []
                for col in range(1, min(15, sheet.max_column + 1)):
                    cell_value = sheet.cell(row, col).value
                    if cell_value is None:
                        row_data.append("None")
                    else:
                        row_data.append(str(cell_value)[:20])
                print(f"Ligne {row:2d}: {' | '.join(row_data)}")
            
            # Focus sur les lignes 9-12 (en-têtes et premières données)
            print("\n=== FOCUS LIGNES 8-12 ===")
            for row in range(8, min(13, sheet.max_row + 1)):
                print(f"\nLigne {row}:")
                for col in range(1, min(sheet.max_column + 1, 15)):
                    cell_value = sheet.cell(row, col).value
                    print(f"  Col {col}: {cell_value}")
                    
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    debug_excel_structure()
