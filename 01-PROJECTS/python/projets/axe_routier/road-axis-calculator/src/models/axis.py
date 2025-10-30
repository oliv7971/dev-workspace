from typing import List, Dict, Tuple, Optional
from .point import Point
from .elements import AxisElement, LineElement, CircularArcElement, ClothoidElement


class Axis:
    def __init__(self):
        self.elements: List[AxisElement] = []
        # optional cached cumulative stations
        self._cum_stations: List[float] = []

    def add_element(self, element: AxisElement):
        self.elements.append(element)
        self._rebuild_stations()

    def _rebuild_stations(self):
        self._cum_stations = [0.0]
        s = 0.0
        for el in self.elements:
            s += el.length()
            self._cum_stations.append(s)

    def total_length(self) -> float:
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
        # linear search (ok for small counts) ; on peut bsearch si nécessaire
        for i in range(len(self.elements)):
            start = self._cum_stations[i]
            end = self._cum_stations[i + 1]
            if s <= end:
                return i, (s - start)
        # fallback to last
        return len(self.elements) - 1, self.elements[-1].length()

    def point_at(self, station: float) -> Point:
        if not self.elements:
            raise ValueError("Axis has no elements")
        idx, local_s = self._find_element_by_station(station)
        return self.elements[idx].point_at(local_s)

    def project_point(self, p: Point) -> Dict:
        """
        Projet global d'un point p sur l'axe (tous éléments).
        Renvoie dict avec :
            'station' : station le long de l'axe (distance depuis début),
            'offset' : distance latérale (positive = distance euclidienne),
            'point' : Point projeté,
            'element_index' : index de l'élément,
            'local_s' : station locale dans l'élément
        """
        if not self.elements:
            return {
                'station': 0.0,
                'offset': float('inf'),
                'point': None,
                'element_index': None,
                'local_s': 0.0
            }
        
        best = {
            'station': 0.0,
            'offset': float('inf'),
            'point': None,
            'element_index': None,
            'local_s': 0.0
        }
        cum = 0.0
        for i, el in enumerate(self.elements):
            local_s, proj_point, d = el.project_point(p)
            if d < best['offset']:
                best['offset'] = d
                best['point'] = proj_point
                best['local_s'] = local_s
                best['element_index'] = i
                best['station'] = cum + local_s
            cum += el.length()
        return best

    def calculate_offset(self, p: Point) -> float:
        """Retourne la distance (offset) du point p à l'axe (valeur positive)."""
        res = self.project_point(p)
        return res['offset']