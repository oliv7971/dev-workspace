#!/usr/bin/env python3
"""
Implémentation améliorée des clothoïdes avec intégrales de Fresnel
Classe ClothoidePrecise pour remplacer l'approximation actuelle
"""
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scipy import special
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from core.geometrie import Point
from core.elements import ElementAxe

class ClothoidePrecise(ElementAxe):
    """
    Clothoïde avec calculs précis utilisant les intégrales de Fresnel
    
    Cette implémentation remplace l'approximation linéaire par les calculs
    mathématiquement exacts basés sur les intégrales de Fresnel.
    """
    
    def __init__(self, point_debut, gisement_debut, rayon_debut, rayon_fin, longueur):
        """
        Initialise une clothoïde précise
        
        Args:
            point_debut: Point de début (Point)
            gisement_debut: Gisement initial en grades
            rayon_debut: Rayon initial (float('inf') pour alignement)
            rayon_fin: Rayon final (float('inf') pour alignement)
            longueur: Longueur de la clothoïde
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy requis pour ClothoidePrecise. pip install scipy")
        
        self.point_debut = point_debut
        self.gisement_debut = gisement_debut % 400
        self.rayon_debut = rayon_debut if abs(rayon_debut) != float('inf') else 1e10
        self.rayon_fin = rayon_fin if abs(rayon_fin) != float('inf') else 1e10
        self._longueur = longueur
        
        # Calcul du paramètre A selon le type de clothoïde
        self.A = self._calculer_parametre_A()
        
        # Sens de la clothoïde (positif ou négatif)
        self.sens = self._determiner_sens()
        
        # Validation des paramètres
        self._valider_parametres()
    
    def _calculer_parametre_A(self):
        """Calcule le paramètre A de la clothoïde"""
        if abs(self.rayon_debut) > 1e9:  # Alignement → Courbe
            return math.sqrt(abs(self.rayon_fin) * self._longueur)
        elif abs(self.rayon_fin) > 1e9:  # Courbe → Alignement
            return math.sqrt(abs(self.rayon_debut) * self._longueur)
        else:  # Courbe → Courbe
            # Formule pour transition entre deux courbes
            R1, R2, L = abs(self.rayon_debut), abs(self.rayon_fin), self._longueur
            return math.sqrt(L * R1 * R2 / abs(R2 - R1))
    
    def _determiner_sens(self):
        """Détermine le sens de la clothoïde (+1 ou -1)"""
        # Logique simplifiée - à améliorer selon les conventions
        if self.rayon_fin < 0 or self.rayon_debut < 0:
            return -1
        return 1
    
    def _valider_parametres(self):
        """Valide les paramètres de la clothoïde"""
        if self.A <= 0:
            raise ValueError(f"Paramètre A invalide: {self.A}")
        if self._longueur <= 0:
            raise ValueError(f"Longueur invalide: {self._longueur}")
    
    def longueur(self):
        """Retourne la longueur de la clothoïde"""
        return self._longueur
    
    def point_at_distance(self, distance):
        """
        Calcule un point à une distance donnée sur la clothoïde
        Utilise les intégrales de Fresnel pour un calcul exact
        
        Args:
            distance: Distance curviligne depuis le début
            
        Returns:
            Point: Coordonnées du point
        """
        if distance < 0 or distance > self._longueur:
            raise ValueError(f"Distance {distance} hors limites [0, {self._longueur}]")
        
        if distance == 0:
            return Point(self.point_debut.x, self.point_debut.y, self.point_debut.z)
        
        # Paramètre normalisé pour les intégrales de Fresnel
        u = distance * math.sqrt(math.pi / (2 * self.A * self.A))
        
        # Intégrales de Fresnel
        S_fresnel, C_fresnel = special.fresnel(u)
        
        # Coordonnées locales de la clothoïde (repère local)
        x_local = self.A * math.sqrt(2 / math.pi) * C_fresnel * self.sens
        y_local = self.A * math.sqrt(2 / math.pi) * S_fresnel
        
        # Transformation vers le repère global
        x_global, y_global = self._transformation_repere_global(x_local, y_local)
        
        # Interpolation de l'altitude
        z_global = self.point_debut.z + distance * 0.02  # Pente 2% par défaut
        
        return Point(x_global, y_global, z_global)
    
    def gisement_at_distance(self, distance):
        """
        Calcule le gisement à une distance donnée
        Formule exacte : θ(s) = s²/(2A²)
        
        Args:
            distance: Distance curviligne
            
        Returns:
            float: Gisement en grades
        """
        if distance == 0:
            return self.gisement_debut
        
        # Variation angulaire exacte
        theta_rad = distance * distance / (2 * self.A * self.A) * self.sens
        theta_grades = theta_rad * 200 / math.pi
        
        return (self.gisement_debut + theta_grades) % 400
    
    def _transformation_repere_global(self, x_local, y_local):
        """
        Transforme les coordonnées locales vers le repère global
        
        Args:
            x_local, y_local: Coordonnées dans le repère de la clothoïde
            
        Returns:
            tuple: (x_global, y_global)
        """
        # Angle de rotation = gisement de début
        gis_rad = self.gisement_debut * math.pi / 200
        cos_gis = math.cos(gis_rad)
        sin_gis = math.sin(gis_rad)
        
        # Rotation + translation
        x_global = self.point_debut.x + x_local * sin_gis - y_local * cos_gis
        y_global = self.point_debut.y + x_local * cos_gis + y_local * sin_gis
        
        return x_global, y_global
    
    def projeter_point(self, point):
        """
        Projette un point sur la clothoïde
        Utilise une recherche par dichotomie pour trouver le point le plus proche
        
        Args:
            point: Point à projeter
            
        Returns:
            tuple: (distance_sur_clothoide, deport)
        """
        def distance_au_point(s):
            """Distance entre un point de la clothoïde et le point à projeter"""
            try:
                pt_clothoide = self.point_at_distance(s)
                return point.distance_2d(pt_clothoide)
            except ValueError:
                return float('inf')
        
        # Recherche par dichotomie
        s_min, s_max = 0, self._longueur
        tolerance = 1e-6
        
        while s_max - s_min > tolerance:
            s1 = s_min + (s_max - s_min) / 3
            s2 = s_max - (s_max - s_min) / 3
            
            if distance_au_point(s1) < distance_au_point(s2):
                s_max = s2
            else:
                s_min = s1
        
        s_optimal = (s_min + s_max) / 2
        
        # Point projeté et calcul du déport
        pt_proj = self.point_at_distance(s_optimal)
        
        # Déport avec signe (positif à droite)
        gisement_local = self.gisement_at_distance(s_optimal)
        gis_perp_rad = (gisement_local + 100) * math.pi / 200  # Perpendiculaire droite
        
        # Vecteur point projeté → point externe
        dx = point.x - pt_proj.x
        dy = point.y - pt_proj.y
        
        # Projection sur la perpendiculaire (produit scalaire)
        deport = dx * math.sin(gis_perp_rad) + dy * math.cos(gis_perp_rad)
        
        return s_optimal, deport
    
    def courbure_at_distance(self, distance):
        """
        Calcule la courbure à une distance donnée
        κ(s) = s / A²
        
        Args:
            distance: Distance curviligne
            
        Returns:
            float: Courbure en 1/m
        """
        if distance == 0:
            return 0.0
        return distance / (self.A * self.A) * self.sens
    
    def rayon_at_distance(self, distance):
        """
        Calcule le rayon de courbure à une distance donnée
        R(s) = A² / s
        
        Args:
            distance: Distance curviligne
            
        Returns:
            float: Rayon en mètres (peut être infini)
        """
        if distance == 0:
            return float('inf')
        return abs(self.A * self.A / distance)
    
    def proprietes_geometriques(self):
        """
        Retourne les propriétés géométriques de la clothoïde
        
        Returns:
            dict: Propriétés (A, longueur, rayons, angles, etc.)
        """
        return {
            'parametre_A': self.A,
            'longueur': self._longueur,
            'rayon_debut': self.rayon_debut if abs(self.rayon_debut) < 1e9 else float('inf'),
            'rayon_fin': self.rayon_fin if abs(self.rayon_fin) < 1e9 else float('inf'),
            'gisement_debut': self.gisement_debut,
            'gisement_fin': self.gisement_at_distance(self._longueur),
            'deviation_totale': (self.gisement_at_distance(self._longueur) - self.gisement_debut) % 400,
            'courbure_max': self.courbure_at_distance(self._longueur),
            'sens': 'droite' if self.sens > 0 else 'gauche'
        }

def test_clothoide_precise():
    """Test de la clothoïde précise"""
    print("=" * 80)
    print("🧪 TEST DE LA CLOTHOÏDE PRÉCISE")
    print("=" * 80)
    
    if not SCIPY_AVAILABLE:
        print("❌ Module scipy non disponible")
        print("   pip install scipy pour utiliser ClothoidePrecise")
        return
    
    try:
        # Créer une clothoïde de test
        clothoide = ClothoidePrecise(
            point_debut=Point(1000, 2000, 100),
            gisement_debut=50.0,
            rayon_debut=float('inf'),
            rayon_fin=200.0,
            longueur=100.0
        )
        
        print("✅ Clothoïde créée avec succès")
        
        # Propriétés
        props = clothoide.proprietes_geometriques()
        print(f"\n📊 PROPRIÉTÉS GÉOMÉTRIQUES:")
        print(f"   Paramètre A: {props['parametre_A']:.2f}")
        print(f"   Longueur: {props['longueur']:.0f}m")
        print(f"   Rayon début: {props['rayon_debut']}")
        print(f"   Rayon fin: {props['rayon_fin']:.0f}m")
        print(f"   Déviation totale: {props['deviation_totale']:.2f}g")
        print(f"   Sens: {props['sens']}")
        
        # Test de points
        print(f"\n📍 POINTS SUR LA CLOTHOÏDE:")
        print(f"{'Distance':<10} {'X':<12} {'Y':<12} {'Z':<10} {'Gisement':<12} {'Courbure'}")
        print("-" * 75)
        
        for d in [0, 25, 50, 75, 100]:
            try:
                pt = clothoide.point_at_distance(d)
                gis = clothoide.gisement_at_distance(d)
                courbure = clothoide.courbure_at_distance(d)
                
                print(f"{d:<10.0f} {pt.x:<12.3f} {pt.y:<12.3f} {pt.z:<10.2f} "
                      f"{gis:<12.3f} {courbure:<12.6f}")
            except Exception as e:
                print(f"{d:<10.0f} Erreur: {e}")
        
        # Test de projection
        print(f"\n🎯 TEST DE PROJECTION:")
        point_externe = Point(1050, 2050, 105)
        distance, deport = clothoide.projeter_point(point_externe)
        
        print(f"Point externe: ({point_externe.x}, {point_externe.y}, {point_externe.z})")
        print(f"Distance sur clothoïde: {distance:.3f}m")
        print(f"Déport: {deport:.3f}m ({'droite' if deport > 0 else 'gauche'})")
        
        pt_proj = clothoide.point_at_distance(distance)
        print(f"Point projeté: ({pt_proj.x:.3f}, {pt_proj.y:.3f}, {pt_proj.z:.3f})")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    test_clothoide_precise()