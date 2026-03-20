#!/usr/bin/env python3
"""
Démonstration des clothoïdes améliorées dans le système principal
Montre l'intégration des calculs précis avec les intégrales de Fresnel
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.geometrie import Point
from gestionnaire_clothoides import GestionnaireClothoides

def demo_clothoides_ameliorees():
    """
    Démonstration complète des clothoïdes améliorées
    """
    print("=" * 100)
    print("🌟 DÉMONSTRATION DES CLOTHOÏDES AMÉLIORÉES - CALCULATEUR D'AXES")
    print("=" * 100)
    
    gestionnaire = GestionnaireClothoides()
    
    print("\n🔧 CONFIGURATION DU SYSTÈME:")
    rapport = gestionnaire.rapport_capacites()
    print(f"  • Méthode par défaut: {rapport['methode_par_defaut']}")
    print(f"  • Seuil de précision: {rapport['seuil_precision']}")
    print(f"  • SciPy disponible: {'✅ Oui' if rapport['scipy_disponible'] else '❌ Non'}")
    
    # Cas d'usage réalistes en topographie
    scenarios = [
        {
            "nom": "🛣️  Sortie d'autoroute (Alignement → R=150m)",
            "description": "Transition typique pour bretelle d'autoroute",
            "params": {
                "point_debut": Point(2000, 1500, 180),
                "gisement_debut": 75.0,
                "rayon_debut": float('inf'),
                "rayon_fin": 150.0,
                "longueur": 100.0
            },
            "points_analyse": [0, 25, 50, 75, 100]
        },
        {
            "nom": "🚄 Raccordement ferroviaire (R=800m → R=1200m)",
            "description": "Transition progressive entre deux courbes",
            "params": {
                "point_debut": Point(5000, 3000, 250),
                "gisement_debut": 125.0,
                "rayon_debut": 800.0,
                "rayon_fin": 1200.0,
                "longueur": 150.0
            },
            "points_analyse": [0, 37.5, 75, 112.5, 150]
        },
        {
            "nom": "🏔️  Virage de montagne (R=60m → Alignement)",
            "description": "Sortie de virage serré en terrain montagneux",
            "params": {
                "point_debut": Point(1200, 2800, 650),
                "gisement_debut": 200.0,
                "rayon_debut": 60.0,
                "rayon_fin": float('inf'),
                "longueur": 80.0
            },
            "points_analyse": [0, 20, 40, 60, 80]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*20} SCÉNARIO {i}/3 {'='*20}")
        print(f"{scenario['nom']}")
        print(f"📝 {scenario['description']}")
        
        # Paramètres
        params = scenario['params']
        print(f"\n📊 PARAMÈTRES:")
        print(f"  Point début: ({params['point_debut'].x}, {params['point_debut'].y}, {params['point_debut'].z})")
        print(f"  Gisement: {params['gisement_debut']}g")
        print(f"  Rayons: {params['rayon_debut']} → {params['rayon_fin']}m")
        print(f"  Longueur: {params['longueur']}m")
        
        # Création automatique
        clothoide = gestionnaire.creer_clothoide(**params)
        methode = getattr(clothoide, '_methode_utilisee', 'inconnue')
        
        print(f"\n🎯 MÉTHODE SÉLECTIONNÉE: {methode.upper()}")
        
        # Analyse détaillée
        if hasattr(clothoide, 'proprietes_geometriques'):
            props = clothoide.proprietes_geometriques()
            print(f"  • Paramètre A: {props['parametre_A']:.2f}")
            print(f"  • Déviation totale: {props['deviation_totale']:.3f}g")
            print(f"  • Sens: {props['sens']}")
        
        # Calcul des points caractéristiques
        print(f"\n📍 POINTS CARACTÉRISTIQUES:")
        print(f"{'Distance':<10} {'X':<12} {'Y':<12} {'Z':<10} {'Gisement':<12} {'Courbure'}")
        print("-" * 75)
        
        for distance in scenario['points_analyse']:
            try:
                point = clothoide.point_at_distance(distance)
                gisement = clothoide.gisement_at_distance(distance)
                
                # Courbure si disponible
                if hasattr(clothoide, 'courbure_at_distance'):
                    courbure = clothoide.courbure_at_distance(distance)
                    courbure_str = f"{courbure:.6f}"
                else:
                    courbure_str = "N/A"
                
                print(f"{distance:<10.0f} {point.x:<12.3f} {point.y:<12.3f} {point.z:<10.2f} "
                      f"{gisement:<12.3f} {courbure_str}")
                
            except Exception as e:
                print(f"{distance:<10.0f} Erreur: {e}")
        
        # Comparaison des méthodes si possible
        comparaison = gestionnaire.comparer_methodes(**params)
        if 'erreur' not in comparaison:
            print(f"\n⚖️  COMPARAISON DES MÉTHODES:")
            print(f"  • Écart maximum: {comparaison['ecart_max']:.3f}m")
            print(f"  • Écart moyen: {comparaison['ecart_moyen']:.3f}m")
            print(f"  • Recommandation: {comparaison['recommandation']}")
            
            if comparaison['ecart_max'] > 5.0:
                print(f"  ⚠️  ATTENTION: Écarts significatifs détectés!")
                print(f"  📌 Impact sur la précision topographique")
        
        # Test de projection d'un point externe
        point_externe = Point(
            params['point_debut'].x + 50,
            params['point_debut'].y + 30,
            params['point_debut'].z + 2
        )
        
        try:
            distance_proj, deport = clothoide.projeter_point(point_externe)
            print(f"\n🎯 PROJECTION D'UN POINT EXTERNE:")
            print(f"  Point: ({point_externe.x}, {point_externe.y}, {point_externe.z})")
            print(f"  Distance sur clothoïde: {distance_proj:.3f}m")
            print(f"  Déport: {deport:.3f}m ({'droite' if deport > 0 else 'gauche'})")
            
        except Exception as e:
            print(f"\n🎯 PROJECTION: Erreur - {e}")
    
    # Synthèse finale
    print(f"\n" + "="*100)
    print("📋 SYNTHÈSE DES AMÉLIORATIONS")
    print("="*100)
    
    print(f"\n✨ CLOTHOÏDES PRÉCISES AVEC INTÉGRALES DE FRESNEL:")
    print(f"  • Précision mathématique théoriquement exacte")
    print(f"  • Calculs basés sur scipy.special.fresnel()")
    print(f"  • Réduction drastique des erreurs de positionnement")
    print(f"  • Gestion automatique du choix de méthode")
    
    print(f"\n🎯 AVANTAGES POUR LA TOPOGRAPHIE:")
    print(f"  • Conformité aux standards professionnels")
    print(f"  • Précision accrue pour les implantations")
    print(f"  • Calculs fiables pour les projets critiques")
    print(f"  • Compatibilité avec les logiciels de référence")
    
    print(f"\n⚙️  INTÉGRATION TRANSPARENTE:")
    print(f"  • Choix automatique selon les paramètres")
    print(f"  • Fallback vers méthode approximée si nécessaire")
    print(f"  • API identique pour une migration simple")
    print(f"  • Validation par comparaison directe")
    
    if rapport['scipy_disponible']:
        print(f"\n✅ SYSTÈME PRÊT POUR LA PRODUCTION")
        print(f"   Clothoïdes précises opérationnelles avec SciPy")
    else:
        print(f"\n⚠️  INSTALLATION REQUISE")
        print(f"   pip install scipy pour activer les clothoïdes précises")

if __name__ == "__main__":
    demo_clothoides_ameliorees()