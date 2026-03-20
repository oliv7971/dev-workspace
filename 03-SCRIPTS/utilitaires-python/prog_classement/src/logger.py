"""
Module de logging pour le système de classement
Fournit un logging structuré avec rotation des fichiers
"""

import logging
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler


class ClassementLogger:
    def __init__(self, config_path="config/config.json"):
        """Initialise le système de logging"""
        # Chargement de la configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.logs_dir = self.config['chemins']['logs_dir']
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Configuration du logger principal
        self.logger = logging.getLogger('classement')
        self.logger.setLevel(getattr(logging, self.config['options']['niveau_log']))
        
        # Éviter les doublons de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configure les handlers de logging"""
        # Handler pour fichier avec rotation
        log_file = os.path.join(self.logs_dir, f"classement_{datetime.now().strftime('%Y%m')}.log")
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Handler pour console
        console_handler = logging.StreamHandler()
        
        # Format des messages
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message, **kwargs):
        """Log niveau INFO avec contexte optionnel"""
        self._log_with_context("INFO", message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log niveau WARNING avec contexte optionnel"""
        self._log_with_context("WARNING", message, **kwargs)
    
    def error(self, message, **kwargs):
        """Log niveau ERROR avec contexte optionnel"""
        self._log_with_context("ERROR", message, **kwargs)
    
    def debug(self, message, **kwargs):
        """Log niveau DEBUG avec contexte optionnel"""
        self._log_with_context("DEBUG", message, **kwargs)
    
    def _log_with_context(self, level, message, **kwargs):
        """Log avec contexte enrichi"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context}"
        else:
            full_message = message
        
        getattr(self.logger, level.lower())(full_message)
    
    def log_operation(self, operation, source, destination, status="SUCCESS", details=None):
        """Log spécialisé pour les opérations de fichiers"""
        self.info(
            f"OPERATION: {operation}",
            source=source,
            destination=destination,
            status=status,
            details=details or "N/A"
        )
    
    def log_classification(self, dossier, categorie_detectee, galerie, confidence="AUTO"):
        """Log spécialisé pour les classifications"""
        self.info(
            f"CLASSIFICATION: {dossier}",
            categorie=categorie_detectee,
            galerie=galerie,
            confidence=confidence
        )
    
    def log_session_start(self, script_name):
        """Log de début de session"""
        self.info(f"=== DEBUT SESSION: {script_name} ===")
    
    def log_session_end(self, script_name, stats=None):
        """Log de fin de session avec statistiques"""
        stats_str = ""
        if stats:
            stats_str = " | " + " | ".join([f"{k}={v}" for k, v in stats.items()])
        self.info(f"=== FIN SESSION: {script_name} ==={stats_str}")


# Instance globale pour faciliter l'usage
logger = None

def get_logger():
    """Retourne l'instance du logger (singleton)"""
    global logger
    if logger is None:
        logger = ClassementLogger()
    return logger