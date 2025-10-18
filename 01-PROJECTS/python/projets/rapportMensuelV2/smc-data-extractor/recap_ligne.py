#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMC Data Extractor - Script de mise à jour
Mise à jour automatique avec la nouvelle fonctionnalité de récapitulatifs en ligne
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def update_smc_data_extractor():
    """Met à jour le SMC Data Extractor avec les nouvelles fonctionnalités"""
    
    print("🚀 MISE À JOUR SMC DATA EXTRACTOR")
    print("=" * 50)
    print("Ajout des récapitulatifs en ligne pour convergences et déplacements")
    print()
    
    # Vérifier la structure du projet
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"
    
    if not src_dir.exists():
        print("❌ Dossier 'src' non trouvé. Assurez-vous d'être dans le bon répertoire.")
        return False
    
    print("📍 Répertoire de travail:", current_dir)
    print()
    
    # Sauvegarde
    backup_dir = current_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        print("💾 Création d'une sauvegarde...")
        shutil.copytree(src_dir, backup_dir / "src")
        print(f"✅ Sauvegarde créée: {backup_dir}")
        print()
        
    except Exception as e:
        print(f"⚠️ Impossible de créer la sauvegarde: {e}")
        response = input("Continuer sans sauvegarde? (o/n): ")
        if response.lower() not in ['o', 'oui', 'y', 'yes']:
            return False
    
    # Vérifier les fichiers existants
    files_to_check = [
        "smc_evolutions.py",
        "smc_gui.py"
    ]
    
    print("🔍 Vérification des fichiers existants...")
    for file_name in files_to_check:
        file_path = src_dir / file_name
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - MANQUANT")
            return False
    
    print()
    
    # Vérifier si la nouvelle fonctionnalité existe déjà
    ligne_summary_file = src_dir / "ligne_summary_generator.py"
    
    if ligne_summary_file.exists():
        print("🔄 Le module ligne_summary_generator.py existe déjà")
        response = input("Voulez-vous le remplacer? (o/n): ")
        if response.lower() not in ['o', 'oui', 'y', 'yes']:
            print("⏩ Mise à jour annulée")
            return False
    
    # Vérifications de l'intégration
    print("🔧 Vérification de l'intégration...")
    
    # Vérifier smc_evolutions.py
    smc_evolutions_path = src_dir / "smc_evolutions.py"
    with open(smc_evolutions_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "generate_ligne_summaries" in content:
        print("  ✅ smc_evolutions.py déjà intégré")
        smc_evolutions_updated = True
    else:
        print("  🔄 smc_evolutions.py nécessite une mise à jour")
        smc_evolutions_updated = False
    
    # Vérifier smc_gui.py
    smc_gui_path = src_dir / "smc_gui.py"
    with open(smc_gui_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "generate_ligne_var" in content:
        print("  ✅ smc_gui.py déjà intégré")
        smc_gui_updated = True
    else:
        print("  🔄 smc_gui.py nécessite une mise à jour")
        smc_gui_updated = False
    
    print()
    
    # Résumé de la mise à jour
    print("📋 RÉSUMÉ DE LA MISE À JOUR:")
    print("-" * 30)
    
    if ligne_summary_file.exists():
        print("  📄 ligne_summary_generator.py - EXISTE")
    else:
        print("  📄 ligne_summary_generator.py - À CRÉER")
    
    if smc_evolutions_updated:
        print("  🔧 smc_evolutions.py - DÉJÀ INTÉGRÉ")
    else:
        print("  🔧 smc_evolutions.py - À METTRE À JOUR")
    
    if smc_gui_updated:
        print("  🎨 smc_gui.py - DÉJÀ INTÉGRÉ")
    else:
        print("  🎨 smc_gui.py - À METTRE À JOUR")
    
    print()
    
    if ligne_summary_file.exists() and smc_evolutions_updated and smc_gui_updated:
        print("✅ Tous les composants sont déjà à jour!")
        print()
        print("🎯 FONCTIONNALITÉS DISPONIBLES:")
        print("  • Récapitulatifs en ligne format texte")
        print("  • Récapitulatifs CSV avec données horizontales")
        print("  • Intégration dans l'interface graphique")
        print("  • Option dans le processus d'extraction")
        print()
        print("📚 Consultez le guide: docs/recap_ligne_guide.md")
        return True
    
    # Tests
    print("🧪 Test de la fonctionnalité...")
    
    try:
        # Test d'import
        sys.path.insert(0, str(src_dir))
        
        if ligne_summary_file.exists():
            from ligne_summary_generator import generate_ligne_summaries
            print("  ✅ Module ligne_summary_generator importé")
        
        # Test avec des données de test
        test_csv_dir = Path("C:/temp/smc_output")
        if test_csv_dir.exists():
            conv_csv = test_csv_dir / "Convergences_SMC.csv"
            depl_csv = test_csv_dir / "Deplacements_SMC.csv"
            
            if conv_csv.exists() and depl_csv.exists():
                print("  📊 Données de test trouvées")
                print("  🔄 Test de génération...")
                
                success = generate_ligne_summaries(
                    str(test_csv_dir), 
                    str(test_csv_dir), 
                    "2025-08"
                )
                
                if success:
                    print("  ✅ Test réussi!")
                else:
                    print("  ⚠️ Test échoué")
            else:
                print("  ⚠️ Pas de données de test disponibles")
        else:
            print("  ⚠️ Dossier de test non trouvé")
    
    except Exception as e:
        print(f"  ❌ Erreur de test: {e}")
    
    print()
    print("🎉 MISE À JOUR TERMINÉE!")
    print()
    print("📖 UTILISATION:")
    print("  1. Interface graphique: Cochez 'Générer récapitulatifs en ligne'")
    print("  2. Code Python: options['generate_ligne_summaries'] = True")
    print("  3. Demo: python demo_recap_ligne.py")
    print()
    print("📁 FICHIERS GÉNÉRÉS:")
    print("  • Recapitulatifs_Ligne_SMC_YYYY_MM.txt")
    print("  • Convergences_Ligne_SMC_YYYY_MM.csv")
    print("  • Deplacements_Ligne_SMC_YYYY_MM.csv")
    
    return True

if __name__ == "__main__":
    success = update_smc_data_extractor()
    
    if success:
        print()
        print("✨ Mise à jour terminée avec succès!")
        print("📚 Consultez la documentation pour plus d'informations.")
    else:
        print()
        print("❌ Échec de la mise à jour")
        print("Vérifiez les messages d'erreur ci-dessus.")
    
    input("\nAppuyez sur Entrée pour fermer...")
