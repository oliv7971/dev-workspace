class Displacement:
    def __init__(self, axis, position, value):
        self.axis = axis  # e.g., 'DH', 'DZ'
        self.position = position  # e.g., '1', 'G'
        self.value = value  # Displacement value in mm

    def __repr__(self):
        return f"Displacement(axis={self.axis}, position={self.position}, value={self.value})"

    def to_dict(self):
        return {
            "axis": self.axis,
            "position": self.position,
            "value": self.value
        }

    @staticmethod
    def from_dict(data):
        return Displacement(
            axis=data["axis"],
            position=data["position"],
            value=data["value"]
        )