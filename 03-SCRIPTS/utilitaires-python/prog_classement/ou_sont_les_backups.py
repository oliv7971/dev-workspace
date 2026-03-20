"""
DÉMONSTRATION : Localisation et gestion des backups
Montre où sont stockés les backups et comment les utiliser
"""

import os
import json
from datetime import datetime

def afficher_localisation_backups():
    """Affiche la localisation exacte des backups"""
    print("📁 LOCALISATION DES BACKUPS")
    print("="*50)
    
    # Lecture de la configuration
    try:
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        backup_dir = config['chemins']['backup_dir']
        logs_dir = config['chemins']['logs_dir']
        
        print(f"🎯 DOSSIER PRINCIPAL:")
        print(f"   📂 {backup_dir}")
        print(f"")
        print(f"📊 LOGS ET TRACES:")
        print(f"   📂 {logs_dir}")
        
        return backup_dir, logs_dir
        
    except Exception as e:
        print(f"❌ Erreur lecture config: {e}")
        return None, None

def afficher_structure_backup(backup_dir):
    """Affiche la structure du dossier de backup"""
    print(f"\n📂 STRUCTURE DU DOSSIER BACKUP")
    print("="*50)
    
    structure = f"""
{backup_dir}/
├── index_backups.json              ← Index de tous les backups
├── auto_collecte_20241029_143015/   ← Backup avant collecte
├── auto_classement_20241029_143020/ ← Backup avant classement
├── manuel_test_20241029_143025.zip  ← Backup manuel (ZIP si >100MB)
└── auto_nettoyage_20241029_143030/  ← Backup avant nettoyage
    """
    
    print(structure)
    
    print("🏷️  NOMENCLATURE DES BACKUPS:")
    print("   • auto_[opération]_[timestamp]     → Backup automatique")
    print("   • manuel_[nom]_[timestamp]         → Backup manuel")
    print("   • [nom]_backup_[timestamp]         → Backup avant écrasement")

def afficher_types_backups():
    """Explique les différents types de backups"""
    print(f"\n🔧 TYPES DE BACKUPS")
    print("="*40)
    
    types = {
        "🤖 AUTOMATIQUES": [
            "• Avant chaque collecte de données",
            "• Avant chaque classement final", 
            "• Avant chaque résolution de conflit",
            "• Avant nettoyage des temporaires"
        ],
        "👤 MANUELS": [
            "• Via menu [5] Gestion des backups",
            "• Avant tests ou modifications importantes",
            "• Sauvegarde ponctuelle de sécurité"
        ],
        "⚡ AVANT ÉCRASEMENT": [
            "• Quand un fichier va être remplacé",
            "• Quand un dossier va être fusionné",
            "• Permet restauration immédiate"
        ]
    }
    
    for type_backup, descriptions in types.items():
        print(f"\n{type_backup}")
        for desc in descriptions:
            print(f"   {desc}")

def afficher_commandes_utiles(backup_dir, logs_dir):
    """Affiche les commandes utiles pour explorer les backups"""
    print(f"\n💻 COMMANDES UTILES")
    print("="*40)
    
    print(f"📁 EXPLORER LES BACKUPS:")
    print(f"   explorer \"{backup_dir}\"")
    print(f"")
    print(f"📄 VOIR LES LOGS:")
    print(f"   notepad \"{logs_dir}\\classement_{datetime.now().strftime('%Y%m')}.log\"")
    print(f"")
    print(f"📊 LISTER LES BACKUPS (PowerShell):")
    print(f"   Get-ChildItem \"{backup_dir}\" | Sort-Object LastWriteTime -Descending")
    print(f"")
    print(f"🔍 VOIR L'INDEX DES BACKUPS:")
    print(f"   Get-Content \"{backup_dir}\\index_backups.json\" | ConvertFrom-Json")

def tester_existence_dossiers(backup_dir, logs_dir):
    """Teste l'existence des dossiers et les crée si nécessaire"""
    print(f"\n🔧 VÉRIFICATION DES DOSSIERS")
    print("="*40)
    
    dossiers = [
        ("Backup", backup_dir),
        ("Logs", logs_dir)
    ]
    
    for nom, chemin in dossiers:
        if os.path.exists(chemin):
            print(f"✅ {nom}: {chemin}")
            # Compter les fichiers
            try:
                nb_fichiers = len(os.listdir(chemin))
                print(f"   📊 {nb_fichiers} éléments")
            except:
                print(f"   ⚠️  Accès limité")
        else:
            print(f"❌ {nom}: {chemin} (n'existe pas)")
            print(f"   🔧 Création automatique au premier backup")

def afficher_taille_backups(backup_dir):
    """Affiche la taille des backups si le dossier existe"""
    if not os.path.exists(backup_dir):
        return
    
    print(f"\n📊 TAILLE DES BACKUPS")
    print("="*30)
    
    try:
        total_size = 0
        backup_count = 0
        
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                total_size += size
                backup_count += 1
                print(f"📄 {item}: {format_size(size)}")
                
            elif os.path.isdir(item_path):
                size = get_directory_size(item_path)
                total_size += size
                backup_count += 1
                print(f"📁 {item}: {format_size(size)}")
        
        print(f"\n📈 TOTAL: {backup_count} backups, {format_size(total_size)}")
        
        # Avertissement si trop gros
        if total_size > 1024*1024*1024:  # Plus de 1GB
            print(f"⚠️  Backups volumineux - pensez au nettoyage via menu [5]")
            
    except Exception as e:
        print(f"❌ Erreur calcul taille: {e}")

def format_size(size_bytes):
    """Formate une taille en bytes"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_directory_size(directory):
    """Calcule la taille d'un dossier"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except:
        pass
    return total

def guide_restauration():
    """Guide pour restaurer depuis un backup"""
    print(f"\n🔄 GUIDE DE RESTAURATION")
    print("="*40)
    
    print(f"🎯 MÉTHODE 1 - Via le menu principal:")
    print(f"   1. python src/main.py")
    print(f"   2. Choisir [5] Gestion des backups")
    print(f"   3. Choisir [4] Restaurer backup")
    print(f"   4. Saisir le nom du backup")
    print(f"   5. Indiquer la destination")
    print(f"")
    print(f"🎯 MÉTHODE 2 - Manuellement:")
    print(f"   1. Aller dans le dossier backup")
    print(f"   2. Copier le dossier/fichier voulu")
    print(f"   3. Coller à l'emplacement souhaité")
    print(f"")
    print(f"⚠️  IMPORTANT:")
    print(f"   • Les backups ZIP doivent être extraits")
    print(f"   • Vérifier la date du backup")
    print(f"   • Faire un backup avant restauration !")

if __name__ == "__main__":
    backup_dir, logs_dir = afficher_localisation_backups()
    
    if backup_dir and logs_dir:
        afficher_structure_backup(backup_dir)
        afficher_types_backups()
        afficher_commandes_utiles(backup_dir, logs_dir)
        tester_existence_dossiers(backup_dir, logs_dir)
        afficher_taille_backups(backup_dir)
        guide_restauration()
        
        print(f"\n🎯 RÉSUMÉ")
        print("="*20)
        print(f"📁 Backups: {backup_dir}")
        print(f"📄 Logs: {logs_dir}")
        print(f"🔧 Gestion: Menu [5] dans le programme principal")
        print(f"📊 Max backups conservés: 10 (configurable)")
    else:
        print("❌ Impossible de lire la configuration")