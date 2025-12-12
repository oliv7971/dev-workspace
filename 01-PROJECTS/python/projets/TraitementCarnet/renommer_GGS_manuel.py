#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renommages manuels supplémentaires dans POLYGGS-251204-G.geo
"""

import re

fichier_in = "carnet/POLYGGS-251204-G.geo"
fichier_out = "carnet/POLYGGS-251204-H.geo"

# Liste des renommages à effectuer
renommages = {
    'GVA.P06G': '006.GVA.2G',
    'GVA.P11G': '011.GVA.2G',
    'G04.P06G': '006.GVA.2G',
    'G04.P11G': '011.GVA.2G',
    'GGS.S2.1': 'S2',
    'GVA.C401': 'C.401.GVA.2',
    'GVA.C402': 'C.402.GVA.2',
    'GVA.C403': 'C.403.GVA.2',
    'GVA.C404': 'C.404.GVA.2',
    'GVA.C405': 'C.405.GVA.2',
    'GVA.C202': 'C.202GRD.1G',
    'GVA.C408': 'C.408.GRD.2',
    'GVA.C198': 'C.198.GRD.2',
    'GVA.C188': 'C.188.GRD.2G',
    'GVA.A1001': 'REF_1101',
    'GVA.A1007': 'REF_1107',
}

# Lire le fichier
with open(fichier_in, 'r', encoding='utf-8') as f:
    contenu = f.read()

# Appliquer les renommages
compteur = {}
for ancien, nouveau in renommages.items():
    pattern = r'(?<=\s)' + re.escape(ancien) + r'(?=\s|$)'
    nb = len(re.findall(pattern, contenu))
    compteur[ancien] = nb
    contenu = re.sub(pattern, nouveau, contenu)

# Sauvegarder
with open(fichier_out, 'w', encoding='utf-8') as f:
    f.write(contenu)

# Affichage des résultats
print("=" * 80)
print("RENOMMAGES MANUELS - POLYGGS-251204-G.geo")
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
