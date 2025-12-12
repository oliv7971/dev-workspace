"""
Système de logging pour le Calculateur d'Axes
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from config import get_config


class CalculateurLogger:
    """Gestionnaire centralisé des logs"""
    
    def __init__(self, nom_module="CalculateurAxes"):
        self.config = get_config()
        self.nom_module = nom_module
        self.logger = None
        self._configurer_logger()
    
    def _configurer_logger(self):
        """Configure le système de logging"""
        # Créer le répertoire de logs
        Path(self.config.REPERTOIRE_LOGS).mkdir(exist_ok=True)
        
        # Créer le logger principal
        self.logger = logging.getLogger(self.nom_module)
        self.logger.setLevel(logging.DEBUG if getattr(self.config, 'DEBUG', False) else logging.INFO)
        
        # Éviter les doublons de handlers
        if self.logger.handlers:
            return
        
        # Formatter pour les messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler pour fichier principal
        fichier_log = os.path.join(self.config.REPERTOIRE_LOGS, self.config.FICHIER_LOG_DEFAUT)
        file_handler = logging.FileHandler(fichier_log, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler pour la console (niveau WARNING et plus)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Handler séparé pour les erreurs critiques
        error_handler = logging.FileHandler(
            os.path.join(self.config.REPERTOIRE_LOGS, 'erreurs.log'),
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def debug(self, message, **kwargs):
        """Log niveau DEBUG"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message, **kwargs):
        """Log niveau INFO"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log niveau WARNING"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message, **kwargs):
        """Log niveau ERROR"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message, **kwargs):
        """Log niveau CRITICAL"""
        self.logger.critical(message, **kwargs)
    
    def log_operation(self, operation, details=None, succes=True):
        """Log une opération métier"""
        niveau = logging.INFO if succes else logging.ERROR
        status = "SUCCÈS" if succes else "ÉCHEC"
        
        message = f"[{operation}] {status}"
        if details:
            message += f" - {details}"
        
        self.logger.log(niveau, message)
    
    def log_calcul(self, type_calcul, parametres, resultat=None, duree=None):
        """Log spécialisé pour les calculs"""
        message = f"CALCUL [{type_calcul}]"
        
        if parametres:
            params_str = ", ".join(f"{k}={v}" for k, v in parametres.items())
            message += f" - Paramètres: {params_str}"
        
        if resultat is not None:
            message += f" - Résultat: {resultat}"
        
        if duree is not None:
            message += f" - Durée: {duree:.3f}s"
        
        self.logger.info(message)
    
    def log_import_export(self, operation, fichier, nb_elements=None, format_detecte=None):
        """Log spécialisé pour les I/O"""
        message = f"I/O [{operation}] {fichier}"
        
        if nb_elements is not None:
            message += f" - {nb_elements} éléments"
        
        if format_detecte:
            message += f" - Format: {format_detecte}"
        
        self.logger.info(message)
    
    def log_performance(self, fonction, duree, nb_elements=None):
        """Log les performances"""
        message = f"PERF [{fonction}] {duree:.3f}s"
        
        if nb_elements:
            vitesse = nb_elements / duree if duree > 0 else 0
            message += f" - {nb_elements} éléments ({vitesse:.0f}/s)"
        
        self.logger.debug(message)


# Instance globale du logger
_logger_instance = None

def get_logger(nom_module=None):
    """Retourne l'instance du logger (singleton)"""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = CalculateurLogger(nom_module or "CalculateurAxes")
    
    return _logger_instance


# Décorateur pour logger automatiquement les fonctions
def log_function(operation_name=None):
    """Décorateur pour logger automatiquement l'entrée/sortie des fonctions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            op_name = operation_name or func.__name__
            
            # Log début
            logger.debug(f"Début {op_name}")
            start_time = datetime.now()
            
            try:
                # Exécuter la fonction
                result = func(*args, **kwargs)
                
                # Log succès
                duree = (datetime.now() - start_time).total_seconds()
                logger.debug(f"Fin {op_name} - Durée: {duree:.3f}s")
                
                return result
                
            except Exception as e:
                # Log erreur
                duree = (datetime.now() - start_time).total_seconds()
                logger.error(f"Erreur {op_name} après {duree:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator


# Fonctions utilitaires pour logging rapide
def log_info(message, **kwargs):
    get_logger().info(message, **kwargs)

def log_error(message, **kwargs):
    get_logger().error(message, **kwargs)

def log_warning(message, **kwargs):
    get_logger().warning(message, **kwargs)

def log_debug(message, **kwargs):
    get_logger().debug(message, **kwargs)