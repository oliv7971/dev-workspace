"""
Tests pour les modules créés lors des améliorations
"""

import unittest
import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from config import get_config, Config
from validation import get_validateur
from cache_utils import Cache, cache_geometrie


class TestConfig(unittest.TestCase):
    """Tests pour le module de configuration"""
    
    def test_config_chargement(self):
        """Test chargement configuration"""
        config = get_config()
        self.assertIsInstance(config.VERSION, str)
        self.assertIsInstance(config.PRECISION_CALCUL, float)
        self.assertIsInstance(config.GRADES_PAR_TOUR, int)
        self.assertEqual(config.GRADES_PAR_TOUR, 400)
    
    def test_validation_coordonnees(self):
        """Test validation coordonnées"""
        config = get_config()
        
        # Coordonnées valides
        self.assertTrue(config.valider_coordonnee(823000))
        self.assertTrue(config.valider_coordonnee(1234000))
        
        # Coordonnées invalides
        self.assertFalse(config.valider_coordonnee(1e15))
        self.assertFalse(config.valider_coordonnee(-1e15))
    
    def test_validation_rayon(self):
        """Test validation rayon"""
        config = get_config()
        
        # Rayons valides
        self.assertTrue(config.valider_rayon(100))
        self.assertTrue(config.valider_rayon(-500))  # Rayon négatif OK
        
        # Rayons invalides
        self.assertFalse(config.valider_rayon(5))     # Trop petit
        self.assertFalse(config.valider_rayon(200000)) # Trop grand


class TestValidation(unittest.TestCase):
    """Tests pour le module de validation"""
    
    def setUp(self):
        self.validateur = get_validateur()
    
    def test_validation_point_valide(self):
        """Test validation point valide"""
        erreurs = self.validateur.valider_point(823000, 1234000, 250)
        self.assertEqual(len(erreurs), 0)
    
    def test_validation_point_invalide(self):
        """Test validation point invalide"""
        # Coordonnées hors limites
        erreurs = self.validateur.valider_point(1e15, 1234000, 250)
        self.assertGreater(len(erreurs), 0)
        
        # Type invalide
        erreurs = self.validateur.valider_point("abc", 1234000, 250)
        self.assertGreater(len(erreurs), 0)
    
    def test_validation_rayon(self):
        """Test validation rayon"""
        # Rayon valide
        erreurs = self.validateur.valider_rayon(200)
        self.assertEqual(len(erreurs), 0)
        
        # Rayon trop petit
        erreurs = self.validateur.valider_rayon(5)
        self.assertGreater(len(erreurs), 0)
        
        # Rayon nul
        erreurs = self.validateur.valider_rayon(0)
        self.assertGreater(len(erreurs), 0)
    
    def test_validation_gisement(self):
        """Test validation gisement"""
        # Gisements valides
        self.assertEqual(len(self.validateur.valider_gisement(0)), 0)
        self.assertEqual(len(self.validateur.valider_gisement(100)), 0)
        self.assertEqual(len(self.validateur.valider_gisement(399.99)), 0)
        
        # Gisements invalides
        self.assertGreater(len(self.validateur.valider_gisement(-10)), 0)
        self.assertGreater(len(self.validateur.valider_gisement(500)), 0)
    
    def test_validation_intervalle_pm(self):
        """Test validation intervalle PM"""
        # Intervalle valide
        erreurs = self.validateur.valider_intervalle_pm(0, 100)
        self.assertEqual(len(erreurs), 0)
        
        # PM début > PM fin
        erreurs = self.validateur.valider_intervalle_pm(100, 50)
        self.assertGreater(len(erreurs), 0)
        
        # PM début négatif
        erreurs = self.validateur.valider_intervalle_pm(-10, 100)
        self.assertGreater(len(erreurs), 0)


class TestCache(unittest.TestCase):
    """Tests pour le système de cache"""
    
    def setUp(self):
        self.cache = Cache(taille_max=5, duree_vie=1)
    
    def test_cache_put_get(self):
        """Test ajout et récupération cache"""
        self.cache.put("test1", "valeur1")
        valeur = self.cache.get("test1")
        self.assertEqual(valeur, "valeur1")
    
    def test_cache_miss(self):
        """Test cache miss"""
        valeur = self.cache.get("inexistant")
        self.assertIsNone(valeur)
    
    def test_cache_lru(self):
        """Test éviction LRU"""
        # Remplir le cache au maximum
        for i in range(5):
            self.cache.put(f"key{i}", f"value{i}")
        
        # Ajouter une 6ème entrée -> éviction de la plus ancienne
        self.cache.put("key5", "value5")
        
        # key0 devrait avoir été évincée
        self.assertIsNone(self.cache.get("key0"))
        self.assertEqual(self.cache.get("key1"), "value1")
    
    def test_cache_stats(self):
        """Test statistiques cache"""
        stats_init = self.cache.stats()
        self.assertEqual(stats_init['hits'], 0)
        self.assertEqual(stats_init['misses'], 0)
        
        # Test hit
        self.cache.put("test", "value")
        self.cache.get("test")
        
        # Test miss
        self.cache.get("inexistant")
        
        stats_final = self.cache.stats()
        self.assertEqual(stats_final['hits'], 1)
        self.assertEqual(stats_final['misses'], 1)
    
    def test_decorateur_cache(self):
        """Test décorateur de cache"""
        call_count = 0
        
        @cache_geometrie
        def fonction_test(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # Premier appel - calcul
        result1 = fonction_test(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # Deuxième appel - cache
        result2 = fonction_test(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # Pas de nouveau calcul
        
        # Appel avec paramètres différents - nouveau calcul
        result3 = fonction_test(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count, 2)


if __name__ == '__main__':
    unittest.main()