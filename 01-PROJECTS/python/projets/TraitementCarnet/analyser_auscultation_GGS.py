#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des écarts pour le carnet GGS-auscultation -251210 - g.geo
Analyse les points d'auscultation (S0xxx, S03xx, S02xx, S06xx, S07xx)
"""

import re
from collections import defaultdict
import math

def lire_fichier_geo(chemin):
    """Lit le fichier .geo et extrait les points"""
    points = {}
    
    with open(chemin, 'r', encoding='utf-8') as f:
        for ligne in f:
            # Extraire les points (type 0 ou 3)
            match = re.match(r'^\d+\s+Point\s+(\S+)\s+[03]\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)', ligne)
            if match:
                nom = match.group(1)
                x = float(match.group(2))
                y = float(match.group(3))
                z = float(match.group(4))
                points[nom] = (x, y, z)
    
    return points

def extraire_nom_base(nom):
    """Extrait le nom de base en enlevant le préfixe ref_"""
    if nom.startswith('ref_'):
        return nom[4:]
    return nom

def calculer_ecart(coord1, coord2):
    """Calcule l'écart planimétrique et altimétrique entre deux points"""
    dx = coord1[0] - coord2[0]
    dy = coord1[1] - coord2[1]
    dz = coord1[2] - coord2[2]
    
    ecart_xy = math.sqrt(dx**2 + dy**2) * 1000  # en mm
    ecart_z = abs(dz) * 1000  # en mm
    
    return ecart_xy, ecart_z, dx*1000, dy*1000, dz*1000

