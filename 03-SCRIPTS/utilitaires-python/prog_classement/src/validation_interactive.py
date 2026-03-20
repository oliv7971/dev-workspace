"""
Script de validation interactive des classifications
Permet de vérifier et ajuster les classifications avant application définitive
"""

import os
import json
import unicodedata
from logger import get_logger


class ValidateurClassification:
    def __init__(self, config_path="config/config.json"):
        """Initialise le validateur"""
        self.logger = get_logger()
        
        # Chargement configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Chargement catégories et correspondances
        with open("config/categories.json", 'r', encoding='utf-8') as f:
            self.categories = json.load(f)
        
        with open("config/correspondances.json", 'r', encoding='utf-8') as f:
            self.correspondances = json.load(f)
        
        self.stats = {
            'total_dossiers': 0,
            'auto_valides': 0,
            'modifies': 0,
            'ignores': 0
        }
    
    def normaliser(self, texte):
        """Normalise le texte (supprime accents, minuscules)"""
        return ''.join(c for c in unicodedata.normalize('NFD', texte)
                      if unicodedata.category(c) != 'Mn').lower()
    
    def detecter_categorie(self, nom_dossier):
        """Détecte la catégorie d'un dossier"""
        nom_norm = self.normaliser(nom_dossier)
        
        # Recherche dans les catégories
        for categorie, mots_cles in self.categories.items():
            for mot in mots_cles:
                if self.normaliser(mot) in nom_norm:
                    confidence = len(mot) / len(nom_dossier)  # Score de confiance simple
                    return categorie, confidence, mot
        
        return self.config['dossiers']['divers'], 0.0, "aucun"
    
    def detecter_galerie(self, nom_dossier):
        """Détecte la galerie d'un dossier"""
        nom_norm = self.normaliser(nom_dossier)
        
        for identifiant, galerie in self.correspondances.items():
            if self.normaliser(identifiant) in nom_norm:
                return galerie, identifiant
        
        return None, None
    
    def analyser_dossier_temp(self):
        """Analyse tous les dossiers dans l'espace temporaire"""
        destination_temp = self.config['chemins']['destination_temp']
        
        if not os.path.exists(destination_temp):
            self.logger.error(f"Dossier temporaire introuvable: {destination_temp}")
            return []
        
        analyses = []
        
        for site in os.listdir(destination_temp):
            chemin_site = os.path.join(destination_temp, site)
            if not os.path.isdir(chemin_site):
                continue
            
            dossier_a_classer = os.path.join(chemin_site, self.config['dossiers']['a_classer'])
            if not os.path.exists(dossier_a_classer):
                continue
            
            for dossier in os.listdir(dossier_a_classer):
                chemin_dossier = os.path.join(dossier_a_classer, dossier)
                if not os.path.isdir(chemin_dossier):
                    continue
                
                # Analyse du dossier
                categorie, confidence, mot_cle = self.detecter_categorie(dossier)
                galerie, identifiant = self.detecter_galerie(dossier)
                
                taille = self._calculer_taille(chemin_dossier)
                nb_fichiers = self._compter_fichiers(chemin_dossier)
                
                analyse = {
                    'nom': dossier,
                    'chemin': chemin_dossier,
                    'site': site,
                    'categorie_proposee': categorie,
                    'confidence': confidence,
                    'mot_cle': mot_cle,
                    'galerie_detectee': galerie,
                    'identifiant': identifiant,
                    'taille_mb': round(taille / (1024*1024), 2),
                    'nb_fichiers': nb_fichiers,
                    'action': 'auto' if confidence > 0.3 else 'manuel'
                }
                
                analyses.append(analyse)
                self.stats['total_dossiers'] += 1
        
        return analyses
    
    def _calculer_taille(self, chemin):
        """Calcule la taille totale d'un dossier"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(chemin):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total += os.path.getsize(filepath)
        except:
            pass
        return total
    
    def _compter_fichiers(self, chemin):
        """Compte le nombre de fichiers dans un dossier"""
        count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(chemin):
                count += len(filenames)
        except:
            pass
        return count
    
    def valider_interactivement(self, analyses):
        """Interface de validation interactive"""
        print(f"\n{'='*80}")
        print(f"🔍 VALIDATION DES CLASSIFICATIONS - {len(analyses)} dossiers à traiter")
        print(f"{'='*80}")
        
        validations = []
        
        for i, analyse in enumerate(analyses, 1):
            print(f"\n📁 [{i}/{len(analyses)}] {analyse['nom']}")
            print(f"   📍 Site: {analyse['site']}")
            print(f"   📂 Catégorie proposée: {analyse['categorie_proposee']} (confiance: {analyse['confidence']:.2f})")
            print(f"   🏢 Galerie détectée: {analyse['galerie_detectee'] or 'NON DÉTECTÉE'}")
            print(f"   📊 {analyse['nb_fichiers']} fichiers, {analyse['taille_mb']} MB")
            
            if analyse['action'] == 'auto' and analyse['confidence'] > 0.7:
                print(f"   ✅ Classification automatique (haute confiance)")
                validation = {
                    'analyse': analyse,
                    'action': 'valider',
                    'categorie_finale': analyse['categorie_proposee']
                }
                self.stats['auto_valides'] += 1
            else:
                # Demande de validation manuelle
                while True:
                    print(f"\n   Actions possibles:")
                    print(f"   [V] Valider la classification proposée")
                    print(f"   [M] Modifier la catégorie")
                    print(f"   [L] Lister les catégories disponibles")
                    print(f"   [I] Ignorer ce dossier")
                    print(f"   [Q] Quitter")
                    
                    choix = input("   Votre choix: ").upper().strip()
                    
                    if choix == 'V':
                        validation = {
                            'analyse': analyse,
                            'action': 'valider',
                            'categorie_finale': analyse['categorie_proposee']
                        }
                        break
                    elif choix == 'M':
                        self._modifier_categorie(analyse)
                        validation = {
                            'analyse': analyse,
                            'action': 'modifier',
                            'categorie_finale': analyse['categorie_proposee']  # Sera modifiée
                        }
                        self.stats['modifies'] += 1
                        break
                    elif choix == 'L':
                        self._lister_categories()
                    elif choix == 'I':
                        validation = {
                            'analyse': analyse,
                            'action': 'ignorer',
                            'categorie_finale': None
                        }
                        self.stats['ignores'] += 1
                        break
                    elif choix == 'Q':
                        return validations  # Sortie anticipée
                    else:
                        print("   ❌ Choix invalide")
            
            validations.append(validation)
        
        return validations
    
    def _modifier_categorie(self, analyse):
        """Permet de modifier la catégorie d'un dossier"""
        print(f"   Catégories disponibles:")
        categories_list = list(self.categories.keys()) + [self.config['dossiers']['divers']]
        for i, cat in enumerate(categories_list, 1):
            print(f"   [{i}] {cat}")
        
        while True:
            try:
                choix = input("   Numéro de catégorie: ").strip()
                if choix.isdigit():
                    idx = int(choix) - 1
                    if 0 <= idx < len(categories_list):
                        nouvelle_categorie = categories_list[idx]
                        analyse['categorie_proposee'] = nouvelle_categorie
                        print(f"   ✅ Catégorie modifiée: {nouvelle_categorie}")
                        break
                    else:
                        print("   ❌ Numéro invalide")
                else:
                    # Recherche par nom
                    for cat in categories_list:
                        if choix.upper() in cat.upper():
                            analyse['categorie_proposee'] = cat
                            print(f"   ✅ Catégorie modifiée: {cat}")
                            return
                    print("   ❌ Catégorie non trouvée")
            except ValueError:
                print("   ❌ Entrée invalide")
    
    def _lister_categories(self):
        """Affiche la liste des catégories disponibles"""
        print(f"\n   📋 Catégories disponibles:")
        for categorie, mots_cles in self.categories.items():
            print(f"   • {categorie}: {', '.join(mots_cles[:3])}{'...' if len(mots_cles) > 3 else ''}")
        print(f"   • {self.config['dossiers']['divers']}: autres cas")
    
    def generer_rapport(self, validations):
        """Génère un rapport des validations"""
        print(f"\n{'='*80}")
        print(f"📊 RAPPORT DE VALIDATION")
        print(f"{'='*80}")
        print(f"Total de dossiers traités: {self.stats['total_dossiers']}")
        print(f"Validations automatiques: {self.stats['auto_valides']}")
        print(f"Modifications manuelles: {self.stats['modifies']}")
        print(f"Dossiers ignorés: {self.stats['ignores']}")
        
        # Sauvegarde du rapport
        rapport_path = os.path.join(
            self.config['chemins']['logs_dir'], 
            f"rapport_validation_{os.getpid()}.json"
        )
        os.makedirs(os.path.dirname(rapport_path), exist_ok=True)
        
        with open(rapport_path, 'w', encoding='utf-8') as f:
            json.dump({
                'stats': self.stats,
                'validations': validations
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Rapport sauvegardé: {rapport_path}")
        
        return validations


def main():
    """Point d'entrée principal"""
    validateur = ValidateurClassification()
    logger = get_logger()
    
    logger.log_session_start("validation_interactive")
    
    try:
        # Analyse des dossiers
        analyses = validateur.analyser_dossier_temp()
        
        if not analyses:
            print("❌ Aucun dossier à valider trouvé")
            return
        
        # Validation interactive
        validations = validateur.valider_interactivement(analyses)
        
        # Génération du rapport
        validateur.generer_rapport(validations)
        
        logger.log_session_end("validation_interactive", validateur.stats)
        
    except KeyboardInterrupt:
        logger.warning("Validation interrompue par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur lors de la validation: {e}")


if __name__ == "__main__":
    main()