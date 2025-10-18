#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMC Récapitulatifs Demo - Démonstration de la nouvelle fonctionnalité
Montre comment utiliser les récapitulatifs en ligne pour les données SMC
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def demo_recap_ligne():
    """Démonstration des récapitulatifs en ligne"""
    print("🚀 DÉMONSTRATION - Récapitulatifs en ligne SMC")
    print("=" * 60)
    
    # Paramètres de test
    csv_folder = r"C:\temp\smc_output"
    output_folder = r"C:\temp\smc_output"
    month = "2025-08"
    
    print(f"📁 Dossier CSV: {csv_folder}")
    print(f"💾 Dossier sortie: {output_folder}")
    print(f"📅 Mois: {month}")
    print()
    
    try:
        # Import de la fonctionnalité
        from ligne_summary_generator import generate_ligne_summaries
        
        print("🔄 Génération des récapitulatifs en ligne...")
        success = generate_ligne_summaries(csv_folder, output_folder, month)
        
        if success:
            print("✅ Récapitulatifs générés avec succès!")
            print()
            print("📋 Fichiers générés:")
            
            # Vérifier les fichiers générés
            output_path = Path(output_folder)
            
            text_file = output_path / f"Recapitulatifs_Ligne_SMC_{month.replace('-', '_')}.txt"
            conv_csv = output_path / f"Convergences_Ligne_SMC_{month.replace('-', '_')}.csv"
            depl_csv = output_path / f"Deplacements_Ligne_SMC_{month.replace('-', '_')}.csv"
            
            if text_file.exists():
                print(f"  📄 {text_file.name} - Récapitulatif texte complet")
            
            if conv_csv.exists():
                print(f"  📊 {conv_csv.name} - Convergences au format CSV ligne")
            
            if depl_csv.exists():
                print(f"  📊 {depl_csv.name} - Déplacements au format CSV ligne")
            
            print()
            print("🔍 Exemple de contenu - Convergences:")
            print("-" * 40)
            
            # Afficher un exemple du contenu texte
            if text_file.exists():
                with open(text_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Trouver une section convergences
                for i, line in enumerate(lines):
                    if "Convergences - périodique" in line:
                        print(line.strip())
                        if i + 1 < len(lines):
                            print(lines[i + 1].strip())
                        break
            
            print()
            print("📊 Format CSV - les données sont organisées avec:")
            print("  • Une ligne par mode (périodique/cumulé)")
            print("  • Une colonne par métrique (BG, HG, HD, BD, etc.)")
            print("  • Regroupement par galerie et section")
            
        else:
            print("❌ Échec de la génération")
            
    except ImportError as e:
        print(f"❌ Module manquant: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print()
    print("=" * 60)
    print("✨ Démonstration terminée")

def demo_integration_complete():
    """Démonstration de l'intégration complète avec smc_evolutions"""
    print()
    print("🔧 DÉMONSTRATION - Intégration complète")
    print("=" * 60)
    
    # Paramètres de test
    root_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250901-rapport mensuel aout\1-tableaux"
    output_folder = r"C:\temp\smc_output_demo"
    month = "2025-08"
    
    print(f"📁 Dossier source: {root_folder}")
    print(f"💾 Dossier sortie: {output_folder}")
    print(f"📅 Mois: {month}")
    print()
    
    try:
        # Import de la fonctionnalité principale
        from smc_evolutions import run_extraction
        
        print("🔄 Extraction complète avec récapitulatifs en ligne...")
        
        # Options incluant les récapitulatifs en ligne
        options = {
            'generate_csv': True,
            'generate_pdf': False,
            'generate_ligne_summaries': True
        }
        
        def log_callback(message):
            print(f"  {message}")
        
        success = run_extraction(root_folder, month, output_folder, options, log_callback)
        
        if success:
            print()
            print("✅ Extraction complète terminée!")
            print("📋 Tous les fichiers ont été générés avec les récapitulatifs en ligne")
        else:
            print("❌ Échec de l'extraction")
            
    except ImportError as e:
        print(f"❌ Module manquant: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🎯 DEMO - Nouvelles fonctionnalités SMC Data Extractor")
    print("Récapitulatifs en ligne pour convergences et déplacements")
    print()
    
    # Démo 1: Récapitulatifs seuls
    demo_recap_ligne()
    
    # Démo 2: Intégration complète (optionnel)
    response = input("Voulez-vous tester l'intégration complète? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        demo_integration_complete()
    
    print()
    print("🎉 Démonstration terminée - Merci!")
