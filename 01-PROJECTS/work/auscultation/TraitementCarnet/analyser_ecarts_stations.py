#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des écarts entre stations pour identifier les problèmes de calage
pour le carnet Gha-poly&aucultations-251209-H.geo
"""

import re
from collections import defaultdict
import math

def lire_fichier_geo(chemin):
    """Lit le fichier .geo et extrait les points"""
    points = {}
    
    with open(chemin, 'r', encoding='utf-8') as f:
        for ligne in f:
            # Extraire les points (type 0 ou 3)
            match = re.match(r'^\d+\s+Point\s+(\S+)\s+[03]\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)', ligne)
            if match:
                nom = match.group(1)
                x = float(match.group(2))
                y = float(match.group(3))
                z = float(match.group(4))
                points[nom] = (x, y, z)
    
    return points

def extraire_nom_base(nom):
    """Extrait le nom de base et le préfixe station"""
    prefixes = ['S1_', 'S2_', 'S3_', 'S4_', 'X_', 'ref_']
    for prefix in prefixes:
        if nom.startswith(prefix):
            return prefix, nom[len(prefix):]
    return None, nom

def calculer_ecart(coord1, coord2):
    """Calcule l'écart planimétrique et altimétrique entre deux points"""
    dx = coord1[0] - coord2[0]
    dy = coord1[1] - coord2[1]
    dz = coord1[2] - coord2[2]
    
    ecart_xy = math.sqrt(dx**2 + dy**2) * 1000  # en mm
    ecart_z = abs(dz) * 1000  # en mm
    
    return ecart_xy, ecart_z, dx*1000, dy*1000, dz*1000

