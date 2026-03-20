"""
Script de lancement de tous les tests
"""

import unittest
import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from config import get_config
from logging_utils import get_logger


def run_all_tests():
    """Lance tous les tests unitaires"""
    config = get_config()
    logger = get_logger("Tests")
    
    print("🧪 Lancement des tests unitaires")
    print(f"   Calculateur d'Axes v{config.VERSION}")
    print("="*50)
    
    # Découvrir et lancer tous les tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Runner avec verbosité
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    
    logger.info("Début des tests unitaires")
    result = runner.run(suite)
    
    # Résumé
    print("\n" + "="*50)
    if result.wasSuccessful():
        print("✅ TOUS LES TESTS SONT PASSÉS")
        logger.info(f"Tests réussis: {result.testsRun} tests, 0 échec")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        logger.error(f"Tests: {result.testsRun}, Échecs: {len(result.failures)}, Erreurs: {len(result.errors)}")
        
        # Détail des échecs
        if result.failures:
            print(f"\n💥 {len(result.failures)} échec(s):")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print(f"\n🚨 {len(result.errors)} erreur(s):")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)