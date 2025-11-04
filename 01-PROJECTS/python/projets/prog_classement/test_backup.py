"""
TEST PRATIQUE du système de backup
Crée des exemples concrets pour montrer le fonctionnement
"""

import sys
import os
sys.path.insert(0, 'src')

from backup_manager import GestionnaireBackup
import tempfile
import shutil

def demo_backup_pratique():
    """Démonstration pratique du système de backup"""
    print("🧪 TEST PRATIQUE DU SYSTÈME DE BACKUP")
    print("="*50)
    
    try:
        # Initialisation du gestionnaire
        gestionnaire = GestionnaireBackup()
        
        # Création d'un dossier d'exemple à sauvegarder
        temp_source = tempfile.mkdtemp(prefix="exemple_a_sauvegarder_")
        
        # Contenu d'exemple
        with open(os.path.join(temp_source, "rapport_important.pdf"), 'w') as f:
            f.write("Contenu d'un rapport important")
        
        with open(os.path.join(temp_source, "plan_technique.dwg"), 'w') as f:
            f.write("Données CAO importantes")
        
        sous_dossier = os.path.join(temp_source, "photos")
        os.makedirs(sous_dossier, exist_ok=True)
        
        with open(os.path.join(sous_dossier, "photo1.jpg"), 'w') as f:
            f.write("Image importante")
        
        print(f"📁 Dossier d'exemple créé: {temp_source}")
        print(f"📄 Contenu:")
        print(f"   • rapport_important.pdf")
        print(f"   • plan_technique.dwg") 
        print(f"   • photos/photo1.jpg")
        
        # Test du backup
        print(f"\n💾 CRÉATION DU BACKUP...")
        backup_info = gestionnaire.creer_backup_complet(temp_source, "demo_test")
        
        if backup_info:
            print(f"✅ Backup créé avec succès!")
            print(f"   📂 Type: {backup_info['type']}")
            print(f"   📁 Chemin: {backup_info['chemin']}")
            print(f"   📊 Taille: {backup_info['taille']} bytes")
            print(f"   🕐 Date: {backup_info['date']}")
            
            # Vérification que le backup existe
            if os.path.exists(backup_info['chemin']):
                print(f"   ✅ Fichier backup confirmé sur disque")
            else:
                print(f"   ❌ Erreur: backup non trouvé sur disque")
        else:
            print(f"❌ Erreur lors de la création du backup")
        
        # Test de listage
        print(f"\n📋 LISTE DES BACKUPS:")
        backups = gestionnaire.lister_backups()
        for backup in backups:
            print(f"   📦 {backup['nom']} - {backup['date'][:16]} - {backup['type']}")
        
        # Affichage des statistiques
        print(f"\n📊 STATISTIQUES:")
        gestionnaire.afficher_statistiques()
        
        # Nettoyage du dossier temporaire
        shutil.rmtree(temp_source)
        print(f"\n🧹 Dossier temporaire nettoyé")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

def afficher_localisation_reelle():
    """Affiche la localisation réelle des backups sur ce système"""
    print(f"\n📍 LOCALISATION RÉELLE SUR VOTRE SYSTÈME")
    print("="*50)
    
    try:
        gestionnaire = GestionnaireBackup()
        backup_dir = gestionnaire.backup_dir
        
        print(f"📁 Dossier de backup: {backup_dir}")
        
        if os.path.exists(backup_dir):
            print(f"✅ Dossier existe")
            
            # Lister le contenu
            contenu = os.listdir(backup_dir)
            if contenu:
                print(f"📂 Contenu actuel:")
                for item in contenu:
                    item_path = os.path.join(backup_dir, item)
                    if os.path.isfile(item_path):
                        taille = os.path.getsize(item_path)
                        print(f"   📄 {item} ({taille} bytes)")
                    else:
                        print(f"   📁 {item}/")
            else:
                print(f"📂 Dossier vide (normal pour premier usage)")
        else:
            print(f"❌ Dossier n'existe pas encore")
            print(f"🔧 Sera créé automatiquement au premier backup")
        
        # Commandes pour explorer
        print(f"\n💻 COMMANDES POUR EXPLORER:")
        print(f"📁 explorer \"{backup_dir}\"")
        print(f"📊 Get-ChildItem \"{backup_dir}\"")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    afficher_localisation_reelle()
    
    if input("\nTester la création d'un backup? (o/N): ").lower() == 'o':
        demo_backup_pratique()
    
    print(f"\n🎯 COMMENT ACCÉDER AUX BACKUPS:")
    print(f"1. Ouvrir l'explorateur Windows")
    print(f"2. Aller à: C:\\Backup\\classement")
    print(f"3. Ou utiliser le menu [5] dans le programme principal")