def analyser_ecarts(fichier):
    """Analyse les écarts entre points d'auscultation et leurs références"""
    print(f"Lecture du fichier: {fichier}")
    points = lire_fichier_geo(fichier)
    
    print(f"Total de {len(points)} points lus\n")
    
    # Grouper les points par nom de base
    groupes = defaultdict(list)
    for nom, coords in points.items():
        nom_base = extraire_nom_base(nom)
        groupes[nom_base].append((nom, coords))
    
    # Filtrer les points d'auscultation avec référence
    points_auscultation = {}
    
    for nom_base, determinations in groupes.items():
        # Chercher si c'est un point d'auscultation (S0xxx, S03xx, etc.)
        if re.match(r'^S\d{4}$', nom_base):
            ref_coords = None
            mes_coords = None
            
            for nom, coords in determinations:
                if nom.startswith('ref_'):
                    ref_coords = coords
                else:
                    mes_coords = coords
            
            if ref_coords and mes_coords:
                ecart_xy, ecart_z, dx, dy, dz = calculer_ecart(mes_coords, ref_coords)
                points_auscultation[nom_base] = {
                    'ecart_xy': ecart_xy,
                    'ecart_z': ecart_z,
                    'dx': dx,
                    'dy': dy,
                    'dz': dz
                }
    
    # Trier par écart XY décroissant
    resultats = sorted(points_auscultation.items(), key=lambda x: x[1]['ecart_xy'], reverse=True)
    
    # Afficher les résultats
    print("=" * 100)
    print(f"{'Point auscultation':<20} {'Écart XY':>12} {'Écart Z':>12} {'dX':>10} {'dY':>10} {'dZ':>10}")
    print("=" * 100)
    
    for nom, data in resultats:
        print(f"{nom:<20} {data['ecart_xy']:>11.1f}mm {data['ecart_z']:>11.1f}mm {data['dx']:>9.1f} {data['dy']:>9.1f} {data['dz']:>9.1f}")
    
    print("=" * 100)
    print()
    
    # Statistiques
    print("=" * 100)
    print("STATISTIQUES")
    print("=" * 100)
    
    nb_total = len(resultats)
    
    if nb_total > 0:
        nb_xy_2mm = sum(1 for _, data in resultats if data['ecart_xy'] <= 2)
        nb_xy_5mm = sum(1 for _, data in resultats if data['ecart_xy'] <= 5)
        nb_xy_10mm = sum(1 for _, data in resultats if data['ecart_xy'] <= 10)
        
        nb_z_2mm = sum(1 for _, data in resultats if data['ecart_z'] <= 2)
        nb_z_5mm = sum(1 for _, data in resultats if data['ecart_z'] <= 5)
        nb_z_10mm = sum(1 for _, data in resultats if data['ecart_z'] <= 10)
        
        print(f"Total points d'auscultation analysés: {nb_total}")
        print()
        print("Écarts planimétriques (XY):")
        print(f"  ≤ 2mm:  {nb_xy_2mm:>4} ({nb_xy_2mm*100/nb_total:>5.1f}%) EXCELLENT")
        print(f"  ≤ 5mm:  {nb_xy_5mm:>4} ({nb_xy_5mm*100/nb_total:>5.1f}%) BON")
        print(f"  ≤ 10mm: {nb_xy_10mm:>4} ({nb_xy_10mm*100/nb_total:>5.1f}%)")
        print(f"  > 10mm: {nb_total-nb_xy_10mm:>4} ({(nb_total-nb_xy_10mm)*100/nb_total:>5.1f}%)")
        print()
        print("Écarts altimétriques (Z):")
        print(f"  ≤ 2mm:  {nb_z_2mm:>4} ({nb_z_2mm*100/nb_total:>5.1f}%) EXCELLENT")
        print(f"  ≤ 5mm:  {nb_z_5mm:>4} ({nb_z_5mm*100/nb_total:>5.1f}%) BON")
        print(f"  ≤ 10mm: {nb_z_10mm:>4} ({nb_z_10mm*100/nb_total:>5.1f}%)")
        print(f"  > 10mm: {nb_total-nb_z_10mm:>4} ({(nb_total-nb_z_10mm)*100/nb_total:>5.1f}%)")
        print()
        
        moy_xy = sum(data['ecart_xy'] for _, data in resultats) / nb_total
        moy_z = sum(data['ecart_z'] for _, data in resultats) / nb_total
        max_xy = max(data['ecart_xy'] for _, data in resultats)
        max_z = max(data['ecart_z'] for _, data in resultats)
        
        print(f"Écart XY moyen: {moy_xy:.1f}mm")
        print(f"Écart XY max:   {max_xy:.1f}mm")
        print(f"Écart Z moyen:  {moy_z:.1f}mm")
        print(f"Écart Z max:    {max_z:.1f}mm")
    
    print("=" * 100)
    
    # Analyser les variations altimétriques (déformations)
    print("\n" + "=" * 100)
    print("ANALYSE DES VARIATIONS ALTIMÉTRIQUES (déformations potentielles)")
    print("=" * 100)
    
    # Grouper par série
    series = defaultdict(list)
    for nom, data in resultats:
        # Extraire la série (S03xx, S02xx, S06xx, S07xx, S0311-315, etc.)
        if nom.startswith('S03'):
            if nom in ['S0311', 'S0312', 'S0313', 'S0314', 'S0315']:
                serie = 'S031x'
            elif nom.startswith('S003'):
                serie = 'S003x'
            else:
                serie = 'S03xx_autre'
        elif nom.startswith('S02'):
            serie = 'S02xx'
        elif nom.startswith('S06'):
            serie = 'S06xx'
        elif nom.startswith('S07'):
            serie = 'S07xx'
        elif nom.startswith('S00'):
            serie = 'S00xx'
        elif nom.startswith('S01'):
            serie = 'S01xx'
        elif nom.startswith('S10'):
            serie = 'S10xx'
        elif nom.startswith('S04'):
            serie = 'S04xx'
        else:
            serie = 'Autres'
        
        series[serie].append((nom, data))
    
    for serie, points_serie in sorted(series.items()):
        if len(points_serie) > 0:
            dz_values = [data['dz'] for _, data in points_serie]
            dz_moy = sum(dz_values) / len(dz_values)
            dz_min = min(dz_values)
            dz_max = max(dz_values)
            
            # Vérifier la cohérence des signes
            signes_positifs = sum(1 for dz in dz_values if dz > 0.5)
            signes_negatifs = sum(1 for dz in dz_values if dz < -0.5)
            signes_proches_zero = len(dz_values) - signes_positifs - signes_negatifs
            
            coherence = "COHÉRENT +" if signes_positifs > len(dz_values) * 0.7 else \
                       "COHÉRENT -" if signes_negatifs > len(dz_values) * 0.7 else \
                       "STABLE" if signes_proches_zero > len(dz_values) * 0.7 else \
                       "DISPERSÉ"
            
            print(f"\nSérie {serie} ({len(points_serie)} points):")
            print(f"  dZ moyen: {dz_moy:>6.1f}mm  |  min: {dz_min:>6.1f}mm  |  max: {dz_max:>6.1f}mm  |  {coherence}")
            
            if coherence in ["COHÉRENT +", "COHÉRENT -"]:
                print(f"  ⚠️  DÉFORMATION POTENTIELLE DÉTECTÉE")
    
    print("=" * 100)

if __name__ == '__main__':
    analyser_ecarts('carnet/GGS-auscultation -251210 - g.geo')
