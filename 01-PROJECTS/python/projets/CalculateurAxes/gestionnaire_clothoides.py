#!/usr/bin/env python3
"""
Module d'intégration des clothoïdes précises dans le système existant
Permet de choisir entre méthode approximée et précise
"""
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.geometrie import Point
from core.elements import Clothoide as ClothoideApproximee

try:
    from clothoide_precise import ClothoidePrecise
    SCIPY_DISPONIBLE = True
except ImportError:
    SCIPY_DISPONIBLE = False

class GestionnaireClothoides:
    """
    Gestionnaire intelligent pour choisir la meilleure méthode de clothoïde
    """
    
    METHODE_APPROXIMEE = "approximee"
    METHODE_PRECISE = "precise"
    METHODE_AUTO = "auto"
    
    def __init__(self, methode_par_defaut=METHODE_AUTO):
        """
        Initialise le gestionnaire
        
        Args:
            methode_par_defaut: "approximee", "precise", ou "auto"
        """
        self.methode_par_defaut = methode_par_defaut
        self.seuil_precision_m = 1.0  # Seuil pour basculer en mode précis
        
    def creer_clothoide(self, point_debut, gisement_debut, rayon_debut, rayon_fin, 
                        longueur, methode=None):
        """
        Crée une clothoïde en choisissant automatiquement la meilleure méthode
        
        Args:
            point_debut: Point de début
            gisement_debut: Gisement initial en grades
            rayon_debut: Rayon initial
            rayon_fin: Rayon final
            longueur: Longueur de la clothoïde
            methode: Force une méthode spécifique (optionnel)
            
        Returns:
            ElementAxe: Instance de clothoïde (approximée ou précise)
        """
        methode_choisie = methode or self.methode_par_defaut
        
        # Choix automatique basé sur les critères
        if methode_choisie == self.METHODE_AUTO:
            methode_choisie = self._determiner_methode_optimale(
                rayon_debut, rayon_fin, longueur
            )
        
        # Création selon la méthode choisie
        if methode_choisie == self.METHODE_PRECISE and SCIPY_DISPONIBLE:
            try:
                clothoide = ClothoidePrecise(
                    point_debut, gisement_debut, rayon_debut, rayon_fin, longueur
                )
                clothoide._methode_utilisee = "precise"
                return clothoide
            except Exception as e:
                print(f"⚠️  Échec clothoïde précise, basculement vers approximée: {e}")
                
        # Fallback vers méthode approximée
        clothoide = ClothoideApproximee(
            point_debut, gisement_debut, rayon_debut, rayon_fin, longueur
        )
        clothoide._methode_utilisee = "approximee"
        return clothoide
    
    def _determiner_methode_optimale(self, rayon_debut, rayon_fin, longueur):
        """
        Détermine la méthode optimale basée sur les paramètres
        
        Args:
            rayon_debut, rayon_fin: Rayons de début et fin
            longueur: Longueur de la clothoïde
            
        Returns:
            str: "precise" ou "approximee"
        """
        if not SCIPY_DISPONIBLE:
            return self.METHODE_APPROXIMEE
        
        # Critères pour utiliser la méthode précise
        criteres_precision = [
            longueur > 50,  # Clothoïdes longues
            abs(rayon_fin) < 100 if abs(rayon_fin) != float('inf') else False,  # Rayons serrés
            abs(rayon_debut) < 100 if abs(rayon_debut) != float('inf') else False,
            longueur > 2 * min(abs(rayon_debut), abs(rayon_fin)) if abs(rayon_fin) != float('inf') else longueur > 100
        ]
        
        # Si au moins 2 critères sont remplis, utiliser la méthode précise
        if sum(criteres_precision) >= 2:
            return self.METHODE_PRECISE
        
        return self.METHODE_APPROXIMEE
    
    def comparer_methodes(self, point_debut, gisement_debut, rayon_debut, rayon_fin, longueur):
        """
        Compare les deux méthodes sur les mêmes paramètres
        
        Returns:
            dict: Résultats de comparaison
        """
        if not SCIPY_DISPONIBLE:
            return {"erreur": "scipy non disponible pour la comparaison"}
        
        try:
            # Création des deux clothoïdes
            clothoide_approx = ClothoideApproximee(
                point_debut, gisement_debut, rayon_debut, rayon_fin, longueur
            )
            clothoide_precise = ClothoidePrecise(
                point_debut, gisement_debut, rayon_debut, rayon_fin, longueur
            )
            
            # Comparaison aux points clés
            distances_test = [longueur * 0.25, longueur * 0.5, longueur * 0.75, longueur]
            ecarts = []
            
            for dist in distances_test:
                pt_approx = clothoide_approx.point_at_distance(dist)
                pt_precise = clothoide_precise.point_at_distance(dist)
                
                ecart = math.sqrt(
                    (pt_precise.x - pt_approx.x)**2 + 
                    (pt_precise.y - pt_approx.y)**2
                )
                ecarts.append(ecart)
            
            return {
                "ecart_max": max(ecarts),
                "ecart_moyen": sum(ecarts) / len(ecarts),
                "ecarts_detailles": dict(zip(distances_test, ecarts)),
                "recommandation": "precise" if max(ecarts) > self.seuil_precision_m else "approximee"
            }
            
        except Exception as e:
            return {"erreur": str(e)}
    
    def rapport_capacites(self):
        """
        Génère un rapport sur les capacités disponibles
        
        Returns:
            dict: État des capacités
        """
        return {
            "scipy_disponible": SCIPY_DISPONIBLE,
            "methode_par_defaut": self.methode_par_defaut,
            "seuil_precision": f"{self.seuil_precision_m}m",
            "methodes_disponibles": {
                "approximee": "Toujours disponible (méthode de base)",
                "precise": "Disponible avec scipy" if SCIPY_DISPONIBLE else "Nécessite scipy"
            }
        }

