"""
CONFIGURATEUR INTERACTIF
Configure automatiquement le système selon vos chemins spécifiques
"""

import os
import json
from pathlib import Path

def afficher_intro():
    """Introduction du configurateur"""
    print("⚙️  CONFIGURATEUR INTERACTIF - SYSTÈME DE CLASSEMENT BURE")
    print("="*65)
    print("Je vais vous aider à configurer le système selon vos chemins.")
    print("Nous allons paramétrer :")
    print("• 📁 Dossier de vos activités chronologiques (source)")
    print("• 📁 Dossier temporaire de travail")
    print("• 📁 Dossier final des galeries (destination)")
    print("• 📁 Dossier des sauvegardes")
    print("• ⚙️  Options de sécurité")
    print("")

def detecter_chemins_actuels():
    """Détecte les chemins actuels dans la configuration"""
    try:
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config_actuelle = json.load(f)
        return config_actuelle
    except:
        return None

def verifier_chemin(chemin, description):
    """Vérifie si un chemin existe et affiche des infos"""
    if os.path.exists(chemin):
        if os.path.isdir(chemin):
            try:
                nb_elements = len(os.listdir(chemin))
                print(f"   ✅ Existe ({nb_elements} éléments)")
                return True
            except:
                print(f"   ⚠️  Existe mais accès limité")
                return True
        else:
            print(f"   ❌ Existe mais c'est un fichier")
            return False
    else:
        print(f"   ❌ N'existe pas")
        return False

def proposer_chemins_intelligents():
    """Propose des chemins intelligents basés sur l'environnement"""
    suggestions = {}
    
    # Base sur le lecteur C: par défaut
    base_c = "C:\\"
    
    # Suggestions pour activités
    suggestions['activites'] = [
        "C:\\data\\11-CHANTIERS\\BURE\\10-ACTIVITES",  # Config actuelle
        "C:\\BURE\\ACTIVITES",
        "C:\\Documents\\BURE\\Activités",
        "C:\\Travail\\BURE\\Activités",
        f"{Path.home()}\\Documents\\BURE\\Activités"
    ]
    
    # Suggestions pour galeries
    suggestions['galeries'] = [
        "C:\\data\\11-CHANTIERS\\BURE\\11-GALERIES",   # Config actuelle
        "C:\\BURE\\GALERIES", 
        "C:\\Documents\\BURE\\Galeries",
        "C:\\Travail\\BURE\\Galeries",
        f"{Path.home()}\\Documents\\BURE\\Galeries"
    ]
    
    # Suggestions pour temporaire
    suggestions['temp'] = [
        "C:\\Temp\\activites-par-galerie",
        "C:\\Temp\\BURE-classement",
        f"{Path.home()}\\AppData\\Local\\Temp\\BURE-classement"
    ]
    
    # Suggestions pour backup
    suggestions['backup'] = [
        "C:\\Backup\\classement",
        "C:\\BURE\\Backups",
        f"{Path.home()}\\Documents\\Backups\\BURE"
    ]
    
    return suggestions

def demander_chemin(type_chemin, description, suggestions, actuel=None):
    """Demande interactivement un chemin"""
    print(f"\n📁 {description.upper()}")
    print("-" * 50)
    
    if actuel:
        print(f"📍 Chemin actuel: {actuel}")
        verifier_chemin(actuel, "actuel")
        print("")
    
    print("💡 Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   [{i}] {suggestion}")
        verifier_chemin(suggestion, f"suggestion {i}")
    
    print(f"   [C] Chemin personnalisé")
    if actuel:
        print(f"   [K] Garder l'actuel ({actuel})")
    
    while True:
        choix = input(f"\n➤ Votre choix pour {description}: ").strip()
        
        if choix.upper() == 'K' and actuel:
            return actuel
        elif choix.upper() == 'C':
            chemin_perso = input("   Saisissez le chemin complet: ").strip()
            if chemin_perso:
                return chemin_perso.replace('/', '\\')  # Normalisation Windows
        elif choix.isdigit():
            idx = int(choix) - 1
            if 0 <= idx < len(suggestions):
                return suggestions[idx]
        
        print("   ❌ Choix invalide, recommencez")

