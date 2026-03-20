#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renommer les points dans polyGRD6-251204.geo
"""

import re

fichier_in = "carnet/polyGRD6-251204.geo"
fichier_out = "carnet/polyGRD6-251204-B.geo"

# Dictionnaire des renommages
renommages = {
    'S1.T06G': 'H06GRD.3G',
    'S1.T06D': 'H06GRD.3D',
    'S1.P115G': '115GRD.3G',
    'S1.T.H09D': 'T.H09D',
    'S1.T.145D': 'T.145D',
    'S1.T.131G': 'T.131G',
    'S1.P.H06G': 'H06GRD.3G',
    'S1.P.H09G': 'H09GRD.3G',
    'S1.P.H06D': 'H06GRD.3D',
    'S1.P.115G': '115GRD.3G',
    'S1.P.125G': '125GRD.4G',
    'S1.P.142D': '142GRD.1D',
    'S1.P.142G': '142GRD.1G',
    'S1.CX.D1G': 'CX.D1.1',
    'S1.CX.G1G': 'CX.G1.1',
    'S1.C.1043N': 'C.1043GRD.2N',
    'S1.C.1044N': 'C.1044GRD.2N',
    'S1.C.537': 'C.1537GRD.4G',
    'S1.C.142D': 'C.142GRD.11D',
    'S1.C.1170': 'C.1170GRD.3G',
}

# Lire le fichier
with open(fichier_in, 'r', encoding='utf-8') as f:
    contenu = f.read()

# Compteur de remplacements
compteur = {}

# Effectuer les renommages avec lookbehind/lookahead pour éviter les remplacements partiels
for ancien, nouveau in renommages.items():
    # Pattern: le nom doit être entouré d'espaces ou en fin de ligne
    pattern = r'(?<=\s)' + re.escape(ancien) + r'(?=\s|$)'
    
    # Compter les occurrences
    nb = len(re.findall(pattern, contenu))
    if nb > 0:
        compteur[ancien] = nb
        contenu = re.sub(pattern, nouveau, contenu)

# Sauvegarder
with open(fichier_out, 'w', encoding='utf-8') as f:
    f.write(contenu)

# Affichage des résultats
print("=" * 80)
print("RENOMMAGE DES POINTS - polyGRD6-251204.geo")
print("=" * 80)
print()

if compteur:
    print(f"Points renommes :")
    print("-" * 80)
    for ancien, nb in sorted(compteur.items()):
        nouveau = renommages[ancien]
        print(f"  {ancien:<20} -> {nouveau:<20} ({nb} occurrence(s))")
    
    print()
    print(f"Total : {sum(compteur.values())} remplacements effectues")
else:
    print("Aucun point trouve a renommer")

print()
print("=" * 80)
print(f"Fichier de sortie : {fichier_out}")
print("=" * 80)
