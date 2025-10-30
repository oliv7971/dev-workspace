"""
Exemple complet : Axe en plan + Profil en long
Simule un axe routier complet avec géométrie horizontale et verticale
"""
from src.models.point import Point
from src.models.elements import LineElement, CircularArcElement, ClothoidElement
from src.models.axis import Axis
from src.models.profile import (LineProfile, CircularVerticalCurve, 
                                 ParabolicVerticalCurve, VerticalProfile)
from math import radians, sqrt


def exemple_profil_simple():
    """Exemple simple de profil en long"""
    print("=== Exemple 1 : Profil en long simple ===\n")
    
    profil = VerticalProfile()
    
    # Segment 1: Rampe montante de 5% sur 100m, départ à altitude 100m
    profil.add_element(LineProfile(
        start_station=0,
        start_elevation=100.0,
        end_station=100,
        end_elevation=105.0  # +5m = 5%
    ))
    print("Ajouté : rampe +5% de 0 à 100m (alt 100→105m)")
    
    # Segment 2: Raccordement parabolique (sommet de côte)
    profil.add_element(ParabolicVerticalCurve(
        start_station=100,
        start_elevation=105.0,
        length=60,
        slope_in=0.05,   # +5%
        slope_out=-0.02  # -2%
    ))
    print("Ajouté : raccordement parabolique 60m (pente +5% → -2%)")
    
    # Segment 3: Descente légère de 2% sur 140m
    elev_end_curve = profil.elevation_at(160)  # altitude à la fin du raccordement
    profil.add_element(LineProfile(
        start_station=160,
        start_elevation=elev_end_curve,
        end_station=300,
        end_elevation=elev_end_curve - 0.02 * 140  # -2% sur 140m
    ))
    print(f"Ajouté : descente -2% de 160 à 300m")
    
    print(f"\nLongueur totale du profil : {profil.total_length():.2f} m")
    
    # Afficher quelques points du profil
    print("\n--- Altitudes et pentes le long du profil ---")
    print(f"{'Station (m)':<15} {'Altitude (m)':<15} {'Pente (%)':<15}")
    print("-" * 45)
    for station in [0, 50, 100, 130, 160, 200, 300]:
        elev = profil.elevation_at(station)
        slope = profil.slope_percent_at(station)
        print(f"{station:<15.1f} {elev:<15.2f} {slope:<15.2f}")
    
    return profil


def exemple_profil_tunnel():
    """Exemple de profil typique d'un tunnel"""
    print("\n\n=== Exemple 2 : Profil en long de tunnel ===\n")
    
    profil = VerticalProfile()
    
    # Descente d'approche : -3%
    profil.add_element(LineProfile(
        start_station=0,
        start_elevation=150.0,
        end_station=200,
        end_elevation=144.0  # -6m sur 200m = -3%
    ))
    print("Approche : descente -3% (200m)")
    
    # Raccordement parabolique concave (entrée tunnel)
    profil.add_element(ParabolicVerticalCurve(
        start_station=200,
        start_elevation=144.0,
        length=80,
        slope_in=-0.03,  # -3%
        slope_out=-0.005 # -0.5% (quasi horizontal dans tunnel)
    ))
    print("Raccordement d'entrée : -3% → -0.5% (80m)")
    
    # Palier quasi-horizontal dans le tunnel : -0.5%
    elev_middle = profil.elevation_at(280)
    profil.add_element(LineProfile(
        start_station=280,
        start_elevation=elev_middle,
        end_station=720,
        end_elevation=elev_middle - 0.005 * 440  # -0.5% sur 440m
    ))
    print("Tunnel : palier -0.5% (440m)")
    
    # Raccordement parabolique concave (sortie tunnel)
    elev_before_exit = profil.elevation_at(720)
    profil.add_element(ParabolicVerticalCurve(
        start_station=720,
        start_elevation=elev_before_exit,
        length=80,
        slope_in=-0.005,  # -0.5%
        slope_out=0.025   # +2.5% (remontée)
    ))
    print("Raccordement de sortie : -0.5% → +2.5% (80m)")
    
    # Remontée : +2.5%
    elev_exit = profil.elevation_at(800)
    profil.add_element(LineProfile(
        start_station=800,
        start_elevation=elev_exit,
        end_station=1000,
        end_elevation=elev_exit + 0.025 * 200  # +2.5% sur 200m
    ))
    print("Sortie : remontée +2.5% (200m)")
    
    print(f"\nLongueur totale : {profil.total_length():.2f} m")
    
    # Points caractéristiques
    print("\n--- Points caractéristiques ---")
    points_car = [
        (0, "Début approche"),
        (200, "Début raccordement entrée"),
        (280, "Entrée tunnel"),
        (720, "Sortie tunnel"),
        (800, "Fin raccordement sortie"),
        (1000, "Fin")
    ]
    
    for station, description in points_car:
        elev = profil.elevation_at(station)
        slope = profil.slope_percent_at(station)
        print(f"PK {station:>4} ({description:<30}) : Z={elev:6.2f}m, p={slope:+5.2f}%")
    
    return profil


