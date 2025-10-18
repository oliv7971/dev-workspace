#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'extracteur carrure précis - Version workspace
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from carrure_precise_extractor import CarrurePreciseExtractor

def test_carrure_precise():
    """Test de l'extracteur avec un fichier exemple"""

    print("🧪 Test Extracteur Carrure Précis")
    print("=" * 50)

    # Fichier de test
    test_file = Path(r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\1-tableaux\GGS\03_100-GGS-GRD-double carrure-XYZ-tableau Jour-25-09-10.xlsm")
    test_month = "2025-09"
    test_output = Path("test_output_carrure")

    print(f"📁 Fichier test: {test_file.name}")
    print(f"📅 Mois cible: {test_month}")
    print(f"📂 Sortie: {test_output}")
    print()

    if not test_file.exists():
        print("❌ Fichier de test non trouvé")
        return False

    try:
        # Créer l'extracteur
        extractor = CarrurePreciseExtractor(test_month)

        # Extraire les données
        print("🔍 Extraction en cours...")
        results = extractor.extract_carrure_file(test_file)

        # Afficher un résumé
        print("\n📊 Résumé de l'extraction:")
        print(f"   • Déplacements carrure: {len(results['deplacements_carrure'])} métriques")
        print(f"   • Déplacements cintres: {len(results['deplacements_cintres'])} métriques")

        # Afficher quelques exemples
        if results['deplacements_carrure']:
            print("\n🔬 Exemples Déplacements carrure:")
            for i, metric in enumerate(results['deplacements_carrure'][:3]):
                print(f"   {i+1}. {metric['code_point']}_{metric['type_mesure']}:")
                print(f"      - Cumulé: {metric['deplacement_cumule']}")
                print(f"      - Périodique: {metric['deplacement_periodique']}")
                print(f"      - Dernière mesure: {metric['date_derniere_mesure']}")

        if results['deplacements_cintres']:
            print("\n🔬 Exemples Déplacements cintres:")
            for i, metric in enumerate(results['deplacements_cintres'][:3]):
                print(f"   {i+1}. {metric['code_point']}_{metric['type_mesure']}:")
                print(f"      - Cumulé: {metric['deplacement_cumule']}")
                print(f"      - Périodique: {metric['deplacement_periodique']}")
                print(f"      - Dernière mesure: {metric['date_derniere_mesure']}")

        # Sauvegarder
        print("\n💾 Sauvegarde...")
        output_file = extractor.save_to_csv(results, test_output)

        if output_file:
            print(f"✅ Fichier généré: {output_file}")

            # Lire quelques lignes du CSV pour vérification
            import pandas as pd
            df = pd.read_csv(output_file)
            print(f"\n📋 Contenu CSV ({len(df)} lignes):")
            print(df.head())

            return True
        else:
            print("❌ Échec sauvegarde")
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_carrure_precise()
    print(f"\n🎯 Test {'RÉUSSI' if success else 'ÉCHOUÉ'}")
