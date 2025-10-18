#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'extraction complète des données de carrure
Démonstration avec le fichier réel
"""

from pathlib import Path
from carrure_extractor import run_carrure_extraction
import tempfile

def demo_carrure_extraction():
    """Démonstration d'extraction de données de carrure"""

    print("🎯 DÉMONSTRATION EXTRACTION CARRURE")
    print("=" * 50)

    # Paramètres
    root_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\1-tableaux"
    month = "2025-09"

    # Dossier temporaire pour les tests
    with tempfile.TemporaryDirectory() as temp_dir:
        output_folder = Path(temp_dir) / "carrure_test"
        output_folder.mkdir(exist_ok=True)

        print(f"📁 Dossier source: {root_folder}")
        print(f"📁 Dossier sortie: {output_folder}")
        print(f"📅 Mois: {month}")
        print()

        # Options
        options = {
            'generate_csv': True,
            'generate_pdf': False,
            'generate_ligne_summaries': True
        }

        # Lancer l'extraction
        success = run_carrure_extraction(root_folder, month, str(output_folder), options, print)

        if success:
            print("\n📊 FICHIERS GÉNÉRÉS:")
            for file in output_folder.rglob("*"):
                if file.is_file():
                    print(f"   📄 {file.name} ({file.stat().st_size} octets)")

            # Afficher aperçu des CSV générés
            print(f"\n👀 APERÇU DES DONNÉES:")

            carrure_csv = output_folder / "carrure_deplacements.csv"
            if carrure_csv.exists():
                import pandas as pd
                df = pd.read_csv(carrure_csv)
                print(f"\n📊 DÉPLACEMENTS CARRURE ({len(df)} lignes):")
                print(f"   Colonnes: {list(df.columns)}")
                if len(df) > 0:
                    print(f"   Première date: {df['date'].iloc[0] if 'date' in df.columns else 'N/A'}")
                    print(f"   Dernière date: {df['date'].iloc[-1] if 'date' in df.columns else 'N/A'}")

            cintres_csv = output_folder / "cintres_deplacements.csv"
            if cintres_csv.exists():
                import pandas as pd
                df = pd.read_csv(cintres_csv)
                print(f"\n🏗️ DÉPLACEMENTS CINTRES ({len(df)} lignes):")
                print(f"   Colonnes: {list(df.columns)}")
                if len(df) > 0:
                    print(f"   Première date: {df['date'].iloc[0] if 'date' in df.columns else 'N/A'}")
                    print(f"   Dernière date: {df['date'].iloc[-1] if 'date' in df.columns else 'N/A'}")

        print(f"\n✅ DÉMONSTRATION TERMINÉE - Succès: {success}")

        # Les fichiers temporaires seront automatiquement supprimés

if __name__ == "__main__":
    demo_carrure_extraction()
