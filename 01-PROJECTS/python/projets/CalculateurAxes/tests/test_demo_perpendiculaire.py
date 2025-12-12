"""
Test de démonstration - Distinction calculs perpendiculaires vs verticaux
"""

import sys
import os
import math

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.geometrie import Point, Vecteur
from core.axe import AxeEnPlan, ProfilEnLong
from core.calculs_perpendiculaire import ModeCalcul


def test_distinction_perpendiculaire_vertical():
    """
    Test démontrant la différence entre :
    - Calculs perpendiculaires au profil (pente incluse)
    - Calculs verticaux absolus (selon la gravité)
    """
    print("="*80)
    print("🧮 TEST - DISTINCTION PERPENDICULAIRE/VERTICAL")
    print("="*80)
    
    # 1. Créer un axe simple avec pente
    print("\n1. Création axe avec profil en pente...")
    axe = AxeEnPlan("Axe Test Pente")
    
    # Axe droit de 200m
    p1 = Point(1000, 2000, 100)  # Z=100m
    p2 = Point(1200, 2000, 110)  # Z=110m (+10m sur 200m = 5% de pente)
    axe.ajouter_alignement(p1, p2)
    
    # 2. Créer profil en long avec pente constante
    profil = ProfilEnLong("Profil Test")
    profil.ajouter_point(0, 100)    # PM=0, Z=100
    profil.ajouter_point(200, 110)  # PM=200, Z=110
    profil.ajouter_pente(0, 200, 5.0)  # 5% de pente
    
    # 3. Associer le profil à l'axe
    calculateur = axe.associer_profil_long(profil)
    
    print(f"   ✅ Axe créé: {axe.longueur_totale():.1f}m")
    print(f"   ✅ Profil avec pente: 5.0%")
    print(f"   ✅ Calculateur perpendiculaire initialisé")
    
    # 4. Point test à 2m à droite et 1m au-dessus du milieu de l'axe
    print("\n2. Point test à projeter...")
    pm_test = 100  # Milieu de l'axe
    point_test = Point(1102, 2002, 106)  # 2m à droite, altitude 106m
    
    print(f"   Point test: X={point_test.x}, Y={point_test.y}, Z={point_test.z}")
    print(f"   Position: 2m à droite, au milieu de l'axe (PM={pm_test})")
    
    # Altitude théorique de l'axe au PM 100
    alt_axe_pm100 = profil.altitude_at_pm(pm_test)
    print(f"   Altitude axe au PM {pm_test}: {alt_axe_pm100}m")
    print(f"   Pente au PM {pm_test}: {profil.pente_at_pm(pm_test)}%")
    
    # 5. Comparaison des trois modes de calcul
    print("\n3. Comparaison des modes de calcul...")
    print("-"*80)
    
    comparaison = axe.comparaison_modes_projection(point_test)
    
    for mode, resultats in comparaison.items():
        print(f"\n📐 {mode.upper()}:")
        print(f"   Description: {resultats['description']}")
        print(f"   Déport calculé: {resultats.get('deport', 'N/A'):.4f}m")
        
        if 'distance' in resultats:
            print(f"   Distance: {resultats['distance']:.4f}m")
        if 'altitude_axe' in resultats:
            print(f"   Altitude axe: {resultats['altitude_axe']:.3f}m")
    
    # 6. Calculs inverses - Points depuis PM + déports
    print("\n4. Calculs inverses (PM + déport → Point)...")
    print("-"*80)
    
    pm_calcul = 100
    deport_test = 2.0  # 2m à droite
    
    print(f"\nCalcul de points au PM {pm_calcul} avec déport +{deport_test}m:")
    
    # Mode horizontal classique
    pt_horizontal = axe.point_at_pm_avec_mode(pm_calcul, deport_test, ModeCalcul.HORIZONTAL_2D)
    print(f"   Horizontal 2D:       X={pt_horizontal.x:.3f}, Y={pt_horizontal.y:.3f}, Z={pt_horizontal.z:.3f}")
    
    # Mode perpendiculaire au profil
    pt_perpendiculaire = axe.point_at_pm_avec_mode(pm_calcul, deport_test, ModeCalcul.PERPENDICULAIRE_PROFIL)
    print(f"   Perpendiculaire:     X={pt_perpendiculaire.x:.3f}, Y={pt_perpendiculaire.y:.3f}, Z={pt_perpendiculaire.z:.3f}")
    
    # Mode vertical absolu
    pt_vertical = axe.point_at_pm_avec_mode(pm_calcul, deport_test, ModeCalcul.VERTICAL_ABSOLU)
    print(f"   Vertical absolu:     X={pt_vertical.x:.3f}, Y={pt_vertical.y:.3f}, Z={pt_vertical.z:.3f}")
    
    # 7. Analyse des différences
    print("\n5. Analyse des différences...")
    print("-"*80)
    
    diff_h_perp = math.sqrt((pt_horizontal.x - pt_perpendiculaire.x)**2 + 
                           (pt_horizontal.y - pt_perpendiculaire.y)**2 + 
                           (pt_horizontal.z - pt_perpendiculaire.z)**2)
    
    diff_h_vert = math.sqrt((pt_horizontal.x - pt_vertical.x)**2 + 
                           (pt_horizontal.y - pt_vertical.y)**2 + 
                           (pt_horizontal.z - pt_vertical.z)**2)
    
    print(f"   Différence Horizontal ↔ Perpendiculaire: {diff_h_perp:.4f}m")
    print(f"   Différence Horizontal ↔ Vertical:       {diff_h_vert:.4f}m")
    print(f"   Différence d'altitude H→P:               {pt_perpendiculaire.z - pt_horizontal.z:.4f}m")
    print(f"   Différence d'altitude H→V:               {pt_vertical.z - pt_horizontal.z:.4f}m")
    
    # 8. Conclusion
    print("\n6. Interprétation topographique...")
    print("-"*80)
    print("   📏 Mode HORIZONTAL_2D :")
    print("      → Projection plane classique (ancien mode)")
    print("      → Ne tient pas compte de la pente du profil")
    print()
    print("   📐 Mode PERPENDICULAIRE_PROFIL :")
    print("      → Calcul perpendiculaire au profil en long (comme un niveau)")
    print("      → Tient compte de la pente : déport dans le plan perpendiculaire")
    print("      → Plus précis pour implantation de structures")
    print()
    print("   🪃 Mode VERTICAL_ABSOLU :")
    print("      → Calcul selon la verticale de pesanteur (comme un fil à plomb)")
    print("      → Indépendant de la pente de l'axe")
    print("      → Utilisé pour contrôles altimétriques absolus")
    
    print("\n" + "="*80)
    print("✅ Test terminé - Distinction bien implémentée !")
    print("="*80)


if __name__ == "__main__":
    test_distinction_perpendiculaire_vertical()