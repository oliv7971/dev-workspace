#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suppression des préfixes S1. à S6. dans POLYGGS-251204-A.geo
"""

import re

fichier_in = "carnet/POLYGGS-251204-A.geo"
fichier_out = "carnet/POLYGGS-251204-B.geo"

# Lire le fichier
with open(fichier_in, 'r', encoding='utf-8') as f:
    contenu = f.read()

# Supprimer les préfixes S1. S2. S3. S4. S5. S6.
# Pattern: S[1-6]. suivi d'un caractère non-espace
pattern_prefixes = r'(?<=\s)S[1-6]\.'
nb_prefixes = len(re.findall(pattern_prefixes, contenu))
contenu = re.sub(pattern_prefixes, '', contenu)

# Sauvegarder
with open(fichier_out, 'w', encoding='utf-8') as f:
    f.write(contenu)

# Affichage des résultats
print("=" * 80)
print("SUPPRESSION DES PREFIXES - POLYGGS-251204-A.geo")
print("=" * 80)
print()
print(f"Suppression prefixes S1. à S6. : {nb_prefixes} suppression(s)")
print()
print("=" * 80)
print(f"Fichier de sortie : {fichier_out}")
print("=" * 80)
