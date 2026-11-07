"""Element matrices K, C, M, F by Gauss-Legendre quadrature (docs/MATH_SPEC.md §5).

Point counts follow §5.2: for a coefficient of known polynomial degree, the
rule is chosen to integrate the full integrand exactly. An unknown
(non-polynomial) degree falls back to a fixed point count and the result is
flagged as approximate (QUADRATURE_APPROX, docs/MATH_SPEC.md §8).
"""

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from fem1d.elements import local_nodes, shape_function_derivatives, shape_functions
from fem1d.mesh import ElementType
from fem1d.quadrature import gauss_legendre

Coefficient = Callable[[float], float]

_FALLBACK_POINTS: dict[ElementType, int] = {"P1": 8, "P2": 10}


@dataclass(frozen=True)
class ElementMatrices:
    """K, C, M element matrices and F load vector for a single element."""

    K: NDArray[np.float64]
    C: NDArray[np.float64]
    M: NDArray[np.float64]
    F: NDArray[np.float64]
    quadrature_approx: bool


def _degree_to_point_count(
    element_type: ElementType, degree: int | None, extra: int
) -> tuple[int, bool]:
    if degree is None:
        return _FALLBACK_POINTS[element_type], True
    return math.ceil((degree + extra + 1) / 2), False


def element_matrices(
    element_type: ElementType,
    interval: tuple[float, float],
    p: Coefficient,
    p_degree: int | None,
    q: Coefficient,
    q_degree: int | None,
    r: Coefficient,
    r_degree: int | None,
    f: Coefficient,
    f_degree: int | None,
) -> ElementMatrices:
    a, b = interval
    h = b - a
    jacobian = h / 2
    k = 1 if element_type == "P1" else 2
    ndof = len(local_nodes(element_type))

    def to_physical(xi: float) -> float:
        return (a + b) / 2 + jacobian * xi

    quadrature_approx = False

    def point_count(degree: int | None, extra: int) -> int:
        nonlocal quadrature_approx
        m, approx = _degree_to_point_count(element_type, degree, extra)
        quadrature_approx = quadrature_approx or approx
        return m

    Integrand = Callable[[float, NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]

    def quad_matrix(m: int, integrand: Integrand) -> NDArray[np.float64]:
        rule = gauss_legendre(m)
        total = np.zeros((ndof, ndof))
        for xi, w in zip(rule.points, rule.weights, strict=True):
            x = to_physical(xi)
            n = shape_functions(element_type, xi)
            dn = shape_function_derivatives(element_type, xi) * (2 / h)
            total += w * jacobian * integrand(x, n, dn)
        return total

    m_k = point_count(p_degree, 2 * (k - 1))
    K = quad_matrix(m_k, lambda x, n, dn: p(x) * np.outer(dn, dn))

    m_c = point_count(q_degree, 2 * k - 1)
    C = quad_matrix(m_c, lambda x, n, dn: q(x) * np.outer(n, dn))

    m_m = point_count(r_degree, 2 * k)
    M = quad_matrix(m_m, lambda x, n, dn: r(x) * np.outer(n, n))

    m_f = point_count(f_degree, k)
    rule_f = gauss_legendre(m_f)
    F = np.zeros(ndof)
    for xi, w in zip(rule_f.points, rule_f.weights, strict=True):
        x = to_physical(xi)
        n = shape_functions(element_type, xi)
        F += w * jacobian * f(x) * n

    return ElementMatrices(K=K, C=C, M=M, F=F, quadrature_approx=quadrature_approx)
