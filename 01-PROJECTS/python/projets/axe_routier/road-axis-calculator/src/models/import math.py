import math
from typing import Optional


class Point:
    """Représente un point 2D ou 3D dans l'espace."""
    
    def __init__(self, x: float, y: float, z: Optional[float] = None):
        self.x = x
        self.y = y
        self.z = z
    
    def distance_to(self, other: 'Point') -> float:
        """Calcule la distance euclidienne à un autre point."""
        dx = self.x - other.x
        dy = self.y - other.y
        if self.z is not None and other.z is not None:
            dz = self.z - other.z
            return math.sqrt(dx * dx + dy * dy + dz * dz)
        return math.sqrt(dx * dx + dy * dy)
    
    def __repr__(self):
        if self.z is not None:
            return f"Point(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})"
        return f"Point(x={self.x:.2f}, y={self.y:.2f})"
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return (abs(self.x - other.x) < 1e-9 and 
                abs(self.y - other.y) < 1e-9 and
                (self.z == other.z or (self.z is not None and other.z is not None and abs(self.z - other.z) < 1e-9)))