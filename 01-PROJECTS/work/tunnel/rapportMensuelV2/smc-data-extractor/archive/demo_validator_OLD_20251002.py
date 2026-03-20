#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demo du validateur de données SMC
Teste le module de contrôle qui vérifie l'intégrité des données extraites
"""

from src.data_validator import SMCDataValidator
import logging

def main():
    """Démonstration du validateur de données"""
    
    print("🔍 DEMO - Validateur de données SMC")
    print("Vérifie que les données CSV correspondent aux fichiers Excel sources")
    print("=" * 60)
    
    # Configuration
    csv_folder = "C:/temp/smc_output_demo"
    source_folder = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/Rapports d'activité/2025/250901-rapport mensuel aout/1-tableaux"
    month = "2025-08"
    
    print(f"📁 Dossier CSV: {csv_folder}")
    print(f"📁 Dossier source: {source_folder}")
    print(f"📅 Mois: {month}")
    print()
    
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    
    # Créer et lancer le validateur
    validator = SMCDataValidator(csv_folder, source_folder, month)
    results = validator.validate_all_data()
    
    print("\n🎯 Validation terminée!")
    print("Vérifiez le rapport détaillé dans le fichier généré.")
    
    return results

if __name__ == "__main__":
    main()
