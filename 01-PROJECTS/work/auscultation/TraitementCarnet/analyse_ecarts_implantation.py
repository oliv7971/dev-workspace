#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des écarts entre points de référence et points d'implantation (i_xxx)
"""

import re
import math

# Lecture du fichier .geo
fichier = "carnet/poly GMA 251202-B.geo"

# Dictionnaires pour stocker les coordonnées
points_ref = {}
points_impl = {}

with open(fichier, 'r', encoding='utf-8') as f:
    for ligne in f:
        # Extraction des points de référence (type 3)
        match_ref = re.match(r'^\d+\s+Point\s+(\S+)\s+3\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)', ligne)
        if match_ref:
            nom = match_ref.group(1)
            x = float(match_ref.group(2))
            y = float(match_ref.group(3))
            z = float(match_ref.group(4))
            points_ref[nom] = (x, y, z)
        
        # Extraction des points calculés (type 0) commençant par i_
        match_impl = re.match(r'^\d+\s+Point\s+(i_\S+)\s+0\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)', ligne)
        if match_impl:
            nom = match_impl.group(1)
            x = float(match_impl.group(2))
            y = float(match_impl.group(3))
            z = float(match_impl.group(4))
            points_impl[nom] = (x, y, z)

# Calcul des écarts
print("=" * 90)
print("ANALYSE DES ÉCARTS - IMPLANTATION vs RÉFÉRENCE")
print("=" * 90)
print()

ecarts_data = []

for nom_impl, coord_impl in sorted(points_impl.items()):
    # Retirer le préfixe i_ pour trouver le point de référence
    nom_ref = nom_impl[2:]  # Enlève "i_"
    
    if nom_ref in points_ref:
        coord_ref = points_ref[nom_ref]
        
        # Calcul des écarts
        dx = coord_impl[0] - coord_ref[0]
        dy = coord_impl[1] - coord_ref[1]
        dz = coord_impl[2] - coord_ref[2]
        
        # Écart planimétrique
        dxy = math.sqrt(dx**2 + dy**2)
        
        # Écart 3D
        d3d = math.sqrt(dx**2 + dy**2 + dz**2)
        
        ecarts_data.append({
            'nom': nom_ref,
            'dx': dx,
            'dy': dy,
            'dz': dz,
            'dxy': dxy,
            'd3d': d3d
        })

# Tri par écart planimétrique décroissant
ecarts_data.sort(key=lambda x: x['dxy'], reverse=True)

# Affichage des résultats
print(f"{'Point':<20} {'dX (mm)':<12} {'dY (mm)':<12} {'dZ (mm)':<12} {'dXY (mm)':<12} {'d3D (mm)':<12}")
print("-" * 90)

for ecart in ecarts_data:
    print(f"{ecart['nom']:<20} "
          f"{ecart['dx']*1000:>10.1f}  "
          f"{ecart['dy']*1000:>10.1f}  "
          f"{ecart['dz']*1000:>10.1f}  "
          f"{ecart['dxy']*1000:>10.1f}  "
          f"{ecart['d3d']*1000:>10.1f}")

print()
print("=" * 90)
print("STATISTIQUES")
print("=" * 90)

if ecarts_data:
    ecarts_xy = [e['dxy'] for e in ecarts_data]
    ecarts_z = [abs(e['dz']) for e in ecarts_data]
    
    print(f"Nombre de points comparés : {len(ecarts_data)}")
    print()
    print(f"Écart planimétrique (dXY):")
    print(f"  Min  : {min(ecarts_xy)*1000:.1f} mm")
    print(f"  Max  : {max(ecarts_xy)*1000:.1f} mm")
    print(f"  Moyen: {sum(ecarts_xy)/len(ecarts_xy)*1000:.1f} mm")
    print()
    print(f"Écart altimétrique (|dZ|):")
    print(f"  Min  : {min(ecarts_z)*1000:.1f} mm")
    print(f"  Max  : {max(ecarts_z)*1000:.1f} mm")
    print(f"  Moyen: {sum(ecarts_z)/len(ecarts_z)*1000:.1f} mm")
    print()
    
    # Points avec écarts importants
    seuil_xy = 0.010  # 10mm
    seuil_z = 0.010   # 10mm
    
    points_alerte = [e for e in ecarts_data if e['dxy'] > seuil_xy or abs(e['dz']) > seuil_z]
    
    if points_alerte:
        print(f"⚠️  {len(points_alerte)} point(s) avec écart > {seuil_xy*1000:.0f} mm (XY) ou > {seuil_z*1000:.0f} mm (Z):")
        for e in points_alerte:
            print(f"   - {e['nom']}: dXY={e['dxy']*1000:.1f}mm, dZ={e['dz']*1000:.1f}mm")
    else:
        print(f"✓ Tous les écarts < {seuil_xy*1000:.0f} mm (XY) et < {seuil_z*1000:.0f} mm (Z)")

print()
print("=" * 90)
