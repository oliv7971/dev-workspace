#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suppression des préfixes GGS. dans les visées de POLYGGS-251204-I.geo
"""

import re

fichier_in = "carnet/POLYGGS-251204-I.geo"
fichier_out = "carnet/POLYGGS-251204-J.geo"

# Lire le fichier
with open(fichier_in, 'r', encoding='utf-8') as f:
    contenu = f.read()

# Supprimer les préfixes GGS. dans les noms de points
# Pattern: GGS. suivi d'un caractère non-espace
pattern_prefixes = r'(?<=\s)GGS\.'
nb_prefixes = len(re.findall(pattern_prefixes, contenu))
contenu = re.sub(pattern_prefixes, '', contenu)

# Sauvegarder
with open(fichier_out, 'w', encoding='utf-8') as f:
    f.write(contenu)

# Affichage des résultats
print("=" * 80)
print("SUPPRESSION DES PREFIXES GGS. - POLYGGS-251204-I.geo")
print("=" * 80)
print()
print(f"Suppression prefixes GGS. : {nb_prefixes} suppression(s)")
print()
print("=" * 80)
print(f"Fichier de sortie : {fichier_out}")
print("=" * 80)
