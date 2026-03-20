#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère un fichier .geo avec les coordonnées moyennées
pour les points ayant plusieurs déterminations (X_, S1_, S2_, S3_, S4_, S5_)
"""

import math
from collections import defaultdict

def lire_points(fichier):
    """Lit tous les points depuis un fichier .geo calculé"""
    points = []
    header_lines = []
    
    with open(fichier, 'r', encoding='utf-8') as f:
        for ligne in f:
            if ligne.strip().startswith('Option'):
                header_lines.append(ligne)
                continue
            
            if not ligne.strip():
                continue
            
            parties = ligne.strip().split()
            if len(parties) < 7:
                continue
            
            if parties[1] != 'Point':
                continue
            
            nom_complet = parties[2]
            type_point = int(parties[3])
            x = float(parties[4])
            y = float(parties[5])
            z = float(parties[6])
            
            # Déterminer le type et le nom de base
            if nom_complet.startswith('X_'):
                type_determination = 'X_'
                nom_base = nom_complet[2:]
            elif nom_complet.startswith('S1_'):
                type_determination = 'S1_'
                nom_base = nom_complet[3:]
            elif nom_complet.startswith('S2_'):
                type_determination = 'S2_'
                nom_base = nom_complet[3:]
            elif nom_complet.startswith('S3_'):
                type_determination = 'S3_'
                nom_base = nom_complet[3:]
            elif nom_complet.startswith('S4_'):
                type_determination = 'S4_'
                nom_base = nom_complet[3:]
            elif nom_complet.startswith('S5_'):
                type_determination = 'S5_'
                nom_base = nom_complet[3:]
            else:
                type_determination = 'REF'
                nom_base = nom_complet
            
            points.append({
                'nom_complet': nom_complet,
                'nom_base': nom_base,
                'type_determination': type_determination,
                'type_point': type_point,
                'x': x,
                'y': y,
                'z': z
            })
    
    return points, header_lines

def regrouper_par_point(points):
    """Regroupe les points par leur nom de base"""
    groupes = defaultdict(list)
    
    for p in points:
        groupes[p['nom_base']].append(p)
    
    return groupes

def calculer_moyenne(groupe):
    """Calcule les coordonnées moyennes d'un groupe de points"""
    if len(groupe) == 1:
        # Un seul point, on le garde tel quel
        p = groupe[0]
        return {
            'nom_base': p['nom_base'],
            'nb_determinations': 1,
            'x_moy': p['x'],
            'y_moy': p['y'],
            'z_moy': p['z'],
            'type_point': p['type_point'],
            'ecart_plani_max': 0.0,
            'ecart_alti_max': 0.0
        }
    
    # Calculer les coordonnées moyennes
    x_moy = sum(p['x'] for p in groupe) / len(groupe)
    y_moy = sum(p['y'] for p in groupe) / len(groupe)
    z_moy = sum(p['z'] for p in groupe) / len(groupe)
    
    # Calculer les écarts max
    ecart_plani_max = max(math.sqrt((p['x'] - x_moy)**2 + (p['y'] - y_moy)**2) for p in groupe)
    ecart_alti_max = max(abs(p['z'] - z_moy) for p in groupe)
    
    # Type du point : référence (3) si au moins un REF, sinon calculé (0)
    type_point = 3 if any(p['type_determination'] == 'REF' for p in groupe) else 0
    
    return {
        'nom_base': groupe[0]['nom_base'],
        'nb_determinations': len(groupe),
        'x_moy': x_moy,
        'y_moy': y_moy,
        'z_moy': z_moy,
        'type_point': type_point,
        'ecart_plani_max': ecart_plani_max,
        'ecart_alti_max': ecart_alti_max
    }

def generer_fichier_geo(moyennes, header_lines, fichier_sortie):
    """Génère un fichier .geo avec les coordonnées moyennées"""
    
    # Trier par nom
    moyennes_triees = sorted(moyennes, key=lambda m: m['nom_base'])
    
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        # Écrire l'entête
        for ligne in header_lines:
            f.write(ligne)
        
        # Écrire les points
        for i, m in enumerate(moyennes_triees, start=1):
            # Format Covadis
            ligne = f"{i:06d}  Point            {m['nom_base']:<20} {m['type_point']}  "
            ligne += f"{m['x_moy']:14.6f} {m['y_moy']:14.6f}  {m['z_moy']:13.6f} \n"
            f.write(ligne)

