#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse du fichier Convergences septembre pour comprendre la structure
"""

import pandas as pd

excel_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251002-rapport mensuel septembre\2-extractions\extraction_clean_20251027_141837\Convergences_Ligne_SMC_2025_09-OB.xlsx"

print("="*80)
print("ANALYSE DU FICHIER CONVERGENCES SEPTEMBRE")
print("="*80)
print(f"Fichier : {excel_path}")
print()

# Lire toutes les feuilles
xl_file = pd.ExcelFile(excel_path)
print(f"Feuilles disponibles : {xl_file.sheet_names}")
print()

# Analyser chaque feuille
for sheet_name in xl_file.sheet_names:
    print("="*80)
    print(f"FEUILLE : {sheet_name}")
    print("="*80)
    
    # Lire avec pandas
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    print(f"Dimensions : {df.shape[0]} lignes x {df.shape[1]} colonnes")
    print()
    print("Colonnes :")
    print(df.columns.tolist())
    print()
    print("Aperçu des données :")
    print(df.to_string())
    print()
    print()
