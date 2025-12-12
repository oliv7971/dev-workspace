"""
Parser pour le format GSI de Leica (GSI-8 et GSI-16)
Permet de lire les fichiers de station totale Leica et les convertir en observations
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import math


@dataclass
class GSIRecord:
    """Un enregistrement GSI (une ligne)"""
    point_id: Optional[str] = None
    hz: Optional[float] = None  # Direction horizontale (gon)
    v: Optional[float] = None   # Angle vertical (gon)
    slope_dist: Optional[float] = None  # Distance inclinée (m)
    horiz_dist: Optional[float] = None  # Distance horizontale (m)
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    reflector_height: Optional[float] = None
    station_id: Optional[str] = None
    
    def __repr__(self):
        return f"GSIRecord(point={self.point_id}, Hz={self.hz}, V={self.v}, dist={self.slope_dist})"


class GSIParser:
    """Parser pour fichiers GSI de Leica"""
    
    # Codes Word Index principaux
    WI_CODES = {
        '11': 'point_id',        # Point number
        '12': 'serial',          # Serial number
        '13': 'code',            # Code
        '21': 'hz',              # Horizontal angle (Hz)
        '22': 'v',               # Vertical angle (V)
        '25': 'hz_rms',          # Hz RMS
        '26': 'v_rms',           # V RMS
        '31': 'slope_dist',      # Slope distance
        '32': 'horiz_dist',      # Horizontal distance
        '33': 'height_diff',     # Height difference
        '51': 'ppm',             # PPM
        '52': 'prism_const',     # Prism constant
        '58': 'instrument_height', # Instrument height
        '59': 'reflector_height', # Reflector/target height
        '71': 'date',            # Date
        '72': 'time',            # Time
        '81': 'x',               # Easting (E, X)
        '82': 'y',               # Northing (N, Y)
        '83': 'z',               # Elevation (H, Z)
        '84': 'station_x',       # Station E
        '85': 'station_y',       # Station N
        '86': 'station_z',       # Station H
        '87': 'reflector_height_2', # Alternative reflector height
        '88': 'instrument_height_2', # Alternative instrument height
    }
    
    def __init__(self):
        self.records: List[GSIRecord] = []
        self.current_station: Optional[str] = None
        self.instrument_height: float = 0.0
        
    def parse_file(self, filepath: Path) -> List[GSIRecord]:
        """Parser un fichier GSI complet"""
        self.records = []
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    record = self.parse_line(line)
                    if record:
                        self.records.append(record)
        
        return self.records
    
    def parse_line(self, line: str) -> Optional[GSIRecord]:
        """Parser une ligne GSI"""
        # Séparer les champs (espaces)
        parts = line.strip().split()
        
        if not parts:
            return None
        
        record = GSIRecord()
        
        for part in parts:
            # Pattern pour un champ GSI
            # Format: WI(2) + INFO(4) + SIGN(1) + VALUE(variable)
            match = re.match(r'(\d{2})([.\d]{4})([\+\-])([\d\.]+)', part)
            
            if not match:
                continue
            
            wi, info, sign, value = match.groups()
            
            # Ignorer les champs avec des points uniquement (données non disponibles)
            if value.replace('.', '') == '':
                continue
            
            # Le premier caractère de info indique l'unité
            unit_code = info[0]
            
            # Traiter selon le Word Index
            if wi in self.WI_CODES:
                attr_name = self.WI_CODES[wi]
                parsed_value = self._parse_value(wi, value, sign, unit_code)
                setattr(record, attr_name, parsed_value)
        
        return record
    
    def _parse_value(self, wi: str, value: str, sign: str, unit_code: str) -> any:
        """Parser une valeur selon son type et son unité"""
        
        # Point ID et codes texte
        if wi in ['11', '12', '13', '84', '85', '86']:
            return value.lstrip('0') or '0'
        
        # Valeurs numériques
        num_value = int(value) if value else 0
        if sign == '-':
            num_value = -num_value
        
        # Angles (Hz, V)
        if wi in ['21', '22']:
            # unit_code:
            # 3 = gon/400
            # 4 = deg/360
            # 5 = mil/6400
            if unit_code == '3':  # Gon
                return num_value / 100000.0  # 5 décimales
            elif unit_code == '4':  # Degrees
                return num_value / 100000.0
            elif unit_code == '5':  # Mil
                return num_value / 100000.0
            else:
                return num_value / 100000.0  # Par défaut gon
        
        # Distances
        elif wi in ['31', '32', '33']:
            # unit_code:
            # 1 = meter
            # 2 = feet
            if unit_code == '1':  # Meter
                return num_value / 1000.0  # mm -> m
            elif unit_code == '2':  # Feet
                return num_value / 1000.0 * 0.3048
            else:
                return num_value / 1000.0
        
        # Coordonnées X, Y, Z
        elif wi in ['81', '82', '83']:
            return num_value / 1000.0  # mm -> m
        
        # Hauteurs (instrument, prisme)
        elif wi in ['58', '59', '87', '88']:
            return num_value / 1000.0  # mm -> m
        
        # PPM, constante prisme
        elif wi in ['51', '52']:
            return num_value / 1.0
        
        else:
            return num_value
    
    def to_observations(self, station_coords: Optional[Dict[str, Tuple[float, float, float]]] = None) -> Tuple[List, Dict]:
        """
        Convertir les enregistrements GSI en observations et points connus
        
        Returns:
            (observations, control_points)
        """
        try:
            from topo_station_ls import Observation, ControlPoint
        except ImportError:
            # Si l'import échoue, créer des classes temporaires
            from dataclasses import dataclass
            
            @dataclass
            class Observation:
                ray_id: str
                pid: str
                obs_type: str
                value: float
                unit: str
                n_series: int
                h_target: float
            
            @dataclass
            class ControlPoint:
                pid: str
                X: float
                Y: float
                Z: float
        
        observations = []
        control_points = {}
        ray_counter = 1
        
        for record in self.records:
            if not record.point_id:
                continue
            
            # Si le point a des coordonnées, c'est un point connu
            if record.x is not None and record.y is not None and record.z is not None:
                point_id = str(record.point_id)
                control_points[point_id] = ControlPoint(
                    pid=point_id,
                    X=record.x,
                    Y=record.y,
                    Z=record.z
                )
            
            # Ajouter les observations
            ray_id = f"R{ray_counter:03d}"
            h_target = record.reflector_height if record.reflector_height else 0.0
            point_id = str(record.point_id)
            
            # Direction horizontale
            if record.hz is not None:
                obs = Observation(
                    ray_id=ray_id,
                    pid=point_id,
                    obs_type='dir',
                    value=record.hz,
                    unit='gon',
                    n_series=1,
                    h_target=h_target
                )
                observations.append(obs)
            
            # Angle vertical (converti en zénith si nécessaire)
            if record.v is not None:
                # Si V est un angle vertical (0 = horizon), convertir en zénith
                # Zénith = 100 - V (en gon)
                zenith = 100.0 - record.v  # Conversion angle vertical -> zénith
                obs = Observation(
                    ray_id=ray_id,
                    pid=point_id,
                    obs_type='zen',
                    value=zenith,
                    unit='gon',
                    n_series=1,
                    h_target=h_target
                )
                observations.append(obs)
            
            # Distance inclinée (préférée)
            if record.slope_dist is not None:
                obs = Observation(
                    ray_id=ray_id,
                    pid=point_id,
                    obs_type='dist',
                    value=record.slope_dist,
                    unit='m',
                    n_series=1,
                    h_target=h_target
                )
                observations.append(obs)
            # Sinon distance horizontale
            elif record.horiz_dist is not None:
                obs = Observation(
                    ray_id=ray_id,
                    pid=point_id,
                    obs_type='dist',
                    value=record.horiz_dist,
                    unit='m',
                    n_series=1,
                    h_target=h_target
                )
                observations.append(obs)
            
            ray_counter += 1
        
        return observations, control_points
    
    def get_instrument_height(self) -> float:
        """Récupérer la hauteur d'instrument depuis les enregistrements"""
        for record in self.records:
            if record.instrument_height is not None:
                return record.instrument_height
            if hasattr(record, 'instrument_height_2') and record.instrument_height_2 is not None:
                return record.instrument_height_2
        return 0.0
    
    def export_summary(self) -> str:
        """Générer un résumé des données GSI"""
        text = "="*70 + "\n"
        text += "  RÉSUMÉ DES DONNÉES GSI\n"
        text += "="*70 + "\n\n"
        
        text += f"Nombre d'enregistrements : {len(self.records)}\n\n"
        
        # Statistiques
        n_hz = sum(1 for r in self.records if r.hz is not None)
        n_v = sum(1 for r in self.records if r.v is not None)
        n_dist = sum(1 for r in self.records if r.slope_dist is not None or r.horiz_dist is not None)
        n_coords = sum(1 for r in self.records if r.x is not None and r.y is not None and r.z is not None)
        
        text += "Observations trouvées :\n"
        text += f"  - Directions Hz    : {n_hz}\n"
        text += f"  - Angles V         : {n_v}\n"
        text += f"  - Distances        : {n_dist}\n"
        text += f"  - Points avec XYZ  : {n_coords}\n\n"
        
        # Points uniques
        unique_points = set(r.point_id for r in self.records if r.point_id)
        text += f"Points uniques : {len(unique_points)}\n"
        text += f"  {', '.join(sorted(unique_points))}\n\n"
        
        # Hauteur instrument
        h_inst = self.get_instrument_height()
        text += f"Hauteur instrument : {h_inst:.3f} m\n"
        
        return text


