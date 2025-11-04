"""
ASSISTANT DE CONFIGURATION
Vérifie votre configuration actuelle et vous guide pour les modifications
"""

import os
import json
from datetime import datetime

def verifier_configuration():
    """Vérifie la configuration actuelle et propose des corrections"""
    print("🔧 VÉRIFICATION DE VOTRE CONFIGURATION ACTUELLE")
    print("="*60)
    
    try:
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Fichier config.json lu avec succès")
        
        # Vérification des chemins
        chemins_status = []
        
        for nom, chemin in config['chemins'].items():
            existe = os.path.exists(chemin)
            accessible = True
            
            if existe:
                try:
                    # Test d'accès en écriture
                    test_file = os.path.join(chemin, f"test_access_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tmp")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                except:
                    accessible = False
            
            chemins_status.append({
                'nom': nom,
                'chemin': chemin,
                'existe': existe,
                'accessible': accessible
            })
        
        # Affichage des résultats
        print(f"\n📂 ÉTAT DES CHEMINS:")
        print("-" * 50)
        
        problemes = []
        
        for status in chemins_status:
            nom = status['nom']
            chemin = status['chemin']
            
            if status['existe'] and status['accessible']:
                print(f"✅ {nom:<20} → {chemin}")
            elif status['existe'] and not status['accessible']:
                print(f"⚠️  {nom:<20} → {chemin} (pas d'accès écriture)")
                problemes.append(f"Problème d'accès: {chemin}")
            else:
                print(f"❌ {nom:<20} → {chemin} (n'existe pas)")
                problemes.append(f"Dossier manquant: {chemin}")
        
        return config, problemes
        
    except FileNotFoundError:
        print("❌ Fichier config/config.json introuvable!")
        return None, ["Fichier config.json manquant"]
    except json.JSONDecodeError as e:
        print(f"❌ Erreur dans config.json: {e}")
        return None, ["Erreur syntaxe JSON"]
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None, [f"Erreur: {e}"]

def proposer_corrections(problemes):
    """Propose des corrections pour les problèmes détectés"""
    if not problemes:
        print(f"\n🎉 AUCUN PROBLÈME DÉTECTÉ!")
        print("Votre configuration semble correcte.")
        return
    
    print(f"\n🔧 PROBLÈMES DÉTECTÉS ET SOLUTIONS:")
    print("="*50)
    
    for i, probleme in enumerate(problemes, 1):
        print(f"\n{i}. {probleme}")
        
        if "manquant" in probleme:
            chemin = probleme.split(": ")[1]
            print(f"   💡 SOLUTIONS:")
            print(f"   A) Créer le dossier: mkdir \"{chemin}\" -Force")
            print(f"   B) Modifier config.json avec un chemin existant")
        
        elif "accès" in probleme:
            chemin = probleme.split(": ")[1]
            print(f"   💡 SOLUTIONS:")
            print(f"   A) Vérifier les permissions du dossier")
            print(f"   B) Exécuter en tant qu'administrateur")
            print(f"   C) Changer vers un dossier accessible")

def assistant_modification_config():
    """Assistant pour modifier la configuration"""
    print(f"\n🛠️  ASSISTANT DE MODIFICATION")
    print("="*40)
    
    if input("Modifier la configuration maintenant? (o/N): ").lower() != 'o':
        return
    
    try:
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"\n📝 MODIFICATION DES CHEMINS:")
        print("(Appuyez sur Entrée pour garder la valeur actuelle)")
        
        nouveaux_chemins = {}
        
        for nom, chemin_actuel in config['chemins'].items():
            print(f"\n📁 {nom}:")
            print(f"   Actuel: {chemin_actuel}")
            nouveau = input(f"   Nouveau (ou Entrée): ").strip()
            
            if nouveau:
                nouveaux_chemins[nom] = nouveau
                # Tenter de créer le dossier
                try:
                    os.makedirs(nouveau, exist_ok=True)
                    print(f"   ✅ Dossier créé: {nouveau}")
                except Exception as e:
                    print(f"   ⚠️  Impossible de créer: {e}")
            else:
                nouveaux_chemins[nom] = chemin_actuel
        
        # Sauvegarde de la nouvelle configuration
        config['chemins'] = nouveaux_chemins
        
        # Backup de l'ancienne config
        backup_config = "config/config.json.backup." + datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open("config/config.json", 'r') as f_old, open(backup_config, 'w') as f_backup:
            f_backup.write(f_old.read())
        
        print(f"💾 Backup ancien config: {backup_config}")
        
        # Écriture nouvelle config
        with open("config/config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuration mise à jour!")
        
    except Exception as e:
        print(f"❌ Erreur modification: {e}")

def tester_apres_config():
    """Test rapide après configuration"""
    print(f"\n🧪 TEST RAPIDE DE LA CONFIGURATION")
    print("="*45)
    
    print("Lancement du test...")
    
    try:
        # Test import des modules
        import sys
        sys.path.insert(0, 'src')
        
        from logger import get_logger
        logger = get_logger()
        print("✅ Module logging: OK")
        
        from backup_manager import GestionnaireBackup
        backup_mgr = GestionnaireBackup()
        print("✅ Gestionnaire backup: OK")
        
        print("\n🎯 CONFIGURATION FONCTIONNELLE!")
        print("Vous pouvez maintenant lancer: python src/main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        print("Vérifiez votre configuration avant de continuer")
        return False

def guide_etapes_suivantes():
    """Guide pour les étapes suivantes"""
    print(f"\n🚀 ÉTAPES SUIVANTES RECOMMANDÉES")
    print("="*40)
    
    etapes = [
        ("1.", "Test complet", "python demo.py"),
        ("2.", "Lancement principal", "python src/main.py"),
        ("3.", "Premier test", "Menu [4] Processus complet"),
        ("4.", "Validation résultats", "Vérifier dossier temporaire"),
        ("5.", "Application finale", "Menu [3] si satisfait")
    ]
    
    for num, action, commande in etapes:
        print(f"{num} {action:<20} → {commande}")

def main():
    """Fonction principale de l'assistant"""
    config, problemes = verifier_configuration()
    
    if config:
        proposer_corrections(problemes)
        
        if problemes:
            assistant_modification_config()
            # Re-vérification après modification
            config, nouveaux_problemes = verifier_configuration()
            if not nouveaux_problemes:
                if tester_apres_config():
                    guide_etapes_suivantes()
        else:
            if tester_apres_config():
                guide_etapes_suivantes()
    
    print(f"\n💡 AIDE SUPPLÉMENTAIRE:")
    print("   📖 Guide complet: python guide_lancement.py")
    print("   🧪 Test installation: python demo.py") 
    print("   🚀 Programme principal: python src/main.py")

if __name__ == "__main__":
    main()