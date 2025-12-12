#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renommages GGS.S1.1, GGS.S2.2 et affichage GVA dans POLYGGS-251204-D.geo
"""

import re

fichier_in = "carnet/POLYGGS-251204-D.geo"
fichier_out = "carnet/POLYGGS-251204-E.geo"

# Liste des renommages à effectuer
renommages = {
    'GGS.S1.1': 'S1',
    'GGS.S2.2': 'S2',
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
print("RENOMMAGES - POLYGGS-251204-D.geo")
print("=" * 80)
print()

total = 0
for ancien, nouveau in sorted(renommages.items()):
    nb = compteur[ancien]
    if nb > 0:
        total += nb
        print(f"  {ancien:<25} -> {nouveau:<25} ({nb} occurrence(s))")

print()
print(f"Total : {total} remplacements effectués")
print()
print(f"Fichier de sortie : {fichier_out}")
print("=" * 80)
print()
print("INFO: Points GVA.P06G et GVA.P11G trouvés (12 mesures)")
print("      Précisez les noms de destination pour ces points.")
