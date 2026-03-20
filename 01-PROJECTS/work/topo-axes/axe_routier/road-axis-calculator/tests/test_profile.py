import unittest
import math
from src.models.profile import (LineProfile, CircularVerticalCurve, 
                                 ParabolicVerticalCurve, VerticalProfile)


class TestLineProfile(unittest.TestCase):
    def test_line_profile_horizontal(self):
        """Test d'un profil horizontal (pente 0%)"""
        line = LineProfile(
            start_station=0,
            start_elevation=100.0,
            end_station=100,
            end_elevation=100.0
        )
        self.assertAlmostEqual(line.length(), 100.0)
        self.assertAlmostEqual(line.elevation_at(50), 100.0)
        self.assertAlmostEqual(line.slope_at(50), 0.0)
        self.assertAlmostEqual(line.slope_percent(), 0.0)
    
    def test_line_profile_ascending(self):
        """Test d'un profil montant (pente +5%)"""
        line = LineProfile(
            start_station=0,
            start_elevation=100.0,
            end_station=100,
            end_elevation=105.0  # +5m sur 100m = 5%
        )
        self.assertAlmostEqual(line.length(), 100.0)
        self.assertAlmostEqual(line.elevation_at(0), 100.0)
        self.assertAlmostEqual(line.elevation_at(50), 102.5)
        self.assertAlmostEqual(line.elevation_at(100), 105.0)
        self.assertAlmostEqual(line.slope_percent(), 5.0)
    
    def test_line_profile_descending(self):
        """Test d'un profil descendant (pente -3%)"""
        line = LineProfile(
            start_station=0,
            start_elevation=100.0,
            end_station=100,
            end_elevation=97.0  # -3m sur 100m = -3%
        )
        self.assertAlmostEqual(line.slope_percent(), -3.0)
        self.assertAlmostEqual(line.elevation_at(50), 98.5)


class TestCircularVerticalCurve(unittest.TestCase):
    def test_vertical_curve_convex(self):
        """Test d'un raccordement convexe (sommet de côte)"""
        curve = CircularVerticalCurve(
            start_station=100,
            start_elevation=105.0,
            length=50,
            slope_in=0.05,   # +5%
            slope_out=-0.03  # -3%
        )
        self.assertAlmostEqual(curve.length(), 50.0)
        
        # Au début: altitude = 105, pente = +5%
        self.assertAlmostEqual(curve.elevation_at(0), 105.0)
        self.assertAlmostEqual(curve.slope_at(0), 0.05)
        
        # Au milieu: pente intermédiaire
        mid_slope = curve.slope_at(25)
        self.assertTrue(-0.03 < mid_slope < 0.05)
        
        # À la fin: pente = -3%
        self.assertAlmostEqual(curve.slope_at(50), -0.03, places=5)
        self.assertTrue(curve.is_convex)
    
    def test_vertical_curve_concave(self):
        """Test d'un raccordement concave (point bas)"""
        curve = CircularVerticalCurve(
            start_station=100,
            start_elevation=100.0,
            length=60,
            slope_in=-0.04,  # -4%
            slope_out=0.02   # +2%
        )
        
        # Au début: pente = -4%
        self.assertAlmostEqual(curve.slope_at(0), -0.04)
        
        # À la fin: pente = +2%
        self.assertAlmostEqual(curve.slope_at(60), 0.02, places=5)
        
        # Point le plus bas devrait être quelque part au milieu
        self.assertFalse(curve.is_convex)
    
    def test_vertical_curve_elevation_continuity(self):
        """Test de continuité des altitudes"""
        curve = CircularVerticalCurve(
            start_station=0,
            start_elevation=100.0,
            length=100,
            slope_in=0.05,
            slope_out=-0.05
        )
        
        # L'altitude doit augmenter au début puis diminuer
        z0 = curve.elevation_at(0)
        z25 = curve.elevation_at(25)
        z50 = curve.elevation_at(50)
        z75 = curve.elevation_at(75)
        z100 = curve.elevation_at(100)
        
        self.assertTrue(z25 > z0)
        self.assertTrue(z50 > z25)


