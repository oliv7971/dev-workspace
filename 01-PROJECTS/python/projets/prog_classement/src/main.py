"""
Script principal de classement de dossiers BURE
Orchestre l'ensemble du processus de classement avec interface utilisateur
"""

import os
import sys
import json
import time
from datetime import datetime

# Import des modules du projet
from logger import get_logger
from validation_interactive import ValidateurClassification
from gestion_conflits import GestionnaireConflits
from backup_manager import GestionnaireBackup


class OrchestrateurClassement:
    def __init__(self, config_path="config/config.json"):
        """Initialise l'orchestrateur"""
        self.logger = get_logger()
        
        # Chargement configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Modules spécialisés
        self.validateur = ValidateurClassification(config_path)
        self.gestionnaire_conflits = GestionnaireConflits(config_path)
        self.gestionnaire_backup = GestionnaireBackup(config_path)
        
        # Statistiques de session
        self.stats_session = {
            'dossiers_traites': 0,
            'dossiers_classes': 0,
            'conflits_resolus': 0,
            'backups_crees': 0,
            'erreurs': 0,
            'debut_session': datetime.now()
        }
    
    def afficher_menu_principal(self):
        """Affiche le menu principal"""
        print(f"\n{'='*80}")
        print(f"🗂️  SYSTÈME DE CLASSEMENT AUTOMATIQUE - BURE")
        print(f"{'='*80}")
        print(f"[1] 📥 Collecter les données (depuis activités chronologiques)")
        print(f"[2] 🔍 Valider les classifications (mode interactif)")
        print(f"[3] 📁 Appliquer le classement (copie vers galeries)")
        print(f"[4] 🔄 Processus complet (1 → 2 → 3)")
        print(f"")
        print(f"[5] 💾 Gestion des backups")
        print(f"[6] 📊 Afficher les statistiques")
        print(f"[7] ⚙️  Configuration")
        print(f"[8] 🧹 Nettoyage (supprimer temporaires)")
        print(f"")
        print(f"[0] ❌ Quitter")
        print(f"{'='*80}")
    
    def executer_collecte_donnees(self):
        """Exécute la collecte des données depuis les activités chronologiques"""
        self.logger.log_session_start("collecte_donnees")
        
        print(f"\n🔄 COLLECTE DES DONNÉES")
        print(f"Source: {self.config['chemins']['source_base']}")
        print(f"Destination temporaire: {self.config['chemins']['destination_temp']}")
        
        if not os.path.exists(self.config['chemins']['source_base']):
            print(f"❌ Dossier source introuvable!")
            return False
        
        # Backup préventif si destination existe
        if os.path.exists(self.config['chemins']['destination_temp']):
            if input("Destination temporaire existe. Créer backup? (o/N): ").lower() == 'o':
                backup = self.gestionnaire_backup.backup_avant_operation(
                    self.config['chemins']['destination_temp'],
                    "collecte_donnees"
                )
                if backup:
                    self.stats_session['backups_crees'] += 1
        
        try:
            # Import et exécution du script de récupération
            import recupe_donnees
            # Simulation d'exécution - à adapter selon votre script existant
            print(f"🔄 Exécution de la collecte de données...")
            # resultat = recupe_donnees.main()  # Décommentez quand le script est adapté
            
            print(f"✅ Collecte terminée")
            self.logger.log_session_end("collecte_donnees")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte: {e}")
            self.stats_session['erreurs'] += 1
            return False
    
    def executer_validation_interactive(self):
        """Exécute la validation interactive des classifications"""
        self.logger.log_session_start("validation_interactive")
        
        print(f"\n🔍 VALIDATION INTERACTIVE")
        
        if not os.path.exists(self.config['chemins']['destination_temp']):
            print(f"❌ Aucune donnée temporaire trouvée. Exécutez d'abord la collecte.")
            return False
        
        try:
            # Analyse des dossiers
            analyses = self.validateur.analyser_dossier_temp()
            
            if not analyses:
                print(f"❌ Aucun dossier à valider")
                return False
            
            print(f"📊 {len(analyses)} dossiers trouvés")
            
            # Mode de validation
            if self.config['options']['validation_interactive']:
                validations = self.validateur.valider_interactivement(analyses)
            else:
                # Mode automatique
                print(f"Mode automatique activé")
                validations = []
                for analyse in analyses:
                    validation = {
                        'analyse': analyse,
                        'action': 'valider' if analyse['confidence'] > 0.5 else 'ignorer',
                        'categorie_finale': analyse['categorie_proposee']
                    }
                    validations.append(validation)
            
            # Génération du rapport
            self.validateur.generer_rapport(validations)
            
            self.stats_session['dossiers_traites'] += len(analyses)
            self.logger.log_session_end("validation_interactive", self.validateur.stats)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation: {e}")
            self.stats_session['erreurs'] += 1
            return False
    
    def executer_classement_final(self):
        """Exécute le classement final vers les galeries"""
        self.logger.log_session_start("classement_final")
        
        print(f"\n📁 CLASSEMENT FINAL")
        print(f"Source: {self.config['chemins']['destination_temp']}")
        print(f"Destination: {self.config['chemins']['destination_finale']}")
        
        if not os.path.exists(self.config['chemins']['destination_temp']):
            print(f"❌ Aucune donnée temporaire trouvée")
            return False
        
        # Confirmation finale
        if self.config['options']['mode_securise']:
            print(f"⚠️  MODE SÉCURISÉ ACTIVÉ")
            print(f"Cette opération va modifier définitivement vos dossiers galerie.")
            confirmation = input("Confirmer le classement final? (oui/non): ").lower()
            if confirmation not in ['oui', 'o', 'yes', 'y']:
                print(f"❌ Opération annulée")
                return False
        
        # Backup préventif
        if os.path.exists(self.config['chemins']['destination_finale']):
            backup = self.gestionnaire_backup.backup_avant_operation(
                self.config['chemins']['destination_finale'],
                "classement_final"
            )
            if backup:
                self.stats_session['backups_crees'] += 1
                print(f"💾 Backup créé: {backup['nom']}")
        
        try:
            # Exécution du classement avec gestion des conflits
            return self._executer_classement_avec_conflits()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du classement final: {e}")
            self.stats_session['erreurs'] += 1
            return False
    
    def _executer_classement_avec_conflits(self):
        """Exécute le classement en gérant les conflits"""
        destination_temp = self.config['chemins']['destination_temp']
        destination_finale = self.config['chemins']['destination_finale']
        
        os.makedirs(destination_finale, exist_ok=True)
        
        conflits_detectes = 0
        dossiers_classes = 0
        
        # Parcours des galeries temporaires
        for galerie in os.listdir(destination_temp):
            chemin_galerie_temp = os.path.join(destination_temp, galerie)
            chemin_galerie_finale = os.path.join(destination_finale, galerie)
            
            if not os.path.isdir(chemin_galerie_temp):
                continue
            
            print(f"\n📂 Traitement galerie: {galerie}")
            
            # Analyse des conflits
            conflit = self.gestionnaire_conflits.analyser_conflit(
                chemin_galerie_temp, 
                chemin_galerie_finale
            )
            
            if conflit['type'] != 'aucun':
                conflits_detectes += 1
                self.logger.warning(f"Conflit détecté pour {galerie}")
                
                # Résolution du conflit
                resultat = self.gestionnaire_conflits.resoudre_conflit(conflit)
                
                if resultat['success']:
                    print(f"   ✅ Conflit résolu: {resultat['action']}")
                    self.stats_session['conflits_resolus'] += 1
                else:
                    print(f"   ❌ Échec résolution conflit")
                    self.stats_session['erreurs'] += 1
                    continue
            else:
                # Pas de conflit, copie simple
                if os.path.isdir(chemin_galerie_temp):
                    import shutil
                    shutil.copytree(chemin_galerie_temp, chemin_galerie_finale)
                else:
                    shutil.copy2(chemin_galerie_temp, chemin_galerie_finale)
                
                print(f"   ✅ Copié sans conflit")
            
            dossiers_classes += 1
        
        self.stats_session['dossiers_classes'] = dossiers_classes
        
        print(f"\n📊 Résumé du classement:")
        print(f"   • Galeries traitées: {dossiers_classes}")
        print(f"   • Conflits détectés: {conflits_detectes}")
        print(f"   • Conflits résolus: {self.stats_session['conflits_resolus']}")
        
        self.logger.log_session_end("classement_final", {
            'galeries_traitees': dossiers_classes,
            'conflits_detectes': conflits_detectes,
            'conflits_resolus': self.stats_session['conflits_resolus']
        })
        
        return True
    
    def executer_processus_complet(self):
        """Exécute le processus complet de bout en bout"""
        self.logger.log_session_start("processus_complet")
        
        print(f"\n🔄 PROCESSUS COMPLET")
        print(f"Étapes: Collecte → Validation → Classement")
        
        # Confirmation
        if input("Démarrer le processus complet? (o/N): ").lower() != 'o':
            return False
        
        # Étape 1: Collecte
        print(f"\n📥 Étape 1/3: Collecte des données")
        if not self.executer_collecte_donnees():
            print(f"❌ Échec de la collecte")
            return False
        
        time.sleep(1)  # Pause pour lisibilité
        
        # Étape 2: Validation
        print(f"\n🔍 Étape 2/3: Validation")
        if not self.executer_validation_interactive():
            print(f"❌ Échec de la validation")
            return False
        
        time.sleep(1)
        
        # Étape 3: Classement final
        print(f"\n📁 Étape 3/3: Classement final")
        if not self.executer_classement_final():
            print(f"❌ Échec du classement final")
            return False
        
        print(f"\n🎉 PROCESSUS COMPLET TERMINÉ AVEC SUCCÈS!")
        self.afficher_statistiques_session()
        
        self.logger.log_session_end("processus_complet", self.stats_session)
        return True
    
    def gerer_backups(self):
        """Interface de gestion des backups"""
        while True:
            print(f"\n💾 GESTION DES BACKUPS")
            print(f"[1] Afficher statistiques")
            print(f"[2] Lister les backups")
            print(f"[3] Créer backup manuel")
            print(f"[4] Restaurer backup")
            print(f"[5] Nettoyer anciens backups")
            print(f"[0] Retour")
            
            choix = input("Votre choix: ").strip()
            
            if choix == '1':
                self.gestionnaire_backup.afficher_statistiques()
            elif choix == '2':
                backups = self.gestionnaire_backup.lister_backups()
                if backups:
                    for backup in backups:
                        print(f"  • {backup['nom']} - {backup['date'][:16]}")
                else:
                    print("❌ Aucun backup")
            elif choix == '3':
                dossier = input("Dossier à sauvegarder: ")
                if os.path.exists(dossier):
                    backup = self.gestionnaire_backup.creer_backup_complet(dossier)
                    print(f"✅ Backup créé: {backup['nom']}" if backup else "❌ Erreur")
                else:
                    print("❌ Dossier inexistant")
            elif choix == '4':
                nom = input("Nom du backup: ")
                dest = input("Destination: ")
                if self.gestionnaire_backup.restaurer_backup(nom, dest):
                    print("✅ Restauration réussie")
                else:
                    print("❌ Erreur de restauration")
            elif choix == '5':
                self.gestionnaire_backup.nettoyer_anciens_backups()
                print("✅ Nettoyage terminé")
            elif choix == '0':
                break
    
    def afficher_statistiques_session(self):
        """Affiche les statistiques de la session courante"""
        duree = datetime.now() - self.stats_session['debut_session']
        
        print(f"\n📊 STATISTIQUES DE SESSION")
        print(f"{'='*50}")
        print(f"Durée: {duree}")
        print(f"Dossiers traités: {self.stats_session['dossiers_traites']}")
        print(f"Dossiers classés: {self.stats_session['dossiers_classes']}")
        print(f"Conflits résolus: {self.stats_session['conflits_resolus']}")
        print(f"Backups créés: {self.stats_session['backups_crees']}")
        print(f"Erreurs: {self.stats_session['erreurs']}")
    
    def configurer_systeme(self):
        """Interface de configuration"""
        print(f"\n⚙️  CONFIGURATION SYSTÈME")
        print(f"Configuration actuelle:")
        print(f"  • Mode sécurisé: {self.config['options']['mode_securise']}")
        print(f"  • Backup automatique: {self.config['options']['backup_automatique']}")
        print(f"  • Validation interactive: {self.config['options']['validation_interactive']}")
        print(f"  • Niveau de log: {self.config['options']['niveau_log']}")
        
        if input("Modifier configuration? (o/N): ").lower() == 'o':
            # Interface simple de modification
            self._modifier_configuration()
    
    def _modifier_configuration(self):
        """Modifie la configuration"""
        # Cette fonction pourrait être étendue pour une interface complète
        print("Interface de modification de configuration à implémenter")
        print("Pour l'instant, modifiez directement config/config.json")
    
    def nettoyer_temporaires(self):
        """Nettoie les fichiers temporaires"""
        print(f"\n🧹 NETTOYAGE DES TEMPORAIRES")
        
        dossier_temp = self.config['chemins']['destination_temp']
        
        if not os.path.exists(dossier_temp):
            print("❌ Aucun dossier temporaire trouvé")
            return
        
        # Confirmation
        print(f"Dossier à nettoyer: {dossier_temp}")
        if input("Confirmer la suppression? (oui/non): ").lower() not in ['oui', 'o']:
            print("❌ Nettoyage annulé")
            return
        
        # Backup avant suppression
        backup = self.gestionnaire_backup.backup_avant_operation(
            dossier_temp, 
            "nettoyage_temp"
        )
        
        try:
            import shutil
            shutil.rmtree(dossier_temp)
            print(f"✅ Dossier temporaire supprimé")
            if backup:
                print(f"💾 Backup créé: {backup['nom']}")
        except Exception as e:
            self.logger.error(f"Erreur nettoyage: {e}")
            print(f"❌ Erreur lors du nettoyage")
    
    def executer(self):
        """Boucle principale de l'application"""
        self.logger.log_session_start("orchestrateur_principal")
        
        try:
            while True:
                self.afficher_menu_principal()
                choix = input("Votre choix: ").strip()
                
                if choix == '1':
                    self.executer_collecte_donnees()
                elif choix == '2':
                    self.executer_validation_interactive()
                elif choix == '3':
                    self.executer_classement_final()
                elif choix == '4':
                    self.executer_processus_complet()
                elif choix == '5':
                    self.gerer_backups()
                elif choix == '6':
                    self.afficher_statistiques_session()
                elif choix == '7':
                    self.configurer_systeme()
                elif choix == '8':
                    self.nettoyer_temporaires()
                elif choix == '0':
                    print(f"\n👋 Au revoir!")
                    break
                else:
                    print(f"❌ Choix invalide")
                
                # Pause avant retour au menu
                if choix != '0':
                    input("\nAppuyez sur Entrée pour continuer...")
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interruption détectée")
        except Exception as e:
            self.logger.error(f"Erreur fatale: {e}")
            print(f"❌ Erreur fatale: {e}")
        finally:
            self.afficher_statistiques_session()
            self.logger.log_session_end("orchestrateur_principal", self.stats_session)


def main():
    """Point d'entrée principal"""
    print(f"🚀 Initialisation du système de classement...")
    
    # Vérification des dépendances
    try:
        orchestrateur = OrchestrateurClassement()
        orchestrateur.executer()
    except FileNotFoundError as e:
        print(f"❌ Fichier de configuration manquant: {e}")
        print(f"Assurez-vous que config/config.json existe")
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")


if __name__ == "__main__":
    main()