def configurer_options():
    """Configure les options de sécurité"""
    print(f"\n⚙️  OPTIONS DE SÉCURITÉ")
    print("-" * 30)
    
    options = {}
    
    # Mode sécurisé
    print("\n🛡️  Mode sécurisé (confirmations avant actions critiques)")
    choix = input("   Activer? [O/n]: ").strip().lower()
    options['mode_securise'] = choix != 'n'
    
    # Backup automatique
    print("\n💾 Backup automatique (sauvegarde avant modifications)")
    choix = input("   Activer? [O/n]: ").strip().lower()
    options['backup_automatique'] = choix != 'n'
    
    # Validation interactive
    print("\n🔍 Validation interactive (vérifier les classifications)")
    choix = input("   Activer? [O/n]: ").strip().lower()
    options['validation_interactive'] = choix != 'n'
    
    # Niveau de log
    print("\n📝 Niveau de détail des logs")
    print("   [1] INFO (normal)")
    print("   [2] DEBUG (détaillé)")
    print("   [3] WARNING (erreurs seulement)")
    
    while True:
        choix = input("   Choix [1]: ").strip() or "1"
        if choix == "1":
            options['niveau_log'] = "INFO"
            break
        elif choix == "2":
            options['niveau_log'] = "DEBUG"
            break
        elif choix == "3":
            options['niveau_log'] = "WARNING"
            break
        print("   ❌ Choix invalide")
    
    # Nombre max de backups
    print("\n🗃️  Nombre maximum de backups à conserver")
    while True:
        choix = input("   Nombre [10]: ").strip() or "10"
        try:
            options['max_backups'] = int(choix)
            if options['max_backups'] > 0:
                break
            else:
                print("   ❌ Doit être supérieur à 0")
        except ValueError:
            print("   ❌ Doit être un nombre")
    
    return options

def creer_dossiers_necessaires(chemins):
    """Crée les dossiers qui n'existent pas"""
    print(f"\n🔧 CRÉATION DES DOSSIERS MANQUANTS")
    print("-" * 40)
    
    dossiers_a_creer = []
    
    for nom, chemin in chemins.items():
        if not os.path.exists(chemin):
            dossiers_a_creer.append((nom, chemin))
    
    if not dossiers_a_creer:
        print("✅ Tous les dossiers existent déjà")
        return True
    
    print("📁 Dossiers à créer:")
    for nom, chemin in dossiers_a_creer:
        print(f"   • {nom}: {chemin}")
    
    if input("\nCréer ces dossiers? [O/n]: ").strip().lower() == 'n':
        print("⚠️  Dossiers non créés - vous devrez les créer manuellement")
        return False
    
    for nom, chemin in dossiers_a_creer:
        try:
            os.makedirs(chemin, exist_ok=True)
            print(f"   ✅ {nom}: {chemin}")
        except Exception as e:
            print(f"   ❌ {nom}: Erreur - {e}")
            return False
    
    return True

def sauvegarder_configuration(nouvelle_config):
    """Sauvegarde la nouvelle configuration"""
    print(f"\n💾 SAUVEGARDE DE LA CONFIGURATION")
    print("-" * 35)
    
    # Backup de l'ancienne config
    if os.path.exists("config/config.json"):
        backup_nom = f"config/config_backup_{int(__import__('time').time())}.json"
        try:
            import shutil
            shutil.copy2("config/config.json", backup_nom)
            print(f"📄 Ancienne config sauvée: {backup_nom}")
        except:
            print("⚠️  Impossible de sauvegarder l'ancienne config")
    
    # Sauvegarde nouvelle config
    try:
        with open("config/config.json", 'w', encoding='utf-8') as f:
            json.dump(nouvelle_config, f, indent=2, ensure_ascii=False)
        print("✅ Nouvelle configuration sauvegardée")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False

