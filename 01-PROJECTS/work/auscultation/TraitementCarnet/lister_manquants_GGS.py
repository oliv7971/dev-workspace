#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Liste des points mesurés sans référence dans POLYGGS-251204-E.geo
"""

from collections import defaultdict

def lire_fichier(fichier):
    """Lit les points et mesures"""
    points_ref = set()
    mesures = defaultdict(int)
    
    with open(fichier, 'r', encoding='utf-8') as f:
        for ligne in f:
            parties = ligne.strip().split()
            if len(parties) < 3:
                continue
            
            if parties[1] == 'Point' and parties[3] == '3':
                # Point de référence
                points_ref.add(parties[2])
            
            elif parties[1] == 'Mesure':
                # Mesure
                point_vise = parties[2]
                mesures[point_vise] += 1
    
    return points_ref, mesures

fichier = "carnet/POLYGGS-251204-K.geo"
points_ref, mesures = lire_fichier(fichier)

# Points mesurés sans référence
manquants = {}
for point, nb_mesures in mesures.items():
    if point not in points_ref:
        manquants[point] = nb_mesures

print("=" * 80)
print("POINTS MESURÉS SANS RÉFÉRENCE - POLYGGS-251204-K.geo")
print("=" * 80)
print()
print(f"Points de référence        : {len(points_ref)}")
print(f"Points visés (uniques)     : {len(mesures)}")
print(f"Points mesurés sans réf.   : {len(manquants)}")
print()
print("=" * 80)
print("LISTE DES POINTS MANQUANTS")
print("=" * 80)
print()

# Regrouper par type
ggs_autres = []
gva = []
g04 = []
autres = []

for point, nb in sorted(manquants.items()):
    if point.startswith('GGS.'):
        ggs_autres.append((point, nb))
    elif point.startswith('GVA.'):
        gva.append((point, nb))
    elif point.startswith('G04.'):
        g04.append((point, nb))
    else:
        autres.append((point, nb))

if ggs_autres:
    print(f"Points GGS.* ({len(ggs_autres)}) :")
    for point, nb in ggs_autres:
        print(f"  {point:<30} ({nb} mesure(s))")
    print()

if gva:
    print(f"Points GVA.* ({len(gva)}) :")
    for point, nb in gva:
        print(f"  {point:<30} ({nb} mesure(s))")
    print()

if g04:
    print(f"Points G04.* ({len(g04)}) :")
    for point, nb in g04:
        print(f"  {point:<30} ({nb} mesure(s))")
    print()

if autres:
    print(f"Autres points ({len(autres)}) :")
    for point, nb in autres:
        print(f"  {point:<30} ({nb} mesure(s))")
    print()

print("=" * 80)
print()
print("Ces points ont été mesurés mais n'ont pas de coordonnées de référence.")
print("Ils seront calculés lors du traitement du carnet.")
