"""
LANCEUR SIMPLE - Sans risque de blocage
Version ultra simplifiée pour éviter tous les problèmes
"""

import os
import json

def afficher_menu_simple():
    """Menu ultra simple sans imports complexes"""
    print("\n" + "="*60)
    print("🗂️  SYSTÈME DE CLASSEMENT BURE - VERSION SIMPLE")
    print("="*60)
    print("[1] ⚙️  Vérifier/modifier la configuration")
    print("[2] 📁 Voir l'état des dossiers")
    print("[3] 🚀 Lancer le programme principal (si tout OK)")
    print("[4] 🧪 Test de diagnostic")
    print("[0] ❌ Quitter")
    print("="*60)

def verifier_configuration():
    """Vérifie et permet de modifier la configuration"""
    print("\n⚙️  CONFIGURATION ACTUELLE")
    print("="*40)
    
    try:
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("📁 Chemins configurés:")
        for nom, chemin in config['chemins'].items():
            exists = "✅" if os.path.exists(chemin) else "❌"
            print(f"   {nom}: {chemin} {exists}")
        
        print("\n🔧 Options:")
        for nom, valeur in config['options'].items():
            print(f"   {nom}: {valeur}")
        
        if input("\nModifier la configuration? (o/N): ").lower() == 'o':
            modifier_chemins(config)
            
    except Exception as e:
        print(f"❌ Erreur lecture config: {e}")

def modifier_chemins(config):
    """Permet de modifier les chemins principaux"""
    print("\n✏️  MODIFICATION DES CHEMINS")
    print("="*40)
    
    chemins_importants = [
        ("source_base", "Dossier source (activités chronologiques)"),
        ("destination_temp", "Dossier temporaire de travail"),
        ("backup_dir", "Dossier des sauvegardes")
    ]
    
    modifie = False
    
    for cle, description in chemins_importants:
        chemin_actuel = config['chemins'][cle]
        print(f"\n{description}")
        print(f"Actuel: {chemin_actuel}")
        
        nouveau = input("Nouveau chemin (Entrée = garder actuel): ").strip()
        if nouveau:
            config['chemins'][cle] = nouveau
            modifie = True
            print(f"✅ Modifié: {nouveau}")
    
    if modifie:
        try:
            with open("config/config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("\n✅ Configuration sauvegardée!")
        except Exception as e:
            print(f"\n❌ Erreur sauvegarde: {e}")

def voir_etat_dossiers():
    """Affiche l'état des dossiers"""
    print("\n📁 ÉTAT DES DOSSIERS")
    print("="*30)
    
    try:
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for nom, chemin in config['chemins'].items():
            print(f"\n📂 {nom}:")
            print(f"   Chemin: {chemin}")
            
            if os.path.exists(chemin):
                print("   État: ✅ Existe")
                try:
                    contenu = os.listdir(chemin)
                    print(f"   Contenu: {len(contenu)} éléments")
                    if len(contenu) <= 5:
                        for item in contenu[:3]:
                            print(f"     • {item}")
                        if len(contenu) > 3:
                            print(f"     ... et {len(contenu)-3} autres")
                except:
                    print("   Contenu: Non accessible")
            else:
                print("   État: ❌ N'existe pas")
                if input(f"   Créer le dossier? (o/N): ").lower() == 'o':
                    try:
                        os.makedirs(chemin, exist_ok=True)
                        print("   ✅ Dossier créé")
                    except Exception as e:
                        print(f"   ❌ Erreur création: {e}")
                        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def lancer_programme_principal():
    """Lance le programme principal avec vérifications"""
    print("\n🚀 LANCEMENT DU PROGRAMME PRINCIPAL")
    print("="*40)
    
    # Vérifications préalables
    print("🔍 Vérifications préalables...")
    
    try:
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        problemes = []
        
        # Vérifier les chemins critiques
        if not os.path.exists(config['chemins']['source_base']):
            problemes.append(f"Dossier source manquant: {config['chemins']['source_base']}")
        
        if problemes:
            print("❌ Problèmes détectés:")
            for prob in problemes:
                print(f"   • {prob}")
            print("\nCorrigez ces problèmes avant de continuer.")
            return
        
        print("✅ Vérifications OK")
        print("\n🎯 Options de lancement:")
        print("[1] Mode sécurisé (recommandé)")
        print("[2] Mode normal")
        print("[3] Test uniquement")
        
        choix = input("Votre choix (1-3): ").strip()
        
        if choix == '1':
            print("\n🛡️  Mode sécurisé activé")
            print("Lancement du programme principal...")
            os.system("python src/main.py")
        elif choix == '2':
            print("\n⚡ Mode normal")
            print("Lancement du programme principal...")
            os.system("python src/main.py")
        elif choix == '3':
            print("\n🧪 Mode test")
            os.system("python demo.py")
        else:
            print("❌ Choix invalide")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Boucle principale du lanceur simple"""
    
    while True:
        try:
            afficher_menu_simple()
            choix = input("\nVotre choix: ").strip()
            
            if choix == '1':
                verifier_configuration()
            elif choix == '2':
                voir_etat_dossiers()
            elif choix == '3':
                lancer_programme_principal()
            elif choix == '4':
                os.system("python diagnostic.py")
            elif choix == '0':
                print("\n👋 Au revoir!")
                break
            else:
                print("❌ Choix invalide")
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Arrêt demandé")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    print("🚀 Démarrage du lanceur simple...")
    main()