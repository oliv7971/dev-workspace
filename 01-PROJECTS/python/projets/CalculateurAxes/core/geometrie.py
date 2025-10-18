"""
Module géométrie - Classes de base pour les calculs topographiques
"""

import math
import numpy as np


class Point:
    """Point 3D avec gestion PM optionnel"""
    
    def __init__(self, x, y, z=0.0, pm=None):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.pm = pm
    
    def distance_2d(self, autre):
        """Distance horizontale à un autre point"""
        return math.sqrt((self.x - autre.x)**2 + (self.y - autre.y)**2)
    
    def distance_3d(self, autre):
        """Distance 3D à un autre point"""
        return math.sqrt((self.x - autre.x)**2 + (self.y - autre.y)**2 + (self.z - autre.z)**2)
    
    def __repr__(self):
        if self.pm is not None:
            return f"Point(X={self.x:.3f}, Y={self.y:.3f}, Z={self.z:.3f}, PM={self.pm:.3f})"
        return f"Point(X={self.x:.3f}, Y={self.y:.3f}, Z={self.z:.3f})"
    
    def __eq__(self, autre):
        if not isinstance(autre, Point):
            return False
        return (abs(self.x - autre.x) < 1e-6 and 
                abs(self.y - autre.y) < 1e-6 and 
                abs(self.z - autre.z) < 1e-6)


class Vecteur:
    """Vecteur 2D pour calculs géométriques"""
    
    def __init__(self, dx, dy):
        self.dx = float(dx)
        self.dy = float(dy)
    
    @classmethod
    def entre_points(cls, p1, p2):
        """Crée un vecteur entre deux points"""
        return cls(p2.x - p1.x, p2.y - p1.y)
    
    @classmethod
    def depuis_gisement(cls, gisement_grades, longueur=1.0):
        """Crée un vecteur depuis un gisement en grades"""
        angle_rad = gisement_grades * math.pi / 200  # Conversion grades -> radians
        # Convention topographique : Nord = 0, sens horaire
        dx = longueur * math.sin(angle_rad)
        dy = longueur * math.cos(angle_rad)
        return cls(dx, dy)
    
    def norme(self):
        """Longueur du vecteur"""
        return math.sqrt(self.dx**2 + self.dy**2)
    
    def gisement(self):
        """
        Gisement en grades (0-400g)
        
        Convention topographique française :
        - Nord = 0g
        - Sens horaire (Est = 100g, Sud = 200g, Ouest = 300g)
        - Utilise math.atan2() pour gestion correcte des 4 cadrans
        
        Returns:
            float: Gisement en grades [0-400[
        """
        # Cas particulier : vecteur nul
        if self.dx == 0 and self.dy == 0:
            return 0.0
        
        # Convention topo : Nord = 0, sens horaire
        # math.atan2(y,x) standard → math.atan2(dx,dy) pour Nord=0
        angle_rad = math.atan2(self.dx, self.dy)  
        angle_grades = angle_rad * 200 / math.pi  # Conversion rad → grades 
        
        # Normalisation [0-400[
        return angle_grades % 400
    
    def normalise(self):
        """Retourne vecteur unitaire"""
        n = self.norme()
        if n == 0:
            return Vecteur(0, 0)
        return Vecteur(self.dx/n, self.dy/n)
    
    def perpendiculaire(self, sens_trigo=True):
        """Retourne le vecteur perpendiculaire"""
        if sens_trigo:
            return Vecteur(-self.dy, self.dx)  # Rotation 90° sens trigo
        else:
            return Vecteur(self.dy, -self.dx)  # Rotation -90°
    
    def produit_scalaire(self, autre):
        """Produit scalaire avec un autre vecteur"""
        return self.dx * autre.dx + self.dy * autre.dy
    
    def produit_vectoriel_2d(self, autre):
        """Produit vectoriel 2D (retourne un scalaire)"""
        return self.dx * autre.dy - self.dy * autre.dx
    
    def __repr__(self):
        return f"Vecteur(dx={self.dx:.3f}, dy={self.dy:.3f}, gis={self.gisement():.4f}g)"


def convertir_grades_degres(grades):
    """Convertit des grades en degrés décimaux"""
    return grades * 0.9


def convertir_degres_grades(degres):
    """Convertit des degrés décimaux en grades"""
    return degres / 0.9


def normaliser_gisement(gisement):
    """
    Normalise un gisement dans l'intervalle [0, 400[
    
    Args:
        gisement: Gisement en grades (peut être négatif ou > 400)
        
    Returns:
        float: Gisement normalisé [0-400[
    """
    return gisement % 400


def gisement_inverse(gisement):
    """
    Calcule le gisement inverse (opposé)
    
    Args:
        gisement: Gisement en grades
        
    Returns:
        float: Gisement inverse (+200g modulo 400g)
    """
    return (gisement + 200) % 400


def difference_gisements(g1, g2):
    """
    Calcule la différence angulaire minimale entre deux gisements
    
    Args:
        g1, g2: Gisements en grades
        
    Returns:
        float: Différence minimale [0-200g]
    """
    # Normaliser les gisements
    g1_norm = g1 % 400
    g2_norm = g2 % 400
    
    # Calculer la différence directe
    diff_directe = abs(g1_norm - g2_norm)
    
    # Calculer la différence en passant par 0/400
    diff_par_zero = 400 - diff_directe
    
    # Retourner la plus petite des deux
    return min(diff_directe, diff_par_zero)


def gisement_depuis_coordonnees(x1, y1, x2, y2):
    """
    Calcule le gisement entre deux points
    
    Args:
        x1, y1: Coordonnées point de départ
        x2, y2: Coordonnées point d'arrivée
        
    Returns:
        float: Gisement en grades
    """
    dx = x2 - x1
    dy = y2 - y1
    
    if dx == 0 and dy == 0:
        return 0.0
    
    angle_rad = math.atan2(dx, dy)
    return (angle_rad * 200 / math.pi) % 400


def valider_gisement(gisement, tolerance=1e-6):
    """
    Valide un gisement calculé
    
    Args:
        gisement: Gisement à valider  
        tolerance: Tolérance numérique
        
    Returns:
        tuple: (bool, str) - (valide, message)
    """
    if not isinstance(gisement, (int, float)):
        return False, "Gisement doit être numérique"
    
    if math.isnan(gisement) or math.isinf(gisement):
        return False, "Gisement invalide (NaN ou infini)"
    
    if gisement < -tolerance or gisement >= 400 + tolerance:
        return False, f"Gisement hors limites: {gisement:.6f}g"
    
    return True, "OK"


def convertir_degres_grades(degres):
    """Convertit des degrés en grades"""
    return degres / 0.9


def convertir_grades_radians(grades):
    """Convertit des grades en radians"""
    return grades * math.pi / 200


def convertir_radians_grades(radians):
    """Convertit des radians en grades"""
    return radians * 200 / math.pi