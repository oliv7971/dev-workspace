#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour transformer les données du format "lignes" vers le format "colonnes"
Utilise votre fonction existante ligne_summary_generator.py
"""

import sys
from pathlib import Path
import pandas as pd
import os

# Ajouter le dossier src au path pour importer les modules
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from ligne_summary_generator import generate_ligne_summaries, LigneSummaryGenerator
except ImportError as e:
    print(f"❌ Impossible d'importer le module ligne_summary_generator: {e}")
    sys.exit(1)

def transform_data_to_columns():
    """Transforme les données récentes en format colonnes"""
    
    print("🔄 Transformation des données vers le format colonnes...")
    print("=" * 60)
    
    # Dossiers de travail
    workspace_root = Path(__file__).parent
    examples_folder = workspace_root / "examples" / "format_apres"
    output_folder = workspace_root / "examples" / "format_colonnes_genere"
    
    # Créer le dossier de sortie
    output_folder.mkdir(exist_ok=True)
    
    # Vérifier que les fichiers sources existent
    convergences_file = examples_folder / "Convergences_SMC.csv"
    deplacements_file = examples_folder / "Deplacements_SMC.csv"
    
    if not convergences_file.exists():
        print(f"❌ Fichier manquant: {convergences_file}")
        return False
    
    if not deplacements_file.exists():
        print(f"❌ Fichier manquant: {deplacements_file}")
        return False
    
    print(f"📊 Source convergences: {convergences_file}")
    print(f"📊 Source déplacements: {deplacements_file}")
    print(f"📁 Dossier sortie: {output_folder}")
    print()
    
    # Utiliser votre fonction existante
    month = "2025-09"  # Mois des nouvelles données
    
    try:
        # Créer une instance du générateur
        generator = LigneSummaryGenerator(
            csv_folder=str(examples_folder),
            output_folder=str(output_folder),
            month=month
        )
        
        print("🔄 Génération du format texte (récapitulatifs)...")
        text_success = generator.generate_all_ligne_summaries()
        
        print("🔄 Génération du format CSV colonnes...")
        csv_success = generator.generate_csv_ligne_summaries()
        
        if text_success or csv_success:
            print("\n✅ Transformation terminée !")
            print("\n📁 Fichiers générés :")
            
            # Lister les fichiers générés
            for file in output_folder.glob("*"):
                if file.is_file():
                    print(f"  📄 {file.name}")
            
            return True
        else:
            print("\n❌ Échec de la transformation")
            return False
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la transformation: {e}")
        return False

def demo_compare_formats():
    """Compare les deux formats pour démonstration"""
    
    print("\n" + "=" * 60)
    print("🔍 COMPARAISON DES FORMATS")
    print("=" * 60)
    
    # Fichier original (format lignes)
    format_lignes = Path(__file__).parent / "examples" / "format_apres" / "Convergences_SMC.csv"
    
    # Fichier généré (format colonnes)
    format_colonnes = Path(__file__).parent / "examples" / "format_colonnes_genere" / "Convergences_Ligne_SMC_2025_09.csv"
    
    if format_lignes.exists():
        print("\n📊 FORMAT LIGNES (original - une ligne par métrique):")
        df_lignes = pd.read_csv(format_lignes)
        print(f"   Taille: {len(df_lignes)} lignes × {len(df_lignes.columns)} colonnes")
        print("   Exemple:")
        print(df_lignes.head(3)[['galerie', 'section', 'metric', 'periodic_mm', 'cumulative_mm']].to_string(index=False))
    
    if format_colonnes.exists():
        print(f"\n📊 FORMAT COLONNES (généré - une ligne par galerie/section):")
        df_colonnes = pd.read_csv(format_colonnes)
        print(f"   Taille: {len(df_colonnes)} lignes × {len(df_colonnes.columns)} colonnes")
        print("   Exemple:")
        print(df_colonnes.head(3).to_string(index=False))
    
    print("\n🎯 RÉSULTAT:")
    print("   Le format 'colonnes' regroupe toutes les métriques d'une galerie/section sur une ligne")
    print("   Le format 'lignes' a une ligne séparée pour chaque métrique")

if __name__ == "__main__":
    print("🎯 TRANSFORMATION DE FORMAT - SMC Data Extractor")
    print("Du format 'lignes' vers le format 'colonnes'")
    print()
    
    # Effectuer la transformation
    success = transform_data_to_columns()
    
    if success:
        # Démonstration comparative
        demo_compare_formats()
    
    print("\n" + "=" * 60)
    print("✨ Transformation terminée")