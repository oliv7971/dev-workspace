#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrections supplémentaires sur polyGRD6-251204-B.geo
"""

import re

fichier_in = "carnet/polyGRD6-251204-B.geo"
fichier_out = "carnet/polyGRD6-251204-C.geo"

# Lire le fichier
with open(fichier_in, 'r', encoding='utf-8') as f:
    contenu = f.read()

# 1. Renommer S1.C.142DD -> C.142GRD.11D
pattern_142dd = r'(?<=\s)S1\.C\.142DD(?=\s|$)'
nb_142dd = len(re.findall(pattern_142dd, contenu))
contenu = re.sub(pattern_142dd, 'C.142GRD.11D', contenu)

# 2. Supprimer les préfixes S1. S2. S3. S4. S5.
# Pattern: S[1-5]. suivi d'un caractère non-espace
pattern_prefixes = r'(?<=\s)S[1-5]\.'
nb_prefixes = len(re.findall(pattern_prefixes, contenu))
contenu = re.sub(pattern_prefixes, '', contenu)

# Sauvegarder
with open(fichier_out, 'w', encoding='utf-8') as f:
    f.write(contenu)

# Affichage des résultats
print("=" * 80)
print("CORRECTIONS SUPPLEMENTAIRES - polyGRD6-251204-B.geo")
print("=" * 80)
print()
print(f"1. S1.C.142DD -> C.142GRD.11D : {nb_142dd} remplacement(s)")
print(f"2. Suppression prefixes S1. a S5. : {nb_prefixes} suppression(s)")
print()
print(f"Total : {nb_142dd + nb_prefixes} modifications")
print()
print("=" * 80)
print(f"Fichier de sortie : {fichier_out}")
print("=" * 80)
