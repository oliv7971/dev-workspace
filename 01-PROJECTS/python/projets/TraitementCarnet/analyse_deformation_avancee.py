#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse avancée de déformation pour galeries sans référentiel stable
Détecte les zones de mouvements cohérents et les mouvements différentiels
"""

import re
from collections import defaultdict
import math

def lire_fichier_geo(chemin):
    """Lit le fichier .geo et extrait les points"""
    points = {}
    
    with open(chemin, 'r', encoding='utf-8') as f:
        for ligne in f:
            match = re.match(r'^\d+\s+Point\s+(\S+)\s+[03]\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)', ligne)
            if match:
                nom = match.group(1)
                x = float(match.group(2))
                y = float(match.group(3))
                z = float(match.group(4))
                points[nom] = (x, y, z)
    
    return points

def extraire_nom_base(nom):
    """Extrait le nom de base en enlevant le préfixe ref_"""
    if nom.startswith('ref_'):
        return nom[4:]
    return nom

def calculer_ecart(coord1, coord2):
    """Calcule l'écart avec composantes"""
    dx = coord1[0] - coord2[0]
    dy = coord1[1] - coord2[1]
    dz = coord1[2] - coord2[2]
    
    ecart_xy = math.sqrt(dx**2 + dy**2) * 1000
    ecart_z = abs(dz) * 1000
    
    return ecart_xy, ecart_z, dx*1000, dy*1000, dz*1000

