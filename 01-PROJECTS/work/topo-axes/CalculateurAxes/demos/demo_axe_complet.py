#!/usr/bin/env python3
"""
Exemple d'axe complet avec alignements, arcs et clothoïdes
Simulation d'un tracé routier réaliste
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.geometrie import Point
from core.axe import AxeEnPlan
from core.elements import AlignementDroit, Arc, Clothoide
import math

def creer_axe_complet():
    print("=" * 80)
    print("🛤️  CRÉATION D'UN AXE COMPLET")
    print("   Alignements → Clothoïdes → Arcs → Clothoïdes → Alignements")
    print("=" * 80)
    
    # Créer l'axe principal
    axe = AxeEnPlan("Route Départementale RD123")
    axe.pm_debut = 1000.0  # Commencé au PM 1000
    
    print(f"Axe: {axe.nom}")
    print(f"PM de début: {axe.pm_debut}m")
    print()
    
    # ========================================================================
    # SÉQUENCE 1: ALIGNEMENT D'APPROCHE
    # ========================================================================
    print("📏 SÉQUENCE 1: Alignement d'approche (150m)")
    debut_seq1 = Point(1000.0, 2000.0, 100.0)
    fin_seq1 = Point(1150.0, 2000.0, 102.0)  # 150m vers l'Est, pente 1.33%
    
    alignement1 = axe.ajouter_alignement(debut_seq1, fin_seq1)
    print(f"  Longueur: {alignement1.longueur():.1f}m")
    print(f"  Gisement: {alignement1.gisement:.1f}g")
    print(f"  Pente: {((fin_seq1.z - debut_seq1.z) / alignement1.longueur() * 100):.2f}%")
    
    # ========================================================================
    # SÉQUENCE 2: CLOTHOÏDE D'ENTRÉE
    # ========================================================================
    print("\n🌊 SÉQUENCE 2: Clothoïde d'entrée ∞ → R500m (100m)")
    
    # Point de début = fin de l'alignement précédent
    debut_clotho1 = fin_seq1
    gisement_clotho1 = alignement1.gisement  # Continuité du gisement
    
    clothoide1 = axe.ajouter_clothoide(
        point_debut=debut_clotho1,
        gisement_debut=gisement_clotho1,
        rayon_debut=float('inf'),  # Alignement
        rayon_fin=500.0,          # Courbe R=500m
        longueur=100.0
    )
    
    print(f"  Longueur: {clothoide1.longueur():.1f}m")
    print(f"  Gisement début: {gisement_clotho1:.1f}g")
    print(f"  Paramètre A: {clothoide1.A:.1f}")
    print(f"  Transition: Alignement → R{clothoide1.rayon_fin:.0f}m")
    
    # ========================================================================
    # SÉQUENCE 3: ARC CENTRAL
    # ========================================================================
    print("\n🌀 SÉQUENCE 3: Arc central R=500m, déviation 60g")
    
    # Arc de rayon 500m, déviation 60g (virage à droite)
    centre_arc = Point(1250.0, 2500.0, 105.0)
    rayon_arc = 500.0  # Positif = virage à droite
    angle_debut_arc = 100.0  # Est
    angle_fin_arc = 160.0    # Sud-Est + 60g
    
    arc_central = axe.ajouter_arc(centre_arc, rayon_arc, angle_debut_arc, angle_fin_arc)
    
    print(f"  Rayon: {rayon_arc:.0f}m ({'droite' if rayon_arc > 0 else 'gauche'})")
    print(f"  Déviation: {arc_central.deviation:.1f}g")
    print(f"  Longueur: {arc_central.longueur():.1f}m")
    print(f"  Centre: ({centre_arc.x}, {centre_arc.y})")
    
    # ========================================================================
    # SÉQUENCE 4: CLOTHOÏDE DE SORTIE
    # ========================================================================
    print("\n🌊 SÉQUENCE 4: Clothoïde de sortie R500m → ∞ (100m)")
    
    # Point de début calculé à partir de la fin de l'arc
    debut_clotho2 = arc_central.point_at_distance(arc_central.longueur())
    gisement_clotho2 = arc_central.gisement_at_distance(arc_central.longueur())
    
    clothoide2 = axe.ajouter_clothoide(
        point_debut=debut_clotho2,
        gisement_debut=gisement_clotho2,
        rayon_debut=500.0,        # Courbe R=500m
        rayon_fin=float('inf'),   # Alignement
        longueur=100.0
    )
    
    print(f"  Longueur: {clothoide2.longueur():.1f}m")
    print(f"  Gisement début: {gisement_clotho2:.1f}g")
    print(f"  Paramètre A: {clothoide2.A:.1f}")
    print(f"  Transition: R{clothoide2.rayon_debut:.0f}m → Alignement")
    
    # ========================================================================
    # SÉQUENCE 5: ALIGNEMENT DE SORTIE
    # ========================================================================
    print("\n📏 SÉQUENCE 5: Alignement de sortie (200m)")
    
    debut_seq5 = clothoide2.point_at_distance(clothoide2.longueur())
    gisement_final = clothoide2.gisement_at_distance(clothoide2.longueur())
    
    # Calculer le point final selon le gisement
    longueur_finale = 200.0
    gis_rad = gisement_final * math.pi / 200
    
    fin_seq5 = Point(
        debut_seq5.x + longueur_finale * math.sin(gis_rad),
        debut_seq5.y + longueur_finale * math.cos(gis_rad),
        debut_seq5.z + 3.0  # Pente 1.5%
    )
    
    alignement2 = axe.ajouter_alignement(debut_seq5, fin_seq5)
    
    print(f"  Longueur: {alignement2.longueur():.1f}m")
    print(f"  Gisement: {alignement2.gisement:.1f}g")
    print(f"  Pente: {((fin_seq5.z - debut_seq5.z) / alignement2.longueur() * 100):.2f}%")
    
    return axe

def analyser_axe(axe):
    """Analyse détaillée de l'axe créé"""
    print("\n" + "=" * 80)
    print("🔍 ANALYSE DE L'AXE")
    print("=" * 80)
    
    print(f"Nombre d'éléments: {len(axe.elements)}")
    print(f"Longueur totale: {axe.longueur_totale():.2f}m")
    print(f"PM début: {axe.pm_debut:.0f}m")
    print(f"PM fin: {axe.pm_debut + axe.longueur_totale():.0f}m")
    
    # Analyse par élément
    print("\nDétail des éléments:")
    pm_cumule = axe.pm_debut
    
    for i, element in enumerate(axe.elements, 1):
        longueur = element.longueur()
        pm_fin = pm_cumule + longueur
        
        type_element = type(element).__name__
        gis_debut = element.gisement_at_distance(0)
        gis_fin = element.gisement_at_distance(longueur)
        
        print(f"  {i}. {type_element:<15} PM {pm_cumule:6.0f} → {pm_fin:6.0f} "
              f"({longueur:6.1f}m) - Gis: {gis_debut:5.1f}g → {gis_fin:5.1f}g")
        
        pm_cumule = pm_fin

