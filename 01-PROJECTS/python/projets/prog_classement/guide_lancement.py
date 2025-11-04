"""
GUIDE PRATIQUE DE LANCEMENT
Guide complet pour démarrer et paramétrer le système de classement
"""

import os
import json

def guide_parametrage():
    """Guide étape par étape pour paramétrer le système"""
    print("🚀 GUIDE DE LANCEMENT - SYSTÈME DE CLASSEMENT BURE")
    print("="*70)
    
    print("\n📋 ÉTAPES À SUIVRE:")
    print("="*30)
    
    etapes = [
        ("1️⃣", "VÉRIFIER LA CONFIGURATION", "Adapter les chemins à votre environnement"),
        ("2️⃣", "TESTER L'INSTALLATION", "S'assurer que tout fonctionne"),
        ("3️⃣", "LANCER LE PROGRAMME", "Utiliser l'interface principal"),
        ("4️⃣", "PREMIER USAGE", "Workflow recommandé pour débuter")
    ]
    
    for numero, titre, description in etapes:
        print(f"{numero} {titre}")
        print(f"   {description}")
    
    return True

def etape1_configuration():
    """Guide de configuration détaillé"""
    print(f"\n" + "="*70)
    print("1️⃣ CONFIGURATION - QUE FAUT-IL PARAMÉTRER ?")
    print("="*70)
    
    print("\n📁 FICHIER PRINCIPAL À MODIFIER:")
    print("   📄 config/config.json")
    print("")
    
    # Lecture de la config actuelle
    try:
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("🔧 PARAMÈTRES À ADAPTER À VOTRE ENVIRONNEMENT:")
        print("-"*50)
        
        parametres_importants = [
            ("source_base", "Dossier de vos activités chronologiques", config['chemins']['source_base']),
            ("destination_temp", "Dossier temporaire de validation", config['chemins']['destination_temp']),
            ("destination_finale", "Dossier final (galeries)", config['chemins']['destination_finale']),
            ("backup_dir", "Dossier de sauvegarde", config['chemins']['backup_dir']),
        ]
        
        for param, description, valeur_actuelle in parametres_importants:
            print(f"\n📌 {param}:")
            print(f"   Description: {description}")
            print(f"   Valeur actuelle: {valeur_actuelle}")
            
            # Vérification de l'existence
            if os.path.exists(valeur_actuelle):
                print(f"   État: ✅ Dossier existe")
            else:
                print(f"   État: ❌ Dossier n'existe pas")
                print(f"   Action: 🔧 À créer ou modifier le chemin")
        
        print(f"\n🎯 EXEMPLE DE CONFIGURATION TYPIQUE:")
        exemple_config = {
            "source_base": "C:\\MesDonnees\\Activités\\Chronologique",
            "destination_temp": "C:\\Temp\\classement-validation", 
            "destination_finale": "C:\\MesDonnees\\Galeries",
            "backup_dir": "C:\\Backup\\classement"
        }
        
        for param, exemple in exemple_config.items():
            print(f"   {param}: \"{exemple}\"")
            
    except Exception as e:
        print(f"❌ Erreur lecture config: {e}")