def exemple_complet_3d():
    """Exemple complet : axe en plan + profil en long = trajectoire 3D"""
    print("\n\n=== Exemple 3 : Axe routier complet 3D ===\n")
    
    # 1. Créer l'axe en plan
    axe_plan = Axis()
    axe_plan.add_element(LineElement(Point(0, 0), Point(200, 0)))
    axe_plan.add_element(CircularArcElement(
        center=Point(200, 50),
        radius=50,
        start_angle=radians(270),
        end_angle=radians(360),
        ccw=True
    ))
    axe_plan.add_element(LineElement(Point(250, 50), Point(350, 50)))
    
    print(f"Axe en plan : {axe_plan.total_length():.2f} m")
    
    # 2. Créer le profil en long
    profil = VerticalProfile()
    profil.add_element(LineProfile(0, 100.0, 200, 110.0))  # +5%
    profil.add_element(ParabolicVerticalCurve(200, 110.0, 78.54, 0.05, 0.0))
    profil.add_element(LineProfile(278.54, profil.elevation_at(278.54), 
                                   axe_plan.total_length(), 
                                   profil.elevation_at(278.54)))
    
    print(f"Profil en long : {profil.total_length():.2f} m")
    
    # 3. Calculer des points 3D (combinaison plan + profil)
    print("\n--- Coordonnées 3D de points sur l'axe ---")
    print(f"{'Station (m)':<15} {'X (m)':<12} {'Y (m)':<12} {'Z (m)':<12} {'Pente (%)':<12}")
    print("-" * 63)
    
    for station in [0, 50, 100, 150, 200, 250, 300, axe_plan.total_length()]:
        if station <= axe_plan.total_length() and station <= profil.total_length():
            # Coordonnées en plan (X, Y)
            pt_plan = axe_plan.point_at(station)
            
            # Altitude (Z)
            altitude = profil.elevation_at(station)
            
            # Pente
            pente = profil.slope_percent_at(station)
            
            print(f"{station:<15.2f} {pt_plan.x:<12.2f} {pt_plan.y:<12.2f} {altitude:<12.2f} {pente:<12.2f}")
    
    # 4. Exemple de projection 3D d'un point
    print("\n--- Projection d'un point sur l'axe 3D ---")
    point_leve = Point(100, 10)  # Point levé au sol (sans altitude)
    
    # Projection sur l'axe en plan
    proj_plan = axe_plan.project_point(point_leve)
    station_proj = proj_plan['station']
    
    # Altitude théorique à cette station
    altitude_theorique = profil.elevation_at(station_proj)
    
    print(f"Point levé : X={point_leve.x:.2f}, Y={point_leve.y:.2f}")
    print(f"Projection sur axe :")
    print(f"  Station : {station_proj:.2f} m")
    print(f"  Déport horizontal : {proj_plan['offset']:.2f} m")
    print(f"  Altitude théorique : {altitude_theorique:.2f} m")
    print(f"  Coordonnées projetées : X={proj_plan['point'].x:.2f}, Y={proj_plan['point'].y:.2f}, Z={altitude_theorique:.2f}")


def exemple_export_profil():
    """Exemple d'export de données de profil pour visualisation"""
    print("\n\n=== Exemple 4 : Export de profil pour traçage ===\n")
    
    profil = VerticalProfile()
    profil.add_element(LineProfile(0, 100.0, 100, 105.0))
    profil.add_element(ParabolicVerticalCurve(100, 105.0, 60, 0.05, -0.02))
    profil.add_element(LineProfile(160, profil.elevation_at(160), 300, 
                                   profil.elevation_at(160) - 0.02 * 140))
    
    # Obtenir les points pour traçage
    points = profil.get_profile_points(step=20.0)
    
    print(f"Points du profil (pas de 20m) :")
    print(f"{'Station (m)':<15} {'Altitude (m)':<15}")
    print("-" * 30)
    for station, elevation in points:
        print(f"{station:<15.2f} {elevation:<15.2f}")
    
    print(f"\nNombre total de points : {len(points)}")
    print("(Ces données peuvent être exportées vers Excel, CSV, ou tracées avec matplotlib)")


if __name__ == "__main__":
    exemple_profil_simple()
    exemple_profil_tunnel()
    exemple_complet_3d()
    exemple_export_profil()
    
    print("\n" + "="*70)
    print("✅ Tous les exemples de profils en long terminés avec succès !")
    print("="*70)
