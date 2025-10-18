"""
Configuration centralisée pour le Calculateur d'Axes
"""

import os
from pathlib import Path


class Config:
    """Configuration principale de l'application"""
    
    # Version de l'application
    VERSION = "1.0.0"
    APP_NAME = "Calculateur d'Axes"
    
    # Précisions de calcul
    PRECISION_CALCUL = 1e-6
    TOLERANCE_PROJECTION = 0.001
    TOLERANCE_HORIZONTALE_DEFAUT = 0.05  # mètres
    TOLERANCE_VERTICALE_DEFAUT = 0.02    # mètres
    
    # Paramètres géométriques
    GRADES_PAR_TOUR = 400
    RAYON_TERRE_MOYEN = 6371000  # mètres
    
    # Paramètres d'export
    ECHELLE_DEFAUT = 1000
    FORMAT_EXPORT_DEFAUT = 'xlsx'
    INTERVALLE_TABULATION_DEFAUT = 20  # mètres
    NB_POINTS_ARC_DEFAUT = 100
    
    # Répertoires
    REPERTOIRE_EXEMPLES = 'exemples'
    REPERTOIRE_LOGS = 'logs'
    REPERTOIRE_TESTS = 'tests'
    REPERTOIRE_CONFIG = '.config'
    
    # Fichiers
    FICHIER_LOG_DEFAUT = 'calculateur_axes.log'
    FICHIER_CONFIG_UTILISATEUR = 'user_config.json'
    
    # Formats d'export DXF
    DXF_VERSION_DEFAUT = 'R2010'
    DXF_CALQUES = {
        'AXES': {'couleur': 1, 'description': 'Axes principaux'},
        'POINTS': {'couleur': 2, 'description': 'Points topographiques'},
        'TEXTES': {'couleur': 3, 'description': 'Annotations'},
        'CONSTRUCTION': {'couleur': 8, 'description': 'Éléments construction'},
        'PROFIL': {'couleur': 4, 'description': 'Profil en long'}
    }
    
    # Cache
    TAILLE_CACHE_MAX = 1000  # Nombre d'éléments en cache
    DUREE_CACHE_SEC = 3600   # 1 heure
    
    # Validation Excel
    COLONNES_POINTS_REQUISES = ['X', 'Y']
    COLONNES_POINTS_OPTIONNELLES = ['Z', 'ID', 'PM']
    COLONNES_ELEMENTS_REQUISES = ['Type', 'Param1', 'Param2']
    COLONNES_PROFIL_REQUISES = ['PM', 'Z']
    
    # Limites de sécurité
    COORDONNEE_MIN = -1e9
    COORDONNEE_MAX = 1e9
    RAYON_MIN = 10     # mètres
    RAYON_MAX = 100000 # mètres
    LONGUEUR_MAX_AXE = 100000  # mètres
    
    # Messages d'erreur standardisés
    MSG_ERREUR_COORDONNEES = "Coordonnées hors limites acceptables"
    MSG_ERREUR_RAYON = f"Rayon doit être entre {RAYON_MIN} et {RAYON_MAX} mètres"
    MSG_ERREUR_PM_HORS_LIMITE = "PM hors limites de l'axe"
    MSG_ERREUR_FICHIER_INEXISTANT = "Fichier introuvable"
    MSG_ERREUR_FORMAT_EXCEL = "Format Excel non reconnu"
    
    @classmethod
    def initialiser_repertoires(cls):
        """Crée les répertoires nécessaires s'ils n'existent pas"""
        repertoires = [
            cls.REPERTOIRE_EXEMPLES,
            cls.REPERTOIRE_LOGS,
            cls.REPERTOIRE_CONFIG
        ]
        
        for rep in repertoires:
            Path(rep).mkdir(exist_ok=True)
    
    @classmethod
    def valider_coordonnee(cls, coord):
        """Valide qu'une coordonnée est dans les limites acceptables"""
        return cls.COORDONNEE_MIN <= coord <= cls.COORDONNEE_MAX
    
    @classmethod
    def valider_rayon(cls, rayon):
        """Valide qu'un rayon est acceptable"""
        return cls.RAYON_MIN <= abs(rayon) <= cls.RAYON_MAX
    
    @classmethod
    def chemin_log_complet(cls):
        """Retourne le chemin complet du fichier de log"""
        return os.path.join(cls.REPERTOIRE_LOGS, cls.FICHIER_LOG_DEFAUT)


class ConfigDeveloppement(Config):
    """Configuration pour développement/test"""
    
    PRECISION_CALCUL = 1e-9
    TAILLE_CACHE_MAX = 100
    DUREE_CACHE_SEC = 60
    
    # Mode debug activé
    DEBUG = True
    VERBOSE_LOGGING = True


class ConfigProduction(Config):
    """Configuration pour production"""
    
    DEBUG = False
    VERBOSE_LOGGING = False
    
    # Limites plus strictes en production
    TOLERANCE_PROJECTION = 0.0001
    TAILLE_CACHE_MAX = 5000


# Configuration active (peut être changée selon l'environnement)
ACTIVE_CONFIG = Config

def get_config():
    """Retourne la configuration active"""
    return ACTIVE_CONFIG