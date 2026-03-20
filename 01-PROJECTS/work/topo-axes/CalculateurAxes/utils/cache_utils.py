"""
Module de cache pour optimiser les calculs répétitifs
"""

import time
import hashlib
from functools import wraps
from collections import OrderedDict
from config import get_config
from logging_utils import get_logger


class Cache:
    """Cache LRU (Least Recently Used) pour les calculs"""
    
    def __init__(self, taille_max=None, duree_vie=None):
        self.config = get_config()
        self.logger = get_logger("Cache")
        
        self.taille_max = taille_max or self.config.TAILLE_CACHE_MAX
        self.duree_vie = duree_vie or self.config.DUREE_CACHE_SEC
        
        self._cache = OrderedDict()
        self._timestamps = {}
        
        # Statistiques
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def _generer_cle(self, func_name, args, kwargs):
        """Génère une clé unique pour la fonction et ses paramètres"""
        # Convertir args et kwargs en string pour hasher
        args_str = str(args)
        kwargs_str = str(sorted(kwargs.items()))
        combined = f"{func_name}:{args_str}:{kwargs_str}"
        
        # Hash pour avoir une clé courte et unique
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _est_expire(self, cle):
        """Vérifie si l'entrée est expirée"""
        if cle not in self._timestamps:
            return True
        
        age = time.time() - self._timestamps[cle]
        return age > self.duree_vie
    
    def get(self, cle):
        """Récupère une valeur du cache"""
        if cle not in self._cache or self._est_expire(cle):
            self.misses += 1
            if cle in self._cache:
                self._supprimer(cle)
            return None
        
        # Déplacer à la fin (LRU)
        value = self._cache.pop(cle)
        self._cache[cle] = value
        self.hits += 1
        
        return value
    
    def put(self, cle, valeur):
        """Ajoute une valeur au cache"""
        # Supprimer si déjà présent
        if cle in self._cache:
            self._supprimer(cle)
        
        # Vérifier la taille max
        while len(self._cache) >= self.taille_max:
            self._evict_oldest()
        
        # Ajouter la nouvelle valeur
        self._cache[cle] = valeur
        self._timestamps[cle] = time.time()
    
    def _supprimer(self, cle):
        """Supprime une entrée du cache"""
        if cle in self._cache:
            del self._cache[cle]
        if cle in self._timestamps:
            del self._timestamps[cle]
    
    def _evict_oldest(self):
        """Supprime l'entrée la plus ancienne"""
        if self._cache:
            oldest = next(iter(self._cache))
            self._supprimer(oldest)
            self.evictions += 1
    
    def clear(self):
        """Vide le cache"""
        self._cache.clear()
        self._timestamps.clear()
        self.logger.debug("Cache vidé")
    
    def stats(self):
        """Retourne les statistiques du cache"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'taille': len(self._cache),
            'taille_max': self.taille_max,
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'taux_hit': hit_rate
        }
    
    def log_stats(self):
        """Log les statistiques"""
        stats = self.stats()
        self.logger.info(
            f"Cache stats - Taille: {stats['taille']}/{stats['taille_max']}, "
            f"Hits: {stats['hits']}, Misses: {stats['misses']}, "
            f"Hit rate: {stats['taux_hit']:.1f}%"
        )


# Cache global pour les calculs géométriques
_cache_geometrie = Cache()
_cache_projections = Cache()
_cache_tabulations = Cache()


def cache_geometrie(func):
    """Décorateur pour mettre en cache les calculs géométriques"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Générer la clé de cache
        cle = _cache_geometrie._generer_cle(func.__name__, args, kwargs)
        
        # Chercher dans le cache
        resultat = _cache_geometrie.get(cle)
        if resultat is not None:
            return resultat
        
        # Calculer et mettre en cache
        resultat = func(*args, **kwargs)
        _cache_geometrie.put(cle, resultat)
        
        return resultat
    
    return wrapper


def cache_projection(func):
    """Décorateur pour mettre en cache les calculs de projection"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cle = _cache_projections._generer_cle(func.__name__, args, kwargs)
        
        resultat = _cache_projections.get(cle)
        if resultat is not None:
            return resultat
        
        resultat = func(*args, **kwargs)
        _cache_projections.put(cle, resultat)
        
        return resultat
    
    return wrapper


def cache_tabulation(func):
    """Décorateur pour mettre en cache les tabulations d'axes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cle = _cache_tabulations._generer_cle(func.__name__, args, kwargs)
        
        resultat = _cache_tabulations.get(cle)
        if resultat is not None:
            return resultat
        
        resultat = func(*args, **kwargs)
        _cache_tabulations.put(cle, resultat)
        
        return resultat
    
    return wrapper


class CacheManager:
    """Gestionnaire centralisé des caches"""
    
    def __init__(self):
        self.logger = get_logger("CacheManager")
        self.caches = {
            'geometrie': _cache_geometrie,
            'projections': _cache_projections,
            'tabulations': _cache_tabulations
        }
    
    def clear_all(self):
        """Vide tous les caches"""
        for nom, cache in self.caches.items():
            cache.clear()
        self.logger.info("Tous les caches ont été vidés")
    
    def stats_globales(self):
        """Retourne les statistiques de tous les caches"""
        stats = {}
        for nom, cache in self.caches.items():
            stats[nom] = cache.stats()
        return stats
    
    def log_stats_globales(self):
        """Log des statistiques de tous les caches"""
        self.logger.info("=== Statistiques des caches ===")
        for nom, cache in self.caches.items():
            stats = cache.stats()
            hit_rate = stats['taux_hit']
            if stats['hits'] + stats['misses'] > 0:
                self.logger.info(
                    f"{nom.capitalize()}: {stats['taille']}/{stats['taille_max']} "
                    f"entrées, {hit_rate:.1f}% hit rate"
                )
    
    def optimiser(self):
        """Optimise les caches (nettoie les entrées expirées)"""
        total_nettoye = 0
        
        for nom, cache in self.caches.items():
            taille_avant = len(cache._cache)
            
            # Nettoyer les entrées expirées
            cles_expirees = [
                cle for cle in cache._cache.keys() 
                if cache._est_expire(cle)
            ]
            
            for cle in cles_expirees:
                cache._supprimer(cle)
            
            nettoye = taille_avant - len(cache._cache)
            total_nettoye += nettoye
            
            if nettoye > 0:
                self.logger.debug(f"Cache {nom}: {nettoye} entrées expirées supprimées")
        
        if total_nettoye > 0:
            self.logger.info(f"Optimisation caches: {total_nettoye} entrées supprimées")


# Instance globale du gestionnaire
_cache_manager = CacheManager()

def get_cache_manager():
    """Retourne le gestionnaire de cache"""
    return _cache_manager


# Fonctions utilitaires
def clear_all_caches():
    """Vide tous les caches"""
    get_cache_manager().clear_all()

def log_cache_stats():
    """Log les statistiques de tous les caches"""
    get_cache_manager().log_stats_globales()

def optimize_caches():
    """Optimise tous les caches"""
    get_cache_manager().optimiser()