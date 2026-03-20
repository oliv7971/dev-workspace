class Tunnel:
    def __init__(self, length, height, width):
        self.length = length
        self.height = height
        self.width = width

    def calculate_volume(self):
        return self.length * self.height * self.width

    def calculate_surface_area(self):
        return 2 * (self.length * self.height + self.length * self.width + self.height * self.width)

    def get_dimensions(self):
        return {
            "length": self.length,
            "height": self.height,
            "width": self.width
        }