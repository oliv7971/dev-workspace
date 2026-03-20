#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supprime les doublons dans les points de référence (garde la première occurrence)
"""

import re
from collections import OrderedDict

fichier_in = "carnet/poly GMA 251202-B.geo"
fichier_out = "carnet/poly GMA 251202-C.geo"

# Dictionnaire pour tracer les points déjà vus (type 3)
points_vus = set()
lignes_a_garder = []
lignes_supprimees = []

with open(fichier_in, 'r', encoding='utf-8') as f:
    lignes = f.readlines()

for num_ligne, ligne in enumerate(lignes, 1):
    # Vérifier si c'est un point de référence (type 3)
    match = re.match(r'^\d+\s+Point\s+(\S+)\s+3\s+', ligne)
    
    if match:
        nom_point = match.group(1)
        if nom_point in points_vus:
            # C'est un doublon, on le supprime
            lignes_supprimees.append((num_ligne, nom_point, ligne.strip()))
        else:
            # Première occurrence, on la garde
            points_vus.add(nom_point)
            lignes_a_garder.append(ligne)
    else:
        # Pas un point de référence, on garde la ligne
        lignes_a_garder.append(ligne)

# Écriture du fichier nettoyé
with open(fichier_out, 'w', encoding='utf-8') as f:
    f.writelines(lignes_a_garder)

# Affichage du résumé
print("=" * 90)
print("NETTOYAGE DES DOUBLONS")
print("=" * 90)
print()
print(f"Fichier d'entrée  : {fichier_in}")
print(f"Fichier de sortie : {fichier_out}")
print()
print(f"Lignes totales     : {len(lignes)}")
print(f"Lignes conservées  : {len(lignes_a_garder)}")
print(f"Doublons supprimés : {len(lignes_supprimees)}")
print()

if lignes_supprimees:
    print("Doublons supprimés (deuxième occurrence) :")
    print("-" * 90)
    for num, nom, contenu in lignes_supprimees[:10]:  # Afficher les 10 premiers
        print(f"  Ligne {num}: {nom}")
    
    if len(lignes_supprimees) > 10:
        print(f"  ... et {len(lignes_supprimees) - 10} autres")

print()
print("=" * 90)
print(f"✓ Fichier nettoyé créé : {fichier_out}")
print("=" * 90)