def tester_projections(axe):
    """Test des projections sur l'axe complet"""
    print("\n" + "=" * 80)
    print("🎯 TEST DES PROJECTIONS")
    print("=" * 80)
    
    # Points de test
    points_test = [
        Point(1075, 2020, 101.5),   # Près de l'alignement 1
        Point(1350, 2250, 106.0),   # Près de l'arc
        Point(1400, 2150, 108.0),   # Près de l'alignement final
    ]
    
    print("Projection de points externes sur l'axe:")
    for i, point in enumerate(points_test, 1):
        pm, deport = axe.projeter_point(point)
        pt_proj = axe.point_at_pm(pm)
        
        print(f"\nPoint {i}: ({point.x}, {point.y}, {point.z:.1f})")
        print(f"  → PM projeté: {pm:.2f}m")
        print(f"  → Déport: {deport:.2f}m ({'droite' if deport > 0 else 'gauche'})")
        print(f"  → Point projeté: ({pt_proj.x:.2f}, {pt_proj.y:.2f}, {pt_proj.z:.2f})")

def generer_points_axes(axe, pas=50):
    """Génère des points le long de l'axe pour visualisation"""
    print(f"\n" + "=" * 80)
    print(f"📋 POINTS CARACTÉRISTIQUES (pas de {pas}m)")
    print("=" * 80)
    
    longueur_totale = axe.longueur_totale()
    
    print(f"{'PM (m)':<8} {'X (m)':<10} {'Y (m)':<10} {'Z (m)':<8} {'Gisement':<10} {'Élément'}")
    print("-" * 70)
    
    pm = axe.pm_debut
    while pm <= axe.pm_debut + longueur_totale:
        try:
            point = axe.point_at_pm(pm)
            
            # Identifier l'élément
            distance = pm - axe.pm_debut
            distance_cumulee = 0
            element_nom = "?"
            
            for element in axe.elements:
                longueur_element = element.longueur()
                if distance_cumulee + longueur_element >= distance:
                    element_nom = type(element).__name__
                    distance_element = distance - distance_cumulee
                    gisement = element.gisement_at_distance(distance_element)
                    break
                distance_cumulee += longueur_element
            
            print(f"{pm:<8.0f} {point.x:<10.2f} {point.y:<10.2f} {point.z:<8.2f} "
                  f"{gisement:<10.1f} {element_nom}")
            
        except ValueError:
            break
            
        pm += pas

def main():
    """Fonction principale"""
    # Créer l'axe complet
    axe = creer_axe_complet()
    
    # Analyser l'axe
    analyser_axe(axe)
    
    # Tester les projections
    tester_projections(axe)
    
    # Générer les points caractéristiques
    generer_points_axes(axe, pas=100)
    
    print("\n" + "=" * 80)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("   Axe complet avec alignements, arcs et clothoïdes créé et testé !")
    print("=" * 80)

if __name__ == "__main__":
    main()