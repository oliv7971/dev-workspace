#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des visées multiples sur polyGRD6-251204-C.geo
Détecte les écarts d'angles et distances entre observations
"""

import math
from collections import defaultdict

def lire_mesures(fichier):
    """Lit les mesures depuis un fichier .geo"""
    mesures = defaultdict(list)
    station_courante = None
    
    with open(fichier, 'r', encoding='utf-8') as f:
        for ligne in f:
            parties = ligne.strip().split()
            if len(parties) < 2:
                continue
            
            # Détecter les stations
            if parties[1] == 'Station':
                station_courante = parties[2]  # Nom de la station
                continue
            
            # Lire les mesures
            if parties[1] == 'Mesure' and len(parties) >= 7:
                cst_prisme = parties[0]  # Constante de prisme
                point = parties[2]       # Nom du point visé
                hauteur = float(parties[3])  # Hauteur
                hz = float(parties[4])       # Angle horizontal (gon)
                v = float(parties[5])        # Angle vertical (gon)
                d = float(parties[6])        # Distance inclinée (m)
                
                mesures[point].append({
                    'station': station_courante,
                    'cst_prisme': cst_prisme,
                    'hauteur': hauteur,
                    'hz': hz,
                    'v': v,
                    'd': d
                })
    
    return mesures

def gon_to_deg(gon):
    """Convertit des gons en degrés"""
    return gon * 0.9

def analyser_ecarts(mesures):
    """Analyse les écarts entre mesures multiples"""
    resultats = []
    
    for point, liste_mesures in sorted(mesures.items()):
        if len(liste_mesures) < 2:
            continue
        
        # Séparer par station
        par_station = defaultdict(list)
        for m in liste_mesures:
            par_station[m['station']].append(m)
        
        for station, mesures_st in par_station.items():
            if len(mesures_st) < 2:
                continue
            
            # Calculer moyenne et écarts
            hz_vals = [m['hz'] for m in mesures_st]
            v_vals = [m['v'] for m in mesures_st]
            d_vals = [m['d'] for m in mesures_st]
            
            # Gérer les angles circulaires (200 gon de différence = double retournement)
            hz_corrected = []
            for hz in hz_vals:
                if hz > 200:
                    hz_corrected.append(hz - 200)
                else:
                    hz_corrected.append(hz)
            
            # Vérifier si on a des doubles retournements
            has_circle_1 = any(hz < 200 for hz in hz_vals)
            has_circle_2 = any(hz >= 200 for hz in hz_vals)
            
            if has_circle_1 and has_circle_2:
                # On a des mesures sur les 2 cercles
                circle_1 = [m for m in mesures_st if m['hz'] < 200]
                circle_2 = [m for m in mesures_st if m['hz'] >= 200]
                
                # Moyenne de chaque cercle
                hz_c1_mean = sum(m['hz'] for m in circle_1) / len(circle_1)
                hz_c2_mean = (sum(m['hz'] for m in circle_2) / len(circle_2)) - 200
                
                # Écart entre cercles (doit être proche de 0)
                ecart_cercles = abs(hz_c1_mean - hz_c2_mean)
                ecart_cercles_mgon = ecart_cercles * 1000
                
                # Stats sur chaque cercle
                hz_c1_max_ecart = max(abs(m['hz'] - hz_c1_mean) for m in circle_1) * 1000
                hz_c2_max_ecart = max(abs((m['hz'] - 200) - hz_c2_mean) for m in circle_2) * 1000
                
                # Distances
                d_mean = sum(m['d'] for m in mesures_st) / len(mesures_st)
                d_max_ecart = max(abs(m['d'] - d_mean) for m in mesures_st) * 1000
                
                # Angles verticaux (correction 300 gon = cercle gauche)
                v_corrected = []
                for m in mesures_st:
                    if m['v'] > 200:
                        v_corrected.append(400 - m['v'])  # Ramener au cercle droit
                    else:
                        v_corrected.append(m['v'])
                
                v_mean = sum(v_corrected) / len(v_corrected)
                v_max_ecart = max(abs(v - v_mean) for v in v_corrected) * 1000
                
                resultats.append({
                    'point': point,
                    'station': station,
                    'nb_mesures': len(mesures_st),
                    'nb_c1': len(circle_1),
                    'nb_c2': len(circle_2),
                    'ecart_cercles_mgon': ecart_cercles_mgon,
                    'hz_c1_max_ecart_mgon': hz_c1_max_ecart,
                    'hz_c2_max_ecart_mgon': hz_c2_max_ecart,
                    'v_max_ecart_mgon': v_max_ecart,
                    'd_mean': d_mean,
                    'd_max_ecart_mm': d_max_ecart,
                    'type': 'double_retournement'
                })
            else:
                # Mesures simples (même cercle)
                hz_mean = sum(hz_corrected) / len(hz_corrected)
                v_mean = sum(v_vals) / len(v_vals)
                d_mean = sum(d_vals) / len(d_vals)
                
                hz_max_ecart = max(abs(hz - hz_mean) for hz in hz_corrected) * 1000  # en mgon
                v_max_ecart = max(abs(v - v_mean) for v in v_vals) * 1000
                d_max_ecart = max(abs(d - d_mean) for d in d_vals) * 1000  # en mm
                
                resultats.append({
                    'point': point,
                    'station': station,
                    'nb_mesures': len(mesures_st),
                    'hz_max_ecart_mgon': hz_max_ecart,
                    'v_max_ecart_mgon': v_max_ecart,
                    'd_mean': d_mean,
                    'd_max_ecart_mm': d_max_ecart,
                    'type': 'simple'
                })
    
    return resultats

def afficher_resultats(resultats):
    """Affiche les résultats de l'analyse"""
    print("=" * 130)
    print("ANALYSE DES VISEES MULTIPLES - polyGRD6-251204-C.geo")
    print("=" * 130)
    print()
    
    # Séparer par type
    doubles = [r for r in resultats if r['type'] == 'double_retournement']
    simples = [r for r in resultats if r['type'] == 'simple']
    
    if doubles:
        print("DOUBLE RETOURNEMENT (Cercle 1 et Cercle 2)")
        print("-" * 130)
        print(f"{'Point':<20} {'St.':<6} {'N':<3} {'C1':<3} {'C2':<3} {'Δ Cercles':<12} {'Δ Hz C1':<12} {'Δ Hz C2':<12} {'Δ V':<12} {'Dist.':<8} {'Δ D':<10}")
        print(f"{'':>20} {'':>6} {'':>3} {'':>3} {'':>3} {'(mgon)':<12} {'(mgon)':<12} {'(mgon)':<12} {'(mgon)':<12} {'(m)':<8} {'(mm)':<10}")
        print("-" * 130)
        
        for r in doubles:
            flag = ""
            if r['ecart_cercles_mgon'] > 5:  # > 5 mgon = 1.6"
                flag = " ⚠"
            if r['d_max_ecart_mm'] > 3:
                flag += " ⚠D"
            
            print(f"{r['point']:<20} {r['station']:<6} {r['nb_mesures']:<3} {r['nb_c1']:<3} {r['nb_c2']:<3} "
                  f"{r['ecart_cercles_mgon']:>10.1f}  {r['hz_c1_max_ecart_mgon']:>10.1f}  "
                  f"{r['hz_c2_max_ecart_mgon']:>10.1f}  {r['v_max_ecart_mgon']:>10.1f}  "
                  f"{r['d_mean']:>7.3f} {r['d_max_ecart_mm']:>9.1f}{flag}")
        print()
    
    if simples:
        print("MESURES SIMPLES (même cercle)")
        print("-" * 100)
        print(f"{'Point':<20} {'St.':<6} {'N':<3} {'Δ Hz max':<12} {'Δ V max':<12} {'Distance':<10} {'Δ D max':<10}")
        print(f"{'':>20} {'':>6} {'':>3} {'(mgon)':<12} {'(mgon)':<12} {'(m)':<10} {'(mm)':<10}")
        print("-" * 100)
        
        for r in simples:
            flag = ""
            if r['hz_max_ecart_mgon'] > 3:
                flag = " ⚠"
            if r['d_max_ecart_mm'] > 3:
                flag += " ⚠D"
            
            print(f"{r['point']:<20} {r['station']:<6} {r['nb_mesures']:<3} "
                  f"{r['hz_max_ecart_mgon']:>10.1f}  {r['v_max_ecart_mgon']:>10.1f}  "
                  f"{r['d_mean']:>9.3f} {r['d_max_ecart_mm']:>9.1f}{flag}")
    
    print("=" * 130)
    print()
    print("LÉGENDE:")
    print("  Δ Cercles : Écart entre moyenne cercle 1 et cercle 2 (doit être proche de 0)")
    print("  Δ Hz/V    : Écart maximal par rapport à la moyenne sur un même cercle")
    print("  Δ D       : Écart maximal de distance")
    print("  ⚠         : Écart angulaire > seuil (5 mgon pour cercles, 3 mgon pour Hz)")
    print("  ⚠D        : Écart distance > 3 mm")
    print()
    
    # Points particuliers
    print("POINTS À ATTENTION PARTICULIÈRE:")
    print("-" * 130)
    
    problemes = []
    for r in resultats:
        issues = []
        if r['type'] == 'double_retournement':
            if r['ecart_cercles_mgon'] > 5:
                issues.append(f"Écart cercles: {r['ecart_cercles_mgon']:.1f} mgon")
        else:
            if r['hz_max_ecart_mgon'] > 3:
                issues.append(f"Écart Hz: {r['hz_max_ecart_mgon']:.1f} mgon")
        
        if r['d_max_ecart_mm'] > 3:
            issues.append(f"Écart distance: {r['d_max_ecart_mm']:.1f} mm")
        
        if issues:
            problemes.append((r['point'], r['station'], ', '.join(issues)))
    
    if problemes:
        for point, station, desc in problemes:
            print(f"  • {point:<20} (Station {station}) : {desc}")
    else:
        print("  ✓ Aucun problème détecté - Toutes les visées sont cohérentes")
    
    print("=" * 130)
    
    # Focus sur 115GRD.3G
    for r in resultats:
        if '115GRD.3G' in r['point']:
            print()
            print("=" * 130)
            print(f"FOCUS SUR {r['point']} (visée rasante)")
            print("=" * 130)
            if r['type'] == 'double_retournement':
                print(f"  Nombre total de mesures : {r['nb_mesures']} ({r['nb_c1']} sur C1, {r['nb_c2']} sur C2)")
                print(f"  Écart entre cercles     : {r['ecart_cercles_mgon']:.2f} mgon ({r['ecart_cercles_mgon']*0.324:.1f}\")")
                print(f"  Écart max Hz cercle 1   : {r['hz_c1_max_ecart_mgon']:.2f} mgon")
                print(f"  Écart max Hz cercle 2   : {r['hz_c2_max_ecart_mgon']:.2f} mgon")
                print(f"  Écart max V             : {r['v_max_ecart_mgon']:.2f} mgon ({r['v_max_ecart_mgon']*0.324:.1f}\")")
                print(f"  Distance moyenne        : {r['d_mean']:.3f} m")
                print(f"  Écart max distance      : {r['d_max_ecart_mm']:.1f} mm")
                
                if r['ecart_cercles_mgon'] < 3 and r['d_max_ecart_mm'] < 2:
                    print()
                    print("  ✓ EXCELLENT - Visée rasante très stable malgré l'angle difficile")
                elif r['ecart_cercles_mgon'] < 5 and r['d_max_ecart_mm'] < 3:
                    print()
                    print("  ✓ BON - Visée rasante acceptable")
                else:
                    print()
                    print("  ⚠ Attention - Vérifier la qualité de la visée")
            print("=" * 130)

# Main
fichier = "carnet/polyGRD6-251204-C.geo"
mesures = lire_mesures(fichier)
resultats = analyser_ecarts(mesures)
afficher_resultats(resultats)
