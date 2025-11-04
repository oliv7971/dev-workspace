#!/usr/bin/env python3
"""
Copier les fichiers sources corrigés pour les synthèses complètes
"""

import shutil
from pathlib import Path
import sys

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

def prepare_complete_synthesis():
    """Prépare les fichiers pour une synthèse complète"""
    
    print("🔄 PRÉPARATION SYNTHÈSE COMPLÈTE")
    print("="*50)
    
    # Dossiers
    source_folder = Path("examples/format_apres")
    target_folder = Path("examples/syntheses_completes")
    month = "2024-09"
    
    # Créer le dossier cible
    target_folder.mkdir(exist_ok=True)
    
    # Copier les fichiers sources corrigés (avec corrections appliquées)
    print("📁 1. Copie des fichiers source avec corrections...")
    
    source_files = [
        "Convergences_SMC.csv",
        "Deplacements_SMC.csv", 
        "Dates_SMC.csv"
    ]
    
    for file in source_files:
        source_path = source_folder / file
        target_path = target_folder / file
        
        if source_path.exists():
            # Copier le fichier
            shutil.copy2(source_path, target_path)
            print(f"   ✅ {file} copié")
        else:
            print(f"   ⚠️ {file} manquant")
    
    # Appliquer les corrections aux fichiers copiés
    print("\n🔧 2. Application des corrections aux fichiers copiés...")
    
    try:
        # Import des modules de correction
        sys.path.append('.')
        from metric_name_corrector import MetricNameCorrector
        import pandas as pd
        import re
        
        corrector = MetricNameCorrector()
        
        # Corriger le fichier des déplacements
        depl_file = target_folder / "Deplacements_SMC.csv"
        if depl_file.exists():
            print("   🔧 Correction du fichier Deplacements_SMC.csv...")
            
            # Charger
            df = pd.read_csv(depl_file, sep=';', encoding='utf-8-sig')
            
            # Nettoyer les lignes corrompues
            numeric_pattern = r'^-?\d+\.?\d*$'
            corrupted_mask = df['galerie'].astype(str).str.match(numeric_pattern, na=False)
            df_clean = df[~corrupted_mask].copy()
            
            print(f"      - Suppression de {corrupted_mask.sum()} lignes corrompues")
            
            # Appliquer les corrections
            df_corrected = corrector.correct_dataframe_metrics(df_clean)
            
            # Sauvegarder
            df_corrected.to_csv(depl_file, sep=';', index=False, encoding='utf-8-sig')
            print(f"      ✅ Fichier corrigé sauvegardé")
            
        # Générer les synthèses complètes
        print("\n📄 3. Génération des synthèses complètes...")
        
        # Récapitulatifs texte
        try:
            from ligne_summary_generator import LigneSummaryGenerator
            
            generator = LigneSummaryGenerator(
                csv_folder=str(target_folder),
                output_folder=str(target_folder),
                month=month
            )
            
            success = generator.generate_all_ligne_summaries()
            if success:
                print("   ✅ Récapitulatifs texte générés")
            else:
                print("   ⚠️ Problème récapitulatifs texte")
                
        except Exception as e:
            print(f"   ❌ Erreur récapitulatifs: {e}")
        
        # Récapitulatifs CSV (format colonnes)
        try:
            success = generator.generate_csv_ligne_summaries()
            if success:
                print("   ✅ Récapitulatifs CSV colonnes générés")
            else:
                print("   ⚠️ Problème récapitulatifs CSV")
        except Exception as e:
            print(f"   ❌ Erreur récapitulatifs CSV: {e}")
        
        # Rapport PDF amélioré
        try:
            from pdf_generator import generate_pdf_from_csv
            
            success = generate_pdf_from_csv(
                csv_folder=str(target_folder),
                output_folder=str(target_folder),
                month=month,
                log_callback=print
            )
            
            if success:
                print("   ✅ Rapport PDF amélioré généré")
            else:
                print("   ⚠️ Problème rapport PDF")
                
        except Exception as e:
            print(f"   ❌ Erreur PDF: {e}")
        
        # Lister tous les fichiers générés
        print(f"\n📋 FICHIERS GÉNÉRÉS DANS {target_folder}:")
        print("="*60)
        
        for file in sorted(target_folder.glob("*")):
            if file.is_file():
                size = file.stat().st_size
                print(f"   📄 {file.name} ({size:,} bytes)")
        
        print(f"\n✅ SYNTHÈSE COMPLÈTE TERMINÉE!")
        print(f"📁 Dossier: {target_folder.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la préparation: {e}")
        return False

if __name__ == "__main__":
    prepare_complete_synthesis()