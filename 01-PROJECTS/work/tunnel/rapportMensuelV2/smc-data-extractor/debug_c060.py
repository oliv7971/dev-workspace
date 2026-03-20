#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de diagnostic pour GGS C060"""

import pandas as pd

csv_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251201-rapport mensuel novembre\2-extractions\smc_output\Deplacements_Ligne_SMC_2025_11.csv"

df = pd.read_csv(csv_path)

# Filtrer C060
c060 = df[df['section'] == 'C060']

print("=" * 70)
print("DIAGNOSTIC GGS C060 - DÉTECTION NOMBRE DE CIBLES")
print("=" * 70)
print()

# Colonnes Inter
cols_inter = [c for c in df.columns if 'IG' in c or 'ID' in c]
print(f"Colonnes 'Inter' trouvées: {cols_inter}")
print()

print("Données GGS C060 pour les colonnes Inter:")
print("-" * 70)
for idx, row in c060.iterrows():
    print(f"\nMode: {row['mode']}")
    print(f"  DPM IG: {row.get('DPM IG', 'N/A')} | DH IG: {row.get('DH IG', 'N/A')} | DZ IG: {row.get('DZ IG', 'N/A')}")
    print(f"  DPM ID: {row.get('DPM ID', 'N/A')} | DH ID: {row.get('DH ID', 'N/A')} | DZ ID: {row.get('DZ ID', 'N/A')}")
    
    # Tester la logique de détection
    has_ig = pd.notna(row.get('DPM IG', None)) or pd.notna(row.get('DH IG', None)) or pd.notna(row.get('DZ IG', None))
    has_id = pd.notna(row.get('DPM ID', None)) or pd.notna(row.get('DH ID', None)) or pd.notna(row.get('DZ ID', None))
    
    print(f"  -> has_ig = {has_ig}, has_id = {has_id}")
    print(f"  -> Nb cibles détecté: {7 if (has_ig or has_id) else 5}")

print()
print("=" * 70)
print("Vérification de TOUTES les colonnes de C060:")
print("=" * 70)
for idx, row in c060.iterrows():
    if row['mode'] == 'périodique':
        print(f"\nMode périodique - valeurs non-nulles:")
        for col in df.columns:
            if pd.notna(row[col]) and row[col] != '':
                print(f"  {col}: {row[col]}")
