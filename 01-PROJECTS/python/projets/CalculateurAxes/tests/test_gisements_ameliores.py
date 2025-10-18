"""
Tests unitaires pour les utilitaires de gisements améliorés
"""

import unittest
import math
import sys
import os

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.geometrie import (
    Point, Vecteur, 
    normaliser_gisement, gisement_inverse, difference_gisements,
    gisement_depuis_coordonnees, valider_gisement,
    convertir_grades_degres, convertir_degres_grades
)


class TestGisementUtils(unittest.TestCase):
    """Tests pour les utilitaires de gisements"""
    
    def test_gisement_4_cadrans(self):
        """Test gisement dans les 4 cadrans"""
        # Directions principales
        directions = [
            (Vecteur(0, 100), 0.0),      # Nord
            (Vecteur(100, 100), 50.0),   # Nord-Est 45°
            (Vecteur(100, 0), 100.0),    # Est
            (Vecteur(100, -100), 150.0), # Sud-Est 45°
            (Vecteur(0, -100), 200.0),   # Sud
            (Vecteur(-100, -100), 250.0), # Sud-Ouest 45°
            (Vecteur(-100, 0), 300.0),   # Ouest
            (Vecteur(-100, 100), 350.0), # Nord-Ouest 45°
        ]
        
        for vecteur, gis_attendu in directions:
            with self.subTest(vecteur=vecteur):
                gis_calc = vecteur.gisement()
                self.assertAlmostEqual(gis_calc, gis_attendu, places=4)
    
    def test_normaliser_gisement(self):
        """Test normalisation gisement"""
        cas_test = [
            (0, 0),
            (100, 100),
            (400, 0),
            (450, 50),
            (-50, 350),
            (-400, 0),
            (800, 0),
        ]
        
        for entree, sortie_attendue in cas_test:
            with self.subTest(entree=entree):
                resultat = normaliser_gisement(entree)
                self.assertAlmostEqual(resultat, sortie_attendue, places=6)
    
    def test_gisement_inverse(self):
        """Test gisement inverse"""
        cas_test = [
            (0, 200),
            (50, 250), 
            (100, 300),
            (150, 350),
            (200, 0),
            (250, 50),
            (300, 100),
            (350, 150),
        ]
        
        for gis, inverse_attendu in cas_test:
            with self.subTest(gis=gis):
                inverse_calc = gisement_inverse(gis)
                self.assertAlmostEqual(inverse_calc, inverse_attendu, places=6)
    
    def test_difference_gisements(self):
        """Test différence entre gisements"""
        cas_test = [
            (0, 100, 100),
            (0, 300, 100),  # Plus court par 400
            (350, 370, 20),  # Différence simple
            (350, 10, 60),   # Passage par 0 - chemin le plus court
            (100, 300, 200),
            (0, 200, 200),
            (0, 0, 0),
        ]
        
        for g1, g2, diff_attendue in cas_test:
            with self.subTest(g1=g1, g2=g2):
                diff_calc = difference_gisements(g1, g2)
                self.assertAlmostEqual(diff_calc, diff_attendue, places=6)
    
    def test_gisement_depuis_coordonnees(self):
        """Test calcul gisement depuis coordonnées"""
        origine = (1000, 2000)
        
        cas_test = [
            ((1000, 2100), 0.0),     # Nord
            ((1100, 2100), 50.0),    # Nord-Est
            ((1100, 2000), 100.0),   # Est
            ((1100, 1900), 150.0),   # Sud-Est
            ((1000, 1900), 200.0),   # Sud
            ((900, 1900), 250.0),    # Sud-Ouest
            ((900, 2000), 300.0),    # Ouest
            ((900, 2100), 350.0),    # Nord-Ouest
        ]
        
        for (x2, y2), gis_attendu in cas_test:
            with self.subTest(destination=(x2, y2)):
                gis_calc = gisement_depuis_coordonnees(origine[0], origine[1], x2, y2)
                self.assertAlmostEqual(gis_calc, gis_attendu, places=4)
    
    def test_valider_gisement(self):
        """Test validation gisement"""
        cas_valides = [0, 100, 200, 300, 399.999]
        cas_invalides = [
            "abc",      # Non numérique
            float('nan'),  # NaN
            float('inf'),  # Infini
            -1,         # Négatif
            400.1,      # Trop grand
        ]
        
        for gis in cas_valides:
            with self.subTest(gis=gis):
                valide, msg = valider_gisement(gis)
                self.assertTrue(valide, f"Gisement {gis} devrait être valide: {msg}")
        
        for gis in cas_invalides:
            with self.subTest(gis=gis):
                valide, msg = valider_gisement(gis)
                self.assertFalse(valide, f"Gisement {gis} devrait être invalide")
    
    def test_conversions_grades_degres(self):
        """Test conversion grades ↔ degrés"""
        cas_test = [
            (0, 0),
            (100, 90),
            (200, 180),
            (300, 270),
            (400, 360),
            (50, 45),
        ]
        
        for grades, degres in cas_test:
            with self.subTest(grades=grades):
                # Grades → Degrés
                deg_calc = convertir_grades_degres(grades)
                self.assertAlmostEqual(deg_calc, degres, places=6)
                
                # Degrés → Grades (test inverse)
                grad_calc = convertir_degres_grades(degres)
                self.assertAlmostEqual(grad_calc, grades, places=6)
    
    def test_vecteur_nul(self):
        """Test cas particulier vecteur nul"""
        vecteur_nul = Vecteur(0, 0)
        gis = vecteur_nul.gisement()
        self.assertEqual(gis, 0.0)
        
        # Validation
        valide, msg = valider_gisement(gis)
        self.assertTrue(valide)
    
    def test_precision_numerique(self):
        """Test précision numérique avec valeurs très petites"""
        # Vecteurs très petits mais non nuls
        vecteurs_petits = [
            (1e-15, 1e-10),  # Nord microscopique
            (1e-10, 1e-15),  # Est microscopique  
            (-1e-15, -1e-10), # Sud microscopique
            (-1e-10, -1e-15), # Ouest microscopique
        ]
        
        for dx, dy in vecteurs_petits:
            with self.subTest(dx=dx, dy=dy):
                vecteur = Vecteur(dx, dy)
                gis = vecteur.gisement()
                
                # Le gisement doit être calculable et valide
                valide, msg = valider_gisement(gis)
                self.assertTrue(valide, f"Gisement {gis} invalide pour vecteur ({dx}, {dy}): {msg}")
                
                # Doit être dans [0, 400[
                self.assertGreaterEqual(gis, 0)
                self.assertLess(gis, 400)


if __name__ == '__main__':
    unittest.main(verbosity=2)