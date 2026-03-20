"""
Module projections - Gestion des altérations linéaires et projections
"""

from enum import Enum
import math
try:
    from pyproj import CRS, Transformer
    PYPROJ_AVAILABLE = True
except ImportError:
    PYPROJ_AVAILABLE = False


class ModeProjection(Enum):
    """Modes de gestion des projections"""
    AUCUNE = "Pas de projection (distances terrain)"
    MANUELLE = "Altération spécifiée manuellement"
    CALIBRAGE = "Calculer depuis les éléments"
    IGN = "Grilles officielles IGN"


class GestionnaireProjection:
    """Gestionnaire des altérations linéaires et projections"""
    
    def __init__(self):
        self.mode = ModeProjection.AUCUNE
        self.alteration_manuelle = 0.0  # en ppm
        self.systeme_projection = 'Lambert93'
        self.altitude_moyenne = 0.0
        self.alterations_calibrees = {}  # Par tronçon
        self._transformer = None
        
    def configurer(self, mode, **params):
        """Configure le mode de projection"""
        self.mode = mode
        
        if mode == ModeProjection.MANUELLE:
            self.alteration_manuelle = params.get('alteration_ppm', 0.0)
            
        elif mode == ModeProjection.CALIBRAGE:
            # Les altérations par tronçon seront calculées plus tard
            pass
            
        elif mode == ModeProjection.IGN:
            self.systeme_projection = params.get('systeme', 'Lambert93')
            self.altitude_moyenne = params.get('altitude', 0.0)
            self._charger_grilles_ign()
    
    def _charger_grilles_ign(self):
        """Charge les grilles IGN si disponibles"""
        if not PYPROJ_AVAILABLE:
            print("⚠️ pyproj non disponible - calculs IGN impossibles")
            return
        
        try:
            if self.systeme_projection == 'Lambert93':
                self.crs_projection = CRS.from_epsg(2154)
                self.crs_geographique = CRS.from_epsg(4171)  # RGF93
                self._transformer = Transformer.from_crs(
                    self.crs_projection, 
                    self.crs_geographique, 
                    always_xy=True
                )
            else:
                print(f"⚠️ Système {self.systeme_projection} non implémenté")
        except Exception as e:
            print(f"⚠️ Erreur chargement grilles IGN: {e}")
    
    def calculer_alteration_ign(self, x, y, h=None):
        """Calcule l'altération selon les grilles IGN"""
        if not PYPROJ_AVAILABLE or self._transformer is None:
            return 0.0
        
        try:
            # Transformation vers géographique
            lon, lat = self._transformer.transform(x, y)
            
            # Paramètres Lambert 93
            lat0 = 46.5  # Latitude origine
            lat1, lat2 = 44.0, 49.0  # Parallèles standards
            
            # Calcul du module linéaire (formule simplifiée)
            lat_rad = math.radians(lat * 0.9)  # Conversion grades->degrés->radians
            lat0_rad = math.radians(lat0)
            
            # Module de projection (approximation)
            m = math.cos(lat_rad) / math.cos(lat0_rad)
            
            # Facteur d'échelle
            k = 0.9996  # Facteur Lambert 93
            module_lineaire = k * m
            
            # Altération de projection
            alteration_projection = (module_lineaire - 1) * 1e6  # en ppm
            
            # Altération d'altitude si fournie
            alteration_altitude = 0.0
            if h is not None:
                R = 6371000  # Rayon moyen terrestre
                alteration_altitude = (h / R) * 1e6  # en ppm
            elif self.altitude_moyenne > 0:
                R = 6371000
                alteration_altitude = (self.altitude_moyenne / R) * 1e6
            
            return alteration_projection + alteration_altitude
            
        except Exception as e:
            print(f"⚠️ Erreur calcul IGN: {e}")
            return 0.0
    
    def calibrer_alteration(self, sommets_avec_pm):
        """Calibre l'altération depuis une liste de sommets avec PM imposés"""
        if len(sommets_avec_pm) < 2:
            return
        
        alterations = []
        self.alterations_calibrees = {}
        
        for i in range(len(sommets_avec_pm) - 1):
            s1 = sommets_avec_pm[i]
            s2 = sommets_avec_pm[i + 1]
            
            # Distance Lambert
            dist_lambert = math.sqrt((s2.x - s1.x)**2 + (s2.y - s1.y)**2)
            
            # Distance PM
            dist_pm = s2.pm - s1.pm
            
            # Altération de ce tronçon
            if dist_lambert > 0:
                alteration = ((dist_pm - dist_lambert) / dist_lambert) * 1e6  # ppm
                alterations.append(alteration)
                
                # Stocker par tronçon
                troncon_key = f"{s1.pm:.0f}-{s2.pm:.0f}"
                self.alterations_calibrees[troncon_key] = alteration
        
        # Statistiques
        if alterations:
            self.alteration_moyenne = sum(alterations) / len(alterations)
            variance = sum((a - self.alteration_moyenne)**2 for a in alterations) / len(alterations)
            self.ecart_type = math.sqrt(variance)
        else:
            self.alteration_moyenne = 0.0
            self.ecart_type = 0.0
    
    def convertir_distance(self, distance, point=None, pm=None):
        """Applique la correction selon le mode configuré"""
        
        if self.mode == ModeProjection.AUCUNE:
            return distance
            
        elif self.mode == ModeProjection.MANUELLE:
            return distance * (1 + self.alteration_manuelle / 1e6)
            
        elif self.mode == ModeProjection.CALIBRAGE:
            # Utilise l'altération moyenne calibrée
            if hasattr(self, 'alteration_moyenne'):
                return distance * (1 + self.alteration_moyenne / 1e6)
            return distance
            
        elif self.mode == ModeProjection.IGN and point is not None:
            alteration = self.calculer_alteration_ign(point.x, point.y, point.z)
            return distance * (1 + alteration / 1e6)
        
        return distance
    
    def rapport_alteration(self):
        """Génère un rapport détaillé sur les altérations"""
        rapport = {
            'mode': self.mode.value,
            'paramètres': {}
        }
        
        if self.mode == ModeProjection.MANUELLE:
            rapport['paramètres'] = {
                'alteration_ppm': self.alteration_manuelle,
                'exemple_100m': self.convertir_distance(100.0),
                'exemple_1000m': self.convertir_distance(1000.0)
            }
            
        elif self.mode == ModeProjection.CALIBRAGE:
            if hasattr(self, 'alteration_moyenne'):
                rapport['paramètres'] = {
                    'alteration_moyenne_ppm': self.alteration_moyenne,
                    'ecart_type_ppm': self.ecart_type,
                    'nb_troncons': len(self.alterations_calibrees),
                    'troncons': self.alterations_calibrees
                }
            
        elif self.mode == ModeProjection.IGN:
            rapport['paramètres'] = {
                'systeme': self.systeme_projection,
                'altitude_moyenne': self.altitude_moyenne,
                'pyproj_disponible': PYPROJ_AVAILABLE
            }
        
        return rapport
    
    def get_info_alteration(self):
        """Retourne les informations sur l'altération active"""
        if self.mode == ModeProjection.AUCUNE:
            return "Aucune correction appliquée (distances terrain)"
        
        elif self.mode == ModeProjection.MANUELLE:
            return f"Altération fixe: {self.alteration_manuelle:+.0f} ppm"
        
        elif self.mode == ModeProjection.CALIBRAGE:
            if hasattr(self, 'alteration_moyenne'):
                return f"Altération calibrée: {self.alteration_moyenne:+.0f} ppm (σ={self.ecart_type:.1f})"
            return "Calibrage non effectué"
        
        elif self.mode == ModeProjection.IGN:
            if PYPROJ_AVAILABLE:
                return f"Grilles IGN {self.systeme_projection} (alt. moy: {self.altitude_moyenne}m)"
            return "Grilles IGN (pyproj non disponible)"
        
        return "Mode inconnu"