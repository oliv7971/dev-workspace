#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renommage des correspondances automatiques dans POLYGGS-251204-F.geo
"""

import re

fichier_in = "carnet/POLYGGS-251204-F.geo"
fichier_out = "carnet/POLYGGS-251204-G.geo"

# Liste des renommages à effectuer (haute confiance)
renommages = {
    'GVA.S073': 'ref_S073',
    'GGS.S202': 'ref_S202',
    'GVA.S072': 'ref_S072',
    'GGS.S315': 'ref_S315',
    'GGS.S205': 'ref_S205',
    'GGS.S314': 'ref_S314',
    'GGS.S201': 'ref_S201',
    'GGS.S311': 'ref_S311',
    'GGS.S203': 'ref_S203',
    'GVA.S075': 'ref_S075',
    'GGS.S312': 'ref_S312',
    'GVA.S071': 'ref_S071',
    'GGS.S313': 'ref_S313',
    'GGS.T38D': '38.GGS.8D',
    'GGS.T48D': '48.GGS.5D',
    'GGS.T51D': '51.GGS.4D',
    'GGS.T51G': '51.GGS.4G',
    'GGS.T43G': '43.GGS.5G',
    'GGS.T43D': '43.GGS.6D',
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
print("RENOMMAGES AUTOMATIQUES - POLYGGS-251204-F.geo")
print("=" * 80)
print()
print("Points renommés :")
print("-" * 80)

total = 0
for ancien, nouveau in sorted(renommages.items()):
    nb = compteur[ancien]
    if nb > 0:
        total += nb
        print(f"  {ancien:<30} -> {nouveau:<30} ({nb} occurrence(s))")

print("-" * 80)
print(f"Total : {total} remplacements effectués")
print()
print(f"Fichier de sortie : {fichier_out}")
print("=" * 80)
