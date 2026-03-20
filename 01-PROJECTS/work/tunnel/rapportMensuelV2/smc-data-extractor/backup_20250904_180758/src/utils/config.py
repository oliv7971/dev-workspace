# Configuration settings for the SMC data extractor application

import os

# Define the root directory for the application
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define paths for input and output directories
INPUT_DIR = os.path.join(ROOT_DIR, 'data', 'input')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'data', 'output')

# Define the default month for processing
DEFAULT_MONTH = '2025-08'

# Define the regex patterns for identifying relevant files and data
REGEX_PATTERNS = {
    'smc_file': r'.*SMC.*\.xlsm?$',
    'date': r'Date|Jour|Heure|Date/Heure',
    'convergence': r'convergen|conv.*',
    'displacement': r'deplac|dpm|dh|dz',
    'graph': r'graph|graphique'
}

# Define logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'filename': os.path.join(ROOT_DIR, 'logs', 'app.log')
}