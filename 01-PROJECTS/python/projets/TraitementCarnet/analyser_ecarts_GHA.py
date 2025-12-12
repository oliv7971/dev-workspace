#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des écarts entre points calculés (S1_, S2_, S3_, S4_, X_) et références
pour le carnet Gha-poly&aucultations-251209-H.geo
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
    """Extrait le nom de base en enlevant les préfixes S1_, S2_, S3_, S4_, X_ et ref_"""
    # Enlever les préfixes
    for prefix in ['S1_', 'S2_', 'S3_', 'S4_', 'X_', 'ref_']:
        if nom.startswith(prefix):
            return nom[len(prefix):]
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
    """Analyse les écarts entre toutes les déterminations d'un même point"""
    print(f"Lecture du fichier: {fichier}")
    points = lire_fichier_geo(fichier)
    
    print(f"Total de {len(points)} points lus\n")
    
    # Grouper les points par nom de base
    groupes = defaultdict(list)
    for nom, coords in points.items():
        nom_base = extraire_nom_base(nom)
        groupes[nom_base].append((nom, coords))
    
    # Filtrer les points avec plusieurs déterminations
    points_multiples = {k: v for k, v in groupes.items() if len(v) > 1}
    
    print(f"Points avec plusieurs déterminations: {len(points_multiples)}\n")
    
    # Analyser les écarts pour chaque point
    resultats = []
    
    for nom_base, determinations in points_multiples.items():
        # Chercher la référence
        ref_nom = None
        ref_coords = None
        autres_det = []
        
        for nom, coords in determinations:
            if nom.startswith('ref_'):
                ref_nom = nom
                ref_coords = coords
            else:
                autres_det.append((nom, coords))
        
        if ref_coords is None:
            # Pas de référence, calculer les écarts entre les déterminations
            # Utiliser la première détermination comme référence
            ref_nom = autres_det[0][0]
            ref_coords = autres_det[0][1]
            autres_det = autres_det[1:]
        
        # Calculer les écarts
        ecarts_point = []
        max_xy = 0
        max_z = 0
        
        for nom, coords in autres_det:
            ecart_xy, ecart_z, dx, dy, dz = calculer_ecart(coords, ref_coords)
            ecarts_point.append({
                'nom': nom,
                'ecart_xy': ecart_xy,
                'ecart_z': ecart_z,
                'dx': dx,
                'dy': dy,
                'dz': dz
            })
            max_xy = max(max_xy, ecart_xy)
            max_z = max(max_z, ecart_z)
        
        if ecarts_point:
            resultats.append({
                'nom_base': nom_base,
                'ref': ref_nom,
                'nb_determinations': len(determinations),
                'max_xy': max_xy,
                'max_z': max_z,
                'ecarts': ecarts_point
            })
    
    # Trier par écart XY décroissant
    resultats.sort(key=lambda x: x['max_xy'], reverse=True)
    
    # Afficher les résultats
    print("=" * 120)
    print(f"{'Point base':<25} {'Ref':<25} {'Nb det':>7} {'Écart XY max':>12} {'Écart Z max':>12}")
    print("=" * 120)
    
    for r in resultats:
        print(f"{r['nom_base']:<25} {r['ref']:<25} {r['nb_determinations']:>7} {r['max_xy']:>11.1f}mm {r['max_z']:>11.1f}mm")
    
    print("=" * 120)
    print()
    
    # Afficher le TOP 20 avec détails
    print("\n" + "=" * 120)
    print("TOP 20 des points avec les plus grands écarts (détails)")
    print("=" * 120)
    
    for i, r in enumerate(resultats[:20], 1):
        print(f"\n{i}. {r['nom_base']} (référence: {r['ref']}, {r['nb_determinations']} déterminations)")
        print(f"   Écart XY max: {r['max_xy']:.1f}mm, Écart Z max: {r['max_z']:.1f}mm")
        print(f"   Détail des écarts:")
        for e in r['ecarts']:
            print(f"      {e['nom']:<30} : XY={e['ecart_xy']:>6.1f}mm  Z={e['ecart_z']:>6.1f}mm  (dX={e['dx']:>6.1f}  dY={e['dy']:>6.1f}  dZ={e['dz']:>6.1f})")
    
    # Statistiques
    print("\n" + "=" * 120)
    print("STATISTIQUES")
    print("=" * 120)
    
    nb_total = len(resultats)
    nb_xy_5mm = sum(1 for r in resultats if r['max_xy'] <= 5)
    nb_xy_10mm = sum(1 for r in resultats if r['max_xy'] <= 10)
    nb_xy_20mm = sum(1 for r in resultats if r['max_xy'] <= 20)
    nb_z_5mm = sum(1 for r in resultats if r['max_z'] <= 5)
    nb_z_10mm = sum(1 for r in resultats if r['max_z'] <= 10)
    
    print(f"Total de points analysés: {nb_total}")
    print(f"\nÉcarts planimétriques:")
    print(f"  ≤ 5mm : {nb_xy_5mm:3d} points ({nb_xy_5mm/nb_total*100:5.1f}%) ⭐ EXCELLENT")
    print(f"  ≤10mm : {nb_xy_10mm:3d} points ({nb_xy_10mm/nb_total*100:5.1f}%) ✓ BON")
    print(f"  ≤20mm : {nb_xy_20mm:3d} points ({nb_xy_20mm/nb_total*100:5.1f}%)")
    print(f"  >20mm : {nb_total-nb_xy_20mm:3d} points ({(nb_total-nb_xy_20mm)/nb_total*100:5.1f}%) ⚠ À VÉRIFIER")
    
    print(f"\nÉcarts altimétriques:")
    print(f"  ≤ 5mm : {nb_z_5mm:3d} points ({nb_z_5mm/nb_total*100:5.1f}%) ⭐ EXCELLENT")
    print(f"  ≤10mm : {nb_z_10mm:3d} points ({nb_z_10mm/nb_total*100:5.1f}%) ✓ BON")
    print(f"  >10mm : {nb_total-nb_z_10mm:3d} points ({(nb_total-nb_z_10mm)/nb_total*100:5.1f}%) ⚠ À VÉRIFIER")
    
    # Moyennes
    moy_xy = sum(r['max_xy'] for r in resultats) / nb_total
    moy_z = sum(r['max_z'] for r in resultats) / nb_total
    print(f"\nÉcarts moyens:")
    print(f"  XY: {moy_xy:.1f}mm")
    print(f"  Z:  {moy_z:.1f}mm")
    
    print("\n" + "=" * 120)

if __name__ == "__main__":
    fichier = r"c:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\TraitementCarnet\carnet\Gha-poly&aucultations-251209-H.geo"
    analyser_ecarts(fichier)
