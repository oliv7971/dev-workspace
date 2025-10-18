
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Iterable
from .geometry import PlanAxis, Line, Arc, Clothoid, gon2rad
from .vertical import VerticalAxis, Grade, Parabola

@dataclass
class AxisModel:
    plan: PlanAxis
    vertical: VerticalAxis

    @property
    def L(self) -> float:
        return min(self.plan.L, self.vertical.L)

    def xyz(self, s: float):
        X, Y = self.plan.xy(s)
        Z = self.vertical.Z(s)
        return X, Y, Z

    def xy_offset(self, s: float, d: float):
        '''From chainage s and signed offset d (droite=+, gauche=-), return (X,Y).'''
        return self.plan.offset_xy(s, d)

    def project_xy(self, X: float, Y: float):
        '''Orthogonal rabattement of (X,Y) onto the axis → (s, d, Xs, Ys).'''
        return self.plan.project_point(X, Y)

    def profile(self, s_vals: Iterable[float]):
        return [self.xyz(s) for s in s_vals]

def build_plan_from_defs(defs: List[Dict], X0=0.0, Y0=0.0, azimut_gon: float = 0.0) -> PlanAxis:
    '''Build PlanAxis from element defs (user conventions):
       - Azimut provided in gons for the first element.
       - ARC: user R>0 = DROITE, R<0 = GAUCHE  → internal uses R_internal = -R_user
       - CLOTH: user k_sign>0 = DROITE, <0 = GAUCHE → internal k_sign = -k_sign_user
    '''
    th0 = gon2rad(azimut_gon)
    elems = []
    Xc, Yc, thc = X0, Y0, th0
    for i, d in enumerate(defs):
        typ = str(d.get('type','')).strip().upper()
        L = float(d['L'])
        if i == 0 and 'azimut_gon' in d:
            thc = gon2rad(float(d['azimut_gon']))
        if typ in ('LINE','DROITE','ALIGN'):
            e = Line(L=L, X0=Xc, Y0=Yc, th0=thc)
        elif typ in ('ARC','CERCLE'):
            R_user = float(d['R'])
            e = Arc(L=L, X0=Xc, Y0=Yc, th0=thc, R=-R_user)  # flip to internal
        elif typ in ('CLOTH','CLOTHO','CLOTHOIDE','CLOTHOÏDE','CLOT'):
            A = float(d['A'])
            k_user = int(d.get('k_sign', 1))
            e = Clothoid(L=L, X0=Xc, Y0=Yc, th0=thc, A=A, k_sign=-k_user)  # flip to internal
        else:
            raise ValueError(f'Unknown plan element type: {typ}')
        elems.append(e)
        Xc, Yc, thc = e.end_pose()
    return PlanAxis(elems)

def build_vertical_from_defs(defs: List[Dict], Z0=0.0, g0_percent: float = 0.0) -> VerticalAxis:
    '''Vertical defs: slopes in percent.'''
    elems = []
    Zc, gc = Z0, (g0_percent/100.0)
    for i, d in enumerate(defs):
        typ = str(d.get('type','')).strip().upper()
        L = float(d['L'])
        if typ in ('GRADE','DROITE','ALIGN','RAMPE','PENTE'):
            g = float(d.get('g_percent', gc*100.0))/100.0
            e = Grade(L=L, Z0=Zc, g0=g)
        elif typ in ('PARAB','PARABOLE','RACCOR','RACCORD'):
            g1 = float(d['g1_percent'])/100.0
            e = Parabola(L=L, Z0=Zc, g0=gc, g1=g1)
        else:
            raise ValueError(f'Unknown vertical element type: {typ}')
        elems.append(e)
        Zc = e.Z(L)
        gc = e.g(L)
    return VerticalAxis(elems)
