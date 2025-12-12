#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparateur multi-époques pour suivi de déformation dans les galeries
Permet de comparer les coordonnées de points entre différentes campagnes de mesure
"""

import re
from collections import defaultdict
import math
from datetime import datetime

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
    """Extrait le nom de base (enlève ref_, S1_, S2_, etc.)"""
    prefixes = ['ref_', 'S1_', 'S2_', 'S3_', 'S4_', 'S5_', 'S6_', 'X_']
    for prefix in prefixes:
        if nom.startswith(prefix):
            return nom[len(prefix):]
    return nom

def calculer_deplacement(coord_ancien, coord_nouveau):
    """Calcule le déplacement entre deux positions"""
    dx = (coord_nouveau[0] - coord_ancien[0]) * 1000  # mm
    dy = (coord_nouveau[1] - coord_ancien[1]) * 1000  # mm
    dz = (coord_nouveau[2] - coord_ancien[2]) * 1000  # mm
    
    deplacement_xy = math.sqrt(dx**2 + dy**2)
    deplacement_3d = math.sqrt(dx**2 + dy**2 + dz**2)
    
    return deplacement_xy, abs(dz), deplacement_3d, dx, dy, dz

def comparer_epoques(fichier_ancien, fichier_nouveau, nom_epoque_ancien="Époque 1", nom_epoque_nouveau="Époque 2"):
    """Compare deux fichiers .geo pour détecter les évolutions"""
    
    print("=" * 120)
    print("COMPARAISON MULTI-ÉPOQUES - Suivi de déformation temporelle")
    print("=" * 120)
    print()
    
    print(f"📅 {nom_epoque_ancien}: {fichier_ancien}")
    print(f"📅 {nom_epoque_nouveau}: {fichier_nouveau}")
    print()
    
    # Lire les deux époques
    points_ancien = lire_fichier_geo(fichier_ancien)
    points_nouveau = lire_fichier_geo(fichier_nouveau)
    
    print(f"Points lus - {nom_epoque_ancien}: {len(points_ancien)}, {nom_epoque_nouveau}: {len(points_nouveau)}")
    print()
    
    # Regrouper par nom de base
    points_ancien_base = {}
    for nom, coords in points_ancien.items():
        nom_base = extraire_nom_base(nom)
        if nom_base not in points_ancien_base or not nom.startswith('ref_'):
            points_ancien_base[nom_base] = coords
    
    points_nouveau_base = {}
    for nom, coords in points_nouveau.items():
        nom_base = extraire_nom_base(nom)
        if nom_base not in points_nouveau_base or not nom.startswith('ref_'):
            points_nouveau_base[nom_base] = coords
    
    # Identifier les points communs
    points_communs = set(points_ancien_base.keys()) & set(points_nouveau_base.keys())
    points_nouveaux_seulement = set(points_nouveau_base.keys()) - set(points_ancien_base.keys())
    points_disparus = set(points_ancien_base.keys()) - set(points_nouveau_base.keys())
    
    print(f"Points communs: {len(points_communs)}")
    if points_nouveaux_seulement:
        print(f"Points nouveaux: {len(points_nouveaux_seulement)} ({', '.join(sorted(list(points_nouveaux_seulement)[:5]))}...)")
    if points_disparus:
        print(f"Points disparus: {len(points_disparus)} ({', '.join(sorted(list(points_disparus)[:5]))}...)")
    print()
    
    # Calculer les déplacements
    deplacements = {}
    
    for point in points_communs:
        coord_ancien = points_ancien_base[point]
        coord_nouveau = points_nouveau_base[point]
        
        depl_xy, depl_z, depl_3d, dx, dy, dz = calculer_deplacement(coord_ancien, coord_nouveau)
        
        deplacements[point] = {
            'depl_xy': depl_xy,
            'depl_z': depl_z,
            'depl_3d': depl_3d,
            'dx': dx,
            'dy': dy,
            'dz': dz,
            'coords_ancien': coord_ancien,
            'coords_nouveau': coord_nouveau
        }
    
    # ==================== ANALYSE 1: VUE D'ENSEMBLE ====================
    print("=" * 120)
    print("1️⃣  VUE D'ENSEMBLE DES MOUVEMENTS")
    print("=" * 120)
    print()
    
    if deplacements:
        dz_values = [d['dz'] for d in deplacements.values()]
        depl_xy_values = [d['depl_xy'] for d in deplacements.values()]
        
        dz_moy = sum(dz_values) / len(dz_values)
        dz_min = min(dz_values)
        dz_max = max(dz_values)
        dz_ecart_type = math.sqrt(sum((dz - dz_moy)**2 for dz in dz_values) / len(dz_values))
        
        depl_xy_moy = sum(depl_xy_values) / len(depl_xy_values)
        depl_xy_max = max(depl_xy_values)
        
        print(f"Déplacement vertical (dZ):")
        print(f"  Moyen:      {dz_moy:+.1f}mm")
        print(f"  Écart-type: {dz_ecart_type:.1f}mm")
        print(f"  Minimum:    {dz_min:+.1f}mm")
        print(f"  Maximum:    {dz_max:+.1f}mm")
        print(f"  Amplitude:  {dz_max - dz_min:.1f}mm")
        print()
        
        print(f"Déplacement horizontal (XY):")
        print(f"  Moyen:      {depl_xy_moy:.1f}mm")
        print(f"  Maximum:    {depl_xy_max:.1f}mm")
        print()
        
        # Interprétation
        if abs(dz_moy) > 2.0:
            print(f"  🚨 MOUVEMENT VERTICAL GLOBAL IMPORTANT ({abs(dz_moy):.1f}mm)")
        elif abs(dz_moy) > 1.0:
            print(f"  ⚠️  Mouvement vertical global modéré ({abs(dz_moy):.1f}mm)")
        else:
            print(f"  ✅ Mouvement vertical global faible ({abs(dz_moy):.1f}mm)")
        
        if dz_ecart_type > 1.5:
            print(f"  🚨 FORTE HÉTÉROGÉNÉITÉ (σ = {dz_ecart_type:.1f}mm) → mouvements différentiels importants")
        elif dz_ecart_type > 1.0:
            print(f"  ⚠️  Hétérogénéité modérée (σ = {dz_ecart_type:.1f}mm)")
        else:
            print(f"  ✅ Mouvements homogènes (σ = {dz_ecart_type:.1f}mm)")
        print()
    
    # ==================== ANALYSE 2: TOP MOUVEMENTS ====================
    print("=" * 120)
    print("2️⃣  POINTS AVEC LES PLUS GRANDS DÉPLACEMENTS")
    print("=" * 120)
    print()
    
    # Trier par déplacement vertical
    deplacements_tries_z = sorted(deplacements.items(), key=lambda x: abs(x[1]['dz']), reverse=True)
    
    print("🔽 Top 10 - Plus grands mouvements verticaux:")
    print()
    print(f"{'Point':<20} {'dZ':>10} {'dX':>10} {'dY':>10} {'XY':>10} {'Type':>15}")
    print("-" * 120)
    
    for point, data in deplacements_tries_z[:10]:
        type_mvt = "⬆️ Soulèvement" if data['dz'] > 0.5 else "⬇️ Affaissement" if data['dz'] < -0.5 else "➡️ Stable"
        print(f"{point:<20} {data['dz']:>+9.1f} {data['dx']:>+9.1f} {data['dy']:>+9.1f} {data['depl_xy']:>9.1f} {type_mvt:>15}")
    print()
    
    # Trier par déplacement horizontal
    deplacements_tries_xy = sorted(deplacements.items(), key=lambda x: x[1]['depl_xy'], reverse=True)
    
    if deplacements_tries_xy[0][1]['depl_xy'] > 2.0:
        print("➡️ Top 5 - Plus grands déplacements horizontaux:")
        print()
        print(f"{'Point':<20} {'XY':>10} {'dX':>10} {'dY':>10}")
        print("-" * 120)
        
        for point, data in deplacements_tries_xy[:5]:
            print(f"{point:<20} {data['depl_xy']:>9.1f} {data['dx']:>+9.1f} {data['dy']:>+9.1f}")
        print()
    
    # ==================== ANALYSE 3: DÉTECTION DE ZONES ====================
    print("=" * 120)
    print("3️⃣  IDENTIFICATION DES ZONES DE DÉFORMATION")
    print("=" * 120)
    print()
    
    # Classifier les points selon leur comportement
    zones_comportement = {
        'Affaissement fort (< -1.5mm)': [],
        'Affaissement modéré (-1.5 à -0.5mm)': [],
        'Stable (-0.5 à +0.5mm)': [],
        'Soulèvement modéré (+0.5 à +1.5mm)': [],
        'Soulèvement fort (> +1.5mm)': []
    }
    
    for point, data in deplacements.items():
        dz = data['dz']
        if dz < -1.5:
            zones_comportement['Affaissement fort (< -1.5mm)'].append((point, dz))
        elif dz < -0.5:
            zones_comportement['Affaissement modéré (-1.5 à -0.5mm)'].append((point, dz))
        elif dz <= 0.5:
            zones_comportement['Stable (-0.5 à +0.5mm)'].append((point, dz))
        elif dz <= 1.5:
            zones_comportement['Soulèvement modéré (+0.5 à +1.5mm)'].append((point, dz))
        else:
            zones_comportement['Soulèvement fort (> +1.5mm)'].append((point, dz))
    
    for zone, points_zone in zones_comportement.items():
        if points_zone:
            emoji = "🚨" if "fort" in zone else "⚠️" if "modéré" in zone else "✅"
            print(f"{emoji} {zone}: {len(points_zone)} points")
            
            if len(points_zone) <= 10:
                points_tries = sorted(points_zone, key=lambda x: abs(x[1]), reverse=True)
                for point, dz in points_tries:
                    print(f"    {point}: {dz:+.1f}mm")
            else:
                points_tries = sorted(points_zone, key=lambda x: abs(x[1]), reverse=True)
                print(f"    Points les plus affectés: {', '.join([f'{p} ({dz:+.1f}mm)' for p, dz in points_tries[:5]])}")
            print()
    
    # ==================== ANALYSE 4: VITESSE DE DÉFORMATION ====================
    print("=" * 120)
    print("4️⃣  ESTIMATION DE LA VITESSE DE DÉFORMATION (si dates connues)")
    print("=" * 120)
    print()
    
    print("💡 Pour activer le calcul de vitesse, ajoutez les dates des campagnes dans le script")
    print("   Exemple: comparer_epoques(fichier1, fichier2, jours_entre_mesures=30)")
    print()
    
    # ==================== ANALYSE 5: RECOMMANDATIONS ====================
    print("=" * 120)
    print("5️⃣  RECOMMANDATIONS ET ACTIONS")
    print("=" * 120)
    print()
    
    points_critiques = [p for p, d in deplacements.items() if abs(d['dz']) > 2.0 or d['depl_xy'] > 3.0]
    points_surveillance = [p for p, d in deplacements.items() if (1.0 < abs(d['dz']) <= 2.0) or (2.0 < d['depl_xy'] <= 3.0)]
    
    if points_critiques:
        print(f"🚨 POINTS CRITIQUES ({len(points_critiques)}) - Action immédiate requise:")
        print(f"   {', '.join(sorted(points_critiques))}")
        print(f"   → Re-mesurer dès que possible")
        print(f"   → Inspection visuelle de la structure")
        print()
    
    if points_surveillance:
        print(f"⚠️  POINTS SOUS SURVEILLANCE RENFORCÉE ({len(points_surveillance)}):")
        print(f"   {', '.join(sorted(points_surveillance[:10]))}{'...' if len(points_surveillance) > 10 else ''}")
        print(f"   → Mesurer plus fréquemment")
        print()
    
    if dz_ecart_type > 1.5:
        print(f"🚨 ALERTE: Forte hétérogénéité des mouvements")
        print(f"   → Risque de contraintes différentielles")
        print(f"   → Rechercher des fissures ou déformations structurelles")
        print()
    
    points_stables = [p for p, d in deplacements.items() if abs(d['dz']) <= 0.5 and d['depl_xy'] <= 1.0]
    if points_stables and len(points_stables) > len(deplacements) * 0.3:
        print(f"✅ {len(points_stables)} points stables peuvent servir de références locales")
        print(f"   Points les plus stables: {', '.join(sorted(points_stables)[:5])}")
        print()
    
    print("=" * 120)
    
    return deplacements

if __name__ == '__main__':
    # Exemple d'utilisation
    print("Outil de comparaison multi-époques")
    print()
    print("USAGE:")
    print("  1. Modifier les noms de fichiers ci-dessous")
    print("  2. Exécuter le script")
    print()
    
    # À modifier selon vos fichiers
    fichier_epoque1 = 'carnet/GGS-auscultation-EPOQUE1.geo'  # Fichier ancien
    fichier_epoque2 = 'carnet/GGS-auscultation -251210 - g.geo'  # Fichier récent
    
    try:
        deplacements = comparer_epoques(
            fichier_epoque1, 
            fichier_epoque2,
            nom_epoque_ancien="Campagne précédente",
            nom_epoque_nouveau="Campagne 10/12/2025"
        )
    except FileNotFoundError as e:
        print(f"❌ Fichier non trouvé: {e}")
        print()
        print("📝 Pour utiliser cet outil:")
        print("   1. Placer vos fichiers .geo dans le dossier 'carnet/'")
        print("   2. Modifier les noms de fichiers dans ce script (lignes 'fichier_epoque1' et 'fichier_epoque2')")
        print("   3. Relancer le script")
