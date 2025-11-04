"""
DIAGNOSTIC RAPIDE - Détection des problèmes
Vérifie tous les fichiers nécessaires et répare ce qui manque
"""

import os
import json

def verifier_fichiers_essentiels():
    """Vérifie que tous les fichiers essentiels existent"""
    print("🔍 DIAGNOSTIC - Vérification des fichiers")
    print("="*50)
    
    fichiers_requis = {
        "config/config.json": "Configuration principale",
        "config/categories.json": "Catégories d'activités", 
        "config/correspondances.json": "Mapping galeries",
        "src/logger.py": "Module de logging",
        "src/main.py": "Programme principal"
    }
    
    manquants = []
    
    for fichier, description in fichiers_requis.items():
        if os.path.exists(fichier):
            print(f"✅ {fichier} - {description}")
        else:
            print(f"❌ {fichier} - {description} - MANQUANT")
            manquants.append(fichier)
    
    return manquants

def creer_fichiers_manquants(manquants):
    """Crée les fichiers manquants avec contenu minimal"""
    print(f"\n🔧 RÉPARATION - Création des fichiers manquants")
    print("="*50)
    
    for fichier in manquants:
        print(f"📝 Création de {fichier}...")
        
        # Création du dossier si nécessaire
        dossier = os.path.dirname(fichier)
        if dossier:
            os.makedirs(dossier, exist_ok=True)
        
        # Contenu selon le type de fichier
        if fichier == "config/config.json":
            contenu = {
                "chemins": {
                    "source_base": "C:\\data\\11-CHANTIERS\\BURE\\10-ACTIVITES",
                    "destination_temp": "C:\\Temp\\activites-par-galerie", 
                    "destination_finale": "C:\\data\\11-CHANTIERS\\BURE\\11-GALERIES",
                    "backup_dir": "C:\\Backup\\classement",
                    "logs_dir": "C:\\Temp\\logs\\classement"
                },
                "dossiers": {
                    "a_classer": "_a_classer",
                    "classe": "_classé", 
                    "divers": "DIVERS",
                    "non_reconnus": "__NON_RECONNUS"
                },
                "options": {
                    "mode_securise": True,
                    "backup_automatique": True,
                    "validation_interactive": True,
                    "niveau_log": "INFO",
                    "max_backups": 10
                }
            }
            with open(fichier, 'w', encoding='utf-8') as f:
                json.dump(contenu, f, indent=2, ensure_ascii=False)
        
        elif fichier == "config/categories.json":
            contenu = {
                "IMPLANTATION": ["implant", "imp", "implantation"],
                "AUSCULTATION": ["aus", "auscult", "conv", "convergences"],
                "LEVE": ["levé", "leve", "lev", "lv"],
                "POLYGO": ["poly", "polygo", "refs"],
                "THEORIQUES": ["theoriques", "theo", "prepa"],
                "METRES": ["metres", "métrés", "metrés"],
                "ETUDE": ["etude"],
                "RECOLEMENT": ["recol", "rec", "doe"]
            }
            with open(fichier, 'w', encoding='utf-8') as f:
                json.dump(contenu, f, indent=2, ensure_ascii=False)
        
        elif fichier == "config/correspondances.json":
            contenu = {
                "1631": "ALVEOLE AHA1631",
                "1632": "ALVEOLE AHA1632", 
                "GCS": "GALERIE GCS",
                "GHA": "GALERIE GHA",
                "GAN": "GALERIE GAN"
            }
            with open(fichier, 'w', encoding='utf-8') as f:
                json.dump(contenu, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ {fichier} créé")

def test_imports():
    """Test des imports critiques"""
    print(f"\n🧪 TEST DES IMPORTS")
    print("="*30)
    
    imports_test = [
        ("os", "Module système"),
        ("json", "Gestion JSON"),
        ("shutil", "Opérations fichiers"),
        ("datetime", "Gestion dates")
    ]
    
    for module, desc in imports_test:
        try:
            __import__(module)
            print(f"✅ {module} - {desc}")
        except ImportError:
            print(f"❌ {module} - {desc} - ERREUR IMPORT")

def test_programme_minimal():
    """Test minimal du programme principal"""
    print(f"\n🚀 TEST PROGRAMME MINIMAL")
    print("="*40)
    
    try:
        print("📝 Test chargement configuration...")
        if os.path.exists("config/config.json"):
            with open("config/config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ Configuration chargée")
        else:
            print("❌ Pas de configuration")
            return False
        
        print("📝 Test des chemins...")
        for nom, chemin in config['chemins'].items():
            exists = os.path.exists(chemin) if os.path.isabs(chemin) else "N/A"
            print(f"   {nom}: {chemin} {'✅' if exists is True else '❌' if exists is False else '⚠️'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def guide_demarrage_simple():
    """Guide de démarrage simplifié"""
    print(f"\n🎯 GUIDE DE DÉMARRAGE SIMPLE")
    print("="*40)
    
    print("1️⃣ PREMIÈRE FOIS - Configuration:")
    print("   • Modifiez config/config.json avec VOS chemins")
    print("   • Vérifiez config/categories.json")
    print("   • Adaptez config/correspondances.json")
    
    print("\n2️⃣ LANCEMENT SIMPLE:")
    print("   python test_simple.py")
    
    print("\n3️⃣ LANCEMENT COMPLET:")
    print("   python src/main.py")
    
    print("\n4️⃣ EN CAS DE PROBLÈME:")
    print("   python diagnostic.py")

def creer_test_simple():
    """Crée un script de test ultra simple"""
    contenu_test = '''"""
Test ultra simple - Sans imports complexes
"""

import os
import json

def test_basique():
    print("🧪 TEST BASIQUE")
    print("="*20)
    
    # Test config
    if os.path.exists("config/config.json"):
        try:
            with open("config/config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ Configuration OK")
            
            # Afficher les chemins
            print("\\n📁 Chemins configurés:")
            for nom, chemin in config['chemins'].items():
                print(f"   {nom}: {chemin}")
                
        except Exception as e:
            print(f"❌ Erreur config: {e}")
    else:
        print("❌ Pas de configuration")
    
    print("\\n🎯 Pour continuer:")
    print("1. Vérifiez/modifiez les chemins dans config/config.json")
    print("2. Lancez: python src/main.py")

if __name__ == "__main__":
    test_basique()
'''
    
    with open("test_simple.py", 'w', encoding='utf-8') as f:
        f.write(contenu_test)
    
    print("📝 Script test_simple.py créé")

if __name__ == "__main__":
    # Diagnostic complet
    manquants = verifier_fichiers_essentiels()
    
    if manquants:
        creer_fichiers_manquants(manquants)
    
    test_imports()
    
    if test_programme_minimal():
        print("\\n🎉 DIAGNOSTIC: Système réparé!")
    else:
        print("\\n⚠️  DIAGNOSTIC: Problèmes détectés")
    
    guide_demarrage_simple()
    creer_test_simple()
    
    print("\\n💡 PROCHAINE ÉTAPE:")
    print("python test_simple.py")