def distance_euclidienne(p1, p2):
    """Distance euclidienne entre deux points"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def analyser_deformations(fichier):
    """Analyse avancée des déformations"""
    print("=" * 120)
    print("ANALYSE AVANCÉE DE DÉFORMATION - Galeries sans référentiel stable")
    print("=" * 120)
    print()
    
    points = lire_fichier_geo(fichier)
    
    # Extraire les points d'auscultation
    groupes = defaultdict(list)
    for nom, coords in points.items():
        nom_base = extraire_nom_base(nom)
        groupes[nom_base].append((nom, coords))
    
    points_ausc = {}
    coords_points = {}
    
    for nom_base, determinations in groupes.items():
        if re.match(r'^S\d{4}$', nom_base):
            ref_coords = None
            mes_coords = None
            
            for nom, coords in determinations:
                if nom.startswith('ref_'):
                    ref_coords = coords
                else:
                    mes_coords = coords
            
            if ref_coords and mes_coords:
                ecart_xy, ecart_z, dx, dy, dz = calculer_ecart(mes_coords, ref_coords)
                points_ausc[nom_base] = {
                    'dx': dx, 'dy': dy, 'dz': dz,
                    'ecart_xy': ecart_xy, 'ecart_z': ecart_z,
                    'coords': ref_coords
                }
                coords_points[nom_base] = ref_coords
    
    if not points_ausc:
        print("Aucun point d'auscultation trouvé.")
        return
    
    print(f"📊 {len(points_ausc)} points d'auscultation analysés")
    print()
    
    # ==================== ANALYSE 1: DÉTECTION DE ZONES COHÉRENTES ====================
    print("=" * 120)
    print("1️⃣  DÉTECTION AUTOMATIQUE DES ZONES DE MOUVEMENT COHÉRENT")
    print("=" * 120)
    print()
    
    # Regrouper par proximité géographique et similarité de mouvement
    seuil_distance = 10.0  # mètres
    seuil_dz_similaire = 0.5  # mm
    
    zones = []
    points_traites = set()
    
    for point1, data1 in sorted(points_ausc.items()):
        if point1 in points_traites:
            continue
        
        # Créer une nouvelle zone
        zone = {
            'points': [point1],
            'dz_values': [data1['dz']],
            'coords': [coords_points[point1]]
        }
        points_traites.add(point1)
        
        # Chercher les points voisins avec mouvement similaire
        for point2, data2 in points_ausc.items():
            if point2 in points_traites:
                continue
            
            dist = distance_euclidienne(coords_points[point1], coords_points[point2])
            
            if dist <= seuil_distance:
                # Vérifier similarité de mouvement
                dz_zone_moy = sum(zone['dz_values']) / len(zone['dz_values'])
                if abs(data2['dz'] - dz_zone_moy) <= seuil_dz_similaire:
                    zone['points'].append(point2)
                    zone['dz_values'].append(data2['dz'])
                    zone['coords'].append(coords_points[point2])
                    points_traites.add(point2)
        
        if len(zone['points']) >= 2:  # Zone = au moins 2 points
            zones.append(zone)
    
    # Analyser chaque zone
    for i, zone in enumerate(zones, 1):
        dz_moy = sum(zone['dz_values']) / len(zone['dz_values'])
        dz_min = min(zone['dz_values'])
        dz_max = max(zone['dz_values'])
        ecart_type = math.sqrt(sum((dz - dz_moy)**2 for dz in zone['dz_values']) / len(zone['dz_values']))
        
        # Déterminer le type de mouvement
        if abs(dz_moy) < 0.3:
            type_mvt = "STABLE"
            emoji = "✅"
        elif dz_moy > 0.5:
            type_mvt = "SOULÈVEMENT"
            emoji = "⬆️"
        elif dz_moy < -0.5:
            type_mvt = "AFFAISSEMENT"
            emoji = "⬇️"
        else:
            type_mvt = "LÉGER"
            emoji = "➡️"
        
        coherence = "COHÉRENT" if ecart_type < 0.5 else "DISPERSÉ"
        
        print(f"Zone #{i} {emoji} - {type_mvt} {coherence}")
        print(f"  Points ({len(zone['points'])}): {', '.join(sorted(zone['points']))}")
        print(f"  dZ moyen: {dz_moy:+.1f}mm  |  Écart-type: {ecart_type:.1f}mm  |  Plage: [{dz_min:+.1f}, {dz_max:+.1f}]")
        
        if coherence == "COHÉRENT" and abs(dz_moy) > 0.5:
            print(f"  ⚠️  ATTENTION: Mouvement cohérent de {abs(dz_moy):.1f}mm détecté sur cette zone")
        print()
    
    # ==================== ANALYSE 2: MOUVEMENTS DIFFÉRENTIELS ====================
    print("=" * 120)
    print("2️⃣  ANALYSE DES MOUVEMENTS DIFFÉRENTIELS (zones qui bougent différemment)")
    print("=" * 120)
    print()
    
    if len(zones) >= 2:
        mouvements_diff = []
        
        for i, zone1 in enumerate(zones):
            for j, zone2 in enumerate(zones[i+1:], i+1):
                dz1_moy = sum(zone1['dz_values']) / len(zone1['dz_values'])
                dz2_moy = sum(zone2['dz_values']) / len(zone2['dz_values'])
                diff = abs(dz1_moy - dz2_moy)
                
                if diff > 0.8:  # Différence significative
                    mouvements_diff.append({
                        'zone1': i+1,
                        'zone2': j+1,
                        'dz1': dz1_moy,
                        'dz2': dz2_moy,
                        'diff': diff
                    })
        
        if mouvements_diff:
            mouvements_diff.sort(key=lambda x: x['diff'], reverse=True)
            
            print("🚨 MOUVEMENTS DIFFÉRENTIELS DÉTECTÉS (zones à surveiller prioritairement):")
            print()
            
            for md in mouvements_diff:
                print(f"  Zone #{md['zone1']} vs Zone #{md['zone2']}:")
                print(f"    Différence: {md['diff']:.1f}mm  ({md['dz1']:+.1f}mm vs {md['dz2']:+.1f}mm)")
                
                if md['diff'] > 1.5:
                    print(f"    ⚠️⚠️  CRITIQUE: Mouvement différentiel > 1.5mm → risque de fissuration")
                elif md['diff'] > 1.0:
                    print(f"    ⚠️  ATTENTION: Mouvement différentiel > 1mm → à surveiller")
                print()
        else:
            print("✅ Aucun mouvement différentiel significatif détecté entre les zones")
            print()
    
    # ==================== ANALYSE 3: POINTS ISOLÉS SUSPECTS ====================
    print("=" * 120)
    print("3️⃣  POINTS ISOLÉS AVEC COMPORTEMENT SUSPECT")
    print("=" * 120)
    print()
    
    points_isoles = [p for p in points_ausc.keys() if p not in points_traites]
    
    if points_isoles:
        print("Points isolés (ne font partie d'aucune zone cohérente):")
        print()
        
        for point in sorted(points_isoles):
            data = points_ausc[point]
            print(f"  {point}: dZ = {data['dz']:+.1f}mm, XY = {data['ecart_xy']:.1f}mm")
            
            if data['ecart_xy'] > 2.0:
                print(f"    ⚠️  Écart XY élevé → vérifier stabilité du point")
            if abs(data['dz']) > 1.5:
                print(f"    ⚠️  Mouvement vertical important et isolé → point suspect")
        print()
    else:
        print("✅ Tous les points font partie de zones cohérentes")
        print()
    
    # ==================== ANALYSE 4: SYNTHÈSE ET RECOMMANDATIONS ====================
    print("=" * 120)
    print("4️⃣  SYNTHÈSE ET RECOMMANDATIONS DE SURVEILLANCE")
    print("=" * 120)
    print()
    
    # Calculer mouvement moyen global
    dz_global_moy = sum(data['dz'] for data in points_ausc.values()) / len(points_ausc)
    dz_global_ecart_type = math.sqrt(sum((data['dz'] - dz_global_moy)**2 for data in points_ausc.values()) / len(points_ausc))
    
    print(f"Mouvement vertical moyen global: {dz_global_moy:+.1f}mm (σ = {dz_global_ecart_type:.1f}mm)")
    print()
    
    # Identifier les zones à surveiller en priorité
    zones_prioritaires = []
    
    for i, zone in enumerate(zones, 1):
        dz_moy = sum(zone['dz_values']) / len(zone['dz_values'])
        
        # Critères de priorité
        score = 0
        raisons = []
        
        # Mouvement important
        if abs(dz_moy) > 1.0:
            score += 3
            raisons.append(f"Mouvement {abs(dz_moy):.1f}mm")
        
        # Différent du mouvement global
        if abs(dz_moy - dz_global_moy) > 0.8:
            score += 2
            raisons.append(f"Mouvement différentiel vs global ({abs(dz_moy - dz_global_moy):.1f}mm)")
        
        # Zone importante (nombre de points)
        if len(zone['points']) >= 4:
            score += 1
            raisons.append(f"{len(zone['points'])} points concernés")
        
        if score > 0:
            zones_prioritaires.append({
                'numero': i,
                'score': score,
                'raisons': raisons,
                'points': zone['points']
            })
    
    if zones_prioritaires:
        zones_prioritaires.sort(key=lambda x: x['score'], reverse=True)
        
        print("🎯 ZONES À SURVEILLER EN PRIORITÉ:")
        print()
        
        for zp in zones_prioritaires:
            print(f"  Zone #{zp['numero']} (Priorité: {'🔴 HAUTE' if zp['score'] >= 4 else '🟠 MOYENNE' if zp['score'] >= 2 else '🟡 FAIBLE'})")
            for raison in zp['raisons']:
                print(f"    - {raison}")
            print(f"    Points: {', '.join(sorted(zp['points']))}")
            print()
    else:
        print("✅ Situation stable globalement, surveillance standard recommandée")
        print()
    
    # Recommandations
    print("📋 RECOMMANDATIONS:")
    print()
    
    if dz_global_ecart_type > 1.0:
        print("  ⚠️  Écart-type élevé → mouvements hétérogènes → augmenter la fréquence de surveillance")
    else:
        print("  ✅ Écart-type faible → mouvements homogènes → surveillance normale")
    
    if mouvements_diff and any(md['diff'] > 1.5 for md in mouvements_diff):
        print("  🚨 CRITIQUE: Mouvements différentiels > 1.5mm → surveillance rapprochée + analyse structurelle recommandée")
    elif mouvements_diff and any(md['diff'] > 1.0 for md in mouvements_diff):
        print("  ⚠️  Mouvements différentiels > 1mm → renforcer la surveillance des zones concernées")
    
    print()
    print("=" * 120)

if __name__ == '__main__':
    analyser_deformations('carnet/GGS-auscultation -251210 - g.geo')
