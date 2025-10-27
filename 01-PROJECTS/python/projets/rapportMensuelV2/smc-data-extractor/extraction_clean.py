#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script d'extraction CLEAN - Version ligne de commande
Réalise une nouvelle extraction propre sans les lignes corrompues
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Ajouter le path pour les modules
sys.path.append(str(Path(__file__).parent / 'src'))

def run_clean_extraction():
    """Lance une extraction clean avec nettoyage automatique"""
    
    print("🚀 EXTRACTION CLEAN SMC")
    print("=" * 50)
    
    # Paramètres par défaut (vous pouvez les modifier)
    root_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\1-tableaux"
    month = "2025-09"
    output_folder = f"examples/extraction_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"📁 Dossier source: {root_folder}")
    print(f"📅 Mois: {month}")
    print(f"💾 Dossier sortie: {output_folder}")
    
    # Vérifier que le dossier source existe
    if not Path(root_folder).exists():
        print(f"❌ Dossier source non trouvé: {root_folder}")
        print("💡 Modifiez le chemin dans le script ou fournissez le bon chemin")
        return False
    
    # Créer le dossier de sortie
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Importer le module d'extraction SMC
        from src.smc_evolutions import run_extraction
        
        print(f"\n🔧 Lancement de l'extraction SMC...")
        
        # Options d'extraction
        options = {
            'generate_csv': True,
            'generate_ligne_summaries': True,
            'clean_corrupted_lines': True  # Option spéciale pour le nettoyage
        }
        
        # Fonction de log
        def log_callback(message):
            print(f"   {message}")
        
        # Lancer l'extraction
        success = run_extraction(
            root_folder=root_folder,
            month=month,
            output_folder=str(output_path),
            options=options,
            log_callback=log_callback
        )
        
        if success:
            print(f"\n✅ Extraction terminée avec succès !")
            print(f"📁 Résultats dans: {output_path.absolute()}")
            
            # Vérifier la propreté des fichiers générés
            verify_clean_files(output_path)
            
        else:
            print(f"\n❌ Échec de l'extraction")
            
        return success
        
    except ImportError as e:
        print(f"❌ Impossible d'importer le module d'extraction: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return False

def verify_clean_files(output_folder):
    """Vérifie que les fichiers générés sont propres"""
    
    print(f"\n🔍 Vérification de la propreté des fichiers générés...")
    
    csv_files = list(Path(output_folder).glob("*.csv"))
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
            
            if 'galerie' in df.columns and 'section' in df.columns:
                # Vérifier les lignes corrompues
                corrupted_count = 0
                for idx, row in df.iterrows():
                    galerie = str(row.get('galerie', ''))
                    section = str(row.get('section', ''))
                    
                    # Détecter les galeries numériques négatives
                    if galerie.startswith('-') and any(c.isdigit() for c in galerie):
                        corrupted_count += 1
                    # Détecter les sections qui sont des dates
                    elif '/' in section and '2025' in section:
                        corrupted_count += 1
                
                if corrupted_count == 0:
                    print(f"   ✅ {csv_file.name}: Propre ({len(df)} lignes)")
                else:
                    print(f"   ⚠️  {csv_file.name}: {corrupted_count} lignes corrompues détectées")
            else:
                print(f"   ℹ️  {csv_file.name}: Format différent (pas de colonnes galerie/section)")
                
        except Exception as e:
            print(f"   ❌ {csv_file.name}: Erreur de lecture - {e}")

if __name__ == "__main__":
    print("🧹 SYSTÈME D'EXTRACTION CLEAN SMC")
    print("Génère une nouvelle extraction sans lignes corrompues")
    print()
    
    # Permettre de personnaliser les paramètres via arguments
    if len(sys.argv) > 1:
        print("💡 Usage: python extraction_clean.py [dossier_source] [mois] [dossier_sortie]")
        print("💡 Exemple: python extraction_clean.py 'C:\\path\\to\\excel\\files' '2025-09' 'output_clean'")
        print()
    
    success = run_clean_extraction()
    
    if success:
        print(f"\n🎉 Extraction clean terminée avec succès !")
        print(f"💡 Vous pouvez maintenant utiliser ces fichiers propres")
        print(f"💡 Régénérez les fichiers colonnes avec: python transform_to_columns.py")
    else:
        print(f"\n😞 Échec de l'extraction clean")
        print(f"💡 Vérifiez les chemins et paramètres dans le script")