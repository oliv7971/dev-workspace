#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Génération complète des données carrure avec corrections GRD
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

def generate_carrure_with_corrections():
    """Génère les données carrure avec toutes les corrections appliquées"""
    
    print("🏗️ GÉNÉRATION CARRURE AVEC CORRECTIONS")
    print("=" * 50)
    
    try:
        from carrure_precise_extractor import run_carrure_precise_extraction
        
        # Paramètres - utiliser le dossier source original
        root_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\1-tableaux"
        month = "2025-09"
        output_folder = "examples/carrure_with_corrections"
        
        print(f"📁 Source: {root_folder}")
        print(f"💾 Sortie: {output_folder}")
        print(f"📅 Mois: {month}")
        
        # Créer le dossier de sortie
        Path(output_folder).mkdir(exist_ok=True)
        
        def log_callback(msg):
            print(f"   {msg}")
        
        print(f"\n🔄 Extraction carrure en cours...")
        
        # Lancer l'extraction carrure
        success = run_carrure_precise_extraction(
            root_folder=root_folder,
            month=month,
            output_folder=output_folder,
            log_callback=log_callback
        )
        
        if success:
            print(f"\n✅ Extraction carrure réussie !")
            print(f"📁 Fichiers dans: {output_folder}")
            
            # Vérifier le fichier généré
            output_file = Path(output_folder) / f"carrure_extractions_2025_09.csv"
            if output_file.exists():
                import pandas as pd
                df = pd.read_csv(output_file)
                
                print(f"\n📊 Résumé des données carrure:")
                print(f"   📝 Total métriques: {len(df)}")
                
                # Compter par galerie
                galeries = df['table'].value_counts()
                for galerie, count in galeries.items():
                    print(f"   🏗️ {galerie}: {count} métriques")
                
                # Vérifier s'il y a des données GRD
                if 'GRD' in galeries:
                    print(f"   ✅ Données GRD incluses !")
                else:
                    print(f"   ℹ️ Pas de données carrure GRD (normal si pas de fichier carrure GRD)")
                    
                # Afficher un échantillon
                print(f"\n🔍 Échantillon des données:")
                for idx, row in df.head(3).iterrows():
                    print(f"   {row['table']} {row['code_point']}: {row['deplacement_cumule']} mm")
                    
            return True
        else:
            print(f"\n❌ Échec de l'extraction carrure")
            return False
            
    except ImportError as e:
        print(f"❌ Impossible d'importer l'extracteur carrure: {e}")
        print(f"ℹ️ Vérifiez que carrure_precise_extractor.py est présent")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def check_carrure_source_files():
    """Vérifie quels fichiers carrure sont disponibles"""
    
    print(f"\n🔍 VÉRIFICATION FICHIERS CARRURE")
    print("=" * 40)
    
    # Chercher dans le dossier des données corrigées
    search_folder = Path("examples/extraction_clean_corrected_grd")
    
    if not search_folder.exists():
        print(f"❌ Dossier {search_folder} n'existe pas")
        return
    
    # Chercher les fichiers carrure
    carrure_patterns = ["*carrure*.xlsx", "*carrure*.xlsm", "*Carrure*.xlsx", "*Carrure*.xlsm"]
    found_files = []
    
    for pattern in carrure_patterns:
        found_files.extend(list(search_folder.rglob(pattern)))
    
    if found_files:
        print(f"✅ {len(found_files)} fichier(s) carrure trouvé(s):")
        for file in found_files:
            print(f"   📄 {file.name}")
    else:
        print(f"⚠️ Aucun fichier carrure trouvé dans {search_folder}")
        print(f"ℹ️ L'extraction carrure utilisera les données CSV existantes")
        
        # Chercher dans le dossier parent
        parent_folder = Path("examples")
        print(f"\n🔍 Recherche dans {parent_folder}...")
        
        all_files = []
        for pattern in carrure_patterns:
            all_files.extend(list(parent_folder.rglob(pattern)))
        
        if all_files:
            print(f"✅ Fichiers carrure trouvés ailleurs:")
            for file in all_files:
                rel_path = file.relative_to(parent_folder)
                print(f"   📄 {rel_path}")

if __name__ == "__main__":
    
    # Vérifier les fichiers source
    check_carrure_source_files()
    
    # Générer les données carrure
    print(f"\n" + "="*60)
    success = generate_carrure_with_corrections()
    
    if success:
        print(f"\n🎉 Données carrure générées avec toutes les corrections !")
        print(f"   🔧 Inclut les corrections GRD si fichiers présents")
        print(f"   📊 Format standardisé avec metric_name_corrector")
    else:
        print(f"\n😞 Problème lors de la génération des données carrure")