#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projection multi-axes - Traitement batch de points sur différents axes
Projette automatiquement chaque point sur son axe selon une colonne identifiant

Usage:
    python projeter_multi_axes.py points.csv --config axes_config.csv --output resultats.csv
    
    Ou avec Excel:
    python projeter_multi_axes.py points.xlsx --config axes_config.csv --output resultats.xlsx

Format fichier d'entrée (CSV/Excel):
    PT,X,Y,Z,axe
    REF-001,823245.5,1091505.2,-123.5,GRE
    REF-002,823110.3,1091385.7,-120.2,GVA

Format fichier config axes (CSV):
    axe,PM,X,Y,Z
    GRE,0.000,823241.141,1091511.231,-123.794
    GRE,9.721,823245.250,1091502.421,-123.697
    GVA,0.000,823100.000,1091400.000,-120.000
    GVA,50.000,823150.000,1091350.000,-119.500

Auteur: Assistant IA
Date: Novembre 2025
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict


def charger_axes(fichier_config):
    """
    Charge les axes depuis le fichier de configuration CSV
    
    Format attendu: axe,PM,X,Y,Z
    Minimum 2 points par axe
    
    Returns:
        dict: {nom_axe: DataFrame(PM, X, Y, Z)}
    """
    print(f"Chargement des axes depuis {fichier_config}...")
    
    # Lire le CSV en gérant les commentaires
    df = pd.read_csv(fichier_config, comment='#', skipinitialspace=True)
    
    # Vérifier les colonnes obligatoires
    colonnes_requises = ['axe', 'PM', 'X', 'Y', 'Z']
    for col in colonnes_requises:
        if col not in df.columns:
            raise ValueError(f"Colonne '{col}' manquante dans {fichier_config}")
    
    # Grouper par axe
    axes = {}
    for nom_axe, groupe in df.groupby('axe'):
        if len(groupe) < 2:
            print(f"⚠️  ATTENTION: L'axe '{nom_axe}' n'a que {len(groupe)} point(s) - minimum 2 requis")
            continue
        
        axes[nom_axe] = groupe[['PM', 'X', 'Y', 'Z']].copy()
        print(f"  ✓ Axe '{nom_axe}': {len(groupe)} points de référence")
    
    if not axes:
        raise ValueError("Aucun axe valide trouvé dans le fichier de configuration")
    
    return axes


def definir_droite_depuis_points(points_axe):
    """
    Définit une droite 3D en utilisant les points extrêmes en planimétrie
    
    Args:
        points_axe: DataFrame avec colonnes PM, X, Y, Z
        
    Returns:
        tuple: (origine, direction_unitaire, gisement_grades, pente_pourcent)
    """
    PM = points_axe['PM'].values
    X = points_axe['X'].values
    Y = points_axe['Y'].values
    Z = points_axe['Z'].values
    
    # Utiliser les points extrêmes (premier et dernier en PM)
    idx_min = np.argmin(PM)
    idx_max = np.argmax(PM)
    
    # Point origine (premier point)
    origine = np.array([X[idx_min], Y[idx_min], Z[idx_min]])
    
    # Vecteur directeur entre les deux points extrêmes
    direction = np.array([
        X[idx_max] - X[idx_min],
        Y[idx_max] - Y[idx_min],
        Z[idx_max] - Z[idx_min]
    ])
    
    # Normaliser pour obtenir le vecteur unitaire
    norme = np.linalg.norm(direction)
    direction_unitaire = direction / norme
    
    # Calcul du gisement (en grades, 0-400)
    gisement_rad = np.arctan2(direction[0], direction[1])
    gisement_grades = (gisement_rad * 200 / np.pi) % 400
    
    # Calcul de la pente en %
    distance_plan = np.sqrt(direction[0]**2 + direction[1]**2)
    pente_pourcent = (direction[2] / distance_plan) * 100 if distance_plan > 0 else 0
    
    return origine, direction_unitaire, gisement_grades, pente_pourcent


