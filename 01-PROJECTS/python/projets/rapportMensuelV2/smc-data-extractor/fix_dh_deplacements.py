#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Correcteur spécifique pour le problème DH dans les déplacements
Corrige les cas où 'DH haut droit' manque mais 'DH bas droit' est présent
"""

import pandas as pd
from pathlib import Path

def fix_missing_dh_haut_droit(csv_file_path):
    """
    Corrige le problème où DH haut droit manque dans certaines sections
    
    Logique :
    1. Pour chaque galerie/section, vérifier la présence de DH haut droit
    2. Si DH bas droit existe mais pas DH haut droit, analyser le contexte
    3. Correction intelligente basée sur l'ordre des métriques
    """
    
    print(f"🔧 Correction DH déplacements pour: {csv_file_path}")
    
    try:
        # Charger le fichier
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
        print(f"✅ Fichier chargé: {len(df)} lignes")
        
        corrections_made = 0
        
        # Analyser par galerie/section
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            group_indices = group.index.tolist()
            metrics = group['metric'].tolist()
            
            # Vérifier les métriques DH
            has_dh_bas_droit = 'DH bas droit' in metrics
            has_dh_haut_droit = 'DH haut droit' in metrics
            has_dh_centre_haut = 'DH centre haut' in metrics
            
            # Problème détecté : DH bas droit existe mais pas DH haut droit
            if has_dh_bas_droit and not has_dh_haut_droit:
                
                print(f"🎯 Problème détecté dans {galerie} {section}:")
                print(f"   - 'DH bas droit' présent, mais 'DH haut droit' manquant")
                
                # Analyser la structure des métriques DH pour déterminer la correction
                dh_metrics_with_pos = []
                for i, metric in enumerate(metrics):
                    if 'DH' in str(metric) and ('gauche' in str(metric) or 'centre' in str(metric) or 'droit' in str(metric)):
                        dh_metrics_with_pos.append((i, metric, group_indices[i]))
                
                print(f"   - Métriques DH trouvées: {[m[1] for m in dh_metrics_with_pos]}")
                
                # Stratégie 1: S'il y a DH centre haut, insérer DH haut droit après
                if has_dh_centre_haut:
                    centre_haut_pos = None
                    bas_droit_pos = None
                    
                    for pos, metric, idx in dh_metrics_with_pos:
                        if metric == 'DH centre haut':
                            centre_haut_pos = pos
                        elif metric == 'DH bas droit':
                            bas_droit_pos = pos
                    
                    # Si DH centre haut vient avant DH bas droit, corriger DH bas droit → DH haut droit
                    if centre_haut_pos is not None and bas_droit_pos is not None and centre_haut_pos < bas_droit_pos:
                        bas_droit_idx = group_indices[bas_droit_pos]
                        df.loc[bas_droit_idx, 'metric'] = 'DH haut droit'
                        print(f"   ✅ Correction: Index {bas_droit_idx}: 'DH bas droit' → 'DH haut droit'")
                        corrections_made += 1
                        continue
                
                # Stratégie 2: S'il n'y a pas de centre haut, analyser l'ordre par rapport aux autres métriques
                if not has_dh_centre_haut:
                    # Chercher la position de DH bas droit
                    bas_droit_idx = None
                    for pos, metric, idx in dh_metrics_with_pos:
                        if metric == 'DH bas droit':
                            bas_droit_idx = idx
                            break
                    
                    if bas_droit_idx is not None:
                        # Analyser ce qui vient avant DH bas droit
                        row_position = group_indices.index(bas_droit_idx)
                        metrics_before = metrics[:row_position]
                        
                        # Si on a DH haut gauche mais pas DH haut droit, 
                        # alors ce DH bas droit pourrait être DH haut droit
                        has_haut_gauche_before = 'DH haut gauche' in metrics_before
                        
                        if has_haut_gauche_before:
                            df.loc[bas_droit_idx, 'metric'] = 'DH haut droit'
                            print(f"   ✅ Correction: Index {bas_droit_idx}: 'DH bas droit' → 'DH haut droit'")
                            corrections_made += 1
        
        if corrections_made > 0:
            # Sauvegarder le fichier corrigé
            backup_path = csv_file_path + '.backup'
            # Créer une sauvegarde seulement si elle n'existe pas déjà
            if not Path(backup_path).exists():
                df_backup = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
                df_backup.to_csv(backup_path, sep=';', index=False, encoding='utf-8-sig')
                print(f"💾 Sauvegarde créée: {backup_path}")
            
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

def verify_corrections(csv_file_path):
    """Vérifie que les corrections ont été appliquées correctement"""
    
    try:
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig')
        
        print(f"\n🔍 Vérification des corrections:")
        print("=" * 50)
        
        problems_remaining = 0
        
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            metrics = group['metric'].tolist()
            
            # Filtrer les métriques DH
            dh_metrics = [m for m in metrics if 'DH' in str(m) and ('gauche' in str(m) or 'droit' in str(m))]
            
            if len(dh_metrics) > 0:
                has_dh_bas_droit = 'DH bas droit' in metrics
                has_dh_haut_droit = 'DH haut droit' in metrics
                
                if has_dh_bas_droit and not has_dh_haut_droit:
                    print(f"❌ {galerie} {section}: Problème persistant (DH bas droit sans DH haut droit)")
                    problems_remaining += 1
                elif has_dh_bas_droit and has_dh_haut_droit:
                    print(f"✅ {galerie} {section}: Équilibre correct")
        
        if problems_remaining == 0:
            print("\n🎉 Toutes les corrections ont été appliquées avec succès !")
        else:
            print(f"\n⚠️  {problems_remaining} problèmes persistent")
            
        return problems_remaining == 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    # Corriger le fichier de déplacements
    examples_dir = Path(__file__).parent / "examples" / "format_apres"
    deplacements_file = examples_dir / "Deplacements_SMC.csv"
    
    if deplacements_file.exists():
        print("🚀 Correction des noms DH dans le fichier déplacements")
        print("=" * 60)
        
        success = fix_missing_dh_haut_droit(str(deplacements_file))
        
        if success:
            # Vérifier les corrections
            verify_corrections(str(deplacements_file))
            
            print("\n🔄 Régénération recommandée des fichiers colonnes...")
            print("💡 Utilisez transform_to_columns.py ou le générateur de lignes")
        
    else:
        print(f"❌ Fichier non trouvé: {deplacements_file}")