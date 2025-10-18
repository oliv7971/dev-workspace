"""
Module transformations - Transformations de coordonnées et conversions
"""

import math
import numpy as np
import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from core.geometrie import Point, Vecteur


class TransformationCoordonnees:
    """Gestionnaire des transformations de coordonnées"""
    
    def __init__(self):
        self.parametres_helmert = None
        self.grille_transformation = None
    
    def transformation_helmert_2d(self, points_origine, points_cible):
        """
        Calcule une transformation de Helmert 2D (4 paramètres)
        
        Args:
            points_origine: Liste de Points dans le système origine
            points_cible: Liste de Points dans le système cible
            
        Returns:
            Dictionnaire avec paramètres de transformation
        """
        if len(points_origine) != len(points_cible) or len(points_origine) < 2:
            raise ValueError("Il faut au moins 2 points correspondants")
        
        n = len(points_origine)
        
        # Matrices pour résolution
        A = np.zeros((2*n, 4))
        B = np.zeros(2*n)
        
        for i, (p_orig, p_cible) in enumerate(zip(points_origine, points_cible)):
            # Ligne X
            A[2*i] = [1, 0, p_orig.x, -p_orig.y]
            B[2*i] = p_cible.x
            
            # Ligne Y
            A[2*i+1] = [0, 1, p_orig.y, p_orig.x]
            B[2*i+1] = p_cible.y
        
        # Résolution par moindres carrés
        params = np.linalg.lstsq(A, B, rcond=None)[0]
        
        tx, ty, a, b = params
        
        # Calcul des paramètres géodésiques
        facteur_echelle = math.sqrt(a**2 + b**2)
        rotation_rad = math.atan2(b, a)
        rotation_grades = rotation_rad * 200 / math.pi
        
        self.parametres_helmert = {
            'tx': tx,
            'ty': ty,
            'facteur_echelle': facteur_echelle,
            'rotation_grades': rotation_grades,
            'a': a,
            'b': b
        }
        
        return self.parametres_helmert
    
    def appliquer_helmert_2d(self, point):
        """Applique la transformation de Helmert à un point"""
        if self.parametres_helmert is None:
            raise ValueError("Paramètres de transformation non calculés")
        
        params = self.parametres_helmert
        
        x_trans = params['tx'] + params['a'] * point.x - params['b'] * point.y
        y_trans = params['ty'] + params['b'] * point.x + params['a'] * point.y
        
        return Point(x_trans, y_trans, point.z)
    
    def transformation_helmert_3d(self, points_origine, points_cible):
        """
        Calcule une transformation de Helmert 3D (7 paramètres)
        """
        # Implémentation simplifiée - à développer
        raise NotImplementedError("Transformation 3D non implémentée")
    
    def calculer_residus(self, points_origine, points_cible):
        """
        Calcule les résidus après transformation
        
        Returns:
            Liste de (point_orig, point_cible, point_transformé, résidu_x, résidu_y, résidu_total)
        """
        if self.parametres_helmert is None:
            raise ValueError("Transformation non calculée")
        
        residus = []
        
        for p_orig, p_cible in zip(points_origine, points_cible):
            p_trans = self.appliquer_helmert_2d(p_orig)
            
            res_x = p_cible.x - p_trans.x
            res_y = p_cible.y - p_trans.y
            res_total = math.sqrt(res_x**2 + res_y**2)
            
            residus.append({
                'point_origine': p_orig,
                'point_cible': p_cible,
                'point_transforme': p_trans,
                'residu_x': res_x,
                'residu_y': res_y,
                'residu_total': res_total
            })
        
        return residus
    
    def conversion_lambert_vers_local(self, point_origine_lambert, point_origine_local, 
                                    gisement_axe_principal):
        """
        Conversion Lambert vers système local d'axe
        
        Args:
            point_origine_lambert: Point origine en Lambert
            point_origine_local: Point origine en système local (généralement PM=0)
            gisement_axe_principal: Gisement de l'axe principal en grades
        """
        # Rotation pour aligner l'axe avec l'axe local
        rotation_rad = -(gisement_axe_principal * math.pi / 200)  # Négatif pour rotation inverse
        
        cos_r = math.cos(rotation_rad)
        sin_r = math.sin(rotation_rad)
        
        def convertir_point(point_lambert):
            # Translation
            dx = point_lambert.x - point_origine_lambert.x
            dy = point_lambert.y - point_origine_lambert.y
            
            # Rotation
            x_local = cos_r * dx + sin_r * dy + point_origine_local.x
            y_local = -sin_r * dx + cos_r * dy + point_origine_local.y
            
            return Point(x_local, y_local, point_lambert.z)
        
        return convertir_point
    
    def conversion_grades_degres_radians(self, valeur, unite_source, unite_cible):
        """
        Conversion entre unités angulaires
        
        Args:
            valeur: Valeur à convertir
            unite_source: 'grades', 'degres', 'radians'
            unite_cible: 'grades', 'degres', 'radians'
        """
        # Conversion vers radians d'abord
        if unite_source == 'grades':
            val_rad = valeur * math.pi / 200
        elif unite_source == 'degres':
            val_rad = valeur * math.pi / 180
        else:  # radians
            val_rad = valeur
        
        # Conversion depuis radians
        if unite_cible == 'grades':
            return val_rad * 200 / math.pi
        elif unite_cible == 'degres':
            return val_rad * 180 / math.pi
        else:  # radians
            return val_rad
    
    def interpolation_grille(self, points_connus, valeurs, point_interpoler):
        """
        Interpolation par grille (méthode inverse de la distance)
        
        Args:
            points_connus: Liste de Points de référence
            valeurs: Liste de valeurs aux points de référence
            point_interpoler: Point où interpoler
            
        Returns:
            Valeur interpolée
        """
        if len(points_connus) != len(valeurs):
            raise ValueError("Nombre de points et valeurs différent")
        
        # Calcul des distances
        distances = [point_interpoler.distance_2d(p) for p in points_connus]
        
        # Si un point est très proche, retourner sa valeur
        min_dist = min(distances)
        if min_dist < 1e-6:
            idx = distances.index(min_dist)
            return valeurs[idx]
        
        # Interpolation par inverse de la distance (IDW)
        poids_total = 0
        valeur_ponderee = 0
        
        for dist, val in zip(distances, valeurs):
            poids = 1 / (dist ** 2)  # Puissance 2
            poids_total += poids
            valeur_ponderee += poids * val
        
        return valeur_ponderee / poids_total if poids_total > 0 else 0
    
    def calcul_surface_triangle(self, p1, p2, p3):
        """Calcule la surface d'un triangle défini par 3 points"""
        # Formule du déterminant
        surface = 0.5 * abs(
            (p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)
        )
        return surface
    
    def point_dans_triangle(self, point, p1, p2, p3):
        """Teste si un point est dans un triangle"""
        # Méthode des aires
        aire_totale = self.calcul_surface_triangle(p1, p2, p3)
        
        aire1 = self.calcul_surface_triangle(point, p2, p3)
        aire2 = self.calcul_surface_triangle(p1, point, p3)
        aire3 = self.calcul_surface_triangle(p1, p2, point)
        
        # Point dans le triangle si somme des sous-aires = aire totale
        return abs((aire1 + aire2 + aire3) - aire_totale) < 1e-10