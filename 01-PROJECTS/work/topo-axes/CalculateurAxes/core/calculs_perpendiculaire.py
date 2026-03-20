"""
Module calculs_perpendiculaire - Distinction entre calculs perpendiculaires au profil et verticaux
"""

import math
from .geometrie import Point, Vecteur


class ModeCalcul:
    """Enumération des modes de calcul"""
    PERPENDICULAIRE_PROFIL = "perpendiculaire_profil"  # Perpendiculaire au profil en long (pente incluse)
    VERTICAL_ABSOLU = "vertical_absolu"                # Selon la verticale (gravité/plomb)
    HORIZONTAL_2D = "horizontal_2d"                    # Projection horizontale simple (ancien mode)


class CalculsPerpendiculaire:
    """
    Gestionnaire des calculs perpendiculaires au profil vs verticaux absolus
    
    DISTINCTION FONDAMENTALE :
    - Perpendiculaire au profil : calcul dans le plan perpendiculaire au profil en long
      (tient compte de la pente, comme un niveau sur chantier)
    - Vertical absolu : calcul selon la verticale de pesanteur 
      (indépendant de la pente, comme un fil à plomb)
    """
    
    def __init__(self, axe_plan=None, profil_long=None):
        self.axe_plan = axe_plan
        self.profil_long = profil_long
    
    def calculer_deport_perpendiculaire_profil(self, point, pm_axe, gisement_axe):
        """
        Calcule le déport perpendiculaire au profil en long
        
        Args:
            point: Point à projeter
            pm_axe: PM du point de projection sur l'axe
            gisement_axe: Gisement de l'axe au PM
            
        Returns:
            (deport_perpendiculaire, distance_perpendiculaire)
        """
        if self.profil_long is None:
            # Sans profil, retombe sur calcul horizontal
            return self._calcul_horizontal_simple(point, pm_axe, gisement_axe)
        
        # Point de référence sur l'axe
        pt_axe = self.axe_plan.point_at_pm(pm_axe)
        
        # Pente du profil en long au PM
        pente_percent = self.profil_long.pente_at_pm(pm_axe)
        pente_rad = math.atan(pente_percent / 100.0)  # Conversion pente% -> radians
        
        # Calcul dans le plan perpendiculaire au profil
        # 1. Projection horizontale
        v_horizontal = Vecteur.entre_points(pt_axe, point)
        gis_perp = (gisement_axe + 100) % 400  # Perpendiculaire horizontale
        v_perp_horizontal = Vecteur.depuis_gisement(gis_perp, 1.0)
        
        deport_horizontal = v_horizontal.produit_scalaire(v_perp_horizontal)
        
        # 2. Composante verticale
        delta_z = point.z - pt_axe.z
        
        # 3. Calcul perpendiculaire au profil (dans le plan vertical contenant la pente)
        # Distance selon la pente
        v_axe_direction = Vecteur.depuis_gisement(gisement_axe, 1.0)
        distance_axe = v_horizontal.produit_scalaire(v_axe_direction)
        
        # Altitude théorique sur le profil à cette distance
        z_profil_theorique = pt_axe.z + distance_axe * math.tan(pente_rad)
        
        # Déport perpendiculaire au profil (tient compte de la pente)
        delta_z_corrige = point.z - z_profil_theorique
        deport_perpendiculaire = math.sqrt(deport_horizontal**2 + (delta_z_corrige * math.cos(pente_rad))**2)
        
        # Signe du déport (droite/gauche)
        if deport_horizontal < 0:
            deport_perpendiculaire = -deport_perpendiculaire
        
        # Distance perpendiculaire réelle (dans l'espace)
        distance_perpendiculaire = math.sqrt(deport_horizontal**2 + delta_z_corrige**2)
        
        return deport_perpendiculaire, distance_perpendiculaire
    
    def calculer_deport_vertical_absolu(self, point, pm_axe):
        """
        Calcule le déport vertical absolu (selon la verticale de pesanteur)
        
        Args:
            point: Point à projeter
            pm_axe: PM du point de projection sur l'axe
            
        Returns:
            (deport_vertical, altitude_axe)
        """
        # Point de référence sur l'axe
        pt_axe = self.axe_plan.point_at_pm(pm_axe)
        
        # Altitude de référence sur l'axe
        if self.profil_long is not None:
            altitude_axe = self.profil_long.altitude_at_pm(pm_axe)
        else:
            altitude_axe = pt_axe.z
        
        # Déport vertical absolu (différence d'altitude selon la verticale)
        deport_vertical = point.z - altitude_axe
        
        return deport_vertical, altitude_axe
    
    def point_avec_deport_perpendiculaire_profil(self, pm, deport_perpendiculaire):
        """
        Calcule un point avec déport perpendiculaire au profil
        
        Args:
            pm: Point métrique sur l'axe
            deport_perpendiculaire: Déport perpendiculaire au profil (+ = droite)
            
        Returns:
            Point avec déport appliqué
        """
        if self.axe_plan is None:
            raise ValueError("Axe en plan non défini")
        
        # Point de base sur l'axe
        pt_axe = self.axe_plan.point_at_pm(pm)
        
        if deport_perpendiculaire == 0:
            return pt_axe
        
        # Gisement de l'axe au PM
        gisement_axe = self._calculer_gisement_at_pm(pm)
        
        if self.profil_long is None:
            # Sans profil, calcul horizontal simple
            gis_perp = (gisement_axe + 100) % 400
            v_perp = Vecteur.depuis_gisement(gis_perp, abs(deport_perpendiculaire))
            signe = 1 if deport_perpendiculaire > 0 else -1
            
            return Point(
                pt_axe.x + v_perp.dx * signe,
                pt_axe.y + v_perp.dy * signe,
                pt_axe.z
            )
        
        # Avec profil : tenir compte de la pente
        pente_percent = self.profil_long.pente_at_pm(pm)
        pente_rad = math.atan(pente_percent / 100.0)
        
        # Direction perpendiculaire horizontale
        gis_perp = (gisement_axe + 100) % 400
        v_perp_h = Vecteur.depuis_gisement(gis_perp, 1.0)
        signe = 1 if deport_perpendiculaire > 0 else -1
        
        # Déport horizontal
        deport_h = abs(deport_perpendiculaire) * math.cos(pente_rad)
        
        # Correction d'altitude due à la pente (déport perpendiculaire au profil)
        correction_z = abs(deport_perpendiculaire) * math.sin(pente_rad)
        
        return Point(
            pt_axe.x + v_perp_h.dx * deport_h * signe,
            pt_axe.y + v_perp_h.dy * deport_h * signe,
            pt_axe.z + correction_z  # Altitude corrigée selon la pente
        )
    
    def point_avec_deport_vertical_absolu(self, pm, deport_vertical):
        """
        Calcule un point avec déport vertical absolu
        
        Args:
            pm: Point métrique sur l'axe
            deport_vertical: Déport vertical absolu (+ = vers le haut)
            
        Returns:
            Point avec déport vertical appliqué
        """
        if self.axe_plan is None:
            raise ValueError("Axe en plan non défini")
        
        # Point de base sur l'axe
        pt_axe = self.axe_plan.point_at_pm(pm)
        
        # Altitude de référence
        if self.profil_long is not None:
            altitude_reference = self.profil_long.altitude_at_pm(pm)
        else:
            altitude_reference = pt_axe.z
        
        return Point(
            pt_axe.x,
            pt_axe.y,
            altitude_reference + deport_vertical  # Déport vertical pur
        )
    
    def _calcul_horizontal_simple(self, point, pm_axe, gisement_axe):
        """Calcul horizontal simple (mode de compatibilité)"""
        pt_axe = self.axe_plan.point_at_pm(pm_axe)
        
        v_horizontal = Vecteur.entre_points(pt_axe, point)
        gis_perp = (gisement_axe + 100) % 400
        v_perp = Vecteur.depuis_gisement(gis_perp, 1.0)
        
        deport = v_horizontal.produit_scalaire(v_perp)
        distance = v_horizontal.norme()
        
        return deport, distance
    
    def _calculer_gisement_at_pm(self, pm):
        """Calcule le gisement de l'axe à un PM donné"""
        # Méthode simplifiée - à améliorer avec une méthode dédiée dans AxeEnPlan
        distance = pm - self.axe_plan.pm_debut
        distance_cumulee = 0
        
        for element in self.axe_plan.elements:
            longueur_element = element.longueur()
            if distance_cumulee + longueur_element >= distance:
                distance_element = distance - distance_cumulee
                return element.gisement_at_distance(distance_element)
            distance_cumulee += longueur_element
        
        # Par défaut, gisement du dernier élément
        if self.axe_plan.elements:
            return self.axe_plan.elements[-1].gisement_at_distance(
                self.axe_plan.elements[-1].longueur()
            )
        
        return 0.0  # Gisement par défaut
    
    def comparaison_modes_calcul(self, point, pm_axe):
        """
        Compare les différents modes de calcul pour un même point
        
        Returns:
            Dictionnaire avec les résultats de chaque mode
        """
        gisement_axe = self._calculer_gisement_at_pm(pm_axe)
        
        # Mode perpendiculaire au profil
        deport_perp, dist_perp = self.calculer_deport_perpendiculaire_profil(
            point, pm_axe, gisement_axe
        )
        
        # Mode vertical absolu
        deport_vert, alt_axe = self.calculer_deport_vertical_absolu(point, pm_axe)
        
        # Mode horizontal simple (ancien)
        deport_horiz, dist_horiz = self._calcul_horizontal_simple(
            point, pm_axe, gisement_axe
        )
        
        return {
            ModeCalcul.PERPENDICULAIRE_PROFIL: {
                'deport': deport_perp,
                'distance': dist_perp,
                'description': 'Perpendiculaire au profil en long (pente incluse)'
            },
            ModeCalcul.VERTICAL_ABSOLU: {
                'deport': deport_vert,
                'altitude_axe': alt_axe,
                'description': 'Vertical absolu (selon la pesanteur)'
            },
            ModeCalcul.HORIZONTAL_2D: {
                'deport': deport_horiz,
                'distance': dist_horiz,
                'description': 'Projection horizontale simple (ancien mode)'
            }
        }