def analyser_ecarts_stations(fichier):
    """Analyse les écarts entre les rayonnés de chaque station"""
    print(f"Lecture du fichier: {fichier}")
    points = lire_fichier_geo(fichier)
    
    print(f"Total de {len(points)} points lus\n")
    
    # Grouper les points par station et nom de base
    groupes = defaultdict(lambda: defaultdict(list))
    
    for nom, coords in points.items():
        prefix, nom_base = extraire_nom_base(nom)
        if prefix and prefix in ['S1_', 'S2_', 'S3_', 'S4_']:
            groupes[nom_base][prefix].append((nom, coords))
    
    # Filtrer les points observés depuis plusieurs stations
    points_multiples = {k: v for k, v in groupes.items() if len(v) > 1}
    
    print(f"Points rayonnés depuis plusieurs stations: {len(points_multiples)}\n")
    
    # Analyser les écarts entre stations pour chaque point
    resultats = []
    ecarts_par_station = defaultdict(lambda: {'nb': 0, 'total_xy': 0, 'total_z': 0, 'max_xy': 0, 'max_z': 0})
    
    for nom_base, stations in points_multiples.items():
        # Comparer chaque paire de stations
        station_list = sorted(stations.keys())
        ecarts_point = []
        max_xy = 0
        max_z = 0
        
        for i, st1 in enumerate(station_list):
            for st2 in station_list[i+1:]:
                if stations[st1] and stations[st2]:
                    nom1, coords1 = stations[st1][0]
                    nom2, coords2 = stations[st2][0]
                    
                    ecart_xy, ecart_z, dx, dy, dz = calculer_ecart(coords1, coords2)
                    
                    ecarts_point.append({
                        'station1': st1,
                        'station2': st2,
                        'nom1': nom1,
                        'nom2': nom2,
                        'ecart_xy': ecart_xy,
                        'ecart_z': ecart_z,
                        'dx': dx,
                        'dy': dy,
                        'dz': dz
                    })
                    
                    max_xy = max(max_xy, ecart_xy)
                    max_z = max(max_z, ecart_z)
                    
                    # Accumuler pour statistiques par station
                    paire = f"{st1}-{st2}"
                    ecarts_par_station[paire]['nb'] += 1
                    ecarts_par_station[paire]['total_xy'] += ecart_xy
                    ecarts_par_station[paire]['total_z'] += ecart_z
                    ecarts_par_station[paire]['max_xy'] = max(ecarts_par_station[paire]['max_xy'], ecart_xy)
                    ecarts_par_station[paire]['max_z'] = max(ecarts_par_station[paire]['max_z'], ecart_z)
        
        if ecarts_point:
            resultats.append({
                'nom_base': nom_base,
                'nb_stations': len(station_list),
                'stations': station_list,
                'max_xy': max_xy,
                'max_z': max_z,
                'ecarts': ecarts_point
            })
    
    # Trier par écart XY décroissant
    resultats.sort(key=lambda x: x['max_xy'], reverse=True)
    
    # Afficher les statistiques par paire de stations
    print("=" * 100)
    print("STATISTIQUES PAR PAIRE DE STATIONS")
    print("=" * 100)
    print(f"{'Stations':<15} {'Nb points':>10} {'Écart XY moy':>15} {'Écart XY max':>15} {'Écart Z moy':>15} {'Écart Z max':>15}")
    print("=" * 100)
    
    paires_triees = sorted(ecarts_par_station.items(), key=lambda x: x[1]['total_xy']/x[1]['nb'], reverse=True)
    
    for paire, stats in paires_triees:
        moy_xy = stats['total_xy'] / stats['nb']
        moy_z = stats['total_z'] / stats['nb']
        print(f"{paire:<15} {stats['nb']:>10} {moy_xy:>14.1f}mm {stats['max_xy']:>14.1f}mm {moy_z:>14.1f}mm {stats['max_z']:>14.1f}mm")
    
    print("=" * 100)
    print()
    
    # Afficher le TOP 20 avec détails
    print("\n" + "=" * 120)
    print("TOP 20 des points avec les plus grands écarts entre stations")
    print("=" * 120)
    
    for i, r in enumerate(resultats[:20], 1):
        print(f"\n{i}. {r['nom_base']} ({r['nb_stations']} stations: {', '.join(r['stations'])})")
        print(f"   Écart XY max: {r['max_xy']:.1f}mm, Écart Z max: {r['max_z']:.1f}mm")
        print(f"   Détail des écarts entre stations:")
        for e in r['ecarts']:
            print(f"      {e['station1']}-{e['station2']:<10} : XY={e['ecart_xy']:>6.1f}mm  Z={e['ecart_z']:>6.1f}mm  (dX={e['dx']:>6.1f}  dY={e['dy']:>6.1f}  dZ={e['dz']:>6.1f})")
    
    # Statistiques globales
    print("\n" + "=" * 100)
    print("STATISTIQUES GLOBALES")
    print("=" * 100)
    
    nb_total = len(resultats)
    nb_xy_5mm = sum(1 for r in resultats if r['max_xy'] <= 5)
    nb_xy_10mm = sum(1 for r in resultats if r['max_xy'] <= 10)
    nb_xy_20mm = sum(1 for r in resultats if r['max_xy'] <= 20)
    
    nb_z_5mm = sum(1 for r in resultats if r['max_z'] <= 5)
    nb_z_10mm = sum(1 for r in resultats if r['max_z'] <= 10)
    nb_z_20mm = sum(1 for r in resultats if r['max_z'] <= 20)
    
    print(f"Total points analysés: {nb_total}")
    print()
    print("Écarts planimétriques (XY):")
    print(f"  ≤ 5mm:  {nb_xy_5mm:>4} ({nb_xy_5mm*100/nb_total:>5.1f}%)")
    print(f"  ≤ 10mm: {nb_xy_10mm:>4} ({nb_xy_10mm*100/nb_total:>5.1f}%)")
    print(f"  ≤ 20mm: {nb_xy_20mm:>4} ({nb_xy_20mm*100/nb_total:>5.1f}%)")
    print(f"  > 20mm: {nb_total-nb_xy_20mm:>4} ({(nb_total-nb_xy_20mm)*100/nb_total:>5.1f}%)")
    print()
    print("Écarts altimétriques (Z):")
    print(f"  ≤ 5mm:  {nb_z_5mm:>4} ({nb_z_5mm*100/nb_total:>5.1f}%)")
    print(f"  ≤ 10mm: {nb_z_10mm:>4} ({nb_z_10mm*100/nb_total:>5.1f}%)")
    print(f"  ≤ 20mm: {nb_z_20mm:>4} ({nb_z_20mm*100/nb_total:>5.1f}%)")
    print(f"  > 20mm: {nb_total-nb_z_20mm:>4} ({(nb_total-nb_z_20mm)*100/nb_total:>5.1f}%)")
    
    if nb_total > 0:
        moy_xy = sum(r['max_xy'] for r in resultats) / nb_total
        moy_z = sum(r['max_z'] for r in resultats) / nb_total
        print()
        print(f"Écart XY moyen: {moy_xy:.1f}mm")
        print(f"Écart Z moyen:  {moy_z:.1f}mm")
    
    print("=" * 100)

if __name__ == '__main__':
    analyser_ecarts_stations('carnet/Gha-poly&aucultations-251209-H.geo')
