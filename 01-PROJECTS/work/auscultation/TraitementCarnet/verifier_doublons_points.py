#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérifie les doublons dans les points de référence
"""

import re
from collections import defaultdict

fichier = "carnet/poly GMA 251202-B.geo"

# Dictionnaire: nom_point -> liste de (numéro_ligne, coordonnées)
points_refs = defaultdict(list)

with open(fichier, 'r', encoding='utf-8') as f:
    lignes = f.readlines()
    
for num_ligne, ligne in enumerate(lignes, 1):
    # Extraction des points de référence (type 3)
    match = re.match(r'^\d+\s+Point\s+(\S+)\s+3\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)', ligne)
    if match:
        nom = match.group(1)
        x = float(match.group(2))
        y = float(match.group(3))
        z = float(match.group(4))
        points_refs[nom].append({
            'ligne': num_ligne,
            'x': x,
            'y': y,
            'z': z
        })

# Recherche des doublons
doublons = {nom: infos for nom, infos in points_refs.items() if len(infos) > 1}

if doublons:
    print("=" * 90)
    print(f"⚠️  POINTS EN DOUBLE DÉTECTÉS : {len(doublons)} point(s)")
    print("=" * 90)
    print()
    
    for nom, infos in sorted(doublons.items()):
        print(f"Point: {nom} ({len(infos)} occurrences)")
        print("-" * 90)
        
        # Vérifier si les coordonnées sont identiques
        coords = [(i['x'], i['y'], i['z']) for i in infos]
        coords_identiques = all(c == coords[0] for c in coords)
        
        for idx, info in enumerate(infos, 1):
            print(f"  Occurrence {idx} (ligne {info['ligne']}): "
                  f"X={info['x']:.6f}  Y={info['y']:.6f}  Z={info['z']:.6f}")
        
        if coords_identiques:
            print(f"  ✓ Coordonnées identiques (doublons exacts)")
        else:
            print(f"  ⚠️  COORDONNÉES DIFFÉRENTES!")
            # Calcul des écarts
            import math
            for i in range(1, len(infos)):
                dx = infos[i]['x'] - infos[0]['x']
                dy = infos[i]['y'] - infos[0]['y']
                dz = infos[i]['z'] - infos[0]['z']
                dxy = math.sqrt(dx**2 + dy**2)
                print(f"     Écart occurrence {i+1} vs 1: dX={dx*1000:.1f}mm, dY={dy*1000:.1f}mm, "
                      f"dZ={dz*1000:.1f}mm, dXY={dxy*1000:.1f}mm")
        print()
    
    print("=" * 90)
    print("RÉSUMÉ")
    print("=" * 90)
    doublons_exacts = sum(1 for nom, infos in doublons.items() 
                          if all((i['x'], i['y'], i['z']) == (infos[0]['x'], infos[0]['y'], infos[0]['z']) 
                                for i in infos))
    doublons_differents = len(doublons) - doublons_exacts
    
    print(f"Total points en double : {len(doublons)}")
    print(f"  - Doublons exacts (mêmes coordonnées) : {doublons_exacts}")
    print(f"  - Doublons avec coordonnées différentes : {doublons_differents}")
    print()
    
    if doublons_differents > 0:
        print("⚠️  ACTION REQUISE : certains points ont des coordonnées différentes!")
    else:
        print("ℹ️  Tous les doublons ont les mêmes coordonnées (imports multiples)")
    
else:
    print("=" * 90)
    print("✓ AUCUN DOUBLON DÉTECTÉ")
    print("=" * 90)
    print(f"Nombre total de points de référence : {len(points_refs)}")

print()
