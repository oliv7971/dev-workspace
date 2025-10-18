"""
Module de validation des données pour le Calculateur d'Axes
"""

import pandas as pd
import numpy as np
from pathlib import Path
from config import get_config
from logging_utils import get_logger


class ValidateurDonnees:
    """Validation centralisée des données d'entrée"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("ValidateurDonnees")
    
    def valider_point(self, x, y, z=None, nom_point="Point"):
        """Valide les coordonnées d'un point"""
        erreurs = []
        
        # Validation des coordonnées X, Y
        for coord, nom in [(x, 'X'), (y, 'Y')]:
            if not isinstance(coord, (int, float)):
                erreurs.append(f"{nom_point}: {nom} doit être numérique")
            elif not self.config.valider_coordonnee(coord):
                erreurs.append(f"{nom_point}: {nom}={coord} - {self.config.MSG_ERREUR_COORDONNEES}")
        
        # Validation Z si fournie
        if z is not None:
            if not isinstance(z, (int, float)):
                erreurs.append(f"{nom_point}: Z doit être numérique")
            elif not self.config.valider_coordonnee(z):
                erreurs.append(f"{nom_point}: Z={z} - {self.config.MSG_ERREUR_COORDONNEES}")
        
        return erreurs
    
    def valider_rayon(self, rayon, nom_element="Élément"):
        """Valide un rayon de courbure"""
        erreurs = []
        
        if not isinstance(rayon, (int, float)):
            erreurs.append(f"{nom_element}: rayon doit être numérique")
        elif rayon == 0:
            erreurs.append(f"{nom_element}: rayon ne peut pas être nul")
        elif not self.config.valider_rayon(rayon):
            erreurs.append(f"{nom_element}: {self.config.MSG_ERREUR_RAYON}")
        
        return erreurs
    
    def valider_gisement(self, gisement, nom="Gisement"):
        """Valide un gisement en grades"""
        erreurs = []
        
        if not isinstance(gisement, (int, float)):
            erreurs.append(f"{nom}: doit être numérique")
        elif not (0 <= gisement < self.config.GRADES_PAR_TOUR):
            erreurs.append(f"{nom}: doit être entre 0 et {self.config.GRADES_PAR_TOUR} grades")
        
        return erreurs
    
    def valider_fichier_excel(self, chemin_fichier):
        """Valide l'existence et la lisibilité d'un fichier Excel"""
        erreurs = []
        
        # Vérifier l'existence du fichier
        if not Path(chemin_fichier).exists():
            erreurs.append(f"Fichier introuvable: {chemin_fichier}")
            return erreurs
        
        # Tenter de lire le fichier
        try:
            df = pd.read_excel(chemin_fichier, nrows=0)  # Juste les en-têtes
            self.logger.debug(f"Fichier Excel valide: {chemin_fichier}")
        except Exception as e:
            erreurs.append(f"Erreur lecture Excel: {e}")
        
        return erreurs
    
    def valider_donnees_points_excel(self, df):
        """Valide un DataFrame de points"""
        erreurs = []
        
        # Vérifier les colonnes requises
        colonnes_disponibles = set(df.columns.str.upper())
        colonnes_requises = set(col.upper() for col in self.config.COLONNES_POINTS_REQUISES)
        
        colonnes_manquantes = colonnes_requises - colonnes_disponibles
        if colonnes_manquantes:
            erreurs.append(f"Colonnes manquantes: {', '.join(colonnes_manquantes)}")
            return erreurs
        
        # Mapping des colonnes
        mapping_colonnes = self._detecter_colonnes_points(df)
        
        # Validation ligne par ligne
        for idx, row in df.iterrows():
            ligne_num = idx + 2  # +2 car Excel commence à 1 et on a les en-têtes
            
            try:
                x = float(row[mapping_colonnes['x']])
                y = float(row[mapping_colonnes['y']])
                z = float(row[mapping_colonnes.get('z', 0)]) if 'z' in mapping_colonnes else None
                
                erreurs_point = self.valider_point(x, y, z, f"Ligne {ligne_num}")
                erreurs.extend(erreurs_point)
                
            except (ValueError, TypeError, KeyError) as e:
                erreurs.append(f"Ligne {ligne_num}: erreur format données - {e}")
        
        return erreurs
    
    def valider_donnees_elements_excel(self, df):
        """Valide un DataFrame de définition d'éléments"""
        erreurs = []
        
        # Vérifier les colonnes requises
        colonnes_disponibles = set(df.columns.str.upper())
        colonnes_requises = set(col.upper() for col in self.config.COLONNES_ELEMENTS_REQUISES)
        
        if not colonnes_requises.issubset(colonnes_disponibles):
            colonnes_manquantes = colonnes_requises - colonnes_disponibles
            erreurs.append(f"Colonnes manquantes: {', '.join(colonnes_manquantes)}")
            return erreurs
        
        # Validation des éléments
        for idx, row in df.iterrows():
            ligne_num = idx + 2
            
            try:
                type_elem = str(row['Type']).upper()
                
                if type_elem == 'AD':  # Alignement droit
                    gisement = float(row['Param1'])
                    longueur = float(row['Param2'])
                    
                    erreurs.extend(self.valider_gisement(gisement, f"Ligne {ligne_num} gisement"))
                    
                    if longueur <= 0:
                        erreurs.append(f"Ligne {ligne_num}: longueur doit être positive")
                    elif longueur > self.config.LONGUEUR_MAX_AXE:
                        erreurs.append(f"Ligne {ligne_num}: longueur excessive ({longueur}m)")
                
                elif type_elem == 'C':  # Arc circulaire
                    rayon = float(row['Param1'])
                    erreurs.extend(self.valider_rayon(rayon, f"Ligne {ligne_num}"))
                    
                    if pd.notna(row['Param2']):
                        param2 = float(row['Param2'])
                        if abs(param2) < 100:  # Probablement une déviation
                            erreurs.extend(self.valider_gisement(abs(param2), f"Ligne {ligne_num} déviation"))
                
                elif type_elem not in ['CL', 'P']:  # Types non reconnus
                    erreurs.append(f"Ligne {ligne_num}: type d'élément '{type_elem}' non reconnu")
                
            except (ValueError, TypeError, KeyError) as e:
                erreurs.append(f"Ligne {ligne_num}: erreur format - {e}")
        
        return erreurs
    
    def _detecter_colonnes_points(self, df):
        """Détecte automatiquement les colonnes de coordonnées"""
        mapping = {}
        
        for col in df.columns:
            col_upper = col.upper()
            if col_upper in ['ID', 'NOM', 'NAME', 'POINT']:
                mapping['id'] = col
            elif col_upper in ['X', 'EAST', 'E']:
                mapping['x'] = col
            elif col_upper in ['Y', 'NORTH', 'N']:
                mapping['y'] = col
            elif col_upper in ['Z', 'H', 'ALT', 'ALTITUDE']:
                mapping['z'] = col
            elif col_upper in ['PM', 'PK']:
                mapping['pm'] = col
        
        return mapping
    
    def valider_intervalle_pm(self, pm_debut, pm_fin, longueur_axe=None):
        """Valide un intervalle de PM"""
        erreurs = []
        
        if not isinstance(pm_debut, (int, float)) or not isinstance(pm_fin, (int, float)):
            erreurs.append("PM début et fin doivent être numériques")
            return erreurs
        
        if pm_debut >= pm_fin:
            erreurs.append("PM début doit être inférieur à PM fin")
        
        if pm_debut < 0:
            erreurs.append("PM début ne peut pas être négatif")
        
        if longueur_axe and pm_fin > longueur_axe:
            erreurs.append(f"PM fin ({pm_fin}) dépasse la longueur de l'axe ({longueur_axe})")
        
        return erreurs
    
    def generer_rapport_validation(self, erreurs, nom_operation="Validation"):
        """Génère un rapport de validation"""
        if not erreurs:
            self.logger.info(f"{nom_operation}: SUCCÈS - Aucune erreur détectée")
            return {"status": "OK", "erreurs": [], "nb_erreurs": 0}
        
        self.logger.warning(f"{nom_operation}: {len(erreurs)} erreur(s) détectée(s)")
        for erreur in erreurs:
            self.logger.warning(f"  - {erreur}")
        
        return {
            "status": "ERREUR",
            "erreurs": erreurs,
            "nb_erreurs": len(erreurs)
        }


# Instance globale du validateur
_validateur_instance = None

def get_validateur():
    """Retourne l'instance du validateur (singleton)"""
    global _validateur_instance
    
    if _validateur_instance is None:
        _validateur_instance = ValidateurDonnees()
    
    return _validateur_instance


# Fonctions de validation rapides
def valider_point(x, y, z=None, nom="Point"):
    return get_validateur().valider_point(x, y, z, nom)

def valider_rayon(rayon, nom="Élément"):
    return get_validateur().valider_rayon(rayon, nom)

def valider_fichier_excel(chemin):
    return get_validateur().valider_fichier_excel(chemin)