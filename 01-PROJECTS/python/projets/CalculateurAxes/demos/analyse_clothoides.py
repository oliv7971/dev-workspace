#!/usr/bin/env python3
"""
Analyse des méthodes de calcul des clothoïdes
Comparaison : Approximation actuelle vs. Intégrales de Fresnel
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import math
import numpy as np
from scipy import special
from core.geometrie import Point
from core.elements import Clothoide

def analyse_methode_actuelle():
    """Analyse de la méthode actuellement implémentée"""
    print("=" * 80)
    print("🔍 ANALYSE DE LA MÉTHODE ACTUELLE DES CLOTHOÏDES")
    print("=" * 80)
    
    print("\n📋 MÉTHODE UTILISÉE ACTUELLEMENT:")
    print("-" * 50)
    print("1. 📐 Paramètre A: A² = R × L (correct)")
    print("2. 📈 Courbure linéaire: κ(s) = κ₀ + s/A² (correct)")
    print("3. ❌ Géométrie: Approximation linéaire simplifiée")
    print("4. ❌ Points: Calcul direct sans intégrales")
    print("5. ❌ Gisements: Approximation quadratique")
    
    print("\n⚠️ LIMITATIONS IDENTIFIÉES:")
    print("-" * 50)
    print("• Géométrie incorrecte pour grandes déviations")
    print("• Points calculés en ligne droite (incorrect)")
    print("• Gisements approximatifs")
    print("• Pas d'utilisation des intégrales de Fresnel")
    print("• Précision insuffisante pour usage professionnel")
    
    # Test avec clothoïde exemple
    print("\n🧪 TEST DE LA MÉTHODE ACTUELLE:")
    print("-" * 50)
    
    clothoide = Clothoide(
        point_debut=Point(1000, 2000, 100),
        gisement_debut=50.0,
        rayon_debut=float('inf'),
        rayon_fin=200.0,
        longueur=100.0
    )
    
    print(f"Clothoïde ∞ → R{clothoide.rayon_fin}m, L={clothoide._longueur}m")
    print(f"Paramètre A: {clothoide.A:.2f}")
    
    distances_test = [0, 25, 50, 75, 100]
    print(f"\n{'Distance':<10} {'X':<12} {'Y':<12} {'Gisement':<10} {'Courbure'}")
    print("-" * 60)
    
    for d in distances_test:
        pt = clothoide.point_at_distance(d)
        gis = clothoide.gisement_at_distance(d)
        
        # Courbure théorique
        ratio = d / clothoide._longueur
        courbure_debut = 0  # Alignement
        courbure_fin = 1/clothoide.rayon_fin
        courbure = courbure_debut + ratio * (courbure_fin - courbure_debut)
        
        print(f"{d:<10.0f} {pt.x:<12.2f} {pt.y:<12.2f} {gis:<10.2f} {courbure:<10.6f}")

def theorie_clothoides():
    """Explication théorique des clothoïdes"""
    print("\n" + "=" * 80)
    print("📚 THÉORIE DES CLOTHOÏDES")
    print("=" * 80)
    
    print("\n🎯 DÉFINITION:")
    print("-" * 50)
    print("Une clothoïde est une courbe où la courbure κ varie linéairement")
    print("avec l'abscisse curviligne s:")
    print()
    print("    κ(s) = s / A²")
    print()
    print("Où A est le paramètre de la clothoïde: A² = R × L")
    print("• R : rayon de courbure final")
    print("• L : longueur de la clothoïde")
    
    print("\n🧮 ÉQUATIONS PARAMÉTRIQUES:")
    print("-" * 50)
    print("Les coordonnées d'un point sur la clothoïde sont données par:")
    print()
    print("    x(s) = ∫₀ˢ cos(t²/(2A²)) dt")
    print("    y(s) = ∫₀ˢ sin(t²/(2A²)) dt")
    print()
    print("Ces intégrales sont les INTÉGRALES DE FRESNEL !")
    
    print("\n🔬 INTÉGRALES DE FRESNEL:")
    print("-" * 50)
    print("Définitions normalisées:")
    print("    C(u) = ∫₀ᵘ cos(πt²/2) dt")
    print("    S(u) = ∫₀ᵘ sin(πt²/2) dt")
    print()
    print("Relation avec la clothoïde:")
    print("    u = s × √(π/(2A²))")
    print("    x(s) = A × √(2/π) × C(u)")
    print("    y(s) = A × √(2/π) × S(u)")
    
    print("\n📐 AUTRES FORMULES IMPORTANTES:")
    print("-" * 50)
    print("• Gisement: θ(s) = s²/(2A²)")
    print("• Rayon local: R(s) = A²/s")
    print("• Déplacement tangentiel: Δt = s³/(6A²R)")
    print("• Déplacement normal: Δn = s⁵/(40A⁴R)")

def implementation_fresnel():
    """Implémentation avec intégrales de Fresnel"""
    print("\n" + "=" * 80)
    print("⚡ IMPLÉMENTATION AVEC INTÉGRALES DE FRESNEL")
    print("=" * 80)
    
    def clothoide_fresnel(s, A, gisement_debut=0):
        """
        Calcule les coordonnées d'un point sur une clothoïde
        en utilisant les intégrales de Fresnel
        
        Args:
            s: Distance curviligne
            A: Paramètre de la clothoïde
            gisement_debut: Gisement initial en grades
            
        Returns:
            (x, y, gisement) : Coordonnées et gisement local
        """
        if s == 0:
            return 0, 0, gisement_debut
        
        # Paramètre normalisé des intégrales de Fresnel
        u = s * math.sqrt(math.pi / (2 * A * A))
        
        # Intégrales de Fresnel (scipy)
        S_fresnel, C_fresnel = special.fresnel(u)
        
        # Coordonnées locales de la clothoïde
        x_local = A * math.sqrt(2 / math.pi) * C_fresnel
        y_local = A * math.sqrt(2 / math.pi) * S_fresnel
        
        # Gisement local (en radians puis grades)
        theta_rad = s * s / (2 * A * A)
        theta_grades = theta_rad * 200 / math.pi
        gisement_local = (gisement_debut + theta_grades) % 400
        
        # Rotation selon gisement de début
        gis_debut_rad = gisement_debut * math.pi / 200
        cos_gis = math.cos(gis_debut_rad)
        sin_gis = math.sin(gis_debut_rad)
        
        x_global = x_local * cos_gis - y_local * sin_gis
        y_global = x_local * sin_gis + y_local * cos_gis
        
        return x_global, y_global, gisement_local
    
    print("\n🧪 TEST AVEC INTÉGRALES DE FRESNEL:")
    print("-" * 50)
    
    # Paramètres de test
    A = 141.42  # Paramètre clothoïde
    gis_debut = 50.0  # grades
    longueur = 100.0
    
    print(f"Clothoïde: A={A:.2f}, Gis_début={gis_debut:.1f}g, L={longueur:.0f}m")
    print()
    print(f"{'Distance':<10} {'X (Fresnel)':<15} {'Y (Fresnel)':<15} {'Gisement':<12} {'Courbure'}")
    print("-" * 70)
    
    distances_test = [0, 20, 40, 60, 80, 100]
    
    for s in distances_test:
        x, y, gis = clothoide_fresnel(s, A, gis_debut)
        courbure = s / (A * A) if s > 0 else 0
        
        print(f"{s:<10.0f} {x:<15.3f} {y:<15.3f} {gis:<12.2f} {courbure:<10.6f}")
    
    return clothoide_fresnel

def comparaison_methodes():
    """Comparaison entre méthode actuelle et Fresnel"""
    print("\n" + "=" * 80)
    print("⚖️ COMPARAISON DES MÉTHODES")
    print("=" * 80)
    
    # Clothoïde test
    clothoide_actuelle = Clothoide(
        point_debut=Point(1000, 2000, 100),
        gisement_debut=50.0,
        rayon_debut=float('inf'),
        rayon_fin=200.0,
        longueur=100.0
    )
    
    A = clothoide_actuelle.A
    
    def clothoide_fresnel_simple(s, A, gis_debut):
        """Version simplifiée pour comparaison"""
        if s == 0:
            return 0, 0, gis_debut
        
        u = s * math.sqrt(math.pi / (2 * A * A))
        S_fresnel, C_fresnel = special.fresnel(u)
        
        x_local = A * math.sqrt(2 / math.pi) * C_fresnel
        y_local = A * math.sqrt(2 / math.pi) * S_fresnel
        
        theta_rad = s * s / (2 * A * A)
        gisement = (gis_debut + theta_rad * 200 / math.pi) % 400
        
        return x_local, y_local, gisement
    
    print(f"\nCOMPARAISON: A={A:.2f}, Gis_début=50.0g")
    print()
    print(f"{'Dist':<6} {'Méthode':<10} {'X':<12} {'Y':<12} {'Gisement':<12} {'Écart XY':<10}")
    print("-" * 75)
    
    distances_test = [25, 50, 75, 100]
    
    for s in distances_test:
        # Méthode actuelle (approximative)
        pt_actuel = clothoide_actuelle.point_at_distance(s)
        gis_actuel = clothoide_actuelle.gisement_at_distance(s)
        
        # Ajuster les coordonnées pour comparaison (origine locale)
        x_actuel = pt_actuel.x - 1000
        y_actuel = pt_actuel.y - 2000
        
        # Méthode Fresnel
        x_fresnel, y_fresnel, gis_fresnel = clothoide_fresnel_simple(s, A, 50.0)
        
        # Écart entre les méthodes
        ecart_xy = math.sqrt((x_actuel - x_fresnel)**2 + (y_actuel - y_fresnel)**2)
        
        print(f"{s:<6.0f} {'Actuelle':<10} {x_actuel:<12.3f} {y_actuel:<12.3f} {gis_actuel:<12.2f} {'-':<10}")
        print(f"{'':<6} {'Fresnel':<10} {x_fresnel:<12.3f} {y_fresnel:<12.3f} {gis_fresnel:<12.2f} {ecart_xy:<10.3f}")
        print()

def recommandations():
    """Recommandations pour l'amélioration"""
    print("\n" + "=" * 80)
    print("💡 RECOMMANDATIONS POUR L'AMÉLIORATION")
    print("=" * 80)
    
    print("\n🎯 AMÉLIORATION PRIORITAIRE:")
    print("-" * 50)
    print("1. ⚡ Remplacer l'approximation linéaire par les intégrales de Fresnel")
    print("2. 📐 Utiliser scipy.special.fresnel() pour les calculs")
    print("3. 🔄 Implémenter la rotation selon le gisement de début") 
    print("4. ✅ Valider avec des cas de test de référence")
    print("5. 📊 Ajouter des tests de précision")
    
    print("\n🔧 IMPLÉMENTATION SUGGÉRÉE:")
    print("-" * 50)
    print("""
class ClothoidePrecise(ElementAxe):
    def point_at_distance(self, distance):
        # Paramètre normalisé
        u = distance * sqrt(π / (2A²))
        
        # Intégrales de Fresnel
        S, C = scipy.special.fresnel(u)
        
        # Coordonnées locales
        x_local = A * sqrt(2/π) * C
        y_local = A * sqrt(2/π) * S
        
        # Rotation selon gisement début
        # ... transformation géométrique
        
        return Point(x_global, y_global, z)
""")
    
    print("\n📈 AVANTAGES DE L'AMÉLIORATION:")
    print("-" * 50)
    print("✅ Précision mathématique exacte")
    print("✅ Conforme aux standards topographiques")
    print("✅ Compatible avec logiciels professionnels")
    print("✅ Calculs corrects pour grandes déviations")
    print("✅ Validation possible avec références")
    
    print("\n⚠️ IMPACT SUR L'EXISTANT:")
    print("-" * 50)
    print("• Modification de la classe Clothoide")
    print("• Ajout dépendance scipy (déjà utilisée)")
    print("• Tests unitaires à adapter")
    print("• Résultats légèrement différents (plus précis)")
    
    print("\n🚀 PRIORITÉ:")
    print("-" * 50)
    print("HAUTE - La précision des clothoïdes est critique pour:")
    print("• Calculs d'implantation")
    print("• Conformité aux normes routières")
    print("• Interopérabilité avec autres logiciels")
    print("• Crédibilité professionnelle")

def main():
    """Fonction principale"""
    print("🔬 ANALYSE DES MÉTHODES DE CALCUL DES CLOTHOÏDES")
    
    # 1. Analyser la méthode actuelle
    analyse_methode_actuelle()
    
    # 2. Rappel théorique
    theorie_clothoides()
    
    # 3. Implémentation Fresnel
    try:
        implementation_fresnel()
        
        # 4. Comparaison
        comparaison_methodes()
        
    except ImportError:
        print("\n❌ Module scipy non disponible pour démonstration Fresnel")
        print("   pip install scipy pour voir la comparaison complète")
    
    # 5. Recommandations
    recommandations()
    
    print("\n" + "=" * 80)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 80)
    print("🎯 CONCLUSION: Les clothoïdes utilisent actuellement une approximation")
    print("   linéaire simplifiée. L'amélioration avec les intégrales de Fresnel")
    print("   est hautement recommandée pour un usage professionnel.")
    print("=" * 80)

if __name__ == "__main__":
    main()