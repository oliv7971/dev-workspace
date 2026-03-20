#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renommage des points GGS.Pxx vers xx.GGS.xx dans POLYGGS-251204-B.geo
"""

import re

fichier_in = "carnet/POLYGGS-251204-B.geo"
fichier_out = "carnet/POLYGGS-251204-C.geo"

# Liste des renommages à effectuer
renommages = {
    'GGS.P03D': '03.GGS.10D',
    'GGS.P03G': '03.GGS.10G',
    'GGS.P10G': '10.GGS.10G',
    'GGS.P14D': '14.GGS.8D',
    'GGS.P14G': '14.GGS.10G',
    'GGS.P26D': '26.GGS.8D',
    'GGS.P31D': '31.GGS.11D',
    'GGS.P31G': '31.GGS.10G',
    'GGS.P35D': '35.GGS.6D',
    'GGS.P38D': '38.GGS.8D',
    'GGS.P38G': '38.GGS.10G',
    'GGS.P51D': '51.GGS.4D',
    'GGS.P51G': '51.GGS.4G',
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
print("RENOMMAGE DES POINTS - POLYGGS-251204-B.geo")
print("=" * 80)
print()
print("Points renommés :")
print("-" * 80)

total = 0
for ancien, nouveau in sorted(renommages.items()):
    nb = compteur[ancien]
    total += nb
    print(f"  {ancien:<25} -> {nouveau:<25} ({nb} occurrence(s))")

print("-" * 80)
print(f"Total : {total} remplacements effectués")
print()
print(f"Fichier de sortie : {fichier_out}")
print("=" * 80)