def afficher_resume(config):
    """Affiche un résumé de la configuration"""
    print(f"\n📋 RÉSUMÉ DE LA CONFIGURATION")
    print("=" * 50)
    
    print(f"\n📁 CHEMINS:")
    for nom, chemin in config['chemins'].items():
        nom_affiche = nom.replace('_', ' ').title()
        print(f"   • {nom_affiche:<15}: {chemin}")
    
    print(f"\n⚙️  OPTIONS:")
    for nom, valeur in config['options'].items():
        nom_affiche = nom.replace('_', ' ').title()
        print(f"   • {nom_affiche:<15}: {valeur}")
    
    print(f"\n🚀 PROCHAINES ÉTAPES:")
    print("   1. Tester: py demo.py")
    print("   2. Lancer: py src/main.py") 
    print("   3. Utiliser option [4] Processus complet")

def main():
    """Fonction principale du configurateur"""
    afficher_intro()
    
    # Détection config actuelle
    config_actuelle = detecter_chemins_actuels()
    if config_actuelle:
        print("✅ Configuration actuelle détectée")
    else:
        print("⚠️  Aucune configuration trouvée, création d'une nouvelle")
        config_actuelle = {"chemins": {}, "options": {}}
    
    # Suggestions intelligentes
    suggestions = proposer_chemins_intelligents()
    
    # Configuration des chemins
    nouveaux_chemins = {}
    
    # 1. Source (activités chronologiques)
    nouveaux_chemins['source_base'] = demander_chemin(
        'source',
        'dossier des activités chronologiques (année/mois/jour)',
        suggestions['activites'],
        config_actuelle.get('chemins', {}).get('source_base')
    )
    
    # 2. Destination temporaire
    nouveaux_chemins['destination_temp'] = demander_chemin(
        'temp',
        'dossier temporaire de travail',
        suggestions['temp'],
        config_actuelle.get('chemins', {}).get('destination_temp')
    )
    
    # 3. Destination finale (galeries)
    nouveaux_chemins['destination_finale'] = demander_chemin(
        'finale',
        'dossier final des galeries',
        suggestions['galeries'],
        config_actuelle.get('chemins', {}).get('destination_finale')
    )
    
    # 4. Backup
    nouveaux_chemins['backup_dir'] = demander_chemin(
        'backup',
        'dossier des sauvegardes',
        suggestions['backup'],
        config_actuelle.get('chemins', {}).get('backup_dir')
    )
    
    # 5. Logs (automatique)
    nouveaux_chemins['logs_dir'] = "C:\\Temp\\logs\\classement"
    
    # Configuration des options
    nouvelles_options = configurer_options()
    
    # Ajout des dossiers par défaut
    dossiers_defaut = {
        "a_classer": "_a_classer",
        "classe": "_classé", 
        "divers": "DIVERS",
        "non_reconnus": "__NON_RECONNUS"
    }
    
    # Assemblage configuration finale
    nouvelle_config = {
        "chemins": nouveaux_chemins,
        "dossiers": dossiers_defaut,
        "options": nouvelles_options,
        "extensions_autorisees": [".pdf", ".docx", ".xlsx", ".dwg", ".jpg", ".png", ".zip", ".7z"],
        "exclusions": ["Thumbs.db", ".DS_Store", "desktop.ini"]
    }
    
    # Affichage résumé
    afficher_resume(nouvelle_config)
    
    # Confirmation finale
    if input(f"\n✅ Sauvegarder cette configuration? [O/n]: ").strip().lower() != 'n':
        if sauvegarder_configuration(nouvelle_config):
            # Création des dossiers
            creer_dossiers_necessaires(nouveaux_chemins)
            
            print(f"\n🎉 CONFIGURATION TERMINÉE!")
            print("🚀 Vous pouvez maintenant lancer: py src/main.py")
        else:
            print(f"\n❌ Erreur lors de la sauvegarde")
    else:
        print(f"\n❌ Configuration annulée")

if __name__ == "__main__":
    main()