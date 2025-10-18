"""
Tests unitaires pour les calculs perpendiculaires vs verticaux
"""

import unittest
import math
import sys
import os

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.geometrie import Point, Vecteur
from core.axe import AxeEnPlan, ProfilEnLong
from core.calculs_perpendiculaire import CalculsPerpendiculaire, ModeCalcul


class TestCalculsPerpendiculaire(unittest.TestCase):
    """Tests pour la distinction perpendiculaire/vertical"""
    
    def setUp(self):
        """Configuration test avec axe en pente"""
        # Axe droit 200m avec pente 5%
        self.axe = AxeEnPlan("Test")
        p1 = Point(1000, 2000, 100)  # Z=100m
        p2 = Point(1200, 2000, 110)  # Z=110m (+10m sur 200m = 5%)
        self.axe.ajouter_alignement(p1, p2)
        
        # Profil avec pente constante
        self.profil = ProfilEnLong("Test Pente")
        self.profil.ajouter_point(0, 100)
        self.profil.ajouter_point(200, 110)
        self.profil.ajouter_pente(0, 200, 5.0)
        
        # Associer profil et initialiser calculateur
        self.calculateur = self.axe.associer_profil_long(self.profil)
    
    def test_creation_calculateur(self):
        """Test création calculateur perpendiculaire"""
        self.assertIsInstance(self.calculateur, CalculsPerpendiculaire)
        self.assertEqual(self.calculateur.axe_plan, self.axe)
        self.assertEqual(self.calculateur.profil_long, self.profil)
    
    def test_profil_pente(self):
        """Test calcul pente profil"""
        pente_0 = self.profil.pente_at_pm(0)
        pente_100 = self.profil.pente_at_pm(100)
        pente_200 = self.profil.pente_at_pm(200)
        
        self.assertAlmostEqual(pente_0, 5.0, places=2)
        self.assertAlmostEqual(pente_100, 5.0, places=2)
        self.assertAlmostEqual(pente_200, 5.0, places=2)
    
    def test_altitude_profil(self):
        """Test calcul altitude sur profil"""
        alt_0 = self.profil.altitude_at_pm(0)
        alt_100 = self.profil.altitude_at_pm(100)
        alt_200 = self.profil.altitude_at_pm(200)
        
        self.assertAlmostEqual(alt_0, 100.0, places=3)
        self.assertAlmostEqual(alt_100, 105.0, places=3)  # 100 + 5m
        self.assertAlmostEqual(alt_200, 110.0, places=3)
    
    def test_point_horizontal_vs_perpendiculaire(self):
        """Test différence entre modes horizontal et perpendiculaire"""
        pm_test = 100
        deport_test = 2.0  # 2m à droite
        
        # Mode horizontal classique
        pt_h = self.axe.point_at_pm_avec_mode(pm_test, deport_test, ModeCalcul.HORIZONTAL_2D)
        
        # Mode perpendiculaire au profil
        pt_p = self.axe.point_at_pm_avec_mode(pm_test, deport_test, ModeCalcul.PERPENDICULAIRE_PROFIL)
        
        # Il doit y avoir une différence en Z due à la pente
        self.assertNotAlmostEqual(pt_h.z, pt_p.z, places=2)
        self.assertGreater(pt_p.z, pt_h.z)  # Perpendiculaire plus haut
        
        # Différence horizontale minime
        diff_h = math.sqrt((pt_h.x - pt_p.x)**2 + (pt_h.y - pt_p.y)**2)
        self.assertLess(diff_h, 0.2)  # < 20cm
    
    def test_point_vertical_absolu(self):
        """Test mode vertical absolu"""
        pm_test = 100
        deport_vertical = 1.0  # 1m vers le haut
        
        pt_v = self.axe.point_at_pm_avec_mode(pm_test, deport_vertical, ModeCalcul.VERTICAL_ABSOLU)
        
        # Point doit être exactement au-dessus de l'axe
        pt_axe = self.axe.point_at_pm(pm_test)
        self.assertAlmostEqual(pt_v.x, pt_axe.x, places=3)
        self.assertAlmostEqual(pt_v.y, pt_axe.y, places=3)
        
        # Altitude = altitude profil + déport
        alt_profil = self.profil.altitude_at_pm(pm_test)
        self.assertAlmostEqual(pt_v.z, alt_profil + deport_vertical, places=3)
    
    def test_projection_modes_comparison(self):
        """Test comparaison des modes de projection"""
        # Point test à 2m à droite, 1m au-dessus
        point_test = Point(1102, 2002, 106)
        
        comparaison = self.axe.comparaison_modes_projection(point_test)
        
        # Vérifier que les 3 modes sont présents
        self.assertIn(ModeCalcul.HORIZONTAL_2D, comparaison)
        self.assertIn(ModeCalcul.PERPENDICULAIRE_PROFIL, comparaison)
        self.assertIn(ModeCalcul.VERTICAL_ABSOLU, comparaison)
        
        # Vérifier différences entre modes
        deport_h = comparaison[ModeCalcul.HORIZONTAL_2D]['deport']
        deport_p = comparaison[ModeCalcul.PERPENDICULAIRE_PROFIL]['deport']
        deport_v = comparaison[ModeCalcul.VERTICAL_ABSOLU]['deport']
        
        # Les déports doivent être différents
        self.assertNotAlmostEqual(deport_h, deport_p, places=2)
        self.assertNotAlmostEqual(deport_h, deport_v, places=2)
        self.assertNotAlmostEqual(deport_p, deport_v, places=2)
    
    def test_coherence_calculs_inverses(self):
        """Test cohérence calculs directs/inverses"""
        pm_orig = 100
        deport_orig = 1.5
        
        # Calcul direct : PM + déport → Point
        pt_calc = self.axe.point_at_pm_avec_mode(pm_orig, deport_orig, ModeCalcul.PERPENDICULAIRE_PROFIL)
        
        # Calcul inverse : Point → PM + déport
        pm_retour, deport_retour = self.axe.projeter_point_avec_mode(pt_calc, ModeCalcul.PERPENDICULAIRE_PROFIL)
        
        # Vérifier cohérence (avec tolérance)
        self.assertAlmostEqual(pm_orig, pm_retour, places=1)
        self.assertAlmostEqual(abs(deport_orig), abs(deport_retour), places=1)
    
    def test_cas_limite_pente_nulle(self):
        """Test avec pente nulle - tous modes identiques"""
        # Axe plat
        axe_plat = AxeEnPlan("Plat")
        p1_plat = Point(0, 0, 50)
        p2_plat = Point(100, 0, 50)  # Même altitude
        axe_plat.ajouter_alignement(p1_plat, p2_plat)
        
        # Profil plat  
        profil_plat = ProfilEnLong("Plat")
        profil_plat.ajouter_point(0, 50)
        profil_plat.ajouter_point(100, 50)
        profil_plat.ajouter_pente(0, 100, 0.0)  # Pente nulle
        
        calc_plat = axe_plat.associer_profil_long(profil_plat)
        
        # Points calculés avec même déport
        pm_test, deport_test = 50, 1.0
        pt_h = axe_plat.point_at_pm_avec_mode(pm_test, deport_test, ModeCalcul.HORIZONTAL_2D)
        pt_p = axe_plat.point_at_pm_avec_mode(pm_test, deport_test, ModeCalcul.PERPENDICULAIRE_PROFIL)
        
        # Avec pente nulle, horizontal et perpendiculaire identiques
        self.assertAlmostEqual(pt_h.x, pt_p.x, places=3)
        self.assertAlmostEqual(pt_h.y, pt_p.y, places=3)
        self.assertAlmostEqual(pt_h.z, pt_p.z, places=2)
    
    def test_precision_calculs(self):
        """Test précision des calculs trigonométriques"""
        pm_test = 100
        
        # Pente connue : 5%
        pente_percent = self.profil.pente_at_pm(pm_test)
        pente_rad = math.atan(pente_percent / 100.0)
        
        # Déport perpendiculaire théorique
        deport_perp = 2.0
        correction_z_theorique = deport_perp * math.sin(pente_rad)
        
        # Calcul avec notre méthode
        pt_calc = self.axe.point_at_pm_avec_mode(pm_test, deport_perp, ModeCalcul.PERPENDICULAIRE_PROFIL)
        pt_base = self.axe.point_at_pm(pm_test)
        
        correction_z_calculee = pt_calc.z - pt_base.z
        
        # Vérifier précision du calcul
        self.assertAlmostEqual(correction_z_calculee, correction_z_theorique, places=3)


if __name__ == '__main__':
    unittest.main(verbosity=2)