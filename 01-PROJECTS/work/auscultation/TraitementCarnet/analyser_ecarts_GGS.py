#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des écarts entre différentes déterminations d'un même point
- Points normaux (références)
- Points X_ (intersections entre stations)
- Points S1_, S2_, S3_, S4_, S5_ (rayonnés depuis chaque station)
"""

import math
from collections import defaultdict

def lire_points(fichier):
    """Lit tous les points depuis un fichier .geo calculé"""
    points = []
    
    with open(fichier, 'r', encoding='utf-8') as f:
        for ligne in f:
            if not ligne.strip() or ligne.startswith('Option'):
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
    
    return points

def regrouper_par_point(points):
    """Regroupe les points par leur nom de base"""
    groupes = defaultdict(list)
    
    for p in points:
        groupes[p['nom_base']].append(p)
    
    return groupes

def calculer_ecarts_groupe(groupe):
    """Calcule les écarts pour un groupe de points"""
    if len(groupe) <= 1:
        return None
    
    # Calculer les coordonnées moyennes
    x_moy = sum(p['x'] for p in groupe) / len(groupe)
    y_moy = sum(p['y'] for p in groupe) / len(groupe)
    z_moy = sum(p['z'] for p in groupe) / len(groupe)
    
    # Calculer les écarts par rapport à la moyenne
    ecarts = []
    for p in groupe:
        dx = p['x'] - x_moy
        dy = p['y'] - y_moy
        dz = p['z'] - z_moy
        ecart_plani = math.sqrt(dx**2 + dy**2)
        
        ecarts.append({
            'nom_complet': p['nom_complet'],
            'type_determination': p['type_determination'],
            'dx': dx,
            'dy': dy,
            'dz': dz,
            'ecart_plani': ecart_plani
        })
    
    # Calculer les écarts max
    ecart_plani_max = max(e['ecart_plani'] for e in ecarts)
    ecart_alti_max = max(abs(e['dz']) for e in ecarts)
    
    # Trouver le point de référence si présent
    point_ref = next((p for p in groupe if p['type_determination'] == 'REF'), None)
    
    return {
        'nom_base': groupe[0]['nom_base'],
        'nb_determinations': len(groupe),
        'types': [p['type_determination'] for p in groupe],
        'ecarts': ecarts,
        'ecart_plani_max': ecart_plani_max,
        'ecart_alti_max': ecart_alti_max,
        'x_moy': x_moy,
        'y_moy': y_moy,
        'z_moy': z_moy,
        'has_ref': point_ref is not None,
        'coords_ref': (point_ref['x'], point_ref['y'], point_ref['z']) if point_ref else None
    }

def afficher_resultats(resultats):
    """Affiche les résultats d'analyse des écarts"""
    
    # Filtrer les points avec plusieurs déterminations
    points_multiples = [r for r in resultats if r is not None]
    
    if not points_multiples:
        print("Aucun point avec plusieurs déterminations trouvé.")
        return
    
    # Tri par écart planimétrique décroissant
    points_tries = sorted(points_multiples, key=lambda r: r['ecart_plani_max'], reverse=True)
    
    print("=" * 140)
    print("ANALYSE DES ÉCARTS - POINTS AVEC PLUSIEURS DÉTERMINATIONS")
    print("=" * 140)
    print()
    print(f"Nombre de points analysés : {len(points_multiples)}")
    print()
    
    # Statistiques globales
    ecarts_plani = [r['ecart_plani_max'] for r in points_multiples]
    ecarts_alti = [r['ecart_alti_max'] for r in points_multiples]
    
    print("STATISTIQUES GLOBALES:")
    print("-" * 140)
    print(f"  Écart planimétrique max : {max(ecarts_plani)*1000:7.1f} mm")
    print(f"  Écart planimétrique moy : {sum(ecarts_plani)/len(ecarts_plani)*1000:7.1f} mm")
    print(f"  Écart planimétrique min : {min(ecarts_plani)*1000:7.1f} mm")
    print()
    print(f"  Écart altimétrique max  : {max(ecarts_alti)*1000:7.1f} mm")
    print(f"  Écart altimétrique moy  : {sum(ecarts_alti)/len(ecarts_alti)*1000:7.1f} mm")
    print(f"  Écart altimétrique min  : {min(ecarts_alti)*1000:7.1f} mm")
    print()
    
    # Tableau récapitulatif
    print("TABLEAU RÉCAPITULATIF (TOP 20 par écarts décroissants):")
    print("-" * 140)
    print(f"{'Point':<30} {'Nb':<4} {'Types':<25} {'Écart XY max (mm)':<18} {'Écart Z max (mm)':<18} {'Qualité':<12}")
    print("-" * 140)
    
    points_a_voir = points_tries  # Tous les points, triés par écart décroissant
    
    for r in points_a_voir[:20]:  # Top 20
        types_str = '+'.join(sorted(set(r['types'])))
        if len(types_str) > 24:
            types_str = types_str[:21] + '...'
        
        dxy_mm = r['ecart_plani_max'] * 1000
        dz_mm = r['ecart_alti_max'] * 1000
        
        # Qualité
        if dxy_mm <= 5 and dz_mm <= 5:
            qualite = "✓ Excellent"
        elif dxy_mm <= 10 and dz_mm <= 10:
            qualite = "○ Bon"
        elif dxy_mm <= 20 and dz_mm <= 20:
            qualite = "△ Acceptable"
        else:
            qualite = "⚠ À vérifier"
        
        print(f"{r['nom_base']:<30} {r['nb_determinations']:<4} {types_str:<25} {dxy_mm:>17.1f}  {dz_mm:>17.1f}  {qualite:<12}")
    
    if len(points_a_voir) > 50:
        print(f"\n... et {len(points_a_voir) - 50} autres points")
    
    print("-" * 140)
    
    # Détail des points problématiques
    points_probleme = [r for r in points_multiples if r['ecart_plani_max'] > 0.020 or r['ecart_alti_max'] > 0.020]
    
    if points_probleme:
        print()
        print(f"DÉTAIL DES POINTS À VÉRIFIER (écart > 20 mm) : {len(points_probleme)}")
        print("-" * 140)
        
        for r in sorted(points_probleme, key=lambda x: x['ecart_plani_max'], reverse=True)[:10]:
            print()
            print(f"Point : {r['nom_base']} ({r['nb_determinations']} déterminations)")
            print(f"  Écart plani max : {r['ecart_plani_max']*1000:6.1f} mm")
            print(f"  Écart alti max  : {r['ecart_alti_max']*1000:6.1f} mm")
            print(f"  Coordonnées moyennes : X={r['x_moy']:.3f}  Y={r['y_moy']:.3f}  Z={r['z_moy']:.3f}")
            
            if r['has_ref']:
                print(f"  Écart par rapport à REF :")
                dx_ref = r['x_moy'] - r['coords_ref'][0]
                dy_ref = r['y_moy'] - r['coords_ref'][1]
                dz_ref = r['z_moy'] - r['coords_ref'][2]
                ecart_ref = math.sqrt(dx_ref**2 + dy_ref**2)
                print(f"    dX={dx_ref*1000:+7.1f} mm, dY={dy_ref*1000:+7.1f} mm, dXY={ecart_ref*1000:6.1f} mm, dZ={dz_ref*1000:+7.1f} mm")
            
            print(f"  Détail par détermination :")
            for e in sorted(r['ecarts'], key=lambda x: x['ecart_plani'], reverse=True):
                print(f"    {e['nom_complet']:<35} : dX={e['dx']*1000:+7.1f} mm, dY={e['dy']*1000:+7.1f} mm, dXY={e['ecart_plani']*1000:6.1f} mm, dZ={e['dz']*1000:+7.1f} mm")
    
    # Points excellents
    points_excellents = [r for r in points_multiples if r['ecart_plani_max'] <= 0.005 and r['ecart_alti_max'] <= 0.005]
    print()
    print(f"✓ Points excellents (écart ≤ 5 mm) : {len(points_excellents)} / {len(points_multiples)} ({len(points_excellents)*100/len(points_multiples):.1f}%)")
    
    points_bons = [r for r in points_multiples if r['ecart_plani_max'] <= 0.010 and r['ecart_alti_max'] <= 0.010]
    print(f"○ Points bons (écart ≤ 10 mm) : {len(points_bons)} / {len(points_multiples)} ({len(points_bons)*100/len(points_multiples):.1f}%)")
    
    print()
    print("=" * 140)

# Main
fichier = "carnet/POLYGGS-251204-M.geo"
print(f"\nAnalyse du fichier : {fichier}\n")

points = lire_points(fichier)
print(f"Points lus : {len(points)}")

groupes = regrouper_par_point(points)
print(f"Points uniques : {len(groupes)}")
print()

# Calculer les écarts pour chaque groupe
resultats = []
for nom_base, groupe in groupes.items():
    resultat = calculer_ecarts_groupe(groupe)
    resultats.append(resultat)

afficher_resultats(resultats)
