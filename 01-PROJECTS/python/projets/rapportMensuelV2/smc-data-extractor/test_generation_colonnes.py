#!/usr/bin/env python3
"""
Test pour générer les fichiers en format colonnes avec corrections des noms
"""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent / "src"))

from ligne_summary_generator import LigneSummaryGenerator

def test_generation_colonnes():
    """Tester la génération des fichiers colonnes avec corrections"""
    
    # Dossier des données d'entrée
    input_folder = Path("examples/format_apres")
    output_folder = Path("examples/format_colonnes_corrige") 
    
    # Créer le dossier de sortie s'il n'existe pas
    output_folder.mkdir(exist_ok=True)
    
    # Mois à traiter (depuis les noms des fichiers)
    month = "2024-09"  # Correspond aux données de septembre
    
    print(f"🔄 Génération des colonnes pour {month}")
    print(f"📁 Entrée: {input_folder}")  
    print(f"📁 Sortie: {output_folder}")
    
    # Créer le générateur
    generator = LigneSummaryGenerator(
        csv_folder=input_folder,
        output_folder=output_folder,
        month=month
    )
    
    # Générer les CSV en format ligne
    success = generator.generate_csv_ligne_summaries()
    
    if success:
        print("✅ Génération réussie!")
        
        # Lister les fichiers générés
        print("\n📄 Fichiers générés:")
        for file in output_folder.glob("*.csv"):
            print(f"   - {file.name}")
            
        return True
    else:
        print("❌ Échec de la génération")
        return False

if __name__ == "__main__":
    test_generation_colonnes()