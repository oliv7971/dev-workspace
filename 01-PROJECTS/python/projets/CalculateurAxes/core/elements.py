"""
Module elements - Éléments géométriques d'axe
"""

from abc import ABC, abstractmethod
import math
import numpy as np
from .geometrie import Point, Vecteur


class ElementAxe(ABC):
    """Classe abstraite pour tous les éléments d'axe"""
    
    @abstractmethod
    def longueur(self):
        """Longueur de l'élément"""
        pass
    
    @abstractmethod
    def point_at_distance(self, distance):
        """Calcule un point à une distance donnée depuis le début"""
        pass
    
    @abstractmethod
    def projeter_point(self, point):
        """Projette un point sur l'élément, retourne (distance, déport)"""
        pass
    
    @abstractmethod
    def gisement_at_distance(self, distance):
        """Gisement à une distance donnée"""
        pass


class AlignementDroit(ElementAxe):
    """Alignement droit entre deux points"""
    
    def __init__(self, debut, fin):
        self.debut = debut
        self.fin = fin
        self.vecteur = Vecteur.entre_points(debut, fin)
        self._longueur = self.vecteur.norme()
        self.gisement = self.vecteur.gisement()
    
    def longueur(self):
        return self._longueur
    
    def point_at_distance(self, distance):
        """Point à une distance donnée sur l'alignement"""
        if distance < 0 or distance > self._longueur:
            raise ValueError(f"Distance {distance} hors limites [0, {self._longueur}]")
        
        if self._longueur == 0:
            return Point(self.debut.x, self.debut.y, self.debut.z)
        
        ratio = distance / self._longueur
        x = self.debut.x + ratio * self.vecteur.dx
        y = self.debut.y + ratio * self.vecteur.dy
        
        # Interpolation Z si disponible
        z = self.debut.z
        if hasattr(self.fin, 'z'):
            z = self.debut.z + ratio * (self.fin.z - self.debut.z)
        
        return Point(x, y, z)
    
    def gisement_at_distance(self, distance):
        """Gisement constant sur un alignement"""
        return self.gisement
    
    def projeter_point(self, point):
        """Projette un point sur l'alignement"""
        if self._longueur == 0:
            return 0.0, point.distance_2d(self.debut)
        
        # Vecteur debut->point
        vp = Vecteur.entre_points(self.debut, point)
        
        # Produit scalaire pour projection
        v_norm = self.vecteur.normalise()
        distance = vp.produit_scalaire(v_norm)
        
        # Limiter à l'alignement
        distance = max(0, min(distance, self._longueur))
        
        # Point projeté
        pt_proj = self.point_at_distance(distance)
        
        # Déport (positif à droite selon convention topographique)
        vp_proj = Vecteur.entre_points(pt_proj, point)
        v_perp = v_norm.perpendiculaire(sens_trigo=False)  # Perpendiculaire à droite
        deport = vp_proj.produit_scalaire(v_perp)
        
        return distance, deport


class Arc(ElementAxe):
    """Arc circulaire"""
    
    def __init__(self, centre, rayon, angle_debut, angle_fin):
        self.centre = centre
        self.rayon_signe = rayon  # Garde le signe pour le sens
        self.rayon = abs(rayon)  # Rayon toujours positif pour calculs
        self.sens = 1 if rayon > 0 else -1  # Sens: +1=droite, -1=gauche
        self.angle_debut = angle_debut % 400  # En grades
        self.angle_fin = angle_fin % 400
        
        # Calcul de la déviation
        self.deviation = (angle_fin - angle_debut) % 400
        if self.sens < 0:
            self.deviation = 400 - self.deviation
            
        self._longueur = self.rayon * self.deviation * math.pi / 200
    
    def longueur(self):
        return self._longueur
    
    def point_at_distance(self, distance):
        """Point à une distance donnée sur l'arc"""
        if distance < 0 or distance > self._longueur:
            raise ValueError(f"Distance {distance} hors limites [0, {self._longueur:.3f}]")
        
        if self._longueur == 0:
            # Arc de longueur nulle
            angle_rad = self.angle_debut * math.pi / 200
            x = self.centre.x + self.rayon * math.sin(angle_rad)
            y = self.centre.y + self.rayon * math.cos(angle_rad)
            return Point(x, y, self.centre.z)
        
        # Angle parcouru
        angle_parcouru = (distance / self._longueur) * self.deviation
        if self.sens < 0:
            angle_parcouru = -angle_parcouru
            
        angle = self.angle_debut + angle_parcouru
        angle_rad = angle * math.pi / 200
        
        x = self.centre.x + self.rayon * math.sin(angle_rad)
        y = self.centre.y + self.rayon * math.cos(angle_rad)
        
        return Point(x, y, self.centre.z)
    
    def gisement_at_distance(self, distance):
        """Gisement à une distance donnée sur l'arc"""
        if self._longueur == 0:
            return self.angle_debut
        
        # Angle parcouru
        angle_parcouru = (distance / self._longueur) * self.deviation
        if self.sens < 0:
            angle_parcouru = -angle_parcouru
            
        # Gisement = angle au centre + 90° (tangente)
        angle_centre = self.angle_debut + angle_parcouru
        gisement = (angle_centre + 100 * self.sens) % 400  # +100g ou -100g selon le sens
        
        return gisement
    
    def projeter_point(self, point):
        """Projette un point sur l'arc"""
        # Vecteur centre->point
        vc = Vecteur.entre_points(self.centre, point)
        distance_centre = vc.norme()
        
        if distance_centre == 0:
            # Point confondu avec le centre
            return 0.0, self.rayon
        
        # Angle du point par rapport au centre
        angle_point = vc.gisement()
        
        # Trouver l'angle le plus proche sur l'arc
        angle_debut = self.angle_debut
        angle_fin = self.angle_fin
        
        # Normaliser les angles pour la comparaison
        if self.sens > 0:
            # Arc dans le sens direct
            if angle_fin < angle_debut:
                angle_fin += 400
            if angle_point < angle_debut:
                angle_point += 400
        else:
            # Arc dans le sens indirect
            if angle_debut < angle_fin:
                angle_debut += 400
            if angle_point < angle_fin:
                angle_point += 400
        
        # Projeter sur l'arc
        if self.sens > 0:
            angle_proj = max(angle_debut, min(angle_point, angle_fin))
        else:
            angle_proj = max(angle_fin, min(angle_point, angle_debut))
        
        # Convertir en distance sur l'arc
        angle_parcouru = abs(angle_proj - angle_debut) % 400
        if self.sens < 0:
            angle_parcouru = 400 - angle_parcouru
        
        distance = (angle_parcouru / self.deviation) * self._longueur if self.deviation > 0 else 0
        distance = max(0, min(distance, self._longueur))
        
        # Déport = différence de rayon
        deport = distance_centre - self.rayon
        
        return distance, deport


