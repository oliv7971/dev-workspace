#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Correcteur spécifique pour le problème DH bas droit / DH haut droit
Analyse intelligente et correction automatique
"""

import pandas as pd
from pathlib import Path
import re

def fix_dh_naming_issue(csv_file_path):
    """
    Corrige le problème spécifique de nommage DH bas droit / DH haut droit
    
    Logique :
    1. Pour chaque galerie/section, identifier les métriques DH existantes
    2. Si on a plus d'un 'DH bas droit' et pas de 'DH haut droit', corriger
    3. Utiliser la logique positionnelle (ordre dans le fichier) pour déterminer lequel corriger
    """
    
    print(f"🔧 Correction spécifique DH pour: {csv_file_path}")
    
    try:
        # Charger le fichier
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
        print(f"✅ Fichier chargé: {len(df)} lignes")
        
        corrections_made = 0
        
        # Analyser par galerie/section
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            group_indices = group.index.tolist()
            metrics = group['metric'].tolist()
            
            # Compter les métriques DH droite
            dh_bas_droit_indices = []
            has_dh_haut_droit = False
            
            for i, metric in enumerate(metrics):
                if metric == 'DH bas droit':
                    dh_bas_droit_indices.append(group_indices[i])
                elif metric == 'DH haut droit':
                    has_dh_haut_droit = True
            
            # Problème détecté : plus d'un 'DH bas droit' et pas de 'DH haut droit'
            if len(dh_bas_droit_indices) > 1 and not has_dh_haut_droit:
                
                print(f"🎯 Problème détecté dans {galerie} {section}:")
                print(f"   - {len(dh_bas_droit_indices)} × 'DH bas droit', 0 × 'DH haut droit'")
                
                # Stratégie de correction : analyser le contexte posititionnel
                # Généralement, les métriques suivent un ordre : bas gauche, haut gauche, centre haut, haut droit, bas droit
                
                # Trouver les positions relatives
                metric_positions = {}
                for i, metric in enumerate(metrics):
                    if 'DH' in metric and ('gauche' in metric or 'centre' in metric or 'droit' in metric):
                        metric_positions[metric] = i
                
                # Ordre attendu des métriques DH
                expected_order = [
                    'DH bas gauche', 'DH haut gauche', 'DH inter gauche',
                    'DH centre haut', 
                    'DH haut droit', 'DH inter droit', 'DH bas droit'
                ]
                
                # Analyser quel 'DH bas droit' devrait être 'DH haut droit'
                indices_to_correct = []
                
                for idx in dh_bas_droit_indices:
                    row_position = group_indices.index(idx)
                    
                    # Analyser le contexte : qu'y a-t-il avant cette métrique ?
                    metrics_before = metrics[:row_position]
                    
                    # Si on a déjà DH centre haut et pas encore de DH haut droit, 
                    # alors ce DH bas droit est probablement DH haut droit
                    if 'DH centre haut' in metrics_before and 'DH haut droit' not in metrics_before:
                        indices_to_correct.append(idx)
                
                # Si on n'a pas pu déterminer par le contexte, prendre le premier
                if not indices_to_correct and len(dh_bas_droit_indices) >= 2:
                    indices_to_correct = [dh_bas_droit_indices[0]]  # Corriger le premier
                
                # Appliquer les corrections
                for idx in indices_to_correct:
                    old_value = df.loc[idx, 'metric']
                    df.loc[idx, 'metric'] = 'DH haut droit'
                    print(f"   ✅ Index {idx}: '{old_value}' → 'DH haut droit'")
                    corrections_made += 1
        
        if corrections_made > 0:
            # Sauvegarder le fichier corrigé
            backup_path = csv_file_path + '.backup'
            df_backup = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
            df_backup.to_csv(backup_path, sep=';', index=False, encoding='utf-8-sig')
            print(f"💾 Sauvegarde créée: {backup_path}")
            
            df.to_csv(csv_file_path, sep=';', index=False, encoding='utf-8-sig')
            print(f"✅ {corrections_made} corrections appliquées et sauvegardées")
            
            # Vérification post-correction
            print("\n🔍 Vérification post-correction:")
            verify_corrections(csv_file_path)
        else:
            print("✅ Aucune correction nécessaire")
        
        return corrections_made > 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verify_corrections(csv_file_path):
    """Vérifie que les corrections ont été appliquées correctement"""
    
    try:
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
        
        all_metrics = df['metric'].tolist()
        dh_bas_droit_count = all_metrics.count('DH bas droit')
        dh_haut_droit_count = all_metrics.count('DH haut droit')
        
        print(f"   - 'DH bas droit': {dh_bas_droit_count} occurrences")
        print(f"   - 'DH haut droit': {dh_haut_droit_count} occurrences")
        
        if dh_bas_droit_count <= dh_haut_droit_count:
            print("   ✅ Équilibrage correct !")
        else:
            print("   ⚠️ Déséquilibre persistant")
        
        # Vérifier par galerie/section
        problems_remaining = 0
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            metrics = group['metric'].tolist()
            local_bas = metrics.count('DH bas droit')
            local_haut = metrics.count('DH haut droit')
            
            if local_bas > 1 and local_haut == 0:
                problems_remaining += 1
                print(f"   ⚠️ Problème restant: {galerie} {section} - {local_bas}×bas, {local_haut}×haut")
        
        if problems_remaining == 0:
            print("   ✅ Tous les problèmes ont été corrigés")
        
    except Exception as e:
        print(f"   ❌ Erreur de vérification: {e}")

def regenerate_with_corrections():
    """Régénère les fichiers colonnes après correction"""
    
    print(f"\n🔄 Régénération des fichiers colonnes avec corrections...")
    
    # Relancer la transformation
    import sys
    from pathlib import Path
    
    # Ajouter le répertoire src au path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))
    
    try:
        from ligne_summary_generator import LigneSummaryGenerator
        
        # Dossiers
        examples_folder = Path(__file__).parent / "examples" / "format_apres"
        output_folder = Path(__file__).parent / "examples" / "format_colonnes_corrige"
        output_folder.mkdir(exist_ok=True)
        
        # Générer avec les données corrigées
        generator = LigneSummaryGenerator(
            csv_folder=str(examples_folder),
            output_folder=str(output_folder),
            month="2025-09"
        )
        
        print("🔄 Génération du format CSV colonnes corrigé...")
        csv_success = generator.generate_csv_ligne_summaries()
        
        if csv_success:
            print("✅ Fichiers colonnes régénérés avec corrections !")
            print(f"📁 Voir le dossier: {output_folder}")
        else:
            print("❌ Échec de la régénération")
        
    except ImportError as e:
        print(f"❌ Impossible d'importer le générateur: {e}")
    except Exception as e:
        print(f"❌ Erreur lors de la régénération: {e}")

if __name__ == "__main__":
    # Corriger le fichier d'exemple
    examples_dir = Path(__file__).parent / "examples" / "format_apres"
    deplacements_file = examples_dir / "Deplacements_SMC.csv"
    
    if deplacements_file.exists():
        success = fix_dh_naming_issue(str(deplacements_file))
        
        if success:
            # Régénérer les fichiers colonnes
            regenerate_with_corrections()
    else:
        print(f"❌ Fichier non trouvé: {deplacements_file}")