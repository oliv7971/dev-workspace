"""
Éléments de profil en long (vertical profile)
Gère les segments verticaux : droites, arcs circulaires et paraboles
"""
from math import sqrt
from typing import Tuple, Optional, List


class ProfileElement:
    """Interface basique pour un élément de profil en long."""
    
    def length(self) -> float:
        """Retourne la longueur horizontale de l'élément."""
        raise NotImplementedError

    def elevation_at(self, s: float) -> float:
        """
        Retourne l'altitude à la distance horizontale s depuis le début de l'élément.
        s : distance horizontale depuis le début (0 <= s <= length)
        """
        raise NotImplementedError
    
    def slope_at(self, s: float) -> float:
        """
        Retourne la pente (en %) à la distance horizontale s.
        """
        raise NotImplementedError


class LineProfile(ProfileElement):
    """Segment de profil en long droit (pente constante)."""
    
    def __init__(self, start_station: float, start_elevation: float, 
                 end_station: float, end_elevation: float):
        """
        start_station : abscisse de début (m)
        start_elevation : altitude de début (m)
        end_station : abscisse de fin (m)
        end_elevation : altitude de fin (m)
        """
        self.start_station = start_station
        self.start_elevation = start_elevation
        self.end_station = end_station
        self.end_elevation = end_elevation
        self._length = end_station - start_station
        
        if self._length > 0:
            self._slope = (end_elevation - start_elevation) / self._length
        else:
            self._slope = 0.0
    
    def length(self) -> float:
        return self._length
    
    def elevation_at(self, s: float) -> float:
        if self._length == 0:
            return self.start_elevation
        s = max(0.0, min(self._length, s))
        return self.start_elevation + self._slope * s
    
    def slope_at(self, s: float) -> float:
        """Retourne la pente en fraction (pas en %)"""
        return self._slope
    
    def slope_percent(self) -> float:
        """Retourne la pente en %"""
        return self._slope * 100.0


class CircularVerticalCurve(ProfileElement):
    """Arc de cercle vertical (raccordement parabolique simplifié en arc)."""
    
    def __init__(self, start_station: float, start_elevation: float,
                 length: float, slope_in: float, slope_out: float):
        """
        start_station : abscisse de début (m)
        start_elevation : altitude de début (m)
        length : longueur horizontale de l'arc (m)
        slope_in : pente entrante (fraction, ex: 0.05 pour 5%)
        slope_out : pente sortante (fraction)
        """
        self.start_station = start_station
        self.start_elevation = start_elevation
        self._length = length
        self.slope_in = slope_in
        self.slope_out = slope_out
        
        # Calcul du rayon à partir de la variation de pente
        delta_slope = slope_out - slope_in
        if abs(delta_slope) > 1e-9 and length > 0:
            # R = L / Δi où Δi = variation de pente
            self.radius = abs(length / delta_slope)
            self.is_convex = delta_slope < 0  # Convexe si pente diminue
        else:
            self.radius = float('inf')
            self.is_convex = False
    
    def length(self) -> float:
        return self._length
    
    def elevation_at(self, s: float) -> float:
        if self._length == 0:
            return self.start_elevation
        
        s = max(0.0, min(self._length, s))
        
        # Approximation parabolique (plus simple et plus utilisée en pratique)
        # z = z0 + slope_in * s + (slope_out - slope_in) * s² / (2*L)
        delta_slope = self.slope_out - self.slope_in
        z = self.start_elevation + self.slope_in * s + (delta_slope * s * s) / (2.0 * self._length)
        return z
    
    def slope_at(self, s: float) -> float:
        """Retourne la pente en fraction à la position s."""
        if self._length == 0:
            return self.slope_in
        
        s = max(0.0, min(self._length, s))
        
        # Dérivée de l'équation parabolique
        # dz/ds = slope_in + (slope_out - slope_in) * s / L
        delta_slope = self.slope_out - self.slope_in
        slope = self.slope_in + (delta_slope * s) / self._length
        return slope
    
    def slope_percent_at(self, s: float) -> float:
        """Retourne la pente en % à la position s."""
        return self.slope_at(s) * 100.0


