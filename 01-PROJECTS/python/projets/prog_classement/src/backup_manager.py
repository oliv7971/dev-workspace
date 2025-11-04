"""
Module de gestion des backups automatiques
Gère les sauvegardes avant modifications importantes
"""

import os
import shutil
import json
import zipfile
from datetime import datetime, timedelta
from logger import get_logger


class GestionnaireBackup:
    def __init__(self, config_path="config/config.json"):
        """Initialise le gestionnaire de backup"""
        self.logger = get_logger()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.backup_dir = self.config['chemins']['backup_dir']
        self.max_backups = self.config['options']['max_backups']
        
        # Création du dossier de backup
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def creer_backup_complet(self, source_dir, nom_operation="backup"):
        """Crée un backup complet d'un dossier"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_backup = f"{nom_operation}_{timestamp}"
        
        # Choix du format selon la taille
        taille_source = self._calculer_taille_dossier(source_dir)
        
        if taille_source > 100 * 1024 * 1024:  # Plus de 100MB -> ZIP
            return self._creer_backup_zip(source_dir, nom_backup)
        else:  # Moins de 100MB -> Copie simple
            return self._creer_backup_copie(source_dir, nom_backup)
    
    def _creer_backup_zip(self, source_dir, nom_backup):
        """Crée un backup sous forme de fichier ZIP"""
        chemin_backup = os.path.join(self.backup_dir, f"{nom_backup}.zip")
        
        try:
            self.logger.info(f"Création backup ZIP: {nom_backup}")
            
            with zipfile.ZipFile(chemin_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            
            # Informations sur le backup
            info_backup = {
                'type': 'zip',
                'source': source_dir,
                'chemin': chemin_backup,
                'taille': os.path.getsize(chemin_backup),
                'date': datetime.now().isoformat(),
                'nom': nom_backup
            }
            
            self._sauvegarder_info_backup(info_backup)
            self.logger.info(f"Backup ZIP créé: {chemin_backup}")
            
            return info_backup
            
        except Exception as e:
            self.logger.error(f"Erreur création backup ZIP: {e}")
            if os.path.exists(chemin_backup):
                os.remove(chemin_backup)
            return None
    
    def _creer_backup_copie(self, source_dir, nom_backup):
        """Crée un backup par copie complète"""
        chemin_backup = os.path.join(self.backup_dir, nom_backup)
        
        try:
            self.logger.info(f"Création backup copie: {nom_backup}")
            
            shutil.copytree(source_dir, chemin_backup)
            
            # Informations sur le backup
            info_backup = {
                'type': 'copie',
                'source': source_dir,
                'chemin': chemin_backup,
                'taille': self._calculer_taille_dossier(chemin_backup),
                'date': datetime.now().isoformat(),
                'nom': nom_backup
            }
            
            self._sauvegarder_info_backup(info_backup)
            self.logger.info(f"Backup copie créé: {chemin_backup}")
            
            return info_backup
            
        except Exception as e:
            self.logger.error(f"Erreur création backup copie: {e}")
            if os.path.exists(chemin_backup):
                shutil.rmtree(chemin_backup)
            return None
    
    def _calculer_taille_dossier(self, dossier):
        """Calcule la taille totale d'un dossier"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(dossier):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total += os.path.getsize(filepath)
        except Exception as e:
            self.logger.warning(f"Erreur calcul taille {dossier}: {e}")
        return total
    
    def _sauvegarder_info_backup(self, info_backup):
        """Sauvegarde les informations d'un backup"""
        fichier_index = os.path.join(self.backup_dir, "index_backups.json")
        
        # Chargement de l'index existant
        if os.path.exists(fichier_index):
            with open(fichier_index, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {'backups': []}
        
        # Ajout du nouveau backup
        index['backups'].append(info_backup)
        
        # Sauvegarde de l'index
        with open(fichier_index, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def lister_backups(self, source_dir=None):
        """Liste les backups disponibles"""
        fichier_index = os.path.join(self.backup_dir, "index_backups.json")
        
        if not os.path.exists(fichier_index):
            return []
        
        with open(fichier_index, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        backups = index.get('backups', [])
        
        # Filtrage par source si spécifié
        if source_dir:
            backups = [b for b in backups if b['source'] == source_dir]
        
        # Tri par date (plus récent en premier)
        backups.sort(key=lambda x: x['date'], reverse=True)
        
        return backups
    
    def restaurer_backup(self, nom_backup, destination):
        """Restaure un backup vers une destination"""
        backups = self.lister_backups()
        backup = next((b for b in backups if b['nom'] == nom_backup), None)
        
        if not backup:
            self.logger.error(f"Backup introuvable: {nom_backup}")
            return False
        
        try:
            self.logger.info(f"Restauration backup: {nom_backup} -> {destination}")
            
            if backup['type'] == 'zip':
                return self._restaurer_backup_zip(backup, destination)
            else:
                return self._restaurer_backup_copie(backup, destination)
                
        except Exception as e:
            self.logger.error(f"Erreur restauration backup: {e}")
            return False
    
    def _restaurer_backup_zip(self, backup, destination):
        """Restaure un backup ZIP"""
        chemin_backup = backup['chemin']
        
        if not os.path.exists(chemin_backup):
            self.logger.error(f"Fichier backup introuvable: {chemin_backup}")
            return False
        
        # Création du dossier de destination
        os.makedirs(destination, exist_ok=True)
        
        # Extraction
        with zipfile.ZipFile(chemin_backup, 'r') as zipf:
            zipf.extractall(destination)
        
        self.logger.info(f"Backup ZIP restauré: {destination}")
        return True
    
    def _restaurer_backup_copie(self, backup, destination):
        """Restaure un backup par copie"""
        chemin_backup = backup['chemin']
        
        if not os.path.exists(chemin_backup):
            self.logger.error(f"Dossier backup introuvable: {chemin_backup}")
            return False
        
        # Suppression de la destination si elle existe
        if os.path.exists(destination):
            shutil.rmtree(destination)
        
        # Copie
        shutil.copytree(chemin_backup, destination)
        
        self.logger.info(f"Backup copie restauré: {destination}")
        return True
    
    def nettoyer_anciens_backups(self):
        """Nettoie les anciens backups selon la politique de rétention"""
        backups = self.lister_backups()
        
        if len(backups) <= self.max_backups:
            return
        
        # Suppression des plus anciens
        backups_a_supprimer = backups[self.max_backups:]
        
        for backup in backups_a_supprimer:
            try:
                chemin = backup['chemin']
                if os.path.exists(chemin):
                    if backup['type'] == 'zip':
                        os.remove(chemin)
                    else:
                        shutil.rmtree(chemin)
                    
                    self.logger.info(f"Backup supprimé: {backup['nom']}")
                
            except Exception as e:
                self.logger.error(f"Erreur suppression backup {backup['nom']}: {e}")
        
        # Mise à jour de l'index
        backups_conserves = backups[:self.max_backups]
        self._mettre_a_jour_index(backups_conserves)
    
    def _mettre_a_jour_index(self, backups):
        """Met à jour l'index des backups"""
        fichier_index = os.path.join(self.backup_dir, "index_backups.json")
        
        index = {'backups': backups}
        
        with open(fichier_index, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def backup_avant_operation(self, dossier_cible, nom_operation):
        """Crée un backup automatique avant une opération"""
        if not self.config['options']['backup_automatique']:
            self.logger.debug("Backup automatique désactivé")
            return None
        
        if not os.path.exists(dossier_cible):
            self.logger.debug(f"Dossier cible inexistant, pas de backup nécessaire: {dossier_cible}")
            return None
        
        self.logger.info(f"Backup automatique avant {nom_operation}")
        backup = self.creer_backup_complet(dossier_cible, f"auto_{nom_operation}")
        
        # Nettoyage automatique
        self.nettoyer_anciens_backups()
        
        return backup
    
    def afficher_statistiques(self):
        """Affiche les statistiques des backups"""
        backups = self.lister_backups()
        
        if not backups:
            print("❌ Aucun backup trouvé")
            return
        
        print(f"\n📊 STATISTIQUES DES BACKUPS")
        print(f"{'='*50}")
        print(f"Nombre total de backups: {len(backups)}")
        
        taille_totale = sum(b['taille'] for b in backups)
        print(f"Taille totale: {self._format_taille(taille_totale)}")
        
        # Répartition par type
        types = {}
        for backup in backups:
            type_backup = backup['type']
            types[type_backup] = types.get(type_backup, 0) + 1
        
        print(f"\nRépartition par type:")
        for type_backup, count in types.items():
            print(f"  • {type_backup}: {count} backups")
        
        # Plus ancien et plus récent
        if backups:
            plus_recent = backups[0]
            plus_ancien = backups[-1]
            
            print(f"\nPlus récent: {plus_recent['nom']} ({plus_recent['date'][:10]})")
            print(f"Plus ancien: {plus_ancien['nom']} ({plus_ancien['date'][:10]})")
    
    def _format_taille(self, taille):
        """Formate une taille en bytes de manière lisible"""
        for unite in ['bytes', 'KB', 'MB', 'GB']:
            if taille < 1024.0:
                return f"{taille:.1f} {unite}"
            taille /= 1024.0
        return f"{taille:.1f} TB"


def main():
    """Interface de test du gestionnaire de backup"""
    gestionnaire = GestionnaireBackup()
    
    while True:
        print(f"\n🔧 GESTIONNAIRE DE BACKUP")
        print(f"[1] Créer un backup")
        print(f"[2] Lister les backups")
        print(f"[3] Restaurer un backup")
        print(f"[4] Afficher statistiques")
        print(f"[5] Nettoyer anciens backups")
        print(f"[0] Quitter")
        
        choix = input("Votre choix: ").strip()
        
        if choix == '1':
            source = input("Dossier à sauvegarder: ")
            nom = input("Nom de l'opération (optionnel): ") or "manuel"
            
            if os.path.exists(source):
                backup = gestionnaire.creer_backup_complet(source, nom)
                if backup:
                    print(f"✅ Backup créé: {backup['nom']}")
                else:
                    print("❌ Erreur lors de la création du backup")
            else:
                print("❌ Dossier source inexistant")
        
        elif choix == '2':
            backups = gestionnaire.lister_backups()
            if backups:
                print(f"\n📋 BACKUPS DISPONIBLES ({len(backups)}):")
                for backup in backups:
                    taille = gestionnaire._format_taille(backup['taille'])
                    print(f"  • {backup['nom']} - {backup['date'][:16]} - {taille} ({backup['type']})")
            else:
                print("❌ Aucun backup trouvé")
        
        elif choix == '3':
            nom_backup = input("Nom du backup à restaurer: ")
            destination = input("Destination: ")
            
            if gestionnaire.restaurer_backup(nom_backup, destination):
                print("✅ Backup restauré avec succès")
            else:
                print("❌ Erreur lors de la restauration")
        
        elif choix == '4':
            gestionnaire.afficher_statistiques()
        
        elif choix == '5':
            gestionnaire.nettoyer_anciens_backups()
            print("✅ Nettoyage terminé")
        
        elif choix == '0':
            break
        
        else:
            print("❌ Choix invalide")


if __name__ == "__main__":
    main()