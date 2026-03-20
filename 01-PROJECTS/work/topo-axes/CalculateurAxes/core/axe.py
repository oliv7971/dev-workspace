"""
Module axe - Gestion des axes en plan et profils en long
"""

from .elements import ElementAxe, AlignementDroit, Arc, Clothoide
from .geometrie import Point, Vecteur
from .projections import GestionnaireProjection, ModeProjection
from .calculs_perpendiculaire import CalculsPerpendiculaire, ModeCalcul
import math


class AxeEnPlan:
    """Axe en plan composé d'éléments géométriques"""
    
    def __init__(self, nom=""):
        self.nom = nom
        self.elements = []
        self.pm_debut = 0.0
        self.gestionnaire_projection = GestionnaireProjection()
        self.calculateur_perpendiculaire = None  # Sera initialisé avec le profil
        
    def configurer_projection(self, mode, **params):
        """Configure la gestion des projections"""
        self.gestionnaire_projection.configurer(mode, **params)
    
    def associer_profil_long(self, profil_long):
        """Associe un profil en long et initialise le calculateur perpendiculaire"""
        self.calculateur_perpendiculaire = CalculsPerpendiculaire(self, profil_long)
        return self.calculateur_perpendiculaire
    
    def ajouter_alignement(self, debut, fin):
        """Ajoute un alignement droit"""
        element = AlignementDroit(debut, fin)
        self.elements.append(element)
        return element
    
    def ajouter_arc(self, centre, rayon, angle_debut, angle_fin):
        """Ajoute un arc circulaire"""
        element = Arc(centre, rayon, angle_debut, angle_fin)
        self.elements.append(element)
        return element
    
    def ajouter_clothoide(self, point_debut, gisement_debut, rayon_debut, rayon_fin, longueur):
        """Ajoute une clothoïde"""
        element = Clothoide(point_debut, gisement_debut, rayon_debut, rayon_fin, longueur)
        self.elements.append(element)
        return element
    
    def longueur_totale(self):
        """Longueur totale de l'axe"""
        return sum(e.longueur() for e in self.elements)
    
    def point_at_pm(self, pm, deport=0, mode_deport='perpendiculaire'):
        """
        Calcule un point à un PM donné avec déport optionnel
        
        Args:
            pm: Point métrique
            deport: Déport latéral (+ = droite, - = gauche)
            mode_deport: 'perpendiculaire' ou 'vertical'
        """
        distance = pm - self.pm_debut
        
        # Recherche de l'élément contenant ce PM
        distance_cumulee = 0
        for element in self.elements:
            longueur_element = element.longueur()
            if distance_cumulee + longueur_element >= distance:
                # Le point est sur cet élément
                distance_element = distance - distance_cumulee
                pt = element.point_at_distance(distance_element)
                
                # Appliquer le déport si nécessaire
                if deport != 0:
                    if mode_deport == 'perpendiculaire':
                        # Déport perpendiculaire à l'axe
                        gisement = element.gisement_at_distance(distance_element)
                        gis_perp = (gisement + 100) % 400  # +100g = perpendiculaire droite
                        
                        # Vecteur unitaire perpendiculaire
                        v_perp = Vecteur.depuis_gisement(gis_perp, abs(deport))
                        
                        pt_avec_deport = Point(
                            pt.x + v_perp.dx * (1 if deport > 0 else -1),
                            pt.y + v_perp.dy * (1 if deport > 0 else -1),
                            pt.z
                        )
                        return pt_avec_deport
                    
                    elif mode_deport == 'vertical':
                        # Déport vertical (changement d'altitude)
                        return Point(pt.x, pt.y, pt.z + deport)
                    
                return pt
            distance_cumulee += longueur_element
            
        raise ValueError(f"PM {pm} hors limites de l'axe (longueur: {self.longueur_totale():.3f}m)")
    
    def projeter_point(self, point, mode='perpendiculaire'):
        """
        Projette un point sur l'axe, retourne (PM, déport)
        
        Args:
            point: Point à projeter
            mode: 'perpendiculaire' ou 'vertical'
        """
        meilleure_distance = float('inf')
        meilleur_pm = None
        meilleur_deport = None
        
        pm_cumule = self.pm_debut
        
        for element in self.elements:
            distance_element, deport = element.projeter_point(point)
            
            # Distance absolue au point projeté
            pt_proj = element.point_at_distance(distance_element)
            
            if mode == 'perpendiculaire':
                dist_abs = point.distance_2d(pt_proj)
            else:  # mode vertical
                dist_abs = abs(point.z - pt_proj.z)
            
            if dist_abs < meilleure_distance:
                meilleure_distance = dist_abs
                meilleur_pm = pm_cumule + distance_element
                
                if mode == 'vertical':
                    meilleur_deport = point.z - pt_proj.z  # Déport vertical
                else:
                    meilleur_deport = deport  # Déport horizontal
                
            pm_cumule += element.longueur()
            
        return meilleur_pm, meilleur_deport
    
    def point_at_pm_avec_mode(self, pm, deport=0, mode_calcul=ModeCalcul.HORIZONTAL_2D):
        """
        Calcule un point avec le nouveau système de modes de calcul
        
        Args:
            pm: Point métrique
            deport: Déport (interprétation selon le mode)
            mode_calcul: ModeCalcul (PERPENDICULAIRE_PROFIL, VERTICAL_ABSOLU, HORIZONTAL_2D)
        """
        if self.calculateur_perpendiculaire is None:
            # Mode de compatibilité
            return self.point_at_pm(pm, deport, 'perpendiculaire')
        
        if mode_calcul == ModeCalcul.PERPENDICULAIRE_PROFIL:
            return self.calculateur_perpendiculaire.point_avec_deport_perpendiculaire_profil(pm, deport)
        elif mode_calcul == ModeCalcul.VERTICAL_ABSOLU:
            return self.calculateur_perpendiculaire.point_avec_deport_vertical_absolu(pm, deport)
        else:  # HORIZONTAL_2D - mode classique
            return self.point_at_pm(pm, deport, 'perpendiculaire')
    
    def projeter_point_avec_mode(self, point, mode_calcul=ModeCalcul.HORIZONTAL_2D):
        """
        Projette un point avec le nouveau système de modes de calcul
        
        Args:
            point: Point à projeter
            mode_calcul: ModeCalcul
            
        Returns:
            (PM, déport) selon le mode choisi
        """
        if self.calculateur_perpendiculaire is None:
            # Mode de compatibilité
            return self.projeter_point(point, 'perpendiculaire')
        
        # Trouver la meilleure projection horizontale d'abord
        pm_proj, _ = self.projeter_point(point, 'perpendiculaire')
        
        # Calculer selon le mode demandé
        if mode_calcul == ModeCalcul.PERPENDICULAIRE_PROFIL:
            gisement_axe = self.calculateur_perpendiculaire._calculer_gisement_at_pm(pm_proj)
            deport, _ = self.calculateur_perpendiculaire.calculer_deport_perpendiculaire_profil(
                point, pm_proj, gisement_axe
            )
            return pm_proj, deport
        elif mode_calcul == ModeCalcul.VERTICAL_ABSOLU:
            deport, _ = self.calculateur_perpendiculaire.calculer_deport_vertical_absolu(point, pm_proj)
            return pm_proj, deport
        else:  # HORIZONTAL_2D
            return self.projeter_point(point, 'perpendiculaire')
    
    def comparaison_modes_projection(self, point):
        """
        Compare les différents modes de projection pour un même point
        
        Returns:
            Dictionnaire avec résultats de chaque mode + analyse
        """
        if self.calculateur_perpendiculaire is None:
            return {"erreur": "Profil en long non associé - utiliser associer_profil_long()"}
        
        # Projection horizontale pour obtenir le PM
        pm_proj, _ = self.projeter_point(point, 'perpendiculaire')
        
        return self.calculateur_perpendiculaire.comparaison_modes_calcul(point, pm_proj)
    
    def tabuler(self, pm_debut, pm_fin, intervalle):
        """
        Génère une tabulation de l'axe
        
        Returns:
            Liste de dictionnaires avec PM, X, Y, Z, Gisement
        """
        resultats = []
        pm = pm_debut
        
        while pm <= pm_fin:
            try:
                point = self.point_at_pm(pm)
                
                # Trouver l'élément pour le gisement
                distance = pm - self.pm_debut
                distance_cumulee = 0
                gisement = 0.0
                
                for element in self.elements:
                    if distance_cumulee + element.longueur() >= distance:
                        distance_element = distance - distance_cumulee
                        gisement = element.gisement_at_distance(distance_element)
                        break
                    distance_cumulee += element.longueur()
                
                resultats.append({
                    'PM': pm,
                    'X': point.x,
                    'Y': point.y,
                    'Z': point.z,
                    'Gisement': gisement
                })
                
            except ValueError:
                # PM hors limites
                break
                
            pm += intervalle
            
        return resultats
    
    def creer_depuis_sommets(self, sommets, rayons=None):
        """
        Crée l'axe depuis une liste de sommets
        
        Args:
            sommets: Liste de Points avec PM optionnel
            rayons: Liste de rayons aux sommets (None pour alignement droit)
        """
        if len(sommets) < 2:
            raise ValueError("Il faut au moins 2 sommets")
        
        self.elements.clear()
        
        # Calibrer les altérations si des PM sont fournis
        sommets_avec_pm = [s for s in sommets if s.pm is not None]
        if len(sommets_avec_pm) >= 2:
            self.gestionnaire_projection.calibrer_alteration(sommets_avec_pm)
        
        for i in range(len(sommets) - 1):
            s1, s2 = sommets[i], sommets[i + 1]
            
            if rayons and i < len(rayons) and rayons[i] is not None:
                # Arc circulaire - implémentation simplifiée
                # En réalité, il faudrait calculer le centre depuis le rayon et les tangentes
                rayon = rayons[i]
                v1 = Vecteur.entre_points(s1, s2)
                gis_debut = v1.gisement()
                
                # Pour l'instant, créer un arc simple (à améliorer)
                longueur_arc = v1.norme()  # Approximation
                deviation = longueur_arc / rayon * 200 / math.pi  # En grades
                
                # Centre approximatif
                centre_x = (s1.x + s2.x) / 2
                centre_y = (s1.y + s2.y) / 2
                centre = Point(centre_x, centre_y, (s1.z + s2.z) / 2)
                
                self.ajouter_arc(centre, rayon, gis_debut, gis_debut + deviation)
            else:
                # Alignement droit
                self.ajouter_alignement(s1, s2)
    
    def creer_depuis_elements(self, point_depart, elements_def):
        """
        Crée l'axe depuis une définition par éléments
        
        Args:
            point_depart: Point de départ
            elements_def: Liste de définitions d'éléments
                Format: [{'type': 'AD', 'gisement': 50.0, 'longueur': 100}, ...]
        """
        self.elements.clear()
        
        point_courant = point_depart
        gisement_courant = 0.0
        
        for elem_def in elements_def:
            type_elem = elem_def['type']
            
            if type_elem == 'AD':  # Alignement droit
                gisement_courant = elem_def['gisement']
                longueur = elem_def['longueur']
                
                # Point d'arrivée
                v = Vecteur.depuis_gisement(gisement_courant, longueur)
                point_fin = Point(
                    point_courant.x + v.dx,
                    point_courant.y + v.dy,
                    point_courant.z
                )
                
                self.ajouter_alignement(point_courant, point_fin)
                point_courant = point_fin
                
            elif type_elem == 'C':  # Arc circulaire
                rayon = elem_def['rayon']
                
                if 'deviation' in elem_def:
                    deviation = elem_def['deviation']
                    longueur_arc = abs(rayon) * deviation * math.pi / 200
                elif 'longueur' in elem_def:
                    longueur_arc = elem_def['longueur']
                    deviation = longueur_arc / abs(rayon) * 200 / math.pi
                else:
                    raise ValueError("Arc: spécifier 'deviation' ou 'longueur'")
                
                # Calcul du centre (perpendiculaire au gisement courant)
                gis_centre = (gisement_courant + (100 if rayon > 0 else -100)) % 400
                v_centre = Vecteur.depuis_gisement(gis_centre, abs(rayon))
                centre = Point(
                    point_courant.x + v_centre.dx,
                    point_courant.y + v_centre.dy,
                    point_courant.z
                )
                
                angle_fin = (gisement_courant + deviation * (1 if rayon > 0 else -1)) % 400
                
                self.ajouter_arc(centre, rayon, gisement_courant, angle_fin)
                
                # Nouveau point courant et gisement
                gisement_courant = angle_fin
                v_fin = Vecteur.depuis_gisement(gisement_courant, abs(rayon))
                point_courant = Point(
                    centre.x + v_fin.dx,
                    centre.y + v_fin.dy,
                    centre.z
                )
                
            elif type_elem == 'CL':  # Clothoïde
                rayon_debut = elem_def.get('rayon_debut', float('inf'))
                rayon_fin = elem_def.get('rayon_fin', float('inf'))
                longueur = elem_def['longueur']
                
                self.ajouter_clothoide(
                    point_courant, gisement_courant,
                    rayon_debut, rayon_fin, longueur
                )
                
                # Mise à jour approximative du point et gisement courants
                # (à améliorer avec les vraies formules de clothoïde)
                v = Vecteur.depuis_gisement(gisement_courant, longueur)
                point_courant = Point(
                    point_courant.x + v.dx,
                    point_courant.y + v.dy,
                    point_courant.z
                )
                
                # Variation de gisement approximative
                if rayon_fin != float('inf'):
                    variation = longueur / rayon_fin * 200 / math.pi / 2  # Approximation
                    gisement_courant = (gisement_courant + variation) % 400


