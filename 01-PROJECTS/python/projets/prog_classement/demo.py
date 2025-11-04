"""
Script de démonstration et test du système de classement amélioré
"""

import os
import sys

# Ajout du répertoire src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logger import get_logger
from validation_interactive import ValidateurClassification
from backup_manager import GestionnaireBackup
from gestion_conflits import GestionnaireConflits


def tester_configuration():
    """Test de la configuration"""
    print("🔧 Test de la configuration...")
    
    try:
        import json
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Configuration chargée avec succès")
        print(f"   • Source: {config['chemins']['source_base']}")
        print(f"   • Destination temp: {config['chemins']['destination_temp']}")
        print(f"   • Mode sécurisé: {config['options']['mode_securise']}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False


def tester_logging():
    """Test du système de logging"""
    print("\n📝 Test du logging...")
    
    try:
        logger = get_logger()
        logger.info("Test du système de logging")
        logger.warning("Test warning")
        logger.log_operation("TEST", "source_test", "dest_test", "SUCCESS")
        
        print("✅ Logging fonctionnel")
        return True
    except Exception as e:
        print(f"❌ Erreur logging: {e}")
        return False


def tester_backup():
    """Test du système de backup"""
    print("\n💾 Test du système de backup...")
    
    try:
        gestionnaire = GestionnaireBackup()
        gestionnaire.afficher_statistiques()
        
        print("✅ Gestionnaire de backup initialisé")
        return True
    except Exception as e:
        print(f"❌ Erreur backup: {e}")
        return False


def tester_detection_categories():
    """Test de la détection de catégories"""
    print("\n🔍 Test de détection de catégories...")
    
    try:
        validateur = ValidateurClassification()
        
        # Test avec quelques noms de dossiers
        test_dossiers = [
            "2024-10-15-a-imp-gcs-implantation-nouvelle",
            "leve-polygo-GHA-octobre",
            "auscultation-convergences-1631",
            "dossier-sans-mot-cle"
        ]
        
        for dossier in test_dossiers:
            categorie, confidence, mot_cle = validateur.detecter_categorie(dossier)
            print(f"   📁 {dossier}")
            print(f"      → {categorie} (confiance: {confidence:.2f}, mot-clé: {mot_cle})")
        
        print("✅ Détection de catégories fonctionnelle")
        return True
    except Exception as e:
        print(f"❌ Erreur détection: {e}")
        return False


def creer_exemple_structure():
    """Crée une structure d'exemple pour les tests"""
    print("\n🏗️  Création structure d'exemple...")
    
    try:
        import tempfile
        import shutil
        
        # Création d'un dossier temporaire pour les tests
        temp_dir = os.path.join(tempfile.gettempdir(), "classement_test")
        
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        os.makedirs(temp_dir, exist_ok=True)
        
        # Structure d'exemple
        exemples = [
            "galerie_test/_a_classer/2024-10-15-a-implantation-GCS",
            "galerie_test/_a_classer/leve-topo-GHA-octobre",
            "galerie_test/_a_classer/auscultation-conv-1631",
            "ALVEOLE AHA1632/_a_classer/metres-1632-nouvelle-zone"
        ]
        
        for exemple in exemples:
            chemin_complet = os.path.join(temp_dir, exemple)
            os.makedirs(chemin_complet, exist_ok=True)
            
            # Création d'un fichier exemple
            with open(os.path.join(chemin_complet, "exemple.txt"), 'w') as f:
                f.write(f"Fichier d'exemple pour {exemple}")
        
        print(f"✅ Structure d'exemple créée dans: {temp_dir}")
        print("   Vous pouvez utiliser ce dossier pour tester le système")
        
        return temp_dir
    except Exception as e:
        print(f"❌ Erreur création structure: {e}")
        return None


def demo_complete():
    """Démonstration complète du système"""
    print(f"\n{'='*80}")
    print(f"🎯 DÉMONSTRATION SYSTÈME DE CLASSEMENT AMÉLIORÉ")
    print(f"{'='*80}")
    
    resultats = []
    
    # Tests des composants
    resultats.append(("Configuration", tester_configuration()))
    resultats.append(("Logging", tester_logging()))
    resultats.append(("Backup", tester_backup()))
    resultats.append(("Détection", tester_detection_categories()))
    
    # Résultats
    print(f"\n📊 RÉSULTATS DES TESTS:")
    print(f"{'='*50}")
    
    tous_ok = True
    for nom, resultat in resultats:
        status = "✅ OK" if resultat else "❌ ERREUR"
        print(f"{nom:<20} {status}")
        if not resultat:
            tous_ok = False
    
    print(f"\n🎯 ÉTAT GLOBAL: {'✅ TOUS LES TESTS PASSÉS' if tous_ok else '❌ DES ERREURS DÉTECTÉES'}")
    
    if tous_ok:
        print(f"\n🚀 Votre système est prêt à être utilisé!")
        print(f"   Exécutez: python src/main.py")
        
        # Création structure d'exemple
        if input("\nCréer structure d'exemple pour test? (o/N): ").lower() == 'o':
            temp_dir = creer_exemple_structure()
            if temp_dir:
                print(f"\n💡 CONSEIL:")
                print(f"   1. Modifiez config/config.json pour pointer vers {temp_dir}")
                print(f"   2. Lancez python src/main.py")
                print(f"   3. Testez les différentes fonctionnalités")
    else:
        print(f"\n⚠️  Corrigez les erreurs avant d'utiliser le système")


if __name__ == "__main__":
    demo_complete()