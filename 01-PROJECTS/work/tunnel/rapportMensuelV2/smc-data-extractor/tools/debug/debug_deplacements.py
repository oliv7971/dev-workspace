#!/usr/bin/env python3
"""
Debug du problème de génération de colonnes
"""

import pandas as pd
from pathlib import Path

def debug_deplacements():
    """Debug du fichier déplacements pour comprendre l'erreur"""
    
    csv_file = Path("examples/format_apres/Deplacements_SMC.csv")
    
    print(f"🔍 Debug du fichier: {csv_file}")
    
    # Charger le fichier
    try:
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
        print(f"✅ Fichier lu avec succès - {len(df)} lignes")
        
        print(f"\n📋 Colonnes: {list(df.columns)}")
        
        # Vérifier les colonnes essentielles
        required_cols = ['galerie', 'section', 'metric']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Colonnes manquantes: {missing_cols}")
            return False
        
        print(f"\n🎯 Types de galeries uniques: {df['galerie'].unique()}")
        print(f"🎯 Sections uniques: {df['section'].unique()}")
        
        # Examiner quelques métriques pour voir le problème de noms
        print(f"\n📊 Quelques métriques d'exemple:")
        metrics_sample = df['metric'].value_counts().head(10)
        for metric, count in metrics_sample.items():
            print(f"   - {metric}: {count} occurrences")
            
        # Focus sur les métriques DH qui posent problème
        print(f"\n🔍 Métriques DH:")
        dh_metrics = df[df['metric'].str.contains('DH', na=False)]['metric'].value_counts()
        for metric, count in dh_metrics.items():
            print(f"   - {metric}: {count} occurrences")
            
        # Tester le groupement
        print(f"\n🔧 Test de groupement...")
        try:
            grouped = df.groupby(['galerie', 'section', 'source_file'])
            print(f"✅ Groupement réussi - {len(grouped)} groupes")
            
            # Tester le premier groupe
            first_group = next(iter(grouped))
            group_key = first_group[0]
            group_data = first_group[1]
            
            print(f"   Premier groupe: {group_key}")
            print(f"   Données du groupe: {len(group_data)} lignes")
            print(f"   Métriques dans ce groupe: {group_data['metric'].unique()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du groupement: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {str(e)}")
        return False

if __name__ == "__main__":
    debug_deplacements()