def etape2_verification_correspondances():
    """Vérification des fichiers de correspondance"""
    print(f"\n" + "="*70)
    print("📋 VÉRIFICATION DES CORRESPONDANCES")
    print("="*70)
    
    print("\n🏢 FICHIER: config/correspondances.json")
    print("   → Mapping entre codes et noms de galeries")
    
    try:
        with open("config/correspondances.json", 'r', encoding='utf-8') as f:
            correspondances = json.load(f)
        
        print(f"\n📊 CORRESPONDANCES ACTUELLES ({len(correspondances)} entrées):")
        print("-"*40)
        
        # Affichage des 5 premiers
        for i, (code, galerie) in enumerate(list(correspondances.items())[:5]):
            print(f"   {code} → {galerie}")
        
        if len(correspondances) > 5:
            print(f"   ... et {len(correspondances) - 5} autres")
        
        print(f"\n🔧 COMMENT MODIFIER:")
        print(f"   1. Ouvrir config/correspondances.json")
        print(f"   2. Ajouter vos codes: \"1234\": \"GALERIE MA_GALERIE\"")
        print(f"   3. Sauvegarder le fichier")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n🎯 FICHIER: config/categories.json")
    print("   → Mots-clés pour détecter les types d'activités")
    
    try:
        with open("config/categories.json", 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        print(f"\n📊 CATÉGORIES ACTUELLES ({len(categories)} types):")
        print("-"*40)
        
        for categorie, mots_cles in list(categories.items())[:3]:
            print(f"   {categorie}: {', '.join(mots_cles[:3])}...")
        
        print(f"\n🔧 COMMENT MODIFIER:")
        print(f"   1. Ouvrir config/categories.json")
        print(f"   2. Ajouter/modifier les mots-clés selon vos usages")
        print(f"   3. Exemple: \"TOPOGRAPHIE\": [\"topo\", \"levé\", \"scanner\"]")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def etape3_test_installation():
    """Test de l'installation"""
    print(f"\n" + "="*70)
    print("2️⃣ TEST DE L'INSTALLATION")
    print("="*70)
    
    print("\n🧪 COMMANDE DE TEST:")
    print("   python demo.py")
    print("")
    print("✅ QUE VÉRIFIER:")
    print("   • Configuration se charge sans erreur")
    print("   • Logging fonctionne")
    print("   • Détection de catégories marche")
    print("   • Backup manager s'initialise")
    print("")
    print("❌ EN CAS D'ERREUR:")
    print("   • Vérifier les chemins dans config.json")
    print("   • S'assurer que les dossiers existent")
    print("   • Vérifier la syntaxe JSON des fichiers config")

def etape4_lancement():
    """Guide de lancement du programme principal"""
    print(f"\n" + "="*70)
    print("3️⃣ LANCEMENT DU PROGRAMME PRINCIPAL")
    print("="*70)
    
    print("\n🚀 COMMANDE PRINCIPALE:")
    print("   python src/main.py")
    print("")
    
    print("📋 MENU QUI APPARAÎT:")
    menu_options = [
        ("[1]", "Collecter les données", "Import depuis activités chronologiques"),
        ("[2]", "Valider les classifications", "Vérification interactive"),
        ("[3]", "Appliquer le classement", "Copie finale vers galeries"),
        ("[4]", "Processus complet", "Automatique 1→2→3"),
        ("[5]", "Gestion des backups", "Sauvegardes et restauration"),
        ("[6]", "Statistiques", "Métriques de session"),
        ("[7]", "Configuration", "Paramètres système"),
        ("[8]", "Nettoyage", "Suppression temporaires")
    ]
    
    for option, titre, description in menu_options:
        print(f"   {option} {titre:<25} → {description}")

def etape5_premier_usage():
    """Workflow pour le premier usage"""
    print(f"\n" + "="*70)
    print("4️⃣ WORKFLOW PREMIER USAGE (RECOMMANDÉ)")
    print("="*70)
    
    workflow = [
        ("🔧", "PRÉPARATION", [
            "Modifier config.json avec VOS chemins",
            "Vérifier que les dossiers sources existent",
            "Tester avec python demo.py"
        ]),
        ("🧪", "TEST EN MODE SÉCURISÉ", [
            "Lancer python src/main.py",
            "Choisir [4] Processus complet",
            "Laisser en mode temporaire (ne pas appliquer)"
        ]),
        ("🔍", "VALIDATION", [
            "Vérifier les résultats dans dossier temporaire", 
            "Corriger config si classifications incorrectes",
            "Relancer jusqu'à satisfaction"
        ]),
        ("✅", "APPLICATION FINALE", [
            "Une fois satisfait des résultats temporaires",
            "Menu [3] Appliquer le classement",
            "Confirmer pour copie vers galeries finales"
        ])
    ]
    
    for emoji, phase, actions in workflow:
        print(f"\n{emoji} {phase}:")
        for action in actions:
            print(f"   • {action}")

def checklist_avant_lancement():
    """Checklist de vérification avant lancement"""
    print(f"\n" + "="*70)
    print("✅ CHECKLIST AVANT LANCEMENT")
    print("="*70)
    
    checks = [
        ("📁 config.json modifié avec MES chemins", "Adapter à votre environnement"),
        ("🏢 correspondances.json vérifié", "Codes galeries corrects"),
        ("🎯 categories.json adapté", "Mots-clés de VOS activités"),
        ("🧪 python demo.py exécuté avec succès", "Test fonctionnel"),
        ("💾 Backup de mes données existantes", "Sécurité avant premier usage"),
        ("📂 Dossiers sources accessibles", "Permissions et existence"),
        ("🕐 Temps disponible pour test complet", "Au moins 30 minutes")
    ]
    
    print("À VÉRIFIER AVANT DE COMMENCER:")
    for i, (check, description) in enumerate(checks, 1):
        print(f"{i:2d}. {check}")
        print(f"    → {description}")

def exemple_concret():
    """Exemple concret avec chemins réels"""
    print(f"\n" + "="*70)
    print("💡 EXEMPLE CONCRET")
    print("="*70)
    
    print("🎯 SITUATION TYPE:")
    print("   Vos activités sont dans: C:\\Projets\\BURE\\Activités\\2024\\10\\29\\")
    print("   Vous voulez classer dans: C:\\Projets\\BURE\\Galeries\\")
    print("")
    
    print("🔧 CONFIGURATION À FAIRE:")
    exemple_config = {
        "source_base": "C:\\Projets\\BURE\\Activités",
        "destination_temp": "C:\\Temp\\classement-test", 
        "destination_finale": "C:\\Projets\\BURE\\Galeries",
        "backup_dir": "C:\\Backup\\classement"
    }
    
    print("   Dans config/config.json, modifier:")
    for param, valeur in exemple_config.items():
        print(f"   \"{param}\": \"{valeur}\"")
    
    print(f"\n🚀 COMMANDES À EXÉCUTER:")
    commandes = [
        "cd C:\\chemin\\vers\\prog_classement",
        "python demo.py",
        "python src/main.py",
        "# Choisir [4] puis suivre les instructions"
    ]
    
    for cmd in commandes:
        print(f"   {cmd}")

if __name__ == "__main__":
    guide_parametrage()
    etape1_configuration()
    etape2_verification_correspondances()
    etape3_test_installation()
    etape4_lancement()
    etape5_premier_usage()
    checklist_avant_lancement()
    exemple_concret()
    
    print(f"\n🎉 VOUS ÊTES PRÊT !")
    print("="*30)
    print("1️⃣ Modifiez config/config.json")
    print("2️⃣ Testez avec: python demo.py") 
    print("3️⃣ Lancez avec: python src/main.py")
    print("4️⃣ Choisissez [4] Processus complet")