#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction de profils à des PM spécifiques depuis un fichier HVPM projeté.

Usage (depuis la racine du projet):
    python outils_projection/extraire_profils.py <fichier_HVPM.csv> <PM1> [PM2] [PM3] ... [--tolerance=0.05]

Exemples:
    python outils_projection/extraire_profils.py "_fichiers/GHA_HVPM.csv" 45 50 55
    python outils_projection/extraire_profils.py "_fichiers/GHA_HVPM.csv" 45 50 --tolerance=0.10

Arguments:
    fichier_HVPM.csv : fichier projeté au format H;V;PM
    PM1, PM2, ...    : liste des PM à extraire
    --tolerance=X    : tolérance en mètres (défaut: 0.05 = ±5cm)

Sortie:
    Fichier <nom_original>_profils.csv avec colonnes H;V;PM
"""

import sys
import pandas as pd
from pathlib import Path

# Répertoire racine du projet (parent du dossier outils_projection)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def extraire_profils(fichier_entree, pm_list, tolerance=0.05):
    """
    Extrait les points autour des PM spécifiés.
    
    Args:
        fichier_entree: chemin du fichier HVPM
        pm_list: liste des PM à extraire
        tolerance: tolérance en mètres (défaut ±5cm)
    
    Returns:
        DataFrame filtré
    """
    print(f"\n{'='*60}")
    print(f"EXTRACTION DE PROFILS")
    print(f"{'='*60}")
    
    # Charger le fichier
    print(f"\n1. Chargement : {fichier_entree}")
    df = pd.read_csv(fichier_entree, sep=';')
    print(f"   Points totaux : {len(df):,}")
    
    # Filtrer pour chaque PM
    print(f"\n2. Extraction des profils (tolérance ±{tolerance*100:.0f} cm)")
    
    masque = pd.Series([False] * len(df))
    
    for pm in pm_list:
        pm_min = pm - tolerance
        pm_max = pm + tolerance
        masque_pm = (df['PM'] >= pm_min) & (df['PM'] <= pm_max)
        nb_points = masque_pm.sum()
        print(f"   PM {pm:>6.2f} : {nb_points:>6,} points (entre {pm_min:.2f} et {pm_max:.2f})")
        masque = masque | masque_pm
    
    df_filtre = df[masque].copy()
    
    print(f"\n   Total extrait : {len(df_filtre):,} points")
    
    # Sauvegarder
    fichier_sortie = Path(fichier_entree).stem + "_profils.csv"
    fichier_sortie = Path(fichier_entree).parent / fichier_sortie
    
    df_filtre.to_csv(fichier_sortie, sep=';', index=False)
    
    print(f"\n3. ✓ Fichier de sortie : {fichier_sortie}")
    print(f"{'='*60}\n")
    
    return df_filtre


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    fichier_entree = sys.argv[1]
    
    # Parser les arguments
    pm_list = []
    tolerance = 0.05  # Défaut : ±5 cm
    
    for arg in sys.argv[2:]:
        if arg.startswith('--tolerance='):
            tolerance = float(arg.split('=')[1])
        else:
            try:
                pm_list.append(float(arg))
            except ValueError:
                print(f"Erreur: '{arg}' n'est pas un PM valide")
                sys.exit(1)
    
    if not pm_list:
        print("Erreur: Aucun PM spécifié")
        sys.exit(1)
    
    # Vérifier que le fichier existe
    if not Path(fichier_entree).exists():
        print(f"Erreur: Fichier non trouvé : {fichier_entree}")
        sys.exit(1)
    
    # Extraire les profils
    extraire_profils(fichier_entree, pm_list, tolerance)


if __name__ == '__main__':
    main()
