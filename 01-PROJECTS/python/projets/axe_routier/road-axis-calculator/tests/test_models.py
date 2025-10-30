import unittest
from src.models.axis import Axis
from src.models.point import Point
from src.models.tunnel import Tunnel

class TestAxis(unittest.TestCase):
    def setUp(self):
        self.axis = Axis()
    
    def test_add_element(self):
        self.axis.add_element(Point(0, 0))
        self.assertEqual(len(self.axis.elements), 1)
    
    def test_calculate_properties(self):
        self.axis.add_element(Point(0, 0))
        self.axis.add_element(Point(1, 1))
        properties = self.axis.calculate_properties()
        self.assertIsNotNone(properties)

class TestPoint(unittest.TestCase):
    def setUp(self):
        self.point = Point(1, 2)
    
    def test_distance(self):
        other_point = Point(4, 6)
        distance = self.point.distance_to(other_point)
        self.assertEqual(distance, 5.0)

class TestTunnel(unittest.TestCase):
    def setUp(self):
        self.tunnel = Tunnel(length=100, height=5, width=10)
    
    def test_tunnel_dimensions(self):
        dimensions = self.tunnel.get_dimensions()
        self.assertEqual(dimensions['length'], 100)
        self.assertEqual(dimensions['height'], 5)
        self.assertEqual(dimensions['width'], 10)

if __name__ == '__main__':
    unittest.main()