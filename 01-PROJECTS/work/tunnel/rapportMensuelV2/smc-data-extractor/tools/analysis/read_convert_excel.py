#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse du fichier convert deplacementsCopilot.xlsx
"""

import pandas as pd

excel_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251103-rapport mensuel octobre\2-extractions\smc_output\convert deplacementsCopilot.xlsx"

print("="*70)
print("ANALYSE DU FICHIER EXCEL CONVERT")
print("="*70)
print(f"Fichier : {excel_path}")
print()

# Lire toutes les feuilles
xl_file = pd.ExcelFile(excel_path)
print(f"Feuilles disponibles : {xl_file.sheet_names}")
print()

# Analyser chaque feuille
for sheet_name in xl_file.sheet_names:
    print("="*70)
    print(f"FEUILLE : {sheet_name}")
    print("="*70)
    
    # Lire avec pandas
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    
    print(f"Dimensions : {df.shape[0]} lignes x {df.shape[1]} colonnes")
    print()
    print("Contenu :")
    print(df.to_string())
    print()
    print()
