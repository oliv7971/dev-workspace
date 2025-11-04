"""
Module de gestion des conflits et doublons
Gère les stratégies de résolution de conflits lors du classement
"""

import os
import shutil
import hashlib
import json
from datetime import datetime
from logger import get_logger


class GestionnaireConflits:
    def __init__(self, config_path="config/config.json"):
        """Initialise le gestionnaire de conflits"""
        self.logger = get_logger()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.strategies = {
            'ecrasement': self._strategie_ecrasement,
            'fusion': self._strategie_fusion,
            'renommage': self._strategie_renommage,
            'comparaison': self._strategie_comparaison,
            'interactif': self._strategie_interactive
        }
    
    def calculer_hash_fichier(self, chemin_fichier):
        """Calcule le hash MD5 d'un fichier"""
        hash_md5 = hashlib.md5()
        try:
            with open(chemin_fichier, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Erreur calcul hash pour {chemin_fichier}: {e}")
            return None
    
    def analyser_conflit(self, source, destination):
        """Analyse un conflit entre source et destination"""
        conflit = {
            'source': source,
            'destination': destination,
            'type': 'inconnu',
            'recommandation': 'interactif',
            'details': {}
        }
        
        # Cas 1: Destination n'existe pas -> pas de conflit
        if not os.path.exists(destination):
            conflit['type'] = 'aucun'
            conflit['recommandation'] = 'copie_simple'
            return conflit
        
        # Cas 2: Les deux sont des fichiers
        if os.path.isfile(source) and os.path.isfile(destination):
            conflit['type'] = 'fichier_vs_fichier'
            return self._analyser_conflit_fichiers(conflit, source, destination)
        
        # Cas 3: Les deux sont des dossiers
        if os.path.isdir(source) and os.path.isdir(destination):
            conflit['type'] = 'dossier_vs_dossier'
            return self._analyser_conflit_dossiers(conflit, source, destination)
        
        # Cas 4: Types différents (fichier vs dossier)
        conflit['type'] = 'type_different'
        conflit['recommandation'] = 'interactif'
        return conflit
    
    def _analyser_conflit_fichiers(self, conflit, source, destination):
        """Analyse un conflit entre deux fichiers"""
        details = conflit['details']
        
        # Informations sur les fichiers
        stat_source = os.stat(source)
        stat_dest = os.stat(destination)
        
        details['taille_source'] = stat_source.st_size
        details['taille_dest'] = stat_dest.st_size
        details['date_source'] = datetime.fromtimestamp(stat_source.st_mtime)
        details['date_dest'] = datetime.fromtimestamp(stat_dest.st_mtime)
        
        # Comparaison des hashs
        hash_source = self.calculer_hash_fichier(source)
        hash_dest = self.calculer_hash_fichier(destination)
        
        details['hash_source'] = hash_source
        details['hash_dest'] = hash_dest
        details['identiques'] = hash_source == hash_dest and hash_source is not None
        
        # Recommandation
        if details['identiques']:
            conflit['recommandation'] = 'ignorer'  # Fichiers identiques
        elif details['date_source'] > details['date_dest']:
            conflit['recommandation'] = 'ecrasement'  # Source plus récent
        elif details['taille_source'] > details['taille_dest']:
            conflit['recommandation'] = 'comparaison'  # Analyse plus poussée
        else:
            conflit['recommandation'] = 'interactif'
        
        return conflit
    
    def _analyser_conflit_dossiers(self, conflit, source, destination):
        """Analyse un conflit entre deux dossiers"""
        details = conflit['details']
        
        # Analyse du contenu
        fichiers_source = self._lister_fichiers_recursif(source)
        fichiers_dest = self._lister_fichiers_recursif(destination)
        
        details['nb_fichiers_source'] = len(fichiers_source)
        details['nb_fichiers_dest'] = len(fichiers_dest)
        
        # Fichiers en commun
        noms_source = set(os.path.relpath(f, source) for f in fichiers_source)
        noms_dest = set(os.path.relpath(f, destination) for f in fichiers_dest)
        
        details['fichiers_communs'] = list(noms_source & noms_dest)
        details['nouveaux_fichiers'] = list(noms_source - noms_dest)
        details['fichiers_existants_seulement'] = list(noms_dest - noms_source)
        
        # Recommandation
        if not details['fichiers_communs']:
            conflit['recommandation'] = 'fusion'  # Pas de conflit réel
        elif len(details['nouveaux_fichiers']) > len(details['fichiers_communs']):
            conflit['recommandation'] = 'fusion'  # Principalement nouveaux fichiers
        else:
            conflit['recommandation'] = 'interactif'  # Beaucoup de conflits
        
        return conflit
    
    def _lister_fichiers_recursif(self, dossier):
        """Liste tous les fichiers d'un dossier récursivement"""
        fichiers = []
        try:
            for root, dirs, files in os.walk(dossier):
                for file in files:
                    fichiers.append(os.path.join(root, file))
        except Exception as e:
            self.logger.error(f"Erreur listage fichiers {dossier}: {e}")
        return fichiers
    
    def resoudre_conflit(self, conflit, strategie=None):
        """Résout un conflit selon la stratégie spécifiée"""
        if strategie is None:
            strategie = conflit['recommandation']
        
        if strategie not in self.strategies:
            self.logger.warning(f"Stratégie inconnue: {strategie}, passage en interactif")
            strategie = 'interactif'
        
        self.logger.info(f"Résolution conflit avec stratégie: {strategie}")
        return self.strategies[strategie](conflit)
    
    def _strategie_ecrasement(self, conflit):
        """Stratégie: écrase la destination avec la source"""
        source = conflit['source']
        destination = conflit['destination']
        
        try:
            # Backup si configuré
            if self.config['options']['backup_automatique']:
                self._backup_avant_ecrasement(destination)
            
            # Suppression et copie
            if os.path.exists(destination):
                if os.path.isdir(destination):
                    shutil.rmtree(destination)
                else:
                    os.remove(destination)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            
            self.logger.log_operation("ECRASEMENT", source, destination, "SUCCESS")
            return {'success': True, 'action': 'ecrasement'}
            
        except Exception as e:
            self.logger.error(f"Erreur écrasement: {e}")
            return {'success': False, 'error': str(e)}
    
    def _strategie_fusion(self, conflit):
        """Stratégie: fusionne le contenu (pour dossiers)"""
        source = conflit['source']
        destination = conflit['destination']
        
        if not os.path.isdir(source):
            # Pour un fichier, fusion = renommage
            return self._strategie_renommage(conflit)
        
        try:
            conflits_sous_fichiers = []
            
            # Copie récursive avec gestion des conflits
            for root, dirs, files in os.walk(source):
                # Créer la structure de dossiers
                rel_path = os.path.relpath(root, source)
                if rel_path == '.':
                    dest_dir = destination
                else:
                    dest_dir = os.path.join(destination, rel_path)
                
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copier les fichiers
                for file in files:
                    source_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    
                    if os.path.exists(dest_file):
                        # Sous-conflit détecté
                        sous_conflit = self.analyser_conflit(source_file, dest_file)
                        if sous_conflit['type'] != 'aucun':
                            conflits_sous_fichiers.append(sous_conflit)
                            # Renommage automatique pour éviter la perte
                            dest_file = self._generer_nom_unique(dest_file)
                    
                    shutil.copy2(source_file, dest_file)
            
            self.logger.log_operation("FUSION", source, destination, "SUCCESS", 
                                     f"{len(conflits_sous_fichiers)} sous-conflits")
            
            return {
                'success': True, 
                'action': 'fusion',
                'sous_conflits': len(conflits_sous_fichiers)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur fusion: {e}")
            return {'success': False, 'error': str(e)}
    
    def _strategie_renommage(self, conflit):
        """Stratégie: renomme la source pour éviter le conflit"""
        source = conflit['source']
        destination = conflit['destination']
        
        try:
            nouveau_nom = self._generer_nom_unique(destination)
            
            if os.path.isdir(source):
                shutil.copytree(source, nouveau_nom)
            else:
                shutil.copy2(source, nouveau_nom)
            
            self.logger.log_operation("RENOMMAGE", source, nouveau_nom, "SUCCESS")
            
            return {
                'success': True, 
                'action': 'renommage',
                'nouveau_nom': nouveau_nom
            }
            
        except Exception as e:
            self.logger.error(f"Erreur renommage: {e}")
            return {'success': False, 'error': str(e)}
    
    def _strategie_comparaison(self, conflit):
        """Stratégie: comparaison détaillée puis décision automatique"""
        details = conflit['details']
        
        # Analyse plus poussée pour fichiers
        if conflit['type'] == 'fichier_vs_fichier':
            # Garde le plus récent ET le plus gros
            if (details['date_source'] > details['date_dest'] and 
                details['taille_source'] >= details['taille_dest']):
                return self._strategie_ecrasement(conflit)
            elif (details['date_dest'] > details['date_source'] and 
                  details['taille_dest'] >= details['taille_source']):
                # Garde l'existant
                return {'success': True, 'action': 'ignore_existant'}
            else:
                # Cas ambigu -> renommage
                return self._strategie_renommage(conflit)
        
        # Pour dossiers, fusion par défaut
        return self._strategie_fusion(conflit)
    
    def _strategie_interactive(self, conflit):
        """Stratégie: demande à l'utilisateur"""
        print(f"\n⚠️  CONFLIT DÉTECTÉ")
        print(f"Source: {conflit['source']}")
        print(f"Destination: {conflit['destination']}")
        print(f"Type: {conflit['type']}")
        
        if 'details' in conflit:
            details = conflit['details']
            if 'taille_source' in details:
                print(f"Taille source: {details['taille_source']} bytes")
                print(f"Taille destination: {details['taille_dest']} bytes")
                print(f"Date source: {details['date_source']}")
                print(f"Date destination: {details['date_dest']}")
                if 'identiques' in details:
                    print(f"Fichiers identiques: {details['identiques']}")
        
        print(f"\nOptions:")
        print(f"[1] Écraser (remplacer destination par source)")
        print(f"[2] Fusionner (pour dossiers) / Renommer (pour fichiers)")
        print(f"[3] Renommer la source")
        print(f"[4] Ignorer (garder destination)")
        print(f"[5] Voir plus de détails")
        
        while True:
            choix = input("Votre choix (1-5): ").strip()
            
            if choix == '1':
                return self._strategie_ecrasement(conflit)
            elif choix == '2':
                if conflit['type'] == 'dossier_vs_dossier':
                    return self._strategie_fusion(conflit)
                else:
                    return self._strategie_renommage(conflit)
            elif choix == '3':
                return self._strategie_renommage(conflit)
            elif choix == '4':
                return {'success': True, 'action': 'ignore'}
            elif choix == '5':
                self._afficher_details_conflit(conflit)
            else:
                print("❌ Choix invalide")
    
    def _afficher_details_conflit(self, conflit):
        """Affiche les détails complets d'un conflit"""
        print(f"\n📋 DÉTAILS DU CONFLIT:")
        print(json.dumps(conflit, indent=2, default=str, ensure_ascii=False))
    
    def _generer_nom_unique(self, chemin):
        """Génère un nom de fichier/dossier unique"""
        base, ext = os.path.splitext(chemin)
        compteur = 1
        
        while True:
            if ext:  # Fichier avec extension
                nouveau_nom = f"{base}_({compteur}){ext}"
            else:  # Dossier
                nouveau_nom = f"{chemin}_({compteur})"
            
            if not os.path.exists(nouveau_nom):
                return nouveau_nom
            
            compteur += 1
            if compteur > 100:  # Sécurité
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return f"{base}_{timestamp}{ext}"
    
    def _backup_avant_ecrasement(self, chemin):
        """Crée un backup avant écrasement"""
        if not os.path.exists(chemin):
            return
        
        backup_dir = self.config['chemins']['backup_dir']
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_backup = f"{os.path.basename(chemin)}_backup_{timestamp}"
        chemin_backup = os.path.join(backup_dir, nom_backup)
        
        try:
            if os.path.isdir(chemin):
                shutil.copytree(chemin, chemin_backup)
            else:
                shutil.copy2(chemin, chemin_backup)
            
            self.logger.info(f"Backup créé: {chemin_backup}")
        except Exception as e:
            self.logger.error(f"Erreur création backup: {e}")


def main():
    """Test du gestionnaire de conflits"""
    gestionnaire = GestionnaireConflits()
    
    # Test d'analyse de conflit
    source = input("Chemin source: ")
    destination = input("Chemin destination: ")
    
    if os.path.exists(source):
        conflit = gestionnaire.analyser_conflit(source, destination)
        print(f"\nAnalyse du conflit:")
        print(json.dumps(conflit, indent=2, default=str, ensure_ascii=False))
        
        # Test de résolution
        if input("\nRésoudre le conflit? (o/n): ").lower() == 'o':
            resultat = gestionnaire.resoudre_conflit(conflit)
            print(f"Résultat: {resultat}")
    else:
        print("❌ Source inexistante")


if __name__ == "__main__":
    main()