def projeter_points_sur_droite(points, origine, direction, mode='vertical', points_ref_axe=None):
    """
    Projette des points XYZ sur une droite 3D
    
    Args:
        points: DataFrame avec colonnes X, Y, Z
        origine: Point origine de la droite (array 3D)
        direction: Vecteur directeur unitaire (array 3D)
        mode: 'vertical' (défaut) ou 'perpendiculaire'
        points_ref_axe: DataFrame optionnel avec points de référence pour interpolation altitude par tronçon
        
    Returns:
        DataFrame avec colonnes PM, H, V ajoutées
    """
    X = points['X'].values
    Y = points['Y'].values
    Z = points['Z'].values
    
    # Vecteur du point vers l'origine
    vecteurs = np.column_stack([X - origine[0], Y - origine[1], Z - origine[2]])
    
    if mode == 'vertical':
        # PM = projection horizontale sur l'axe
        dir_plan = np.array([direction[0], direction[1], 0])
        dir_plan = dir_plan / np.linalg.norm(dir_plan)
        
        vect_plan = np.column_stack([vecteurs[:, 0], vecteurs[:, 1], np.zeros(len(vecteurs))])
        PM = np.sum(vect_plan * dir_plan, axis=1)
        
        # Point projeté sur l'axe (en plan)
        points_projetes_plan = origine + PM[:, np.newaxis] * dir_plan
        
        # H = distance horizontale perpendiculaire
        diff_plan = np.column_stack([X - points_projetes_plan[:, 0], 
                                      Y - points_projetes_plan[:, 1]])
        H = np.sqrt(np.sum(diff_plan**2, axis=1))
        
        # Signe de H (produit vectoriel en plan)
        produit_vectoriel = (diff_plan[:, 0] * dir_plan[1] - 
                            diff_plan[:, 1] * dir_plan[0])
        H = H * np.sign(produit_vectoriel)
        
        # V = différence d'altitude
        if points_ref_axe is not None and len(points_ref_axe) > 2:
            # Interpolation de l'altitude par tronçon
            z_axe = np.interp(PM, points_ref_axe['PM'].values, points_ref_axe['Z'].values)
        else:
            # Pente constante
            z_axe = origine[2] + PM * direction[2] / np.linalg.norm(direction[:2])
        V = Z - z_axe
        
    else:  # mode perpendiculaire
        # PM = projection sur l'axe
        PM = np.sum(vecteurs * direction, axis=1)
        
        # Point projeté sur l'axe
        points_projetes = origine + PM[:, np.newaxis] * direction
        
        # Vecteur perpendiculaire
        vect_perpendiculaire = np.column_stack([X - points_projetes[:, 0],
                                                Y - points_projetes[:, 1],
                                                Z - points_projetes[:, 2]])
        
        # Distance 3D perpendiculaire
        distance_3d = np.sqrt(np.sum(vect_perpendiculaire**2, axis=1))
        
        # Décomposition en H (horizontal) et V (vertical)
        H_vect = np.column_stack([vect_perpendiculaire[:, 0], 
                                  vect_perpendiculaire[:, 1], 
                                  np.zeros(len(vect_perpendiculaire))])
        H = np.sqrt(np.sum(H_vect**2, axis=1))
        
        # Signe de H
        dir_plan = np.array([direction[0], direction[1], 0])
        if np.linalg.norm(dir_plan) > 0:
            dir_plan = dir_plan / np.linalg.norm(dir_plan)
            produit_vectoriel = (H_vect[:, 0] * dir_plan[1] - 
                                H_vect[:, 1] * dir_plan[0])
            H = H * np.sign(produit_vectoriel)
        
        V = vect_perpendiculaire[:, 2]
    
    # Créer DataFrame résultat
    result = points.copy()
    result['PM'] = PM
    result['H'] = H
    result['V'] = V
    
    return result


