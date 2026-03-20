
import math
from topo_axis.geometry import Line, Arc, Clothoid

def approx(a,b,eps=1e-6): return abs(a-b) < eps

def test_line():
    e = Line(L=100, X0=0, Y0=0, th0=0.0)
    X,Y = e.xy(100)
    assert approx(X,100.0) and approx(Y,0.0)

def test_arc():
    R = 50.0
    e = Arc(L=math.pi*R/2, X0=0, Y0=0, th0=0.0, R=R) # quarter circle left
    X,Y = e.xy(e.L)
    # expect close to (R, R)
    assert abs(X-R) < 1e-6 and abs(Y-R) < 1e-6

def test_clothoid_small():
    A = 100.0
    e = Clothoid(L=10.0, X0=0, Y0=0, th0=0.0, A=A, k_sign=1, n_sub=200)
    X,Y = e.xy(10.0)
    # For very small s/A, curve is nearly a straight line
    assert X > 9.9 and abs(Y) < 0.1
