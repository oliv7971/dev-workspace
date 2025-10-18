#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnostic des doublons de métriques
Script pour analyser et corriger le problème spécifique de "DH bas droit" vs "DH haut droit"
"""

import pandas as pd
from pathlib import Path
import sys

def analyze_metric_duplicates(csv_path):
    """Analyse les doublons de métriques dans le fichier CSV"""
    
    print(f"🔍 Analyse du fichier: {csv_path}")
    
    try:
        # Essayer plusieurs séparateurs
        for sep in [';', ',']:
            try:
                df = pd.read_csv(csv_path, sep=sep, encoding='utf-8-sig')
                if 'metric' in df.columns:
                    print(f"✅ Fichier lu avec séparateur '{sep}' - {len(df)} lignes")
                    break
            except:
                continue
        else:
            print("❌ Impossible de lire le fichier")
            return
        
        print(f"📊 Colonnes disponibles: {list(df.columns)}")
        
        if 'metric' not in df.columns:
            print("❌ Colonne 'metric' non trouvée")
            return
        
        print("\n🔍 ANALYSE DES MÉTRIQUES:")
        print("=" * 50)
        
        # Analyser par galerie/section
        if 'galerie' in df.columns and 'section' in df.columns:
            duplicates_found = False
            
            for (galerie, section), group in df.groupby(['galerie', 'section']):
                metrics = group['metric'].tolist()
                
                # Compter les occurrences
                metric_counts = {}
                for metric in metrics:
                    if pd.notna(metric):
                        metric_counts[metric] = metric_counts.get(metric, 0) + 1
                
                # Chercher les doublons
                group_duplicates = {k: v for k, v in metric_counts.items() if v > 1}
                
                if group_duplicates:
                    duplicates_found = True
                    print(f"\n⚠️  {galerie} {section}:")
                    for metric, count in group_duplicates.items():
                        print(f"   - '{metric}' apparaît {count} fois")
                    
                    # Analyser spécifiquement le problème DH
                    dh_metrics = [m for m in metrics if 'DH' in str(m) and 'droit' in str(m)]
                    if len(dh_metrics) > 1:
                        print(f"   🎯 Métriques DH droite: {dh_metrics}")
                        
                        # Suggestion de correction
                        if dh_metrics.count('DH bas droit') > 1:
                            print(f"   💡 Suggestion: Une des '{dh_metrics[0]}' devrait probablement être 'DH haut droit'")
            
            if not duplicates_found:
                print("✅ Aucun doublon détecté dans les métriques")
        
        # Statistiques globales
        print(f"\n📈 STATISTIQUES GLOBALES:")
        print("=" * 30)
        
        all_metrics = df['metric'].dropna().tolist()
        unique_metrics = set(all_metrics)
        
        print(f"Total métriques: {len(all_metrics)}")
        print(f"Métriques uniques: {len(unique_metrics)}")
        print(f"Doublons globaux: {len(all_metrics) - len(unique_metrics)}")
        
        # Lister les métriques DH
        dh_metrics = [m for m in unique_metrics if 'DH' in str(m)]
        print(f"\n🎯 Métriques DH trouvées:")
        for metric in sorted(dh_metrics):
            count = all_metrics.count(metric)
            print(f"   - {metric}: {count} occurrences")
        
        # Recherche spécifique du problème
        bas_droit_count = all_metrics.count('DH bas droit')
        haut_droit_count = all_metrics.count('DH haut droit')
        
        print(f"\n🎯 ANALYSE SPÉCIFIQUE DU PROBLÈME:")
        print(f"   - 'DH bas droit': {bas_droit_count} occurrences")
        print(f"   - 'DH haut droit': {haut_droit_count} occurrences")
        
        if bas_droit_count > haut_droit_count:
            print(f"   ⚠️  Problème détecté: Plus de 'DH bas droit' que 'DH haut droit'")
            print(f"   💡 Certaines occurrences de 'DH bas droit' devraient être 'DH haut droit'")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def suggest_corrections(df):
    """Suggère des corrections spécifiques"""
    
    print(f"\n🔧 SUGGESTIONS DE CORRECTIONS:")
    print("=" * 40)
    
    corrections = []
    
    if 'galerie' in df.columns and 'section' in df.columns:
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            metrics = group['metric'].tolist()
            
            # Chercher le pattern problématique
            dh_bas_droit_indices = [i for i, m in enumerate(metrics) if m == 'DH bas droit']
            
            if len(dh_bas_droit_indices) > 1:
                # Plus d'un 'DH bas droit' dans le groupe
                has_haut_droit = 'DH haut droit' in metrics
                
                if not has_haut_droit:
                    # Pas de 'DH haut droit', donc probablement une erreur
                    suggested_idx = dh_bas_droit_indices[-1]  # Corriger le dernier
                    corrections.append({
                        'galerie': galerie,
                        'section': section,
                        'index': group.index[suggested_idx],
                        'from': 'DH bas droit',
                        'to': 'DH haut droit',
                        'reason': 'Doublon détecté, manque DH haut droit'
                    })
    
    if corrections:
        print("📝 Corrections suggérées:")
        for correction in corrections:
            print(f"   - {correction['galerie']} {correction['section']}: "
                  f"'{correction['from']}' → '{correction['to']}' "
                  f"({correction['reason']})")
        
        return corrections
    else:
        print("✅ Aucune correction automatique suggérée")
        return []

if __name__ == "__main__":
    # Analyser le fichier d'exemple
    examples_dir = Path(__file__).parent / "examples" / "format_apres"
    deplacements_file = examples_dir / "Deplacements_SMC.csv"
    
    if deplacements_file.exists():
        df = analyze_metric_duplicates(str(deplacements_file))
        if df is not None:
            suggest_corrections(df)
    else:
        print(f"❌ Fichier non trouvé: {deplacements_file}")
    
    # Analyser aussi le fichier de sortie colonnes généré
    output_dir = examples_dir.parent / "format_colonnes_genere"
    depl_colonnes_file = output_dir / "Deplacements_Ligne_SMC_2025_09.csv"
    
    if depl_colonnes_file.exists():
        print(f"\n" + "="*60)
        print("ANALYSE DU FICHIER COLONNES GÉNÉRÉ")
        print("="*60)
        
        df_colonnes = pd.read_csv(str(depl_colonnes_file))
        print(f"📊 Colonnes dans le fichier généré:")
        
        # Chercher les colonnes DH
        dh_columns = [col for col in df_colonnes.columns if 'DH' in col]
        print(f"🎯 Colonnes DH trouvées: {dh_columns}")
        
        # Vérifier les doublons dans les noms de colonnes
        column_counts = {}
        for col in df_colonnes.columns:
            column_counts[col] = column_counts.get(col, 0) + 1
        
        duplicates = {k: v for k, v in column_counts.items() if v > 1}
        if duplicates:
            print(f"⚠️ Doublons dans les colonnes: {duplicates}")
        else:
            print("✅ Pas de doublons dans les noms de colonnes")
    else:
        print(f"⚠️ Fichier colonnes non trouvé: {depl_colonnes_file}")