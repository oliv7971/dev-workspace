#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renommages supplémentaires dans POLYGGS-251204-C.geo
"""

import re

fichier_in = "carnet/POLYGGS-251204-C.geo"
fichier_out = "carnet/POLYGGS-251204-D.geo"

# Liste des renommages à effectuer
renommages = {
    # Points spécifiques
    'GGS.P41D': '43.GGS.6D',
    'GGS.P41G': '43.GGS.5G',
    'GGS.P59D': '59GGS.2D',
    'GGS.P59G': '59GGS.2G',
    'GGS.P19G': '19.GG.10G',
    
    # GGS.S02.x -> S2
    'GGS.S02.1': 'S2',
    'GGS.S02.2': 'S2',
    'GGS.S02.3': 'S2',
    'GGS.S02.4': 'S2',
    'GGS.S02.5': 'S2',
    'GGS.S02.6': 'S2',
    'GGS.S02.7': 'S2',
    'GGS.S02.8': 'S2',
    'GGS.S02.9': 'S2',
    
    # GGS.S1.x -> S1
    'GGS.S1.2': 'S1',
    'GGS.S1.3': 'S1',
    'GGS.S1.4': 'S1',
    'GGS.S1.5': 'S1',
    'GGS.S1.6': 'S1',
    'GGS.S1.7': 'S1',
    'GGS.S1.8': 'S1',
    'GGS.S1.9': 'S1',
}

# Lire le fichier
with open(fichier_in, 'r', encoding='utf-8') as f:
    contenu = f.read()

# Appliquer les renommages
compteur = {}
for ancien, nouveau in renommages.items():
    # Pattern avec lookbehind/lookahead pour matcher exactement le nom
    pattern = r'(?<=\s)' + re.escape(ancien) + r'(?=\s|$)'
    nb = len(re.findall(pattern, contenu))
    compteur[ancien] = nb
    contenu = re.sub(pattern, nouveau, contenu)

# Sauvegarder
with open(fichier_out, 'w', encoding='utf-8') as f:
    f.write(contenu)

# Affichage des résultats
print("=" * 80)
print("RENOMMAGES SUPPLEMENTAIRES - POLYGGS-251204-C.geo")
print("=" * 80)
print()
print("Points renommés :")
print("-" * 80)

total = 0
for ancien, nouveau in sorted(renommages.items()):
    nb = compteur[ancien]
    if nb > 0:
        total += nb
        print(f"  {ancien:<25} -> {nouveau:<25} ({nb} occurrence(s))")

print("-" * 80)
print(f"Total : {total} remplacements effectués")
print()
print(f"Fichier de sortie : {fichier_out}")
print("=" * 80)
