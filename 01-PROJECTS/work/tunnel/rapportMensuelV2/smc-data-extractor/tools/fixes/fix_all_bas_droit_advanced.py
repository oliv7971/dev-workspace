#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Correcteur avancé pour tous les doublons "bas droit" dans les déplacements
Analyse l'ordre des métriques pour déterminer lesquelles corriger
"""

import pandas as pd
from pathlib import Path

def fix_all_bas_droit_duplicates(csv_file_path):
    """
    Corrige tous les doublons 'bas droit' en analysant l'ordre des métriques
    
    Logique :
    1. Pour chaque galerie/section, analyser toutes les métriques DH/DPM/DZ
    2. Identifier l'ordre attendu : bas gauche → haut gauche → (inter gauche) → centre haut → haut droit → (inter droit) → bas droit
    3. Corriger automatiquement les métriques mal placées
    """
    
    print(f"🔧 Correction avancée des doublons 'bas droit': {csv_file_path}")
    
    try:
        # Charger le fichier
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
        print(f"✅ Fichier chargé: {len(df)} lignes")
        
        corrections_made = 0
        
        # Ordre logique attendu des positions
        position_order = [
            'bas gauche', 'haut gauche', 'inter gauche',
            'centre haut', 
            'haut droit', 'inter droit', 'bas droit'
        ]
        
        # Analyser par galerie/section
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            group_indices = group.index.tolist()
            metrics = group['metric'].tolist()
            
            print(f"\n🔍 Analyse: {galerie} {section}")
            
            # Analyser chaque type de métrique (DH, DPM, DZ)
            for metric_type in ['DH', 'DPM', 'DZ']:
                
                # Trouver toutes les métriques de ce type
                type_metrics = []
                for i, metric in enumerate(metrics):
                    if str(metric).startswith(f'{metric_type} '):
                        type_metrics.append((i, metric, group_indices[i]))
                
                if len(type_metrics) == 0:
                    continue
                
                # Vérifier s'il y a des doublons "bas droit"
                bas_droit_metrics = [(i, metric, idx) for i, metric, idx in type_metrics if 'bas droit' in metric]
                
                if len(bas_droit_metrics) > 1:
                    print(f"   ⚠️  {metric_type}: {len(bas_droit_metrics)} métriques 'bas droit' détectées")
                    
                    # Analyser l'ordre pour déterminer les corrections
                    all_positions_found = []
                    for i, metric, idx in type_metrics:
                        for pos in position_order:
                            if pos in metric:
                                all_positions_found.append((i, pos, metric, idx))
                                break
                    
                    # Trier par ordre d'apparition dans le fichier
                    all_positions_found.sort(key=lambda x: x[0])
                    
                    print(f"   📋 Ordre trouvé: {[pos[1] for pos in all_positions_found]}")
                    
                    # Correction logique : si on a plus d'un "bas droit", 
                    # celui qui n'est pas à la fin devrait être autre chose
                    corrections_for_type = []
                    
                    if len(bas_droit_metrics) >= 2:
                        # Garder seulement le dernier "bas droit" dans l'ordre
                        bas_droit_positions = [(i, metric, idx) for i, metric, idx in bas_droit_metrics]
                        bas_droit_positions.sort(key=lambda x: x[0])  # Trier par position dans le fichier
                        
                        # Corriger tous sauf le dernier
                        for i, (pos, metric, idx) in enumerate(bas_droit_positions[:-1]):
                            
                            # Déterminer quelle devrait être la correction
                            correction_pos = None
                            
                            # Analyser le contexte : qu'est-ce qui manque ?
                            positions_present = [pos[1] for pos in all_positions_found if pos[1] != 'bas droit' or pos[3] == bas_droit_positions[-1][2]]
                            
                            # Stratégies de correction selon ce qui manque
                            if 'haut droit' not in positions_present:
                                correction_pos = 'haut droit'
                            elif 'inter droit' not in positions_present:
                                correction_pos = 'inter droit'
                            elif 'centre haut' not in positions_present:
                                correction_pos = 'centre haut'
                            else:
                                # Par défaut, supposer que c'est haut droit
                                correction_pos = 'haut droit'
                            
                            new_metric = f'{metric_type} {correction_pos}'
                            corrections_for_type.append((idx, metric, new_metric))
                    
                    # Appliquer les corrections pour ce type
                    for idx, old_metric, new_metric in corrections_for_type:
                        df.loc[idx, 'metric'] = new_metric
                        print(f"   ✅ Correction: '{old_metric}' → '{new_metric}'")
                        corrections_made += 1
        
        if corrections_made > 0:
            # Sauvegarder le fichier corrigé
            backup_path = csv_file_path + '.backup_advanced'
            if not Path(backup_path).exists():
                df_backup = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
                df_backup.to_csv(backup_path, sep=';', index=False, encoding='utf-8-sig')
                print(f"\n💾 Sauvegarde créée: {backup_path}")
            
            # Sauvegarder le fichier corrigé
            df.to_csv(csv_file_path, sep=';', index=False, encoding='utf-8-sig')
            print(f"✅ {corrections_made} corrections appliquées et sauvegardées")
            
            return True
        else:
            print("✅ Aucune correction nécessaire")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verify_all_corrections(csv_file_path):
    """Vérifie que toutes les corrections ont été appliquées"""
    
    try:
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
        
        print(f"\n🔍 Vérification complète des corrections:")
        print("=" * 60)
        
        total_problems = 0
        
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            metrics = group['metric'].tolist()
            
            # Vérifier chaque type de métrique
            for metric_type in ['DH', 'DPM', 'DZ']:
                type_metrics = [m for m in metrics if str(m).startswith(f'{metric_type} ')]
                bas_droit_count = len([m for m in type_metrics if 'bas droit' in m])
                
                if bas_droit_count > 1:
                    print(f"❌ {galerie} {section} {metric_type}: {bas_droit_count} 'bas droit' (problème persistant)")
                    total_problems += 1
                elif bas_droit_count == 1:
                    print(f"✅ {galerie} {section} {metric_type}: 1 'bas droit' (correct)")
        
        if total_problems == 0:
            print("\n🎉 Toutes les corrections ont été appliquées avec succès !")
            print("   Chaque type de métrique (DH/DPM/DZ) a au maximum 1 'bas droit' par section")
        else:
            print(f"\n⚠️  {total_problems} problèmes persistent")
            
        return total_problems == 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    # Corriger le fichier de déplacements
    examples_dir = Path(__file__).parent / "examples" / "format_apres"
    deplacements_file = examples_dir / "Deplacements_SMC.csv"
    
    if deplacements_file.exists():
        print("🚀 Correction avancée de TOUS les doublons 'bas droit'")
        print("=" * 60)
        
        success = fix_all_bas_droit_duplicates(str(deplacements_file))
        
        if success:
            # Vérifier les corrections
            verify_all_corrections(str(deplacements_file))
            
            print("\n🔄 Maintenant, relancez transform_to_columns.py pour régénérer les fichiers !")
        
    else:
        print(f"❌ Fichier non trouvé: {deplacements_file}")