class Clothoide(ElementAxe):
    """Clothoïde (spirale de transition)"""
    
    def __init__(self, point_debut, gisement_debut, rayon_debut, rayon_fin, longueur):
        self.point_debut = point_debut
        self.gisement_debut = gisement_debut % 400
        self.rayon_debut = rayon_debut if abs(rayon_debut) != float('inf') else 1e10
        self.rayon_fin = rayon_fin if abs(rayon_fin) != float('inf') else 1e10
        self._longueur = longueur
        
        # Paramètre de la clothoïde A² = R × L
        if abs(self.rayon_debut) > 1e9:  # Rayon infini (alignement)
            self.A = math.sqrt(abs(self.rayon_fin) * self._longueur)
        elif abs(self.rayon_fin) > 1e9:  # Vers alignement
            self.A = math.sqrt(abs(self.rayon_debut) * self._longueur)
        else:
            # Entre deux courbes - formule plus complexe
            self.A = math.sqrt(self._longueur * abs(self.rayon_debut * self.rayon_fin) / 
                             abs(self.rayon_fin - self.rayon_debut))
    
    def longueur(self):
        return self._longueur
    
    def point_at_distance(self, distance):
        """Point à une distance donnée sur la clothoïde (approximation)"""
        # Implémentation simplifiée - à améliorer avec les intégrales de Fresnel
        if distance < 0 or distance > self._longueur:
            raise ValueError(f"Distance {distance} hors limites")
        
        # Approximation linéaire pour l'instant
        ratio = distance / self._longueur
        
        # Changement de courbure linéaire
        courbure_debut = 1/self.rayon_debut if abs(self.rayon_debut) < 1e9 else 0
        courbure_fin = 1/self.rayon_fin if abs(self.rayon_fin) < 1e9 else 0
        courbure = courbure_debut + ratio * (courbure_fin - courbure_debut)
        
        # Calcul approximatif du point (à améliorer)
        gis_rad = self.gisement_debut * math.pi / 200
        x = self.point_debut.x + distance * math.sin(gis_rad)
        y = self.point_debut.y + distance * math.cos(gis_rad)
        
        return Point(x, y, self.point_debut.z)
    
    def gisement_at_distance(self, distance):
        """Gisement à une distance donnée (approximation)"""
        # Variation de gisement due à la courbure variable
        # Approximation : variation quadratique
        ratio = distance / self._longueur
        
        courbure_debut = 1/self.rayon_debut if abs(self.rayon_debut) < 1e9 else 0
        courbure_fin = 1/self.rayon_fin if abs(self.rayon_fin) < 1e9 else 0
        
        # Variation approximative du gisement
        variation = 0.5 * distance * (courbure_debut + ratio * (courbure_fin - courbure_debut))
        variation_grades = variation * 200 / math.pi
        
        return (self.gisement_debut + variation_grades) % 400
    
    def projeter_point(self, point):
        """Projection approximative sur clothoïde"""
        # Implémentation simplifiée - recherche par dichotomie
        meilleure_distance = None
        meilleur_ecart = float('inf')
        
        # Recherche par pas
        pas = self._longueur / 100
        for i in range(101):
            d = i * pas
            try:
                pt = self.point_at_distance(d)
                ecart = point.distance_2d(pt)
                if ecart < meilleur_ecart:
                    meilleur_ecart = ecart
                    meilleure_distance = d
            except ValueError:
                continue
        
        # Affiner par dichotomie autour du meilleur point
        if meilleure_distance is not None:
            # Déport approximatif
            pt_proj = self.point_at_distance(meilleure_distance)
            deport = point.distance_2d(pt_proj)  # Simplification
            return meilleure_distance, deport
        
        return 0.0, point.distance_2d(self.point_debut)