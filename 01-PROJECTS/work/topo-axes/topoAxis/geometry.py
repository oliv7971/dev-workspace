
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import math

def deg2rad(d: float) -> float:
    return d * math.pi / 180.0

def rad2deg(r: float) -> float:
    return r * 180.0 / math.pi

def gon2rad(g: float) -> float:
    # 400 gons = 2*pi
    return g * math.pi / 200.0

@dataclass
class PlanElement:
    L: float                      # length (m)
    X0: float                     # start X (m)
    Y0: float                     # start Y (m)
    th0: float                    # start azimuth (radians)

    def end_pose(self) -> Tuple[float,float,float]:
        X,Y = self.xy(self.L)
        return X, Y, self.th(self.L)

    def th(self, s: float) -> float:
        '''Tangent azimuth at curvilinear abscissa s (rad).'''
        raise NotImplementedError

    def xy(self, s: float) -> Tuple[float,float]:
        '''Coordinates at curvilinear abscissa s (m).'''
        raise NotImplementedError

    def frame(self, s: float) -> Tuple[float,float,float, float,float, float,float]:
        '''Return pose and Frenet frame at s:
           (X,Y,theta, tx,ty, nx_right, ny_right)
           Convention: right-normal is (sin theta, -cos theta).
        '''
        X,Y = self.xy(s)
        theta = self.th(s)
        tx, ty = math.cos(theta), math.sin(theta)
        nx_r, ny_r = math.sin(theta), -math.cos(theta)  # right normal
        return X,Y,theta, tx,ty, nx_r, ny_r

    def project_point(self, X: float, Y: float) -> Tuple[float, float, float, float]:
        '''Project a point (X,Y) onto this element.
           Returns (s_local, d_signed, Xs, Ys), where d>0 = droite, d<0 = gauche.
        '''
        raise NotImplementedError

    def offset_xy(self, s: float, d: float) -> Tuple[float,float]:
        '''Apply signed offset d (droite=+; gauche=-) at abscissa s.'''
        X,Y,theta, tx,ty, nx_r, ny_r = self.frame(s)
        return X + nx_r * d, Y + ny_r * d

@dataclass
class Line(PlanElement):
    '''Straight segment.'''
    def th(self, s: float) -> float:
        return self.th0
    def xy(self, s: float) -> Tuple[float,float]:
        c, snt = math.cos(self.th0), math.sin(self.th0)
        return self.X0 + s*c, self.Y0 + s*snt
    def project_point(self, X: float, Y: float):
        # Project on infinite line then clamp to [0,L]
        dx, dy = math.cos(self.th0), math.sin(self.th0)
        vx, vy = X - self.X0, Y - self.Y0
        s = vx*dx + vy*dy
        s_clamped = min(max(0.0, s), self.L)
        Xs, Ys = self.xy(s_clamped)
        # signed offset (droite + / gauche -) => dot with right-normal
        nx_r, ny_r = math.sin(self.th0), -math.cos(self.th0)
        d = (X - Xs)*nx_r + (Y - Ys)*ny_r
        return s_clamped, d, Xs, Ys

@dataclass
class Arc(PlanElement):
    '''Circular arc with signed radius R_internal (our internal convention: R>0 = LEFT).
       Input convention (engine/parser) will map user: Droite=+ / Gauche=- to this by flipping sign.
    '''
    R: float                      # signed radius (internal: + = left)

    def _center(self) -> Tuple[float,float]:
        # Xc = X0 - R*sin(th0); Yc = Y0 + R*cos(th0)
        return (self.X0 - self.R * math.sin(self.th0),
                self.Y0 + self.R * math.cos(self.th0))

    def th(self, s: float) -> float:
        return self.th0 + s / self.R

    def xy(self, s: float) -> Tuple[float,float]:
        Xc, Yc = self._center()
        ths = self.th0 + s / self.R
        return Xc + self.R * math.sin(ths), Yc - self.R * math.cos(ths)

    def project_point(self, X: float, Y: float):
        # Radial projection to circle, then clamp angle range to [0,L]
        Xc, Yc = self._center()
        vx, vy = X - Xc, Y - Yc
        phi_p = math.atan2(vy, vx)                       # angle of radius to point
        # start radius angle at s=0
        phi0 = self.th0 - math.pi/2.0
        # signed angle difference along arc parameterization
        dphi = phi_p - phi0
        # normalize to nearest equivalent considering R sign
        # Wrap to [-pi, pi] for stability
        while dphi > math.pi: dphi -= 2*math.pi
        while dphi < -math.pi: dphi += 2*math.pi
        s = dphi * self.R
        s_clamped = min(max(0.0, s), self.L)
        Xs, Ys = self.xy(s_clamped)
        ths = self.th(s_clamped)
        nx_r, ny_r = math.sin(ths), -math.cos(ths)
        d = (X - Xs)*nx_r + (Y - Ys)*ny_r
        return s_clamped, d, Xs, Ys