def generer_rapport(moyennes, fichier_rapport):
    """Génère un rapport détaillé des points moyennés"""
    
    moyennes_multiples = sorted([m for m in moyennes if m['nb_determinations'] > 1], 
                                key=lambda x: x['nom_base'])
    
    with open(fichier_rapport, 'w', encoding='utf-8') as f:
        f.write("=" * 120 + "\n")
        f.write("RAPPORT DES POINTS MOYENNÉS\n")
        f.write("=" * 120 + "\n\n")
        
        f.write(f"Total de points moyennés : {len(moyennes_multiples)}\n\n")
        
        f.write("-" * 120 + "\n")
        f.write(f"{'Point':<30} {'Nb':<5} {'X moyen':<16} {'Y moyen':<16} {'Z moyen':<16} {'Écart XY (mm)':<15} {'Écart Z (mm)':<15}\n")
        f.write("-" * 120 + "\n")
        
        for m in moyennes_multiples:
            f.write(f"{m['nom_base']:<30} {m['nb_determinations']:<5} ")
            f.write(f"{m['x_moy']:15.6f}  {m['y_moy']:15.6f}  {m['z_moy']:15.6f}  ")
            f.write(f"{m['ecart_plani_max']*1000:>14.1f}  {m['ecart_alti_max']*1000:>14.1f}\n")
        
        f.write("-" * 120 + "\n")

def afficher_stats(moyennes):
    """Affiche les statistiques sur les moyennes calculées"""
    
    moyennes_multiples = [m for m in moyennes if m['nb_determinations'] > 1]
    moyennes_simples = [m for m in moyennes if m['nb_determinations'] == 1]
    
    print("=" * 120)
    print("GÉNÉRATION DU FICHIER AVEC COORDONNÉES MOYENNÉES")
    print("=" * 120)
    print()
    print(f"Points avec plusieurs déterminations : {len(moyennes_multiples)}")
    print(f"Points avec une seule détermination  : {len(moyennes_simples)}")
    print(f"Total de points                      : {len(moyennes)}")
    print()
    
    if moyennes_multiples:
        ecarts_plani = [m['ecart_plani_max'] for m in moyennes_multiples]
        ecarts_alti = [m['ecart_alti_max'] for m in moyennes_multiples]
        
        print("ÉCARTS MAX ENTRE DÉTERMINATIONS (points moyennés) :")
        print("-" * 120)
        print(f"  Écart planimétrique max : {max(ecarts_plani)*1000:7.1f} mm")
        print(f"  Écart planimétrique moy : {sum(ecarts_plani)/len(ecarts_plani)*1000:7.1f} mm")
        print()
        print(f"  Écart altimétrique max  : {max(ecarts_alti)*1000:7.1f} mm")
        print(f"  Écart altimétrique moy  : {sum(ecarts_alti)/len(ecarts_alti)*1000:7.1f} mm")
        print()
        
        # Points avec écarts importants
        points_attention = [m for m in moyennes_multiples if m['ecart_plani_max'] > 0.005 or m['ecart_alti_max'] > 0.005]
        
        if points_attention:
            print(f"Points avec écart > 5 mm : {len(points_attention)}")
            print("-" * 120)
            print(f"{'Point':<30} {'Nb det.':<8} {'Écart XY (mm)':<15} {'Écart Z (mm)':<15}")
            print("-" * 120)
            
            for m in sorted(points_attention, key=lambda x: x['ecart_plani_max'], reverse=True):
                print(f"{m['nom_base']:<30} {m['nb_determinations']:<8} {m['ecart_plani_max']*1000:>14.1f}  {m['ecart_alti_max']*1000:>14.1f}")
    
    print()
    print("=" * 120)

# Main
fichier_entree = "carnet/POLYGGS-251204-M.geo"
fichier_sortie = "carnet/POLYGGS-251204-N-MOYENNE.geo"
fichier_rapport = "carnet/POLYGGS-251204-N-RAPPORT.txt"

print(f"\nFichier d'entrée  : {fichier_entree}")
print(f"Fichier de sortie : {fichier_sortie}")
print(f"Rapport détaillé  : {fichier_rapport}\n")

# Lire les points
points, header_lines = lire_points(fichier_entree)
print(f"Points lus : {len(points)}\n")

# Regrouper par nom de base
groupes = regrouper_par_point(points)

# Calculer les moyennes
moyennes = []
for nom_base, groupe in groupes.items():
    moyenne = calculer_moyenne(groupe)
    moyennes.append(moyenne)

# Afficher les stats
afficher_stats(moyennes)

# Générer le fichier
generer_fichier_geo(moyennes, header_lines, fichier_sortie)

# Générer le rapport
generer_rapport(moyennes, fichier_rapport)

print(f"\n✓ Fichier généré : {fichier_sortie}")
print(f"✓ Rapport généré : {fichier_rapport}\n")
