#!/usr/bin/env python3
"""
Tester le correcteur automatique sur les données réelles
"""

import pandas as pd
import sys
from pathlib import Path

# Ajouter le correcteur au path
sys.path.append('.')

from metric_name_corrector import MetricNameCorrector

def test_corrector_on_real_data():
    """Tester le correcteur sur les vraies données"""
    
    print("🔧 Test du correcteur automatique sur les données réelles")
    
    # Charger le fichier de déplacements
    df = pd.read_csv('examples/format_apres/Deplacements_SMC.csv', sep=';')
    
    # Nettoyer les lignes corrompues
    import re
    numeric_pattern = r'^-?\d+\.?\d*$'
    df_clean = df[~df['galerie'].astype(str).str.match(numeric_pattern, na=False)]
    
    print(f"📊 Données chargées: {len(df_clean)} lignes après nettoyage")
    
    # Analyser avant correction
    dh_before = df_clean[df_clean['metric'].str.contains('DH', na=False)]['metric'].value_counts()
    print(f"\n📋 Métriques DH AVANT correction:")
    for metric, count in dh_before.items():
        print(f"   - {metric}: {count}")
    
    # Créer le correcteur et tester
    corrector = MetricNameCorrector()
    
    print(f"\n🔧 Application du correcteur...")
    df_corrected = corrector.correct_dataframe_metrics(df_clean)
    
    # Analyser après correction
    dh_after = df_corrected[df_corrected['metric'].str.contains('DH', na=False)]['metric'].value_counts()
    print(f"\n📋 Métriques DH APRÈS correction:")
    for metric, count in dh_after.items():
        print(f"   - {metric}: {count}")
    
    # Vérifier les changements
    changes_detected = False
    for metric in dh_before.index:
        if metric in dh_after.index:
            if dh_before[metric] != dh_after[metric]:
                print(f"   🔄 {metric}: {dh_before[metric]} → {dh_after[metric]}")
                changes_detected = True
        else:
            print(f"   ❌ {metric}: {dh_before[metric]} → 0 (supprimé)")
            changes_detected = True
    
    # Nouvelles métriques
    for metric in dh_after.index:
        if metric not in dh_before.index:
            print(f"   ✅ {metric}: 0 → {dh_after[metric]} (nouveau)")
            changes_detected = True
    
    if not changes_detected:
        print(f"   ⚠️ Aucun changement détecté")
        print(f"\n🔍 Analyse du problème...")
        
        # Regarder spécifiquement les cas problématiques
        dh_bas_droit_entries = df_clean[df_clean['metric'] == 'DH bas droit']
        print(f"\n📋 Analyse des entrées 'DH bas droit' ({len(dh_bas_droit_entries)}):")
        
        for i, (idx, row) in enumerate(dh_bas_droit_entries.head(5).iterrows()):
            print(f"   Entrée {i+1}: galerie={row['galerie']}, section={row['section']}")
            
        # Tester manuellement la logique du correcteur
        print(f"\n🧪 Test manuel de la logique de correction:")
        test_row = dh_bas_droit_entries.iloc[0] if len(dh_bas_droit_entries) > 0 else None
        
        if test_row is not None:
            # Obtenir les métriques du même contexte (galerie/section)
            same_context = df_clean[
                (df_clean['galerie'] == test_row['galerie']) & 
                (df_clean['section'] == test_row['section'])
            ]
            context_metrics = same_context['metric'].tolist()
            
            correct_name = corrector._detect_correct_dh_name('DH bas droit', context_metrics)
            print(f"   Résultat de _detect_correct_dh_name: '{correct_name}'")
            print(f"   Contexte (galerie={test_row['galerie']}, section={test_row['section']}): {context_metrics}")
            print(f"   Nombre de 'DH bas droit' dans ce contexte: {context_metrics.count('DH bas droit')}")

if __name__ == "__main__":
    test_corrector_on_real_data()