@dataclass
class Clothoid(PlanElement):
    '''Euler spiral / clothoïd where curvature k(s) = k_sign * s / A^2.
       The parameter A (m) defines the rate; k_sign = +1 LEFT, -1 RIGHT (internal).
       Integration is done numerically (composite Simpson).
    '''
    A: float
    k_sign: int = 1              # internal: +1 left, -1 right
    n_sub: int = 200             # integration substeps for xy(s)

    def th(self, s: float) -> float:
        return self.th0 + self.k_sign * (s*s) / (2.0 * self.A * self.A)

    def _local_xy(self, s: float) -> Tuple[float,float]:
        if s == 0.0:
            return 0.0, 0.0
        n = max(4, int(self.n_sub * max(1.0, s / 50.0)))
        if n % 2 == 1:
            n += 1
        h = s / n
        def theta_rel(u: float) -> float:
            return self.k_sign * (u*u) / (2.0 * self.A * self.A)
        def fcos(u): return math.cos(theta_rel(u))
        def fsin(u): return math.sin(theta_rel(u))
        def simpson(f):
            acc = f(0.0) + f(s)
            for i in range(1, n):
                coeff = 4.0 if i % 2 == 1 else 2.0
                acc += coeff * f(i*h)
            return acc * h / 3.0
        x = simpson(fcos)
        y = simpson(fsin)
        return x, y

    def xy(self, s: float) -> Tuple[float,float]:
        x, y = self._local_xy(s)
        ct, st = math.cos(self.th0), math.sin(self.th0)
        X = self.X0 + ct * x - st * y
        Y = self.Y0 + st * x + ct * y
        return X, Y

    def project_point(self, X: float, Y: float):
        # 1D search on s in [0,L] to minimize squared distance
        # coarse grid + golden-section refine
        def f(s):
            xs, ys = self.xy(s)
            dx, dy = X - xs, Y - ys
            return dx*dx + dy*dy
        # coarse search
        n = 60
        best_s = 0.0
        best_v = f(0.0)
        for i in range(1, n+1):
            s = self.L * i / n
            v = f(s)
            if v < best_v:
                best_v, best_s = v, s
        # golden-section refine
        a = max(0.0, best_s - self.L/10.0)
        b = min(self.L, best_s + self.L/10.0)
        phi = (1 + 5**0.5) / 2
        invphi = 1/phi
        x1 = b - (b-a)*invphi
        x2 = a + (b-a)*invphi
        f1 = f(x1); f2 = f(x2)
        for _ in range(40):
            if f1 > f2:
                a = x1
                x1 = x2
                f1 = f2
                x2 = a + (b-a)*invphi
                f2 = f(x2)
            else:
                b = x2
                x2 = x1
                f2 = f1
                x1 = b - (b-a)*invphi
                f1 = f(x1)
        s_clamped = 0.5*(a+b)
        Xs,Ys,theta,tx,ty,nx_r,ny_r = (*self.frame(s_clamped),)
        d = (X - Xs)*nx_r + (Y - Ys)*ny_r
        return s_clamped, d, Xs, Ys

class PlanAxis:
    '''Sequence of planar elements (Line, Arc, Clothoid) with continuous pose.
       Provides projection (rabattement) and offset utilities.
    '''
    def __init__(self, elements: List[PlanElement]):
        if not elements:
            raise ValueError('PlanAxis requires at least one element')
        self.elems = elements
        self._build_chain()

    def _build_chain(self):
        for i in range(1, len(self.elems)):
            prev = self.elems[i-1]
            X1, Y1, th1 = prev.end_pose()
            e = self.elems[i]
            e.X0, e.Y0, e.th0 = X1, Y1, th1

    @property
    def L(self) -> float:
        return sum(e.L for e in self.elems)

    def locate(self, s: float) -> Tuple[int, float]:
        if s < 0 or s > self.L + 1e-9:
            raise ValueError(f's={s} outside [0,{self.L}]')
        acc = 0.0
        for i, e in enumerate(self.elems):
            if s <= acc + e.L or i == len(self.elems)-1:
                return i, s - acc
            acc += e.L
        return len(self.elems)-1, self.elems[-1].L

    def xy(self, s: float) -> Tuple[float,float]:
        i, sl = self.locate(s)
        return self.elems[i].xy(sl)

    def th(self, s: float) -> float:
        i, sl = self.locate(s)
        return self.elems[i].th(sl)

    def frame(self, s: float):
        i, sl = self.locate(s)
        return self.elems[i].frame(sl)

    def offset_xy(self, s: float, d: float) -> Tuple[float,float]:
        i, sl = self.locate(s)
        return self.elems[i].offset_xy(sl, d)

    def project_point(self, X: float, Y: float) -> Tuple[float,float,float,float]:
        '''Orthogonal rabattement of (X,Y) onto the axis.
           Returns (s_global, d_signed, Xs, Ys).
           d>0 → droite ; d<0 → gauche.
        '''
        acc = 0.0
        best = (0.0, 0.0, float('inf'), 0.0, 0.0)  # (s_global, d, dist2, Xs, Ys)
        for e in self.elems:
            sl, d, Xs, Ys = e.project_point(X, Y)
            dx, dy = X - Xs, Y - Ys
            dist2 = dx*dx + dy*dy
            sg = acc + sl
            if dist2 < best[2]:
                best = (sg, d, dist2, Xs, Ys)
            acc += e.L
        return best[0], best[1], best[3], best[4]
