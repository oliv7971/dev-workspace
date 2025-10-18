#!/usr/bin/env python3
"""
Comparaison des deux méthodes de calcul des clothoïdes
Démontre l'amélioration apportée par l'implémentation précise
"""
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.geometrie import Point
from core.elements import Clothoide as ClothoideApproximee
from clothoide_precise import ClothoidePrecise

def comparer_clothoides():
    """
    Compare les deux implémentations sur les mêmes paramètres
    """
    print("=" * 90)
    print("🔍 COMPARAISON CLOTHOÏDE APPROXIMÉE vs PRÉCISE")
    print("=" * 90)
    
    # Paramètres identiques pour les deux clothoïdes
    point_debut = Point(1000, 2000, 100)
    gisement_debut = 50.0
    rayon_debut = float('inf')
    rayon_fin = 200.0
    longueur = 100.0
    
    print(f"Paramètres communs:")
    print(f"  Point début: ({point_debut.x}, {point_debut.y}, {point_debut.z})")
    print(f"  Gisement début: {gisement_debut}g")
    print(f"  Transition: Alignement → Courbe R={rayon_fin}m")
    print(f"  Longueur: {longueur}m")
    
    # Création des deux clothoïdes
    try:
        clothoide_approx = ClothoideApproximee(point_debut, gisement_debut, rayon_debut, rayon_fin, longueur)
        clothoide_precise = ClothoidePrecise(point_debut, gisement_debut, rayon_debut, rayon_fin, longueur)
        
        print(f"\n✅ Deux clothoïdes créées avec succès")
        
        # Comparaison des propriétés
        print(f"\n📊 PROPRIÉTÉS GÉOMÉTRIQUES:")
        print(f"{'Propriété':<20} {'Approximée':<15} {'Précise':<15} {'Différence'}")
        print("-" * 70)
        
        # Paramètre A (si disponible)
        try:
            A_precise = clothoide_precise.A
            print(f"{'Paramètre A':<20} {'N/A':<15} {A_precise:<15.2f} {'N/A'}")
        except:
            pass
        
        # Comparaison point par point
        distances_test = [0, 10, 25, 50, 75, 100]
        
        print(f"\n📍 COMPARAISON DES POINTS:")
        print(f"{'Distance':<8} {'Méthode':<12} {'X':<12} {'Y':<12} {'Gisement':<12} {'Écart X':<10} {'Écart Y':<10} {'Écart Total'}")
        print("-" * 100)
        
        for distance in distances_test:
            try:
                # Points calculés par les deux méthodes
                pt_approx = clothoide_approx.point_at_distance(distance)
                pt_precise = clothoide_precise.point_at_distance(distance)
                
                gis_approx = clothoide_approx.gisement_at_distance(distance)
                gis_precise = clothoide_precise.gisement_at_distance(distance)
                
                # Écarts
                ecart_x = pt_precise.x - pt_approx.x
                ecart_y = pt_precise.y - pt_approx.y
                ecart_total = math.sqrt(ecart_x**2 + ecart_y**2)
                
                # Affichage approximée
                print(f"{distance:<8.0f} {'Approximée':<12} {pt_approx.x:<12.3f} {pt_approx.y:<12.3f} {gis_approx:<12.3f}")
                
                # Affichage précise avec écarts
                print(f"{distance:<8.0f} {'Précise':<12} {pt_precise.x:<12.3f} {pt_precise.y:<12.3f} {gis_precise:<12.3f} "
                      f"{ecart_x:<10.3f} {ecart_y:<10.3f} {ecart_total:<10.3f}")
                
                print()  # Ligne vide pour clarté
                
            except Exception as e:
                print(f"{distance:<8.0f} Erreur: {e}")
        
        # Analyse des écarts
        print(f"\n📈 ANALYSE DES ÉCARTS:")
        ecarts_totaux = []
        
        for distance in [25, 50, 75, 100]:
            try:
                pt_approx = clothoide_approx.point_at_distance(distance)
                pt_precise = clothoide_precise.point_at_distance(distance)
                
                ecart = math.sqrt((pt_precise.x - pt_approx.x)**2 + (pt_precise.y - pt_approx.y)**2)
                ecarts_totaux.append(ecart)
                print(f"  Distance {distance}m: écart = {ecart:.3f}m")
            except:
                pass
        
        if ecarts_totaux:
            ecart_max = max(ecarts_totaux)
            ecart_moyen = sum(ecarts_totaux) / len(ecarts_totaux)
            print(f"\n  Écart maximum: {ecart_max:.3f}m")
            print(f"  Écart moyen: {ecart_moyen:.3f}m")
        
        # Test de projection comparée
        print(f"\n🎯 COMPARAISON DES PROJECTIONS:")
        point_externe = Point(1050, 2050, 105)
        
        try:
            dist_approx, deport_approx = clothoide_approx.projeter_point(point_externe)
            dist_precise, deport_precise = clothoide_precise.projeter_point(point_externe)
            
            print(f"Point externe: ({point_externe.x}, {point_externe.y})")
            print(f"Approximée - Distance: {dist_approx:.3f}m, Déport: {deport_approx:.3f}m")
            print(f"Précise    - Distance: {dist_precise:.3f}m, Déport: {deport_precise:.3f}m")
            print(f"Écart distance: {abs(dist_precise - dist_approx):.3f}m")
            print(f"Écart déport: {abs(deport_precise - deport_approx):.3f}m")
            
        except Exception as e:
            print(f"Erreur projection: {e}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        if ecarts_totaux and max(ecarts_totaux) > 1.0:
            print(f"  ⚠️  Écarts significatifs détectés (max: {max(ecarts_totaux):.1f}m)")
            print(f"  📌 Recommandation: Utiliser ClothoidePrecise pour la production")
        else:
            print(f"  ✅ Écarts acceptables pour la plupart des applications")
        
        print(f"  🔧 ClothoidePrecise utilise les intégrales de Fresnel (scipy)")
        print(f"  📊 Précision mathématique théoriquement exacte")
        print(f"  ⚡ Performance légèrement inférieure (calculs plus complexes)")
        
    except Exception as e:
        print(f"❌ Erreur lors de la comparaison: {e}")

def test_cas_extremes():
    """
    Test des cas extrêmes pour valider la robustesse
    """
    print(f"\n" + "=" * 90)
    print("🧪 TEST DES CAS EXTRÊMES")
    print("=" * 90)
    
    cas_tests = [
        {
            'nom': 'Clothoïde courte (10m)',
            'longueur': 10.0,
            'rayon_fin': 500.0
        },
        {
            'nom': 'Clothoïde longue (200m)',
            'longueur': 200.0,
            'rayon_fin': 300.0
        },
        {
            'nom': 'Rayon très petit (50m)',
            'longueur': 50.0,
            'rayon_fin': 50.0
        },
        {
            'nom': 'Rayon très grand (2000m)',
            'longueur': 100.0,
            'rayon_fin': 2000.0
        }
    ]
    
    for cas in cas_tests:
        print(f"\n🔬 {cas['nom']}:")
        try:
            clothoide = ClothoidePrecise(
                Point(0, 0, 0), 0.0, float('inf'), 
                cas['rayon_fin'], cas['longueur']
            )
            
            # Test du point final
            pt_fin = clothoide.point_at_distance(cas['longueur'])
            gis_fin = clothoide.gisement_at_distance(cas['longueur'])
            
            print(f"  ✅ Point final: ({pt_fin.x:.3f}, {pt_fin.y:.3f})")
            print(f"  ✅ Gisement final: {gis_fin:.3f}g")
            print(f"  ✅ Paramètre A: {clothoide.A:.2f}")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")

if __name__ == "__main__":
    comparer_clothoides()
    test_cas_extremes()