def test_parser():
    """Test du parser GSI"""
    # Exemple GSI-8
    gsi8_data = """110001+00001001 21.324+00012345 22.324+00098765 31..00+00012345 87..10+00001500
110002+00001002 21.324+00056789 22.324+00095432 31..00+00023456 87..10+00001500
81..00+01000000 82..00+02000000 83..00+00250000 11....+00001001"""
    
    parser = GSIParser()
    
    print("Test du parser GSI")
    print("="*70)
    
    # Test regex
    line = "110001+00001001 21.324+00012345 22.324+00098765 31..00+00012345"
    print(f"\nTest regex sur: {line}")
    pattern = r'(\d{2})(\d{4})([\+\-\.])([\d\.]+)'
    matches = re.findall(pattern, line)
    print(f"Matches trouvés: {len(matches)}")
    for m in matches:
        print(f"  {m}")
    
    print("\n" + "="*70)
    
    for line in gsi8_data.strip().split('\n'):
        record = parser.parse_line(line)
        if record:
            print(f"\nLigne: {line[:50]}...")
            print(f"  Point: {record.point_id}")
            print(f"  Hz: {record.hz}")
            print(f"  V: {record.v}")
            print(f"  Distance: {record.slope_dist}")
            print(f"  XYZ: {record.x}, {record.y}, {record.z}")
            print(f"  H prisme: {record.reflector_height}")


if __name__ == "__main__":
    test_parser()
