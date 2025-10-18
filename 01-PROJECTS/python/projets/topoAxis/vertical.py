
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class VerticalElement:
    L: float      # length (m)
    Z0: float     # elevation at element start (m)
    g0: float     # grade/slope at element start (in ratio, e.g., +0.02 for 2%)

    def Z(self, s: float) -> float:
        raise NotImplementedError
    def g(self, s: float) -> float:
        raise NotImplementedError

@dataclass
class Grade(VerticalElement):
    '''Constant grade (ramp/pente).'''
    def Z(self, s: float) -> float:
        return self.Z0 + self.g0 * s
    def g(self, s: float) -> float:
        return self.g0

@dataclass
class Parabola(VerticalElement):
    '''Parabolic vertical curve between g0 and g1 over L.'''
    g1: float = 0.0
    def Z(self, s: float) -> float:
        # Z = Z0 + g0*s + (g1 - g0) * s^2 / (2*L)
        return self.Z0 + self.g0 * s + (self.g1 - self.g0) * (s*s) / (2.0 * self.L)
    def g(self, s: float) -> float:
        # g(s) = g0 + (g1 - g0)* s / L
        return self.g0 + (self.g1 - self.g0) * (s / self.L)

class VerticalAxis:
    def __init__(self, elements: List[VerticalElement]):
        if not elements:
            raise ValueError('VerticalAxis requires at least one element')
        self.elems = elements
        self._build_chain()

    def _build_chain(self):
        # Continuity for Z0,g0 across elements
        for i in range(1, len(self.elems)):
            prev = self.elems[i-1]
            e = self.elems[i]
            # Set start Z0/g0 to previous end
            Z1 = prev.Z(prev.L)
            g1 = prev.g(prev.L)
            e.Z0 = Z1
            e.g0 = g1

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

    def Z(self, s: float) -> float:
        i, sl = self.locate(s)
        return self.elems[i].Z(sl)

    def g(self, s: float) -> float:
        i, sl = self.locate(s)
        return self.elems[i].g(sl)
