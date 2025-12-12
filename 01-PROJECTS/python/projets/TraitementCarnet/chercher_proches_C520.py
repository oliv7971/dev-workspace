#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recherche les points proches de C.520
"""

import re
import math

fichier = "carnet/poly GMA 251202-C.geo"

# Coordonnées de C.520 (point calculé)
c520_x = 823263.053760
c520_y = 1091521.601093
c520_z = -123.753688

# Lecture de tous les points de référence
points = []

with open(fichier, 'r', encoding='utf-8') as f:
    for ligne in f:
        match = re.match(r'^\d+\s+Point\s+(\S+)\s+3\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)', ligne)
        if match:
            nom = match.group(1)
            x = float(match.group(2))
            y = float(match.group(3))
            z = float(match.group(4))
            
            # Calcul des distances par rapport à C.520
            dx = x - c520_x
            dy = y - c520_y
            dz = z - c520_z
            dxy = math.sqrt(dx**2 + dy**2)
            d3d = math.sqrt(dx**2 + dy**2 + dz**2)
            
            points.append({
                'nom': nom,
                'x': x,
                'y': y,
                'z': z,
                'dx': dx,
                'dy': dy,
                'dz': dz,
                'dxy': dxy,
                'd3d': d3d
            })

# Tri par distance planimétrique
points.sort(key=lambda p: p['dxy'])

print("=" * 100)
print(f"POINTS PROCHES DE C.520 (calculé: X={c520_x:.3f}, Y={c520_y:.3f}, Z={c520_z:.3f})")
print("=" * 100)
print()
print(f"{'Point':<20} {'X':<15} {'Y':<15} {'Z':<12} {'dXY (mm)':<12} {'dZ (mm)':<12}")
print("-" * 100)

# Afficher les 20 points les plus proches
for p in points[:20]:
    print(f"{p['nom']:<20} {p['x']:<15.3f} {p['y']:<15.3f} {p['z']:<12.3f} "
          f"{p['dxy']*1000:>10.1f}  {p['dz']*1000:>10.1f}")

print()
print("=" * 100)
print(f"Point le plus proche: {points[0]['nom']} à {points[0]['dxy']*1000:.1f} mm")
print("=" * 100)
