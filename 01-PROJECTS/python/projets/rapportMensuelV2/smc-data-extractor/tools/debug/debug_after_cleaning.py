#!/usr/bin/env python3
"""
Debug des données après nettoyage
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent / "src"))

from ligne_summary_generator import LigneSummaryGenerator

def debug_after_cleaning():
    """Debug de l'état des données après nettoyage"""
    
    input_folder = Path("examples/format_apres")
    output_folder = Path("examples/debug_clean")
    output_folder.mkdir(exist_ok=True)
    month = "2024-09"
    
    generator = LigneSummaryGenerator(
        csv_folder=input_folder,
        output_folder=output_folder,
        month=month
    )
    
    # Charger les données et voir leur état
    print("🔍 Chargement et vérification des données...")
    data = generator.load_csv_data()
    
    for key, df in data.items():
        print(f"\n📊 Dataset '{key}':")
        print(f"   - Nombre de lignes: {len(df)}")
        print(f"   - Colonnes: {list(df.columns) if not df.empty else 'VIDE'}")
        
        if not df.empty and len(df) > 0:
            # Vérifier les colonnes requises pour le groupement
            required_cols = ['galerie', 'section', 'source_file']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"   ❌ Colonnes manquantes pour groupement: {missing_cols}")
            else:
                print(f"   ✅ Toutes les colonnes requises présentes")
                
                # Tester le groupement
                try:
                    grouped = df.groupby(['galerie', 'section', 'source_file'])
                    print(f"   ✅ Groupement réussi: {len(grouped)} groupes")
                except Exception as e:
                    print(f"   ❌ Erreur groupement: {e}")
                    
                    # Analyser les valeurs problématiques
                    print(f"   🔍 Analyse des valeurs:")
                    for col in required_cols:
                        if col in df.columns:
                            unique_vals = df[col].unique()
                            print(f"      {col}: {len(unique_vals)} valeurs uniques")
                            if len(unique_vals) <= 10:
                                print(f"         Valeurs: {list(unique_vals)}")
                            else:
                                print(f"         Premières valeurs: {list(unique_vals[:5])}")
                        else:
                            print(f"      {col}: COLONNE MANQUANTE")

if __name__ == "__main__":
    debug_after_cleaning()