class TestParabolicVerticalCurve(unittest.TestCase):
    def test_parabolic_curve_basic(self):
        """Test d'une parabole de base"""
        parabola = ParabolicVerticalCurve(
            start_station=0,
            start_elevation=100.0,
            length=100,
            slope_in=0.04,   # +4%
            slope_out=-0.02  # -2%
        )
        
        self.assertAlmostEqual(parabola.length(), 100.0)
        self.assertAlmostEqual(parabola.elevation_at(0), 100.0)
        self.assertAlmostEqual(parabola.slope_at(0), 0.04)
        self.assertAlmostEqual(parabola.slope_at(100), -0.02, places=5)
    
    def test_parabolic_vs_circular(self):
        """Comparaison parabole vs arc circulaire (doivent être similaires)"""
        params = {
            'start_station': 0,
            'start_elevation': 100.0,
            'length': 100,
            'slope_in': 0.05,
            'slope_out': -0.03
        }
        
        circular = CircularVerticalCurve(**params)
        parabolic = ParabolicVerticalCurve(**params)
        
        # Les deux méthodes doivent donner des résultats très proches
        for s in [0, 25, 50, 75, 100]:
            elev_c = circular.elevation_at(s)
            elev_p = parabolic.elevation_at(s)
            # Différence doit être minime
            self.assertAlmostEqual(elev_c, elev_p, places=5)


class TestVerticalProfile(unittest.TestCase):
    def setUp(self):
        """Crée un profil complet pour les tests"""
        self.profile = VerticalProfile()
        
        # Segment 1: Rampe montante de 5% sur 100m
        self.profile.add_element(LineProfile(
            start_station=0,
            start_elevation=100.0,
            end_station=100,
            end_elevation=105.0
        ))
        
        # Segment 2: Raccordement parabolique sur 50m
        self.profile.add_element(ParabolicVerticalCurve(
            start_station=100,
            start_elevation=105.0,
            length=50,
            slope_in=0.05,
            slope_out=0.0
        ))
        
        # Segment 3: Palier horizontal sur 100m
        self.profile.add_element(LineProfile(
            start_station=150,
            start_elevation=105.0 + 0.05 * 50 / 2,  # approximation
            end_station=250,
            end_elevation=105.0 + 0.05 * 50 / 2
        ))
    
    def test_total_length(self):
        """Test de la longueur totale"""
        expected = 100 + 50 + 100
        self.assertAlmostEqual(self.profile.total_length(), expected)
    
    def test_elevation_at_boundaries(self):
        """Test des altitudes aux limites"""
        # Au début
        z0 = self.profile.elevation_at(0)
        self.assertAlmostEqual(z0, 100.0)
        
        # À la fin du premier segment
        z100 = self.profile.elevation_at(100)
        self.assertAlmostEqual(z100, 105.0)
    
    def test_slope_at(self):
        """Test des pentes à différentes positions"""
        # Au début: pente = 5%
        slope0 = self.profile.slope_percent_at(10)
        self.assertAlmostEqual(slope0, 5.0)
    
    def test_get_profile_points(self):
        """Test de génération de points pour traçage"""
        points = self.profile.get_profile_points(step=25.0)
        
        # Doit avoir des points tout le long
        self.assertTrue(len(points) > 0)
        
        # Premier point doit être à station 0
        self.assertAlmostEqual(points[0][0], 0.0)
        
        # Dernier point doit être à la fin
        self.assertAlmostEqual(points[-1][0], self.profile.total_length())


class TestProfileEdgeCases(unittest.TestCase):
    def test_empty_profile(self):
        """Test d'un profil vide"""
        profile = VerticalProfile()
        self.assertEqual(profile.total_length(), 0.0)
        
        with self.assertRaises(ValueError):
            profile.elevation_at(50)
    
    def test_zero_length_element(self):
        """Test d'un élément de longueur nulle"""
        line = LineProfile(
            start_station=100,
            start_elevation=105.0,
            end_station=100,
            end_elevation=105.0
        )
        self.assertEqual(line.length(), 0.0)
        self.assertEqual(line.elevation_at(0), 105.0)


if __name__ == '__main__':
    unittest.main()
