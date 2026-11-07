"""P1/P2 reference shape functions on xi in [-1, 1] (docs/MATH_SPEC.md §4.1-4.2)."""

import numpy as np
import sympy as sp
from numpy.typing import NDArray

from fem1d.mesh import ElementType

_XI = sp.Symbol("xi")

_SYMBOLIC: dict[ElementType, list[sp.Expr]] = {
    "P1": [(1 - _XI) / 2, (1 + _XI) / 2],
    "P2": [_XI * (_XI - 1) / 2, 1 - _XI**2, _XI * (_XI + 1) / 2],
}

_LOCAL_NODES: dict[ElementType, list[float]] = {
    "P1": [-1.0, 1.0],
    "P2": [-1.0, 0.0, 1.0],
}


def local_nodes(element_type: ElementType) -> NDArray[np.float64]:
    """Local node coordinates on the reference interval [-1, 1]."""
    return np.array(_LOCAL_NODES[element_type])


def shape_functions_symbolic(element_type: ElementType) -> list[sp.Expr]:
    """Shape functions N_i(xi) as SymPy expressions in the symbol `xi`."""
    return _SYMBOLIC[element_type]


def shape_functions(element_type: ElementType, xi: float) -> NDArray[np.float64]:
    """Shape function values N_i(xi) at a single point xi."""
    return np.array([float(expr.subs(_XI, xi)) for expr in _SYMBOLIC[element_type]])


def shape_function_derivatives(element_type: ElementType, xi: float) -> NDArray[np.float64]:
    """Shape function derivatives dN_i/dxi at a single point xi."""
    derivs = [sp.diff(expr, _XI) for expr in _SYMBOLIC[element_type]]
    return np.array([float(d.subs(_XI, xi)) for d in derivs])