def traiter_fichier(fichier_entree, fichier_config, fichier_sortie=None, 
                   mode='vertical', colonne_axe='axe', alteration_ppm=0.0):
    """
    Traite un fichier de points avec projection multi-axes
    
    Args:
        fichier_entree: Fichier CSV ou Excel avec les points
        fichier_config: Fichier CSV avec la configuration des axes
        fichier_sortie: Fichier de sortie (optionnel, auto si None)
        mode: 'vertical' ou 'perpendiculaire'
        colonne_axe: Nom de la colonne contenant l'identifiant d'axe
        alteration_ppm: Altération linéaire en ppm (0 = pas de correction, ex: 52 pour +52 ppm)
    """
    print("\n" + "="*80)
    print("PROJECTION MULTI-AXES")
    print("="*80)
    
    # Charger les axes
    axes = charger_axes(fichier_config)
    
    # Lire le fichier d'entrée
    print(f"\nChargement des points depuis {fichier_entree}...")
    path = Path(fichier_entree)
    
    if path.suffix.lower() in ['.xlsx', '.xls']:
        df_points = pd.read_excel(fichier_entree)
    else:
        # Tenter différents séparateurs
        for sep in [',', ';', '\t']:
            try:
                df_points = pd.read_csv(fichier_entree, sep=sep)
                if len(df_points.columns) > 1:
                    break
            except:
                continue
    
    print(f"  {len(df_points)} points chargés")
    
    # Vérifier les colonnes obligatoires
    colonnes_requises = ['X', 'Y', 'Z', colonne_axe]
    colonnes_manquantes = [col for col in colonnes_requises if col not in df_points.columns]
    if colonnes_manquantes:
        raise ValueError(f"Colonnes manquantes: {', '.join(colonnes_manquantes)}")
    
    # Calculer module linéaire
    module_lineaire = 1.0 + (alteration_ppm / 1_000_000.0)
    if alteration_ppm != 0:
        print(f"\nAltération linéaire: +{alteration_ppm} ppm (module = {module_lineaire:.8f})")
    
    # Calculer les paramètres de chaque axe
    print(f"\nCalcul des paramètres des axes (mode: {mode})...")
    axes_params = {}
    for nom_axe, points_ref in axes.items():
        origine, direction, gisement, pente = definir_droite_depuis_points(points_ref)
        axes_params[nom_axe] = {
            'origine': origine,
            'direction': direction,
            'gisement': gisement,
            'pente': pente
        }
        print(f"  Axe '{nom_axe}': Gis={gisement:.4f}g, Pente={pente:.2f}%")
    
    # Traiter chaque groupe de points par axe
    print("\nProjection des points...")
    resultats = []
    stats = defaultdict(int)
    
    for nom_axe, groupe in df_points.groupby(colonne_axe):
        if nom_axe not in axes_params:
            print(f"  ⚠️  Axe '{nom_axe}' inconnu - {len(groupe)} points ignorés")
            stats['ignorés'] += len(groupe)
            continue
        
        params = axes_params[nom_axe]
        groupe_projete = projeter_points_sur_droite(
            groupe, 
            params['origine'], 
            params['direction'], 
            mode,
            axes[nom_axe]  # Passer les points de référence pour interpolation
        )
        
        # Appliquer correction d'altération si nécessaire
        if alteration_ppm != 0:
            groupe_projete['PM'] = groupe_projete['PM'] * module_lineaire
        
        resultats.append(groupe_projete)
        stats[nom_axe] = len(groupe)
        print(f"  ✓ Axe '{nom_axe}': {len(groupe)} points projetés")
    
    if not resultats:
        raise ValueError("Aucun point n'a pu être projeté")
    
    # Concaténer tous les résultats
    df_resultat = pd.concat(resultats, ignore_index=True)
    
    # Générer nom de fichier de sortie si nécessaire
    if fichier_sortie is None:
        fichier_sortie = path.stem + "_projections" + path.suffix
    
    # Sauvegarder
    print(f"\nSauvegarde des résultats dans {fichier_sortie}...")
    path_sortie = Path(fichier_sortie)
    
    if path_sortie.suffix.lower() in ['.xlsx', '.xls']:
        df_resultat.to_excel(fichier_sortie, index=False)
    else:
        # Déterminer le séparateur du fichier d'origine
        sep = ';' if fichier_entree.endswith('.csv') else ','
        df_resultat.to_csv(fichier_sortie, sep=sep, index=False, float_format='%.6f')
    
    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ")
    print("="*80)
    print(f"Total points traités: {len(df_resultat)}")
    for axe, count in sorted(stats.items()):
        print(f"  - {axe}: {count} points")
    print(f"\nFichier généré: {fichier_sortie}")
    print("="*80)
    
    return df_resultat


def main():
    parser = argparse.ArgumentParser(
        description="Projection multi-axes - Traite des points sur différents axes selon un identifiant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python projeter_multi_axes.py points.csv
  python projeter_multi_axes.py points.xlsx --config mes_axes.csv
  python projeter_multi_axes.py points.csv --mode perpendiculaire
  python projeter_multi_axes.py points.csv --alteration 52
  python projeter_multi_axes.py points.csv --alteration 0  # Sans correction
  python projeter_multi_axes.py points.csv --colonne-axe galerie
        """
    )
    
    parser.add_argument('fichier', help="Fichier d'entrée (CSV ou Excel) avec colonnes X,Y,Z,axe")
    parser.add_argument('--config', default='axes_config.csv', 
                       help="Fichier de configuration des axes (défaut: axes_config.csv)")
    parser.add_argument('--output', '-o', help="Fichier de sortie (optionnel)")
    parser.add_argument('--mode', choices=['vertical', 'perpendiculaire'], 
                       default='vertical',
                       help="Mode de projection (défaut: vertical)")
    parser.add_argument('--colonne-axe', default='axe',
                       help="Nom de la colonne contenant l'identifiant d'axe (défaut: axe)")
    parser.add_argument('--alteration', type=float, default=0.0,
                       help="Altération linéaire en ppm (défaut: 0 = pas de correction, ex: 52 pour géom 32 + niveau mer 20)")
    
    args = parser.parse_args()
    
    try:
        traiter_fichier(
            args.fichier,
            args.config,
            args.output,
            args.mode,
            args.colonne_axe,
            args.alteration
        )
        return 0
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
