#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de comparaison des versions multiples pour identifier les meilleures
"""

import pandas as pd
from datetime import datetime
import traceback

def test_version_comparison():
    """Compare les différentes versions de fonctions similaires"""
    
    print("🔍 COMPARAISON DES VERSIONS MULTIPLES")
    print("=" * 50)
    
    # Test 1: Validation avec logs vs sans logs
    print("\n📊 TEST 1: VALIDATEURS")
    print("-" * 30)
    
    try:
        import demo_validator
        print("✅ demo_validator: FONCTIONNE")
        if hasattr(demo_validator, 'validate_data'):
            print("   - Fonction validate_data: PRÉSENTE")
        if hasattr(demo_validator, 'check_columns'):
            print("   - Fonction check_columns: PRÉSENTE")
    except Exception as e:
        print(f"❌ demo_validator: ERREUR - {e}")
    
    try:
        import demo_validator_with_log
        print("✅ demo_validator_with_log: FONCTIONNE")
        if hasattr(demo_validator_with_log, 'validate_data'):
            print("   - Fonction validate_data: PRÉSENTE")
        if hasattr(demo_validator_with_log, 'setup_logging'):
            print("   - Fonction setup_logging: PRÉSENTE (AVANTAGE)")
    except Exception as e:
        print(f"❌ demo_validator_with_log: ERREUR - {e}")
    
    # Test 2: Parsing des dates
    print("\n📅 TEST 2: PARSING DATES")
    print("-" * 30)
    
    try:
        import debug_comparison
        print("✅ debug_comparison: FONCTIONNE")
        if hasattr(debug_comparison, 'parse_date_safe'):
            print("   - Fonction parse_date_safe: PRÉSENTE")
        if hasattr(debug_comparison, 'compare_parsing_methods'):
            print("   - Fonction compare_parsing_methods: PRÉSENTE (AVANTAGE)")
    except Exception as e:
        print(f"❌ debug_comparison: ERREUR - {e}")
    
    # Test 3: Tests colonnes
    print("\n📋 TEST 3: EXTRACTION COLONNES")
    print("-" * 30)
    
    try:
        import test_extractor_columns
        print("✅ test_extractor_columns: FONCTIONNE")
        if hasattr(test_extractor_columns, 'test_column_extraction'):
            print("   - Fonction test_column_extraction: PRÉSENTE")
    except Exception as e:
        print(f"❌ test_extractor_columns: ERREUR - {e}")
    
    # Test 4: Recap ligne
    print("\n📝 TEST 4: RECAP LIGNE")
    print("-" * 30)
    
    try:
        import demo_recap_ligne
        print("✅ demo_recap_ligne: FONCTIONNE")
        if hasattr(demo_recap_ligne, 'generate_recap'):
            print("   - Fonction generate_recap: PRÉSENTE")
    except Exception as e:
        print(f"❌ demo_recap_ligne: ERREUR - {e}")
    
    try:
        import update_recap_ligne
        print("✅ update_recap_ligne: FONCTIONNE")
        if hasattr(update_recap_ligne, 'update_recap_function'):
            print("   - Fonction update_recap_function: PRÉSENTE (MISE À JOUR)")
    except Exception as e:
        print(f"❌ update_recap_ligne: ERREUR - {e}")

def recommend_best_versions():
    """Recommande les meilleures versions à garder"""
    
    print("\n\n🎯 RECOMMANDATIONS")
    print("=" * 50)
    
    recommendations = [
        ("demo_validator_with_log.py", "GARDER", "Version avec logging - plus complète"),
        ("demo_validator.py", "SUPPRIMER", "Version simple - redondante"),
        ("debug_comparison.py", "GARDER", "Fonctions de parsing robustes"),
        ("demo_recap_ligne.py", "ÉVALUER", "Vérifier si plus récent qu'update_recap_ligne"),
        ("update_recap_ligne.py", "ÉVALUER", "Vérifier si plus récent que demo_recap_ligne"),
        ("test_extractor_columns.py", "GARDER", "Tests utiles pour validation")
    ]
    
    for fichier, action, raison in recommendations:
        emoji = "🔴" if action == "SUPPRIMER" else "🟢" if action == "GARDER" else "🟡"
        print(f"{emoji} {fichier:<30} {action:<10} - {raison}")

if __name__ == "__main__":
    test_version_comparison()
    recommend_best_versions()