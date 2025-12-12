#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identifie les nouveaux points déterminés (non présents dans les références initiales)
"""

def lire_points_geo(fichier):
    """Lit tous les points d'un fichier .geo"""
    points = set()
    
    with open(fichier, 'r', encoding='utf-8') as f:
        for ligne in f:
            if not ligne.strip() or ligne.startswith('Option'):
                continue
            
            parties = ligne.strip().split()
            if len(parties) < 7:
                continue
            
            if parties[1] != 'Point':
                continue
            
            nom_complet = parties[2]
            
            # Enlever les préfixes X_, S1_, S2_, etc pour avoir le nom de base
            if nom_complet.startswith('X_'):
                nom_base = nom_complet[2:]
            elif nom_complet.startswith(('S1_', 'S2_', 'S3_', 'S4_', 'S5_')):
                nom_base = nom_complet[3:]
            else:
                nom_base = nom_complet
            
            points.add(nom_base)
    
    return points

# Fichiers
fichier_calcule = "carnet/POLYGGS-251204-M.geo"

# Lire tous les points
points_calcules = lire_points_geo(fichier_calcule)

# Lire les lignes du fichier pour identifier les références initiales (lignes 1-100 environ)
references_initiales = set()

with open(fichier_calcule, 'r', encoding='utf-8') as f:
    for i, ligne in enumerate(f, 1):
        if i > 150:  # On s'arrête après les premières lignes de références
            break
        
        if not ligne.strip() or ligne.startswith('Option'):
            continue
        
        parties = ligne.strip().split()
        if len(parties) >= 7 and parties[1] == 'Point':
            # Type 3 = référence
            if int(parties[3]) == 3:
                nom = parties[2]
                references_initiales.add(nom)

# Points nouveaux = calculés mais pas dans les références initiales
nouveaux_points = points_calcules - references_initiales

# Lire les coordonnées des nouveaux points
nouveaux_avec_coords = []

with open(fichier_calcule, 'r', encoding='utf-8') as f:
    for ligne in f:
        if not ligne.strip() or ligne.startswith('Option'):
            continue
        
        parties = ligne.strip().split()
        if len(parties) < 7:
            continue
        
        if parties[1] != 'Point':
            continue
        
        nom_complet = parties[2]
        type_point = int(parties[3])
        x = float(parties[4])
        y = float(parties[5])
        z = float(parties[6])
        
        # Enlever les préfixes
        if nom_complet.startswith('X_'):
            nom_base = nom_complet[2:]
        elif nom_complet.startswith(('S1_', 'S2_', 'S3_', 'S4_', 'S5_')):
            nom_base = nom_complet[3:]
        else:
            nom_base = nom_complet
        
        if nom_base in nouveaux_points:
            nouveaux_avec_coords.append({
                'nom': nom_base,
                'x': x,
                'y': y,
                'z': z,
                'type': type_point
            })

# Dédoublonner (même point peut apparaître plusieurs fois avec X_, S1_, etc)
points_uniques = {}
for p in nouveaux_avec_coords:
    if p['nom'] not in points_uniques:
        points_uniques[p['nom']] = p

# Afficher les résultats
print("=" * 100)
print("NOUVEAUX POINTS DÉTERMINÉS (non présents dans les références initiales)")
print("=" * 100)
print()
print(f"Nombre de nouveaux points : {len(points_uniques)}")
print()
print("-" * 100)
print(f"{'Point':<30} {'Type':<8} {'X':<16} {'Y':<16} {'Z':<16}")
print("-" * 100)

for nom in sorted(points_uniques.keys()):
    p = points_uniques[nom]
    type_str = "Calc" if p['type'] == 0 else "Ref"
    print(f"{nom:<30} {type_str:<8} {p['x']:15.6f}  {p['y']:15.6f}  {p['z']:15.6f}")

print("-" * 100)
print()

# Classification par type de nom
points_targets = [n for n in points_uniques.keys() if n.startswith('T')]
points_c = [n for n in points_uniques.keys() if n.startswith('C')]
points_s = [n for n in points_uniques.keys() if n.startswith('S') and not n.startswith(('S1', 'S2', 'S3', 'S4', 'S5'))]
points_autres = [n for n in points_uniques.keys() if n not in points_targets + points_c + points_s]

print("CLASSIFICATION:")
print("-" * 100)
if points_targets:
    print(f"Targets (T*) : {len(points_targets)}")
    print(f"  {', '.join(sorted(points_targets))}")
    print()

if points_c:
    print(f"Points C* : {len(points_c)}")
    print(f"  {', '.join(sorted(points_c))}")
    print()

if points_s:
    print(f"Points S* : {len(points_s)}")
    print(f"  {', '.join(sorted(points_s))}")
    print()

if points_autres:
    print(f"Autres points : {len(points_autres)}")
    print(f"  {', '.join(sorted(points_autres))}")
    print()

print("=" * 100)
