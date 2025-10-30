from math import atan2, cos, sin, sqrt, fabs, pi
from typing import Tuple, Optional, List
from .point import Point


class AxisElement:
    """Interface basique pour un élément d'axe en plan."""
    def length(self) -> float:
        raise NotImplementedError

    def point_at(self, s: float) -> Point:
        """Retourne le point situé à la distance s depuis le début de l'élément (0 <= s <= length)."""
        raise NotImplementedError

    def project_point(self, p: Point) -> Tuple[float, Point, float]:
        """
        Projeté orthogonal du point p sur cet élément.
        Retourne (s, projected_point, distance) où s est la station locale (distance depuis début élément).
        """
        raise NotImplementedError


class LineElement(AxisElement):
    def __init__(self, p0: Point, p1: Point):
        self.p0 = p0
        self.p1 = p1
        dx = p1.x - p0.x
        dy = p1.y - p0.y
        self._length = sqrt(dx * dx + dy * dy)
        self._dx = dx
        self._dy = dy

    def length(self) -> float:
        return self._length

    def point_at(self, s: float) -> Point:
        if self._length == 0:
            return Point(self.p0.x, self.p0.y)
        t = max(0.0, min(1.0, s / self._length))
        return Point(self.p0.x + t * self._dx, self.p0.y + t * self._dy)

    def project_point(self, p: Point) -> Tuple[float, Point, float]:
        # projection onto segment
        if self._length == 0:
            proj = Point(self.p0.x, self.p0.y)
            d = p.distance_to(proj)
            return 0.0, proj, d
        vx = p.x - self.p0.x
        vy = p.y - self.p0.y
        dot = vx * self._dx + vy * self._dy
        t = dot / (self._length * self._length)
        t_clamped = max(0.0, min(1.0, t))
        proj = Point(self.p0.x + t_clamped * self._dx, self.p0.y + t_clamped * self._dy)
        s = t_clamped * self._length
        d = p.distance_to(proj)
        return s, proj, d


class CircularArcElement(AxisElement):
    def __init__(self, center: Point, radius: float, start_angle: float, end_angle: float, ccw: bool = True):
        """
        center : centre du cercle
        radius : rayon (>0)
        start_angle, end_angle : angles en radians (orientation standard)
        ccw : sens positif (True si anti-horaire)
        """
        self.center = center
        self.radius = abs(radius)
        self.start_angle = start_angle
        self.end_angle = end_angle
        if ccw:
            delta = end_angle - start_angle
            if delta < 0:
                delta += 2 * pi
        else:
            delta = start_angle - end_angle
            if delta < 0:
                delta += 2 * pi
        self._angle = delta
        self.ccw = ccw

    def length(self) -> float:
        return self.radius * self._angle

    def _angle_at_s(self, s: float) -> float:
        L = self.length()
        if L == 0:
            return self.start_angle
        frac = max(0.0, min(1.0, s / L))
        if self.ccw:
            return self.start_angle + frac * self._angle
        else:
            return self.start_angle - frac * self._angle

    def point_at(self, s: float) -> Point:
        theta = self._angle_at_s(s)
        x = self.center.x + self.radius * cos(theta)
        y = self.center.y + self.radius * sin(theta)
        return Point(x, y)

    def project_point(self, p: Point) -> Tuple[float, Point, float]:
        # projection onto circle then clamp to arc angles
        vx = p.x - self.center.x
        vy = p.y - self.center.y
        r = sqrt(vx * vx + vy * vy)
        if r == 0:
            # ambiguous center; return start
            proj_angle = self.start_angle
            proj = self.point_at(0.0)
            d = p.distance_to(proj)
            return 0.0, proj, d
        # closest point on full circle
        proj_angle = atan2(vy, vx)
        # normalize angles to [0,2pi)
        def norm(a): 
            while a < 0:
                a += 2 * pi
            while a >= 2 * pi:
                a -= 2 * pi
            return a
        sa = norm(self.start_angle)
        ea = norm(self.end_angle)
        pa = norm(proj_angle)
        # check if projected angle lies inside arc; if not use nearest end
        def angle_in_arc(angle):
            if self.ccw:
                if ea >= sa:
                    return sa <= angle <= ea
                else:
                    return angle >= sa or angle <= ea
            else:
                # clockwise arc
                if sa >= ea:
                    return ea <= angle <= sa
                else:
                    return angle >= ea or angle <= ea

        if angle_in_arc(pa):
            proj = Point(self.center.x + self.radius * cos(pa), self.center.y + self.radius * sin(pa))
            # compute s from start angle
            if self.ccw:
                delta = pa - sa
                if delta < 0:
                    delta += 2 * pi
            else:
                delta = sa - pa
                if delta < 0:
                    delta += 2 * pi
            s = self.radius * delta
            d = p.distance_to(proj)
            return s, proj, d
        else:
            # nearest of endpoints
            p_start = self.point_at(0.0)
            p_end = self.point_at(self.length())
            ds = p.distance_to(p_start)
            de = p.distance_to(p_end)
            if ds <= de:
                return 0.0, p_start, ds
            else:
                return self.length(), p_end, de