def demo_gestionnaire():
    """
    Démonstration du gestionnaire de clothoïdes
    """
    print("=" * 80)
    print("🎛️  DÉMONSTRATION DU GESTIONNAIRE DE CLOTHOÏDES")
    print("=" * 80)
    
    gestionnaire = GestionnaireClothoides()
    
    # Rapport des capacités
    print("\n📋 CAPACITÉS DISPONIBLES:")
    rapport = gestionnaire.rapport_capacites()
    for cle, valeur in rapport.items():
        if isinstance(valeur, dict):
            print(f"  {cle}:")
            for sous_cle, sous_valeur in valeur.items():
                print(f"    {sous_cle}: {sous_valeur}")
        else:
            print(f"  {cle}: {valeur}")
    
    # Test de différents cas
    cas_tests = [
        {
            "nom": "Clothoïde courte et rayon large",
            "params": (Point(0, 0, 0), 0.0, float('inf'), 500.0, 30.0)
        },
        {
            "nom": "Clothoïde longue et rayon serré", 
            "params": (Point(100, 200, 10), 25.0, float('inf'), 80.0, 120.0)
        },
        {
            "nom": "Transition courbe-courbe",
            "params": (Point(500, 500, 50), 100.0, 300.0, 150.0, 80.0)
        }
    ]
    
    for cas in cas_tests:
        print(f"\n🧪 TEST: {cas['nom']}")
        print("-" * 60)
        
        # Création automatique
        clothoide_auto = gestionnaire.creer_clothoide(*cas['params'])
        methode_auto = getattr(clothoide_auto, '_methode_utilisee', 'inconnue')
        print(f"  Méthode automatique: {methode_auto}")
        
        # Test du point à mi-parcours
        longueur = cas['params'][4]
        try:
            pt_milieu = clothoide_auto.point_at_distance(longueur / 2)
            print(f"  Point milieu: ({pt_milieu.x:.3f}, {pt_milieu.y:.3f})")
        except Exception as e:
            print(f"  Erreur calcul point: {e}")
        
        # Comparaison si possible
        if SCIPY_DISPONIBLE:
            comparaison = gestionnaire.comparer_methodes(*cas['params'])
            if 'erreur' not in comparaison:
                print(f"  Écart max: {comparaison['ecart_max']:.3f}m")
                print(f"  Recommandation: {comparaison['recommandation']}")
            else:
                print(f"  Erreur comparaison: {comparaison['erreur']}")
    
    print(f"\n💡 CONCLUSION:")
    print(f"  Le gestionnaire choisit automatiquement la meilleure méthode")
    print(f"  selon les paramètres et la précision requise.")
    if SCIPY_DISPONIBLE:
        print(f"  ✅ Clothoïdes précises disponibles avec scipy")
    else:
        print(f"  ⚠️  Clothoïdes précises indisponibles (pip install scipy)")

if __name__ == "__main__":
    demo_gestionnaire()