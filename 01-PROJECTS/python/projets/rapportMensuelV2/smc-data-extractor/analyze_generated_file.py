#!/usr/bin/env python3
"""
Analyser les métriques dans le fichier généré pour vérifier les corrections
"""

import pandas as pd

def analyze_generated_file():
    """Analyser le fichier généré pour voir les corrections"""
    
    # Analyser le fichier de déplacements généré
    csv_file = "examples/format_colonnes_corrige/Deplacements_Ligne_SMC_2024_09.csv"
    
    print(f"🔍 Analyse du fichier généré: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    print(f"✅ Fichier lu: {len(df)} lignes")
    print(f"📋 Colonnes: {list(df.columns)}")
    
    # Chercher les colonnes DH pour voir si le problème est résolu
    dh_columns = [col for col in df.columns if 'DH' in col]
    print(f"\n🎯 Colonnes DH trouvées: {dh_columns}")
    
    # Vérifier s'il y a des données dans DH HD vs DH BD
    dh_hd_data = df['DH HD'].dropna()
    dh_bd_data = df['DH BD'].dropna() 
    
    print(f"\n📊 Données DH HD: {len(dh_hd_data)} valeurs non-nulles")
    print(f"📊 Données DH BD: {len(dh_bd_data)} valeurs non-nulles")
    
    if len(dh_hd_data) > 0:
        print(f"   DH HD - Exemples: {list(dh_hd_data.head())}")
    
    if len(dh_bd_data) > 0:
        print(f"   DH BD - Exemples: {list(dh_bd_data.head())}")
    
    # Compter les galeries qui ont des données DH HD vs DH BD
    galeries_with_hd = df[df['DH HD'].notna()]['galerie'].unique()
    galeries_with_bd = df[df['DH BD'].notna()]['galerie'].unique()
    
    print(f"\n🏛️ Galeries avec données DH HD: {list(galeries_with_hd)}")
    print(f"🏛️ Galeries avec données DH BD: {list(galeries_with_bd)}")
    
    # Analyser le fichier source pour comparaison
    print(f"\n" + "="*60)
    print("COMPARAISON AVEC FICHIER SOURCE")
    print("="*60)
    
    source_file = "examples/format_apres/Deplacements_SMC.csv"
    df_source = pd.read_csv(source_file, sep=';')
    
    # Après nettoyage des lignes corrompues
    import re
    numeric_pattern = r'^-?\d+\.?\d*$'
    df_source_clean = df_source[~df_source['galerie'].astype(str).str.match(numeric_pattern, na=False)]
    
    # Compter les métriques DH dans le fichier source
    dh_haut_droit = len(df_source_clean[df_source_clean['metric'] == 'DH haut droit'])
    dh_bas_droit = len(df_source_clean[df_source_clean['metric'] == 'DH bas droit'])
    
    print(f"🔍 Fichier source (après nettoyage):")
    print(f"   - 'DH haut droit': {dh_haut_droit} occurrences")
    print(f"   - 'DH bas droit': {dh_bas_droit} occurrences")
    
    if dh_bas_droit > dh_haut_droit:
        print(f"   ⚠️ Toujours plus de 'DH bas droit' que 'DH haut droit' ({dh_bas_droit} vs {dh_haut_droit})")
        print(f"   💡 Il faut encore corriger {dh_bas_droit - dh_haut_droit} occurrences")
    else:
        print(f"   ✅ Équilibre correct entre 'DH haut droit' et 'DH bas droit'")

if __name__ == "__main__":
    analyze_generated_file()