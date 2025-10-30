import unittest
from src.calculations.projections import project_point
from src.calculations.offsets import calculate_offset
from src.calculations.geometry import calculate_distance
from src.models.axis import Axis
from src.models.point import Point
from src.models.tunnel import Tunnel

class TestCalculations(unittest.TestCase):

    def setUp(self):
        self.axis = Axis()
        self.point = Point(10, 5)
        self.tunnel = Tunnel(20, 10)

    def test_project_point(self):
        projected_point = project_point(self.point, self.axis)
        self.assertEqual(projected_point.x, 10)  # Assuming the projection logic
        self.assertEqual(projected_point.y, 0)   # Assuming the projection logic

    def test_calculate_offset(self):
        offset = calculate_offset(self.point, self.axis)
        self.assertEqual(offset, 5)  # Assuming the offset logic

    def test_calculate_distance(self):
        point_a = Point(0, 0)
        point_b = Point(3, 4)
        distance = calculate_distance(point_a, point_b)
        self.assertEqual(distance, 5)  # 3-4-5 triangle

    def test_axis_addition(self):
        self.axis.add_element(self.point)
        self.assertIn(self.point, self.axis.elements)

    def test_tunnel_dimensions(self):
        dimensions = self.tunnel.calculate_dimensions()
        self.assertEqual(dimensions['length'], 20)
        self.assertEqual(dimensions['height'], 10)

if __name__ == '__main__':
    unittest.main()