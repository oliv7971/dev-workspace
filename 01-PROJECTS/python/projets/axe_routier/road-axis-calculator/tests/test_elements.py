import unittest
import math
from src.models.point import Point
from src.models.elements import LineElement, CircularArcElement, ClothoidElement
from src.models.axis import Axis


class TestLineElement(unittest.TestCase):
    def test_line_length(self):
        line = LineElement(Point(0, 0), Point(3, 4))
        self.assertAlmostEqual(line.length(), 5.0)
    
    def test_line_point_at(self):
        line = LineElement(Point(0, 0), Point(10, 0))
        p = line.point_at(5)
        self.assertAlmostEqual(p.x, 5.0)
        self.assertAlmostEqual(p.y, 0.0)
    
    def test_line_project_point(self):
        line = LineElement(Point(0, 0), Point(10, 0))
        p = Point(5, 3)
        s, proj, dist = line.project_point(p)
        self.assertAlmostEqual(s, 5.0)
        self.assertAlmostEqual(proj.x, 5.0)
        self.assertAlmostEqual(proj.y, 0.0)
        self.assertAlmostEqual(dist, 3.0)
    
    def test_line_project_point_outside(self):
        line = LineElement(Point(0, 0), Point(10, 0))
        p = Point(-5, 3)
        s, proj, dist = line.project_point(p)
        self.assertAlmostEqual(s, 0.0)  # clamped to start
        self.assertAlmostEqual(proj.x, 0.0)
        self.assertAlmostEqual(proj.y, 0.0)
        self.assertAlmostEqual(dist, math.sqrt(25 + 9))


class TestCircularArcElement(unittest.TestCase):
    def test_arc_length(self):
        # Quarter circle, radius 10
        arc = CircularArcElement(
            center=Point(0, 0), 
            radius=10, 
            start_angle=0, 
            end_angle=math.pi/2,
            ccw=True
        )
        expected_length = 10 * math.pi / 2
        self.assertAlmostEqual(arc.length(), expected_length)
    
    def test_arc_point_at(self):
        arc = CircularArcElement(
            center=Point(0, 0),
            radius=10,
            start_angle=0,
            end_angle=math.pi/2,
            ccw=True
        )
        # Point at start
        p0 = arc.point_at(0)
        self.assertAlmostEqual(p0.x, 10.0)
        self.assertAlmostEqual(p0.y, 0.0)
        # Point at end
        pend = arc.point_at(arc.length())
        self.assertAlmostEqual(pend.x, 0.0, places=5)
        self.assertAlmostEqual(pend.y, 10.0, places=5)
    
    def test_arc_project_point_on_arc(self):
        arc = CircularArcElement(
            center=Point(0, 0),
            radius=10,
            start_angle=0,
            end_angle=math.pi,
            ccw=True
        )
        # Point outside but projecting onto arc
        p = Point(0, 15)
        s, proj, dist = arc.project_point(p)
        self.assertAlmostEqual(proj.x, 0.0, places=5)
        self.assertAlmostEqual(proj.y, 10.0, places=5)
        self.assertAlmostEqual(dist, 5.0, places=5)
        self.assertAlmostEqual(s, arc.length() / 2, places=4)


class TestClothoidElement(unittest.TestCase):
    def test_clothoid_length(self):
        cloth = ClothoidElement(
            p0=Point(0, 0),
            heading0=0,
            length=100,
            k0=0,
            k1=0.01,
            n_steps=100
        )
        self.assertAlmostEqual(cloth.length(), 100.0)
    
    def test_clothoid_straight(self):
        # Clothoid with zero curvature = straight line
        cloth = ClothoidElement(
            p0=Point(0, 0),
            heading0=0,
            length=100,
            k0=0,
            k1=0,
            n_steps=100
        )
        p = cloth.point_at(50)
        self.assertAlmostEqual(p.x, 50.0, places=2)
        self.assertAlmostEqual(p.y, 0.0, places=2)
    
    def test_clothoid_projection(self):
        cloth = ClothoidElement(
            p0=Point(0, 0),
            heading0=0,
            length=100,
            k0=0,
            k1=0,
            n_steps=100
        )
        p = Point(50, 5)
        s, proj, dist = cloth.project_point(p)
        self.assertAlmostEqual(s, 50.0, places=1)
        self.assertAlmostEqual(dist, 5.0, places=1)


class TestAxis(unittest.TestCase):
    def setUp(self):
        self.axis = Axis()
        self.axis.add_element(LineElement(Point(0, 0), Point(100, 0)))
        self.axis.add_element(CircularArcElement(
            center=Point(100, 50),
            radius=50,
            start_angle=3*math.pi/2,
            end_angle=0,
            ccw=True
        ))
    
    def test_total_length(self):
        expected = 100 + 50 * math.pi / 2
        self.assertAlmostEqual(self.axis.total_length(), expected, places=5)
    
    def test_point_at_on_line(self):
        p = self.axis.point_at(50)
        self.assertAlmostEqual(p.x, 50.0)
        self.assertAlmostEqual(p.y, 0.0)
    
    def test_point_at_on_arc(self):
        # Point on the arc
        arc_start = 100
        p = self.axis.point_at(arc_start)
        self.assertAlmostEqual(p.x, 100.0)
        self.assertAlmostEqual(p.y, 0.0)
    
    def test_project_point(self):
        p = Point(50, 10)
        result = self.axis.project_point(p)
        self.assertAlmostEqual(result['station'], 50.0)
        self.assertAlmostEqual(result['offset'], 10.0)
        self.assertEqual(result['element_index'], 0)
    
    def test_calculate_offset(self):
        p = Point(50, 10)
        offset = self.axis.calculate_offset(p)
        self.assertAlmostEqual(offset, 10.0)


if __name__ == '__main__':
    unittest.main()
