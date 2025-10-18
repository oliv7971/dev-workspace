"""
Tests unitaires pour le module géométrie
"""

import unittest
import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from core.geometrie import Point, Vecteur, convertir_grades_degres, convertir_degres_grades
from config import get_config


class TestPoint(unittest.TestCase):
    """Tests pour la classe Point"""
    
    def setUp(self):
        self.config = get_config()
    
    def test_creation_point_2d(self):
        """Test création point 2D"""
        p = Point(100, 200)
        self.assertEqual(p.x, 100)
        self.assertEqual(p.y, 200)
        self.assertEqual(p.z, 0.0)
        self.assertIsNone(p.pm)
    
    def test_creation_point_3d(self):
        """Test création point 3D avec PM"""
        p = Point(100, 200, 50, pm=150.5)
        self.assertEqual(p.x, 100)
        self.assertEqual(p.y, 200)
        self.assertEqual(p.z, 50)
        self.assertEqual(p.pm, 150.5)
    
    def test_distance_2d(self):
        """Test calcul distance 2D"""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        distance = p1.distance_2d(p2)
        self.assertAlmostEqual(distance, 5.0, places=6)
    
    def test_distance_3d(self):
        """Test calcul distance 3D"""
        p1 = Point(0, 0, 0)
        p2 = Point(3, 4, 12)
        distance = p1.distance_3d(p2)
        self.assertAlmostEqual(distance, 13.0, places=6)
    
    def test_egalite_points(self):
        """Test égalité de points"""
        p1 = Point(100.0, 200.0, 50.0)
        p2 = Point(100.0, 200.0, 50.0)
        p3 = Point(100.1, 200.0, 50.0)
        
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)
    
    def test_representation(self):
        """Test représentation string"""
        p1 = Point(100, 200, 50)
        p2 = Point(100, 200, 50, pm=150)
        
        self.assertIn("X=100.000", str(p1))
        self.assertIn("PM=150.000", str(p2))


class TestVecteur(unittest.TestCase):
    """Tests pour la classe Vecteur"""
    
    def test_creation_vecteur(self):
        """Test création vecteur"""
        v = Vecteur(3, 4)
        self.assertEqual(v.dx, 3)
        self.assertEqual(v.dy, 4)
    
    def test_vecteur_entre_points(self):
        """Test création vecteur entre points"""
        p1 = Point(10, 20)
        p2 = Point(13, 24)
        v = Vecteur.entre_points(p1, p2)
        
        self.assertEqual(v.dx, 3)
        self.assertEqual(v.dy, 4)
    
    def test_norme_vecteur(self):
        """Test calcul norme"""
        v = Vecteur(3, 4)
        self.assertAlmostEqual(v.norme(), 5.0, places=6)
    
    def test_vecteur_depuis_gisement(self):
        """Test création vecteur depuis gisement"""
        # Gisement 0g = Nord (dy=1, dx=0)
        v1 = Vecteur.depuis_gisement(0, 1)
        self.assertAlmostEqual(v1.dx, 0, places=6)
        self.assertAlmostEqual(v1.dy, 1, places=6)
        
        # Gisement 100g = Est (dy=0, dx=1)
        v2 = Vecteur.depuis_gisement(100, 1)
        self.assertAlmostEqual(v2.dx, 1, places=6)
        self.assertAlmostEqual(v2.dy, 0, places=6)
    
    def test_gisement_vecteur(self):
        """Test calcul gisement"""
        # Vecteur vers Nord
        v1 = Vecteur(0, 1)
        self.assertAlmostEqual(v1.gisement(), 0, places=3)
        
        # Vecteur vers Est
        v2 = Vecteur(1, 0)
        self.assertAlmostEqual(v2.gisement(), 100, places=3)
        
        # Vecteur vers Sud
        v3 = Vecteur(0, -1)
        self.assertAlmostEqual(v3.gisement(), 200, places=3)
    
    def test_normalisation(self):
        """Test normalisation vecteur"""
        v = Vecteur(3, 4)
        vn = v.normalise()
        
        self.assertAlmostEqual(vn.norme(), 1.0, places=6)
        self.assertAlmostEqual(vn.dx, 0.6, places=6)
        self.assertAlmostEqual(vn.dy, 0.8, places=6)
    
    def test_perpendiculaire(self):
        """Test vecteur perpendiculaire"""
        v = Vecteur(1, 0)  # Vers Est
        
        # Perpendiculaire sens trigo (vers Nord)
        vp1 = v.perpendiculaire(sens_trigo=True)
        self.assertAlmostEqual(vp1.dx, 0, places=6)
        self.assertAlmostEqual(vp1.dy, 1, places=6)
        
        # Perpendiculaire sens horaire (vers Sud)
        vp2 = v.perpendiculaire(sens_trigo=False)
        self.assertAlmostEqual(vp2.dx, 0, places=6)
        self.assertAlmostEqual(vp2.dy, -1, places=6)
    
    def test_produits_scalaire_vectoriel(self):
        """Test produits scalaire et vectoriel"""
        v1 = Vecteur(2, 3)
        v2 = Vecteur(4, 5)
        
        # Produit scalaire : 2*4 + 3*5 = 23
        self.assertEqual(v1.produit_scalaire(v2), 23)
        
        # Produit vectoriel : 2*5 - 3*4 = -2
        self.assertEqual(v1.produit_vectoriel_2d(v2), -2)


class TestConversionsAngulaires(unittest.TestCase):
    """Tests pour les conversions d'angles"""
    
    def test_grades_degres(self):
        """Test conversion grades <-> degrés"""
        # 400g = 360°
        self.assertAlmostEqual(convertir_grades_degres(400), 360, places=6)
        self.assertAlmostEqual(convertir_degres_grades(360), 400, places=6)
        
        # 100g = 90°
        self.assertAlmostEqual(convertir_grades_degres(100), 90, places=6)
        self.assertAlmostEqual(convertir_degres_grades(90), 100, places=6)
    
    def test_grades_radians(self):
        """Test conversion grades <-> radians"""
        import math
        from core.geometrie import convertir_grades_radians, convertir_radians_grades
        
        # 400g = 2π rad
        self.assertAlmostEqual(convertir_grades_radians(400), 2*math.pi, places=6)
        self.assertAlmostEqual(convertir_radians_grades(2*math.pi), 400, places=6)
        
        # 200g = π rad
        self.assertAlmostEqual(convertir_grades_radians(200), math.pi, places=6)
        self.assertAlmostEqual(convertir_radians_grades(math.pi), 200, places=6)


if __name__ == '__main__':
    unittest.main()