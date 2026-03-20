"""
Tests unitaires pour les éléments d'axe
"""

import unittest
import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from core.geometrie import Point, Vecteur
from core.elements import AlignementDroit, Arc


class TestAlignementDroit(unittest.TestCase):
    """Tests pour la classe AlignementDroit"""
    
    def setUp(self):
        self.debut = Point(0, 0, 10)
        self.fin = Point(100, 0, 15)
        self.alignement = AlignementDroit(self.debut, self.fin)
    
    def test_creation_alignement(self):
        """Test création alignement droit"""
        self.assertEqual(self.alignement.debut, self.debut)
        self.assertEqual(self.alignement.fin, self.fin)
        self.assertAlmostEqual(self.alignement.longueur(), 100.0, places=6)
        self.assertAlmostEqual(self.alignement.gisement, 100.0, places=3)  # Vers Est = 100g
    
    def test_longueur_alignement(self):
        """Test calcul longueur"""
        # Alignement de 100m
        self.assertAlmostEqual(self.alignement.longueur(), 100.0, places=6)
        
        # Alignement diagonal
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        alignement_diag = AlignementDroit(p1, p2)
        self.assertAlmostEqual(alignement_diag.longueur(), 5.0, places=6)
    
    def test_point_at_distance(self):
        """Test calcul point à une distance"""
        # Point au début
        p0 = self.alignement.point_at_distance(0)
        self.assertEqual(p0.x, 0)
        self.assertEqual(p0.y, 0)
        self.assertEqual(p0.z, 10)
        
        # Point au milieu
        p50 = self.alignement.point_at_distance(50)
        self.assertEqual(p50.x, 50)
        self.assertEqual(p50.y, 0)
        self.assertEqual(p50.z, 12.5)  # Interpolation Z
        
        # Point à la fin
        p100 = self.alignement.point_at_distance(100)
        self.assertEqual(p100.x, 100)
        self.assertEqual(p100.y, 0)
        self.assertEqual(p100.z, 15)
    
    def test_point_at_distance_limites(self):
        """Test limites pour point_at_distance"""
        # Distance négative
        with self.assertRaises(ValueError):
            self.alignement.point_at_distance(-10)
        
        # Distance trop grande
        with self.assertRaises(ValueError):
            self.alignement.point_at_distance(150)
    
    def test_gisement_constant(self):
        """Test gisement constant sur alignement"""
        gis_debut = self.alignement.gisement_at_distance(0)
        gis_milieu = self.alignement.gisement_at_distance(50)
        gis_fin = self.alignement.gisement_at_distance(100)
        
        self.assertAlmostEqual(gis_debut, gis_milieu, places=6)
        self.assertAlmostEqual(gis_milieu, gis_fin, places=6)
        self.assertAlmostEqual(gis_debut, 100.0, places=3)  # Vers Est
    
    def test_projection_point(self):
        """Test projection d'un point sur alignement"""
        # Point sur l'alignement
        point_sur = Point(50, 0)
        distance, deport = self.alignement.projeter_point(point_sur)
        self.assertAlmostEqual(distance, 50.0, places=6)
        self.assertAlmostEqual(deport, 0.0, places=6)
        
        # Point à droite de l'alignement
        point_droite = Point(50, -10)  # 10m à droite (Y négatif)
        distance, deport = self.alignement.projeter_point(point_droite)
        self.assertAlmostEqual(distance, 50.0, places=6)
        self.assertAlmostEqual(deport, 10.0, places=6)  # Positif = droite
        
        # Point à gauche de l'alignement
        point_gauche = Point(50, 10)  # 10m à gauche (Y positif)
        distance, deport = self.alignement.projeter_point(point_gauche)
        self.assertAlmostEqual(distance, 50.0, places=6)
        self.assertAlmostEqual(deport, -10.0, places=6)  # Négatif = gauche


class TestArc(unittest.TestCase):
    """Tests pour la classe Arc"""
    
    def setUp(self):
        # Arc de rayon 100m, de 0g à 100g (quart de cercle)
        self.centre = Point(100, 0, 20)
        self.rayon = 100
        self.angle_debut = 0  # Nord
        self.angle_fin = 100  # Est
        self.arc = Arc(self.centre, self.rayon, self.angle_debut, self.angle_fin)
    
    def test_creation_arc(self):
        """Test création arc"""
        self.assertEqual(self.arc.centre, self.centre)
        self.assertEqual(self.arc.rayon, 100)
        self.assertEqual(self.arc.sens, 1)  # Sens direct
        self.assertAlmostEqual(self.arc.deviation, 100, places=3)
    
    def test_longueur_arc(self):
        """Test calcul longueur d'arc"""
        # Quart de cercle : L = 2πR/4 = πR/2
        import math
        longueur_theorique = math.pi * 100 / 2
        self.assertAlmostEqual(self.arc.longueur(), longueur_theorique, places=3)
    
    def test_arc_sens_inverse(self):
        """Test arc sens inverse (rayon négatif)"""
        arc_gauche = Arc(self.centre, -100, self.angle_debut, self.angle_fin)
        self.assertEqual(arc_gauche.sens, -1)
        self.assertEqual(arc_gauche.rayon, 100)  # Rayon toujours positif interne
    
    def test_point_at_distance_arc(self):
        """Test calcul point sur arc"""
        # Point au début de l'arc
        p0 = self.arc.point_at_distance(0)
        # Au début : angle 0g = Nord, donc point à (centre.x + 0, centre.y + rayon)
        self.assertAlmostEqual(p0.x, 100, places=3)
        self.assertAlmostEqual(p0.y, 100, places=3)
        
        # Point à la fin de l'arc
        longueur_totale = self.arc.longueur()
        p_fin = self.arc.point_at_distance(longueur_totale)
        # À la fin : angle 100g = Est, donc point à (centre.x + rayon, centre.y + 0)
        self.assertAlmostEqual(p_fin.x, 200, places=3)
        self.assertAlmostEqual(p_fin.y, 0, places=3)
    
    def test_gisement_variable_arc(self):
        """Test gisement variable sur arc"""
        gis_debut = self.arc.gisement_at_distance(0)
        gis_fin = self.arc.gisement_at_distance(self.arc.longueur())
        
        # Au début : tangente = angle + 90° = 0 + 100 = 100g
        self.assertAlmostEqual(gis_debut, 100, places=1)
        
        # À la fin : tangente = angle + 90° = 100 + 100 = 200g
        self.assertAlmostEqual(gis_fin, 200, places=1)
    
    def test_projection_sur_arc(self):
        """Test projection d'un point sur arc"""
        # Point proche du centre de l'arc
        point_test = Point(150, 50)  # Entre début et fin
        distance, deport = self.arc.projeter_point(point_test)
        
        # Vérifications basiques
        self.assertGreaterEqual(distance, 0)
        self.assertLessEqual(distance, self.arc.longueur())
        # Le déport peut être positif ou négatif selon la position


if __name__ == '__main__':
    unittest.main()