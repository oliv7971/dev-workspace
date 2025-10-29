"""
Exemple d'utilisation du système d'axes routiers
"""
from src.models.point import Point
from src.models.elements import LineElement, CircularArcElement, ClothoidElement
from src.models.axis import Axis
from math import radians, pi, degrees


def exemple_simple():
    """Exemple simple avec une ligne droite et un arc"""
    print("=== Exemple 1 : Axe simple (ligne + arc) ===\n")
    
    # Créer un axe
    axe = Axis()
    
    # Ajouter une ligne droite de 100m
    axe.add_element(LineElement(Point(0, 0), Point(100, 0)))
    print(f"Ajouté : ligne droite de (0,0) à (100,0)")
    
    # Ajouter un arc de cercle (quart de cercle, rayon 50m)
    # Centre à (100, 50), de 270° à 360° (anti-horaire)
    axe.add_element(CircularArcElement(
        center=Point(100, 50),
        radius=50,
        start_angle=radians(270),  # 270° = 3π/2
        end_angle=radians(360),     # 360° = 0 (ou 2π)
        ccw=True
    ))
    print(f"Ajouté : arc de cercle (rayon 50m, quart de cercle)")
    
    print(f"\nLongueur totale de l'axe : {axe.total_length():.2f} m")
    
    # Calculer quelques points
    print("\n--- Points calculés sur l'axe ---")
    for station in [0, 50, 100, 120, axe.total_length()]:
        pt = axe.point_at(station)
        print(f"Station {station:6.2f}m : {pt}")
    
    # Projeter un point sur l'axe
    print("\n--- Projection de points ---")
    point_a_projeter = Point(50, 20)
    resultat = axe.project_point(point_a_projeter)
    print(f"Point à projeter : {point_a_projeter}")
    print(f"  Station projetée : {resultat['station']:.2f} m")
    print(f"  Point projeté : {resultat['point']}")
    print(f"  Offset (distance) : {resultat['offset']:.2f} m")
    print(f"  Élément n° : {resultat['element_index']}")


def exemple_clothoide():
    """Exemple avec clothoïde"""
    print("\n\n=== Exemple 2 : Axe avec clothoïde ===\n")
    
    axe = Axis()
    
    # Ligne droite de départ
    axe.add_element(LineElement(Point(0, 0), Point(100, 0)))
    print(f"Ajouté : ligne droite de 100m")
    
    # Clothoïde de raccordement (courbure 0 -> 0.02)
    # heading0 = 0 (horizontal), longueur 50m
    axe.add_element(ClothoidElement(
        p0=Point(100, 0),
        heading0=0,           # Direction horizontale
        length=50,
        k0=0.0,              # Courbure nulle au début
        k1=0.02,             # Courbure à la fin
        n_steps=200          # Précision de l'approximation
    ))
    print(f"Ajouté : clothoïde de 50m (k: 0 → 0.02)")
    
    print(f"\nLongueur totale de l'axe : {axe.total_length():.2f} m")
    
    # Points sur la clothoïde
    print("\n--- Points sur la clothoïde ---")
    for station in [100, 110, 125, 150]:
        pt = axe.point_at(station)
        print(f"Station {station:6.2f}m : {pt}")


def exemple_tunnel():
    """Exemple d'application tunnel avec déport"""
    print("\n\n=== Exemple 3 : Application tunnel - Calcul de déports ===\n")
    
    # Créer un axe simple
    axe = Axis()
    axe.add_element(LineElement(Point(0, 0), Point(200, 0)))
    
    # Points à projeter (simule des points de levé topographique)
    points_leves = [
        Point(50, 5),      # 5m à gauche/droite
        Point(100, -3),    # 3m de l'autre côté
        Point(150, 10),    # 10m d'écart
    ]
    
    print("Axe de référence : ligne de (0,0) à (200,0)")
    print("\n--- Calcul des déports pour des points levés ---")
    
    for i, pt in enumerate(points_leves, 1):
        resultat = axe.project_point(pt)
        print(f"\nPoint {i} : {pt}")
        print(f"  → Station (PK) : {resultat['station']:.2f} m")
        print(f"  → Déport : {resultat['offset']:.2f} m")
        print(f"  → Point projeté : {resultat['point']}")


if __name__ == "__main__":
    exemple_simple()
    exemple_clothoide()
    exemple_tunnel()
    
    print("\n" + "="*60)
    print("✅ Exemples terminés avec succès !")
    print("="*60)
