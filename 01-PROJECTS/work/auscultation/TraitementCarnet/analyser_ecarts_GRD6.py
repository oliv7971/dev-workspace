#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des écarts entre points de référence et points réimplantés
Les points réimplantés commencent par "i_"
"""

import math

def lire_points(fichier):
    """Lit les points depuis un fichier .geo calculé"""
    points_ref = {}
    points_reimplantes = {}
    
    with open(fichier, 'r', encoding='utf-8') as f:
        for ligne in f:
            if not ligne.strip() or ligne.startswith('Option'):
                continue
            
            parties = ligne.strip().split()
            if len(parties) < 7:
                continue
            
            if parties[1] != 'Point':
                continue
            
            nom = parties[2]
            type_point = int(parties[3])
            x = float(parties[4])
            y = float(parties[5])
            z = float(parties[6])
            
            if nom.startswith('i_'):
                # Point réimplanté
                nom_ref = nom[2:]  # Enlever le préfixe "i_"
                points_reimplantes[nom_ref] = {'x': x, 'y': y, 'z': z, 'nom_complet': nom}
            else:
                # Point de référence (type 3) ou calculé (type 0)
                points_ref[nom] = {'x': x, 'y': y, 'z': z, 'type': type_point}
    
    return points_ref, points_reimplantes

def calculer_ecarts(points_ref, points_reimplantes):
    """Calcule les écarts entre points de référence et réimplantés"""
    ecarts = []
    
    for nom_ref, coords_reimpl in points_reimplantes.items():
        if nom_ref not in points_ref:
            print(f"⚠ Point de référence non trouvé : {nom_ref}")
            continue
        
        coords_ref = points_ref[nom_ref]
        
        # Calcul des écarts
        dx = coords_reimpl['x'] - coords_ref['x']
        dy = coords_reimpl['y'] - coords_ref['y']
        dz = coords_reimpl['z'] - coords_ref['z']
        
        # Écart planimétrique
        ecart_plani = math.sqrt(dx**2 + dy**2)
        
        ecarts.append({
            'nom': nom_ref,
            'dx': dx,
            'dy': dy,
            'dz': dz,
            'ecart_plani': ecart_plani,
            'type_ref': coords_ref['type']
        })
    
    return ecarts

def afficher_resultats(ecarts):
    """Affiche les résultats d'analyse des écarts"""
    
    if not ecarts:
        print("Aucun point réimplanté trouvé.")
        return
    
    # Tri par écart planimétrique décroissant
    ecarts_tries = sorted(ecarts, key=lambda e: e['ecart_plani'], reverse=True)
    
    print("=" * 120)
    print("ANALYSE DES ÉCARTS - POINTS RÉIMPLANTÉS vs RÉFÉRENCE")
    print("=" * 120)
    print()
    print(f"Nombre de points analysés : {len(ecarts)}")
    print()
    
    # Statistiques
    ecarts_plani = [e['ecart_plani'] for e in ecarts]
    ecarts_alti = [abs(e['dz']) for e in ecarts]
    
    print("STATISTIQUES:")
    print("-" * 120)
    print(f"  Écart planimétrique max : {max(ecarts_plani)*1000:7.1f} mm")
    print(f"  Écart planimétrique moy : {sum(ecarts_plani)/len(ecarts_plani)*1000:7.1f} mm")
    print(f"  Écart planimétrique min : {min(ecarts_plani)*1000:7.1f} mm")
    print()
    print(f"  Écart altimétrique max  : {max(ecarts_alti)*1000:7.1f} mm")
    print(f"  Écart altimétrique moy  : {sum(ecarts_alti)/len(ecarts_alti)*1000:7.1f} mm")
    print(f"  Écart altimétrique min  : {min(ecarts_alti)*1000:7.1f} mm")
    print()
    
    # Tableau détaillé
    print("ÉCARTS DÉTAILLÉS:")
    print("-" * 120)
    print(f"{'Point':<25} {'Type':<5} {'dX (mm)':<12} {'dY (mm)':<12} {'Écart XY (mm)':<15} {'dZ (mm)':<12} {'Qualité':<10}")
    print("-" * 120)
    
    for e in ecarts_tries:
        dx_mm = e['dx'] * 1000
        dy_mm = e['dy'] * 1000
        dxy_mm = e['ecart_plani'] * 1000
        dz_mm = e['dz'] * 1000
        
        type_str = "Ref" if e['type_ref'] == 3 else "Calc"
        
        # Qualité
        if dxy_mm <= 5 and abs(dz_mm) <= 5:
            qualite = "✓ Excellent"
        elif dxy_mm <= 10 and abs(dz_mm) <= 10:
            qualite = "○ Bon"
        elif dxy_mm <= 20 and abs(dz_mm) <= 20:
            qualite = "△ Moyen"
        else:
            qualite = "⚠ À vérifier"
        
        print(f"{e['nom']:<25} {type_str:<5} {dx_mm:>11.1f}  {dy_mm:>11.1f}  {dxy_mm:>14.1f}  {dz_mm:>11.1f}  {qualite:<10}")
    
    print("-" * 120)
    
    # Points à surveiller
    points_surveillance = [e for e in ecarts if e['ecart_plani'] > 0.010 or abs(e['dz']) > 0.010]
    
    if points_surveillance:
        print()
        print(f"POINTS À SURVEILLER (écart > 10 mm) : {len(points_surveillance)}")
        print("-" * 120)
        for e in points_surveillance:
            print(f"  • {e['nom']:<25} : Écart XY = {e['ecart_plani']*1000:5.1f} mm, dZ = {e['dz']*1000:+6.1f} mm")
    else:
        print()
        print("✓ Tous les points sont dans la tolérance (≤ 10 mm)")
    
    print()
    print("=" * 120)

# Main
fichier = "carnet/polyGRD6-251204-D.geo"
print(f"\nAnalyse du fichier : {fichier}\n")

points_ref, points_reimplantes = lire_points(fichier)
print(f"Points de référence lus  : {len(points_ref)}")
print(f"Points réimplantés lus   : {len(points_reimplantes)}")
print()

ecarts = calculer_ecarts(points_ref, points_reimplantes)
afficher_resultats(ecarts)
