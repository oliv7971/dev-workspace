#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrections C.40x.GVA vers C.40x.GRD dans POLYGGS-251204-H.geo
"""

import re

fichier_in = "carnet/POLYGGS-251204-H.geo"
fichier_out = "carnet/POLYGGS-251204-I.geo"

# Liste des renommages à effectuer
renommages = {
    'C.403.GVA.2': 'C.403.GRD.2',
    'C.404.GVA.2': 'C.404.GRD.2',
    'C.405.GVA.2': 'C.405.GRD.3',
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
print("CORRECTIONS C.40x.GVA -> C.40x.GRD - POLYGGS-251204-H.geo")
print("=" * 80)
print()
print("Points corrigés :")
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
