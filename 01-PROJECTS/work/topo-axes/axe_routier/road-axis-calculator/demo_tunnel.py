"""
Démonstration interactive du calculateur d'axes routiers
Montre un cas d'utilisation complet : tunnel en courbe avec profil en long
"""
from src.models import (Axis, Point, LineElement, CircularArcElement, 
                        VerticalProfile, LineProfile, ParabolicVerticalCurve)
from math import radians, degrees


def demo_tunnel_complet():
    """
    Exemple complet : tunnel en courbe
    - Axe en plan avec ligne droite + courbe + ligne droite
    - Profil en long avec descente, palier en tunnel, remontée
    """
    print("="*70)
    print("  DÉMONSTRATION : TUNNEL ROUTIER EN COURBE")
    print("="*70)
    
    # =========================================================================
    # 1. DÉFINITION DE L'AXE EN PLAN
    # =========================================================================
    print("\n📍 ÉTAPE 1 : Définition de l'axe en plan")
    print("-" * 70)
    
    axe = Axis()
    
    # Approche : ligne droite 300m
    axe.add_element(LineElement(Point(0, 0), Point(300, 0)))
    print("✓ Approche : ligne droite 300m (PK 0+000 → PK 0+300)")
    
    # Courbe : arc de cercle rayon 500m, 45°
    centre_courbe = Point(300, 500)
    angle_debut = radians(270)  # 270° = vers le bas
    angle_fin = radians(315)    # 315° = 45° de rotation
    axe.add_element(CircularArcElement(
        center=centre_courbe,
        radius=500,
        start_angle=angle_debut,
        end_angle=angle_fin,
        ccw=True
    ))
    longueur_courbe = 500 * radians(45)  # L = R × θ
    print(f"✓ Courbe : rayon 500m, 45° ({longueur_courbe:.2f}m)")
    
    # Sortie : ligne droite 300m
    # Point de fin de courbe
    pt_fin_courbe = axe.point_at(300 + longueur_courbe)
    direction_sortie = 45  # Direction à 45° après la courbe
    pt_fin = Point(
        pt_fin_courbe.x + 300 * 0.707,  # cos(45°)
        pt_fin_courbe.y + 300 * 0.707   # sin(45°)
    )
    axe.add_element(LineElement(pt_fin_courbe, pt_fin))
    print(f"✓ Sortie : ligne droite 300m")
    
    longueur_totale_plan = axe.total_length()
    print(f"\n→ Longueur totale de l'axe : {longueur_totale_plan:.2f} m")
    
    # =========================================================================
    # 2. DÉFINITION DU PROFIL EN LONG
    # =========================================================================
    print("\n📈 ÉTAPE 2 : Définition du profil en long")
    print("-" * 70)
    
    profil = VerticalProfile()
    
    # Zone 1 : Approche en descente -4%
    profil.add_element(LineProfile(
        start_station=0,
        start_elevation=200.0,
        end_station=200,
        end_elevation=200.0 - 0.04 * 200  # -4% sur 200m
    ))
    print("✓ Approche : descente -4% (PK 0+000 → PK 0+200)")
    print(f"  Altitude : 200.00m → {200.0 - 0.04 * 200:.2f}m")
    
    # Zone 2 : Raccordement parabolique d'entrée
    elev_200 = profil.elevation_at(200)
    profil.add_element(ParabolicVerticalCurve(
        start_station=200,
        start_elevation=elev_200,
        length=100,
        slope_in=-0.04,  # -4%
        slope_out=-0.005 # -0.5% dans le tunnel
    ))
    print("✓ Raccordement d'entrée : -4% → -0.5% (100m)")
    
    # Zone 3 : Palier en tunnel -0.5%
    elev_300 = profil.elevation_at(300)
    longueur_tunnel = longueur_courbe + 100  # La courbe + un peu après
    fin_tunnel = 300 + longueur_tunnel
    profil.add_element(LineProfile(
        start_station=300,
        start_elevation=elev_300,
        end_station=fin_tunnel,
        end_elevation=elev_300 - 0.005 * longueur_tunnel
    ))
    print(f"✓ Palier en tunnel : -0.5% ({longueur_tunnel:.2f}m)")
    
    # Zone 4 : Raccordement parabolique de sortie
    elev_fin_tunnel = profil.elevation_at(fin_tunnel)
    profil.add_element(ParabolicVerticalCurve(
        start_station=fin_tunnel,
        start_elevation=elev_fin_tunnel,
        length=100,
        slope_in=-0.005,  # -0.5%
        slope_out=0.03    # +3% en sortie
    ))
    print("✓ Raccordement de sortie : -0.5% → +3% (100m)")
    
    # Zone 5 : Sortie en montée +3%
    fin_raccordement = fin_tunnel + 100
    elev_fin_raccordement = profil.elevation_at(fin_raccordement)
    profil.add_element(LineProfile(
        start_station=fin_raccordement,
        start_elevation=elev_fin_raccordement,
        end_station=longueur_totale_plan,
        end_elevation=elev_fin_raccordement + 0.03 * (longueur_totale_plan - fin_raccordement)
    ))
    print(f"✓ Sortie : montée +3%")
    
    print(f"\n→ Longueur totale du profil : {profil.total_length():.2f} m")
    
    # =========================================================================
    # 3. POINTS CARACTÉRISTIQUES DU TUNNEL
    # =========================================================================
    print("\n🎯 ÉTAPE 3 : Points caractéristiques du tunnel")
    print("-" * 70)
    print(f"{'PK':<12} {'X (m)':<10} {'Y (m)':<10} {'Z (m)':<10} {'Pente (%)':<12} {'Description'}")
    print("-" * 90)
    
    points_caracteristiques = [
        (0, "Début"),
        (200, "Début raccordement entrée"),
        (300, "Entrée tunnel"),
        (300 + longueur_courbe / 2, "Milieu courbe"),
        (fin_tunnel, "Sortie tunnel"),
        (fin_raccordement, "Fin raccordement"),
        (longueur_totale_plan, "Fin")
    ]
    
    for pk, desc in points_caracteristiques:
        pt = axe.point_at(pk)
        z = profil.elevation_at(pk)
        pente = profil.slope_percent_at(pk)
        pk_format = f"{int(pk/1000)}+{int(pk%1000):03d}"
        print(f"{pk_format:<12} {pt.x:<10.2f} {pt.y:<10.2f} {z:<10.2f} {pente:<12.2f} {desc}")
    
    # =========================================================================
    # 4. SIMULATION DE LEVÉS TOPOGRAPHIQUES
    # =========================================================================
    print("\n📏 ÉTAPE 4 : Simulation de levés topographiques (contrôle qualité)")
    print("-" * 70)
    
    # Simuler quelques points levés avec des écarts
    points_leves = [
        (Point(150, 2), "Point de contrôle approche"),
        (Point(300, -1), "Entrée tunnel"),
        (Point(400, 5), "Dans la courbe"),
        (Point(500, -3), "Sortie tunnel")
    ]
    
    print(f"{'Description':<30} {'X levé':<10} {'Y levé':<10} {'Station':<12} {'Déport (m)':<12}")
    print("-" * 90)
    
    for pt_leve, description in points_leves:
        projection = axe.project_point(pt_leve)
        pk = projection['station']
        offset = projection['offset']
        pk_format = f"{int(pk/1000)}+{int(pk%1000):03d}"
        
        print(f"{description:<30} {pt_leve.x:<10.2f} {pt_leve.y:<10.2f} {pk_format:<12} {offset:<12.2f}")
    
    # =========================================================================
    # 5. STATISTIQUES DU PROJET
    # =========================================================================
    print("\n📊 ÉTAPE 5 : Statistiques du projet")
    print("-" * 70)
    
    # Calcul de la dénivelée
    z_debut = profil.elevation_at(0)
    z_fin = profil.elevation_at(longueur_totale_plan)
    denivelee = z_fin - z_debut
    
    # Point le plus bas
    z_min = min([profil.elevation_at(pk) for pk, _ in points_caracteristiques])
    
    print(f"Longueur totale        : {longueur_totale_plan:.2f} m")
    print(f"Longueur du tunnel     : {longueur_tunnel:.2f} m")
    print(f"Rayon de la courbe     : 500.00 m")
    print(f"Angle de la courbe     : 45.00°")
    print(f"Altitude début         : {z_debut:.2f} m")
    print(f"Altitude fin           : {z_fin:.2f} m")
    print(f"Dénivelée              : {denivelee:+.2f} m")
    print(f"Point le plus bas      : {z_min:.2f} m")
    print(f"Pente max descente     : -4.00 %")
    print(f"Pente max montée       : +3.00 %")
    print(f"Pente en tunnel        : -0.50 %")
    
    # =========================================================================
    # 6. EXPORT DE DONNÉES
    # =========================================================================
    print("\n💾 ÉTAPE 6 : Export de données (échantillon)")
    print("-" * 70)
    
    print(f"{'PK':<12} {'X':<12} {'Y':<12} {'Z':<12}")
    print("-" * 50)
    
    # Export tous les 50m
    pk = 0
    while pk <= longueur_totale_plan:
        pt = axe.point_at(pk)
        z = profil.elevation_at(pk)
        pk_format = f"{int(pk/1000)}+{int(pk%1000):03d}"
        print(f"{pk_format:<12} {pt.x:<12.2f} {pt.y:<12.2f} {z:<12.2f}")
        pk += 50
    
    print("\n" + "="*70)
    print("  ✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS")
    print("="*70)
    print("\nCe tunnel en courbe est maintenant complètement défini et calculable.")
    print("Vous pouvez utiliser ces fonctions pour :")
    print("  • Calculer n'importe quel point 3D sur l'axe")
    print("  • Projeter des points de levé topographique")
    print("  • Calculer des déports pour le contrôle qualité")
    print("  • Exporter les données vers Excel ou AutoCAD")


if __name__ == "__main__":
    demo_tunnel_complet()
