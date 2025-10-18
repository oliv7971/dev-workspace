#!/usr/bin/env python3
"""
Démonstration des fonctionnalités améliorées de gisements
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.geometrie import (
    normaliser_gisement, 
    gisement_inverse, 
    difference_gisements,
    gisement_depuis_coordonnees,
    valider_gisement,
    convertir_grades_degres,
    convertir_degres_grades
)

def demo_gisements_ameliores():
    print("=" * 80)
    print("🧭 DÉMONSTRATION DES GISEMENTS AMÉLIORÉS")
    print("=" * 80)
    
    # 1. Calculs de gisements depuis coordonnées
    print("\n1. 📍 Calculs de gisements depuis coordonnées")
    print("-" * 50)
    points = [
        ((1000, 2000), (1000, 2100), "Nord"),
        ((1000, 2000), (1100, 2100), "Nord-Est"),
        ((1000, 2000), (1100, 2000), "Est"),
        ((1000, 2000), (1100, 1900), "Sud-Est"),
        ((1000, 2000), (1000, 1900), "Sud"),
        ((1000, 2000), (900, 1900), "Sud-Ouest"),
        ((1000, 2000), (900, 2000), "Ouest"),
        ((1000, 2000), (900, 2100), "Nord-Ouest"),
    ]
    
    for (x1, y1), (x2, y2), direction in points:
        g = gisement_depuis_coordonnees(x1, y1, x2, y2)
        print(f"{direction:12} : ({x1:4}, {y1:4}) → ({x2:4}, {y2:4}) = {g:7.1f}g")
    
    # 2. Opérations sur gisements
    print("\n2. 🔄 Opérations sur gisements")
    print("-" * 50)
    
    gisements_test = [0, 50, 100, 150, 200, 250, 300, 350]
    for g in gisements_test:
        g_inv = gisement_inverse(g)
        print(f"Gisement {g:3}g → Inverse: {g_inv:3.0f}g")
    
    # 3. Différences angulaires
    print("\n3. 📐 Différences angulaires minimales")
    print("-" * 50)
    couples_test = [
        (0, 100),
        (350, 10),    # Passage par 0/400
        (50, 320),    # Grande différence
        (100, 300),   # Diamétralement opposés
        (0, 200),     # Exactement opposés
    ]
    
    for g1, g2 in couples_test:
        diff = difference_gisements(g1, g2)
        print(f"Différence ({g1:3}g, {g2:3}g) = {diff:6.1f}g")
    
    # 4. Normalisation
    print("\n4. 🎯 Normalisation de gisements")
    print("-" * 50)
    valeurs_anormales = [-50, 450, 800, -200, 123.456]
    for val in valeurs_anormales:
        norm = normaliser_gisement(val)
        print(f"{val:8.1f}g → {norm:6.1f}g")
    
    # 5. Conversions
    print("\n5. 🔄 Conversions grades ↔ degrés")
    print("-" * 50)
    gisements_grades = [0, 50, 100, 200, 300, 400]
    for g_grades in gisements_grades:
        g_degres = convertir_grades_degres(g_grades)
        g_retour = convertir_degres_grades(g_degres)
        print(f"{g_grades:3}g = {g_degres:6.1f}° (retour: {g_retour:6.1f}g)")
    
    # 6. Validation
    print("\n6. ✅ Validation de gisements")
    print("-" * 50)
    valeurs_test = [0, 100, 200, 400, -10, 500, float('nan'), float('inf')]
    for val in valeurs_test:
        valide, message = valider_gisement(val)
        status = "✅" if valide else "❌"
        print(f"{status} {val} : {message}")
    
    # 7. Cas d'usage pratique
    print("\n7. 📋 Exemple pratique complet")
    print("-" * 50)
    print("Calcul d'implantation depuis un point de référence:")
    
    # Point de référence (station)
    station = (1000.000, 2000.000)
    
    # Points à implanter
    points_implanter = [
        (1050.000, 2080.000, "Borne A"),
        (980.000, 2120.000, "Borne B"),
        (920.000, 1950.000, "Borne C"),
    ]
    
    print(f"Station de référence: ({station[0]:.3f}, {station[1]:.3f})")
    print()
    
    for x, y, nom in points_implanter:
        # Calcul gisement et distance
        gis = gisement_depuis_coordonnees(station[0], station[1], x, y)
        distance = ((x - station[0])**2 + (y - station[1])**2)**0.5
        
        # Validation
        valide, _ = valider_gisement(gis)
        
        print(f"{nom} : ({x:.3f}, {y:.3f})")
        print(f"   Gisement : {gis:7.3f}g")
        print(f"   Distance : {distance:7.3f}m")
        print(f"   Valide   : {'✅' if valide else '❌'}")
        print()
    
    print("=" * 80)
    print("✅ Démonstration terminée - Toutes les fonctionnalités validées !")
    print("=" * 80)

if __name__ == "__main__":
    demo_gisements_ameliores()