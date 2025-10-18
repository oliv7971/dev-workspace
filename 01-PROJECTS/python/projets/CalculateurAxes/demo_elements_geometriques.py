#!/usr/bin/env python3
"""
Démonstration des éléments géométriques d'axes
Alignements droits, Arcs circulaires et Clothoïdes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import math
from core.geometrie import Point
from core.elements import AlignementDroit, Arc, Clothoide

def demo_elements_geometriques():
    print("=" * 80)
    print("🛣️  DÉMONSTRATION DES ÉLÉMENTS GÉOMÉTRIQUES D'AXE")
    print("=" * 80)
    
    # ========================================================================
    # 1. ALIGNEMENT DROIT
    # ========================================================================
    print("\n1. 📏 ALIGNEMENT DROIT")
    print("-" * 50)
    
    # Créer un alignement de 200m en direction Nord-Est
    debut = Point(1000.0, 2000.0, 100.0)
    fin = Point(1141.42, 2141.42, 105.0)  # ~200m à 45°
    
    alignement = AlignementDroit(debut, fin)
    
    print(f"Début: ({debut.x}, {debut.y}, {debut.z})")
    print(f"Fin: ({fin.x}, {fin.y}, {fin.z})")
    print(f"Longueur: {alignement.longueur():.2f}m")
    print(f"Gisement: {alignement.gisement:.1f}g (constant)")
    
    # Points caractéristiques
    points_test = [0, 50, 100, 150, 200]
    print("\nPoints sur l'alignement:")
    for dist in points_test:
        if dist <= alignement.longueur():
            pt = alignement.point_at_distance(dist)
            gis = alignement.gisement_at_distance(dist)
            print(f"  PM {dist:3}m: ({pt.x:7.2f}, {pt.y:7.2f}, {pt.z:6.2f}) - Gis: {gis:5.1f}g")
    
    # Test de projection
    point_externe = Point(1050, 2080, 102)
    distance, deport = alignement.projeter_point(point_externe)
    print(f"\nProjection du point ({point_externe.x}, {point_externe.y}):")
    print(f"  Distance sur axe: {distance:.2f}m")
    print(f"  Déport: {deport:.2f}m ({'droite' if deport > 0 else 'gauche'})")
    
    # ========================================================================
    # 2. ARC CIRCULAIRE
    # ========================================================================
    print("\n\n2. 🌀 ARC CIRCULAIRE")
    print("-" * 50)
    
    # Arc de rayon 300m, déviation 50g (sens droite)
    centre = Point(1300, 2000, 100)
    rayon = 300.0  # Positif = sens droite
    angle_debut = 100.0  # Est
    angle_fin = 150.0    # Sud-Est
    
    arc = Arc(centre, rayon, angle_debut, angle_fin)
    
    print(f"Centre: ({centre.x}, {centre.y})")
    print(f"Rayon: {rayon}m ({'droite' if rayon > 0 else 'gauche'})")
    print(f"Angle début: {angle_debut}g")
    print(f"Angle fin: {angle_fin}g")
    print(f"Déviation: {arc.deviation:.1f}g")
    print(f"Longueur: {arc.longueur():.2f}m")
    
    # Points sur l'arc
    print("\nPoints sur l'arc:")
    longueur_arc = arc.longueur()
    for i in range(6):
        dist = i * longueur_arc / 5
        pt = arc.point_at_distance(dist)
        gis = arc.gisement_at_distance(dist)
        print(f"  PM {dist:5.1f}m: ({pt.x:7.2f}, {pt.y:7.2f}) - Gis: {gis:5.1f}g")
    
    # ========================================================================
    # 3. CLOTHOÏDE
    # ========================================================================
    print("\n\n3. 🌊 CLOTHOÏDE (Spirale de transition)")
    print("-" * 50)
    
    # Clothoïde de raccordement alignement → courbe R=200m
    point_debut = Point(2000, 2000, 100)
    gisement_debut = 50.0  # Nord-Est
    rayon_debut = float('inf')  # Alignement (rayon infini)
    rayon_fin = 200.0  # Courbe R=200m
    longueur = 100.0  # 100m de transition
    
    clothoide = Clothoide(point_debut, gisement_debut, rayon_debut, rayon_fin, longueur)
    
    print(f"Point début: ({point_debut.x}, {point_debut.y})")
    print(f"Gisement début: {gisement_debut}g")
    print(f"Rayon début: {'∞' if abs(rayon_debut) > 1e9 else f'{rayon_debut}m'} (alignement)")
    print(f"Rayon fin: {rayon_fin}m")
    print(f"Longueur: {longueur}m")
    print(f"Paramètre A: {clothoide.A:.1f}")
    
    # Points sur la clothoïde
    print("\nPoints sur la clothoïde (approximation):")
    for i in range(6):
        dist = i * longueur / 5
        pt = clothoide.point_at_distance(dist)
        gis = clothoide.gisement_at_distance(dist)
        print(f"  PM {dist:5.1f}m: ({pt.x:7.2f}, {pt.y:7.2f}) - Gis: {gis:5.1f}g")
    
    # ========================================================================
    # 4. COMPARAISON DES CARACTÉRISTIQUES
    # ========================================================================
    print("\n\n4. 📊 COMPARAISON DES CARACTÉRISTIQUES")
    print("-" * 50)
    
    elements = [
        ("Alignement", alignement),
        ("Arc", arc),
        ("Clothoïde", clothoide)
    ]
    
    print(f"{'Élément':<12} {'Longueur (m)':<12} {'Gis. début':<12} {'Gis. fin':<12} {'Courbure'}")
    print("-" * 65)
    
    for nom, element in elements:
        longueur = element.longueur()
        gis_debut = element.gisement_at_distance(0)
        gis_fin = element.gisement_at_distance(longueur)
        
        if isinstance(element, AlignementDroit):
            courbure = "Nulle (droite)"
        elif isinstance(element, Arc):
            courbure = f"1/{element.rayon:.0f} (constante)"
        else:  # Clothoïde
            courbure = "Variable"
        
        print(f"{nom:<12} {longueur:<12.2f} {gis_debut:<12.1f} {gis_fin:<12.1f} {courbure}")
    
    # ========================================================================
    # 5. CAS D'USAGE PRATIQUE : TRACÉ ROUTIER
    # ========================================================================
    print("\n\n5. 🚗 CAS D'USAGE : TRACÉ ROUTIER COMPLET")
    print("-" * 50)
    print("Séquence typique : Alignement → Clothoïde → Arc → Clothoïde → Alignement")
    
    # Définir une séquence d'éléments
    sequence = [
        ("Alignement d'approche", 150.0, "Gisement constant"),
        ("Clothoïde d'entrée", 80.0, "∞ → R300m"),
        ("Arc central", 157.08, "R=300m, Δ=30g"),
        ("Clothoïde de sortie", 80.0, "R300m → ∞"),
        ("Alignement de sortie", 200.0, "Gisement constant"),
    ]
    
    pm_cumul = 0
    print(f"{'PM début':<10} {'PM fin':<10} {'Élément':<20} {'Long.(m)':<10} {'Caractéristique'}")
    print("-" * 75)
    
    for nom, longueur, caracteristique in sequence:
        pm_fin = pm_cumul + longueur
        print(f"{pm_cumul:<10.0f} {pm_fin:<10.0f} {nom:<20} {longueur:<10.1f} {caracteristique}")
        pm_cumul = pm_fin
    
    print(f"\nLongueur totale du tronçon: {pm_cumul:.1f}m")
    
    # ========================================================================
    # 6. RECOMMANDATIONS PRATIQUES
    # ========================================================================
    print("\n\n6. 💡 RECOMMANDATIONS PRATIQUES")
    print("-" * 50)
    
    recommandations = [
        "🔹 Alignements : Utilisés pour les sections droites, gisement constant",
        "🔹 Arcs : Courbes à rayon constant, attention au sens (rayon +/-)",
        "🔹 Clothoïdes : Transitions essentielles pour le confort de conduite",
        "🔹 Paramètre A des clothoïdes : A² = R × L (formule fondamentale)",
        "🔹 Projection : Tous les éléments supportent le calcul PM/déport",
        "🔹 Validation : Toujours vérifier les limites de distances",
    ]
    
    for rec in recommandations:
        print(f"  {rec}")
    
    print("\n\n" + "=" * 80)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("   Les trois types d'éléments géométriques sont opérationnels !")
    print("=" * 80)

if __name__ == "__main__":
    demo_elements_geometriques()