class ClothoidElement(AxisElement):
    def __init__(self, p0: Point, heading0: float, length: float, k0: float, k1: float, n_steps: int = 400):
        """
        Clothoid (Euler spiral) approximated by small segments.
        p0 : point at s=0
        heading0 : initial heading (rad)
        length : longueur totale
        k0, k1 : curvature at start and end (1/m). Curvature varies linearly.
        n_steps : discrétisation pour intégration (plus élevé = plus précis)
        """
        self.p0 = p0
        self.heading0 = heading0
        self.L = max(0.0, length)
        self.k0 = k0
        self.k1 = k1
        self.n_steps = max(1, int(n_steps))
        # precompute polyline approximating clothoid
        self._s_list: List[float] = [0.0]
        self._pts: List[Point] = [Point(p0.x, p0.y)]
        if self.L > 0:
            ds = self.L / self.n_steps
            heading = heading0
            x = p0.x
            y = p0.y
            for i in range(1, self.n_steps + 1):
                s_mid = (i - 0.5) * ds
                curvature = self.k0 + (self.k1 - self.k0) * (s_mid / self.L)
                # small advance using heading and curvature
                heading += curvature * ds
                x += ds * cos(heading)
                y += ds * sin(heading)
                self._s_list.append(min(i * ds, self.L))
                self._pts.append(Point(x, y))

    def length(self) -> float:
        return self.L

    def point_at(self, s: float) -> Point:
        if self.L == 0:
            return Point(self.p0.x, self.p0.y)
        s = max(0.0, min(self.L, s))
        # find segment
        idx = 0
        while idx + 1 < len(self._s_list) and self._s_list[idx + 1] < s:
            idx += 1
        s0 = self._s_list[idx]
        if idx + 1 >= len(self._s_list):
            return Point(self._pts[-1].x, self._pts[-1].y)
        s1 = self._s_list[idx + 1]
        p0 = self._pts[idx]
        p1 = self._pts[idx + 1]
        if s1 == s0:
            return Point(p0.x, p0.y)
        t = (s - s0) / (s1 - s0)
        return Point(p0.x + t * (p1.x - p0.x), p0.y + t * (p1.y - p0.y))

    def project_point(self, p: Point) -> Tuple[float, Point, float]:
        # brute force: find nearest among discretized points and then refine to the segment
        best_d = float('inf')
        best_idx = 0
        for i, pt in enumerate(self._pts):
            d = p.distance_to(pt)
            if d < best_d:
                best_d = d
                best_idx = i
        # refine by checking neighbor segment projection
        idx0 = max(0, best_idx - 1)
        idx1 = min(len(self._pts) - 1, best_idx + 1)
        # parametrize line segment idx0->idx1
        a = self._pts[idx0]
        b = self._pts[idx1]
        seg = LineElement(a, b)
        s_seg, proj, d = seg.project_point(p)
        # compute absolute s along clothoid: s_at_idx0 + s_seg_clamped
        s_at_idx0 = self._s_list[idx0]
        s_abs = s_at_idx0 + s_seg
        s_abs = max(0.0, min(self.L, s_abs))
        return s_abs, proj, d