class ParabolicVerticalCurve(ProfileElement):
    """Parabole verticale (raccordement parabolique du 2e degré)."""
    
    def __init__(self, start_station: float, start_elevation: float,
                 length: float, slope_in: float, slope_out: float):
        """
        start_station : abscisse de début (m)
        start_elevation : altitude de début (m)
        length : longueur horizontale de la parabole (m)
        slope_in : pente entrante (fraction, ex: 0.05 pour 5%)
        slope_out : pente sortante (fraction)
        
        Note: Identique à CircularVerticalCurve dans l'implémentation courante
        car les paraboles du 2e degré sont l'approximation standard des raccordements verticaux.
        """
        self.start_station = start_station
        self.start_elevation = start_elevation
        self._length = length
        self.slope_in = slope_in
        self.slope_out = slope_out
        
        # Coefficient de la parabole: z = a*s² + b*s + c
        # Conditions: z(0) = start_elevation, z'(0) = slope_in, z'(L) = slope_out
        self.a = (slope_out - slope_in) / (2.0 * length) if length > 0 else 0.0
        self.b = slope_in
        self.c = start_elevation
    
    def length(self) -> float:
        return self._length
    
    def elevation_at(self, s: float) -> float:
        if self._length == 0:
            return self.start_elevation
        
        s = max(0.0, min(self._length, s))
        
        # Équation parabolique: z = a*s² + b*s + c
        z = self.a * s * s + self.b * s + self.c
        return z
    
    def slope_at(self, s: float) -> float:
        """Retourne la pente en fraction à la position s."""
        if self._length == 0:
            return self.slope_in
        
        s = max(0.0, min(self._length, s))
        
        # Dérivée: dz/ds = 2*a*s + b
        slope = 2.0 * self.a * s + self.b
        return slope
    
    def slope_percent_at(self, s: float) -> float:
        """Retourne la pente en % à la position s."""
        return self.slope_at(s) * 100.0


class VerticalProfile:
    """Profil en long complet, composé de plusieurs éléments."""
    
    def __init__(self):
        self.elements: List[ProfileElement] = []
        self._cum_stations: List[float] = []
    
    def add_element(self, element: ProfileElement):
        """Ajoute un élément au profil."""
        self.elements.append(element)
        self._rebuild_stations()
    
    def _rebuild_stations(self):
        """Recalcule les stations cumulées."""
        self._cum_stations = [0.0]
        s = 0.0
        for el in self.elements:
            s += el.length()
            self._cum_stations.append(s)
    
    def total_length(self) -> float:
        """Retourne la longueur totale du profil."""
        if not self._cum_stations:
            self._rebuild_stations()
        return self._cum_stations[-1] if self._cum_stations else 0.0
    
    def _find_element_by_station(self, station: float) -> Tuple[int, float]:
        """Retourne (index_element, local_s) pour une station globale."""
        if not self._cum_stations:
            self._rebuild_stations()
        
        L = self.total_length()
        if L == 0:
            return 0, 0.0
        
        s = max(0.0, min(L, station))
        
        # Recherche linéaire (OK pour petit nombre d'éléments)
        for i in range(len(self.elements)):
            start = self._cum_stations[i]
            end = self._cum_stations[i + 1]
            if s <= end:
                return i, (s - start)
        
        # Fallback au dernier élément
        return len(self.elements) - 1, self.elements[-1].length()
    
    def elevation_at(self, station: float) -> float:
        """Retourne l'altitude à la station donnée."""
        if not self.elements:
            raise ValueError("VerticalProfile has no elements")
        
        idx, local_s = self._find_element_by_station(station)
        return self.elements[idx].elevation_at(local_s)
    
    def slope_at(self, station: float) -> float:
        """Retourne la pente (fraction) à la station donnée."""
        if not self.elements:
            raise ValueError("VerticalProfile has no elements")
        
        idx, local_s = self._find_element_by_station(station)
        return self.elements[idx].slope_at(local_s)
    
    def slope_percent_at(self, station: float) -> float:
        """Retourne la pente en % à la station donnée."""
        return self.slope_at(station) * 100.0
    
    def get_profile_points(self, step: float = 10.0) -> List[Tuple[float, float]]:
        """
        Retourne une liste de points (station, elevation) pour tracer le profil.
        step : pas d'échantillonnage (m)
        """
        points = []
        L = self.total_length()
        
        if L == 0:
            return points
        
        station = 0.0
        while station <= L:
            elev = self.elevation_at(station)
            points.append((station, elev))
            station += step
        
        # Ajouter le dernier point si pas déjà inclus
        if points[-1][0] < L:
            points.append((L, self.elevation_at(L)))
        
        return points
