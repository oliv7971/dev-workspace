#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demo du validateur de données SMC avec log détaillé des calculs
Version améliorée qui explique comment chaque valeur a été calculée
"""

from src.data_validator import SMCDataValidator
import logging

def main():
    """Démonstration du validateur avec explications détaillées"""
    
    print("🔍 DEMO - Validateur SMC avec Log des Calculs")
    print("Vérifie les données ET explique comment elles ont été calculées")
    print("=" * 70)
    
    # Configuration
    csv_folder = "C:/temp/smc_output_demo"
    source_folder = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/Rapports d'activité/2025/250901-rapport mensuel aout/1-tableaux"
    month = "2025-08"
    
    print(f"📁 Dossier CSV: {csv_folder}")
    print(f"📁 Dossier source: {source_folder}")
    print(f"📅 Mois: {month}")
    print()
    print("🎯 Le validateur va :")
    print("   ✅ Vérifier la correspondance des données")
    print("   📊 Expliquer chaque calcul de valeur périodique")
    print("   📋 Montrer les formules utilisées")
    print("   📄 Générer un rapport détaillé")
    print()
    
    # Configuration du logging
    logging.basicConfig(level=logging.WARNING, format='%(name)s - %(levelname)s - %(message)s')
    
    # Créer et lancer le validateur
    validator = SMCDataValidator(csv_folder, source_folder, month)
    
    # Test sur un seul fichier d'abord pour voir le log détaillé
    print("🧪 Test sur un fichier spécifique pour voir le log détaillé...")
    
    try:
        # Tester juste un fichier pour commencer
        import openpyxl
        from pathlib import Path
        
        test_file = Path(source_folder) / "GHA" / "04_303-GHA_SMC_T15_25_08_18.xlsm"
        if test_file.exists():
            print(f"📊 Test sur: {test_file.name}")
            
            # Charger les données CSV
            csv_data = validator.load_csv_data()
            
            # Tester l'extraction avec log
            wb = openpyxl.load_workbook(test_file, data_only=True)
            if 'Convergences' in wb.sheetnames:
                print("\n🔄 Extraction des convergences avec log détaillé...")
                excel_data = validator.extract_excel_convergences(wb['Convergences'])
                
                print(f"✅ {len(excel_data)} métriques extraites")
                print("\n📋 Exemple de log de calcul :")
                
                # Afficher le log pour la première métrique
                if validator.validation_results['calculation_log']:
                    first_calc = validator.validation_results['calculation_log'][0]
                    print(f"   Métrique: {first_calc['metric']}")
                    for step in first_calc['calculations']:
                        print(f"   • {step['step']}: {step['description']}")
                        print(f"     Formule: {step['formula']}")
                
                # Sauvegarder le log détaillé
                validator.save_calculation_log()
                
        else:
            print("❌ Fichier de test non trouvé, lancement validation complète...")
            results = validator.validate_all_data()
    
    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        print("Lancement validation complète...")
        results = validator.validate_all_data()
    
    print("\n🎉 Test terminé!")
    print("Vérifiez les fichiers générés :")
    print("   📄 Rapport_Validation_SMC_xxxx.txt - Rapport complet")
    print("   📊 Log_Calculs_SMC_xxxx.txt - Explications détaillées des calculs")

if __name__ == "__main__":
    main()
