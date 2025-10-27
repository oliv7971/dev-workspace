#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scanner complet pour identifier les lignes corrompues dans tous les fichiers CSV
"""

import pandas as pd
from pathlib import Path
import os

def scan_corrupted_lines():
    """Scan tous les fichiers CSV pour identifier les lignes corrompues"""
    
    workspace_root = Path(__file__).parent
    
    # Dossiers à scanner
    folders_to_scan = [
        "examples/format_apres",
        "examples/format_avant", 
        "examples/format_colonnes_genere",
        "examples/format_colonnes_corrige",
        ".", # répertoire racine
    ]
    
    print("🔍 SCAN COMPLET DES LIGNES CORROMPUES")
    print("=" * 70)
    
    total_corrupted = 0
    
    for folder in folders_to_scan:
        folder_path = workspace_root / folder
        
        if not folder_path.exists():
            continue
            
        print(f"\n📁 Dossier: {folder}")
        print("-" * 50)
        
        # Chercher tous les fichiers CSV
        csv_files = list(folder_path.glob("*.csv"))
        
        if not csv_files:
            print("   Aucun fichier CSV trouvé")
            continue
        
        for csv_file in csv_files:
            try:
                # Essayer de lire le fichier
                df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
                
                # Vérifier s'il y a des colonnes galerie/section
                if 'galerie' in df.columns and 'section' in df.columns:
                    
                    # Chercher les lignes corrompues
                    corrupted_lines = []
                    for idx, row in df.iterrows():
                        galerie = str(row.get('galerie', ''))
                        section = str(row.get('section', ''))
                        
                        # Critères de corruption
                        is_corrupted = False
                        
                        # Galeries qui sont des nombres négatifs
                        if galerie.startswith('-') and any(c.isdigit() for c in galerie):
                            is_corrupted = True
                        
                        # Sections qui sont des dates
                        if '/' in section and '2025' in section:
                            is_corrupted = True
                            
                        # Galeries/sections vides ou bizarres
                        if galerie in ['nan', '', 'NaN'] or section in ['nan', '', 'NaN']:
                            is_corrupted = True
                        
                        if is_corrupted:
                            corrupted_lines.append((idx, galerie, section, row.get('metric', '')))
                    
                    # Afficher les résultats
                    if corrupted_lines:
                        print(f"   ❌ {csv_file.name}: {len(corrupted_lines)} lignes corrompues")
                        total_corrupted += len(corrupted_lines)
                        
                        # Afficher quelques exemples
                        for i, (idx, gal, sec, metric) in enumerate(corrupted_lines[:3]):
                            print(f"      Ligne {idx}: galerie='{gal}', section='{sec}', metric='{metric[:30]}...'")
                        
                        if len(corrupted_lines) > 3:
                            print(f"      ... et {len(corrupted_lines) - 3} autres")
                    else:
                        print(f"   ✅ {csv_file.name}: Aucune ligne corrompue")
                else:
                    print(f"   ℹ️  {csv_file.name}: Pas de colonnes galerie/section (fichier différent)")
                    
            except Exception as e:
                print(f"   ❌ {csv_file.name}: Erreur de lecture - {e}")
    
    print(f"\n{'='*70}")
    print(f"📊 RÉSUMÉ GLOBAL")
    print(f"Total lignes corrompues trouvées: {total_corrupted}")
    
    if total_corrupted > 0:
        print(f"\n💡 RECOMMANDATIONS:")
        print(f"1. Les lignes corrompues semblent être des résidus de parsing Excel")
        print(f"2. Vous pouvez les nettoyer automatiquement")
        print(f"3. Ou vérifier les fichiers Excel sources pour éviter le problème à la source")
    else:
        print(f"\n🎉 EXCELLENT ! Aucune ligne corrompue détectée.")
        print(f"Vos fichiers sont propres !")

if __name__ == "__main__":
    scan_corrupted_lines()