class ProfilEnLong:
    """Profil en long d'un axe"""
    
    def __init__(self, nom=""):
        self.nom = nom
        self.points = []  # Liste de (PM, Z)
        self.pentes = []  # Liste de (PM_début, PM_fin, pente_%)
        self.raccords = []  # Liste de (PM_centre, rayon, longueur)
    
    def ajouter_point(self, pm, z):
        """Ajoute un point du profil"""
        self.points.append((pm, z))
        self.points.sort(key=lambda x: x[0])  # Trier par PM
    
    def ajouter_pente(self, pm_debut, pm_fin, pente_pourcent):
        """Ajoute une pente entre deux PM"""
        self.pentes.append((pm_debut, pm_fin, pente_pourcent))
    
    def ajouter_raccord_parabolique(self, pm_centre, rayon, longueur):
        """Ajoute un raccord parabolique"""
        self.raccords.append((pm_centre, rayon, longueur))
    
    def altitude_at_pm(self, pm):
        """Calcule l'altitude à un PM donné"""
        # Recherche par interpolation linéaire entre les points
        if not self.points:
            return 0.0
        
        # Si PM avant le premier point
        if pm <= self.points[0][0]:
            return self.points[0][1]
        
        # Si PM après le dernier point
        if pm >= self.points[-1][0]:
            return self.points[-1][1]
        
        # Interpolation entre deux points
        for i in range(len(self.points) - 1):
            pm1, z1 = self.points[i]
            pm2, z2 = self.points[i + 1]
            
            if pm1 <= pm <= pm2:
                if pm2 == pm1:
                    return z1
                ratio = (pm - pm1) / (pm2 - pm1)
                return z1 + ratio * (z2 - z1)
        
        return 0.0
    
    def pente_at_pm(self, pm):
        """Calcule la pente à un PM donné"""
        for pm_deb, pm_fin, pente in self.pentes:
            if pm_deb <= pm <= pm_fin:
                return pente
        
        # Calcul par différences finies si pas de pente définie
        delta_pm = 1.0  # 1 mètre
        z1 = self.altitude_at_pm(pm - delta_pm/2)
        z2 = self.altitude_at_pm(pm + delta_pm/2)
        return (z2 - z1) / delta_pm * 100  # En %