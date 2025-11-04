#!/usr/bin/env python3
"""
Analyser les lignes problématiques dans le fichier CSV
"""

import pandas as pd
import re

def analyze_problematic_lines():
    """Analyser les lignes avec des galeries numériques"""
    
    df = pd.read_csv('examples/format_apres/Deplacements_SMC.csv', sep=';')
    
    # Trouver les lignes avec des galeries numériques
    numeric_pattern = r'^-?\d+\.?\d*$'
    weird_lines = df[df['galerie'].astype(str).str.match(numeric_pattern, na=False)]
    
    print(f"🔍 Lignes avec galeries numériques: {len(weird_lines)}")
    
    if len(weird_lines) > 0:
        print("\n📋 Exemples de lignes problématiques:")
        for i, (idx, row) in enumerate(weird_lines.head(10).iterrows()):
            print(f"Ligne {idx}: galerie='{row['galerie']}', section='{row['section']}', metric='{row['metric']}'")
            
    # Trouver les lignes avec des sections qui sont des dates
    date_pattern = r'\d{2}/\d{2}/\d{4}'
    date_sections = df[df['section'].astype(str).str.match(date_pattern, na=False)]
    
    print(f"\n🔍 Lignes avec sections-dates: {len(date_sections)}")
    
    if len(date_sections) > 0:
        print("\n📋 Exemples de sections-dates:")
        for i, (idx, row) in enumerate(date_sections.head(10).iterrows()):
            print(f"Ligne {idx}: galerie='{row['galerie']}', section='{row['section']}', metric='{row['metric']}'")
    
    # Lignes normales pour comparaison
    normal_lines = df[~df['galerie'].astype(str).str.match(numeric_pattern, na=False)]
    print(f"\n✅ Lignes normales: {len(normal_lines)}")
    
    if len(normal_lines) > 0:
        print("\n📋 Exemples de lignes normales:")
        for i, (idx, row) in enumerate(normal_lines.head(5).iterrows()):
            print(f"Ligne {idx}: galerie='{row['galerie']}', section='{row['section']}', metric='{row['metric']}'")

if __name__ == "__main__":
    analyze_problematic_lines()