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
import sympy as sp
from numpy.typing import NDArray

from fem1d.elements import (
    local_nodes,
    shape_function_derivatives,
    shape_functions,
    shape_functions_symbolic,
)
from fem1d.mesh import ElementType
from fem1d.quadrature import gauss_legendre

Coefficient = Callable[[float], float]

_FALLBACK_POINTS: dict[ElementType, int] = {"P1": 8, "P2": 10}

_X = sp.Symbol("x")
_XI = sp.Symbol("xi")


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


@dataclass(frozen=True)
class ElementMatricesSymbolic:
    """Exact K, C, M element matrices and F load vector (docs/MATH_SPEC.md §5.2.1)."""

    K: sp.Matrix
    C: sp.Matrix
    M: sp.Matrix
    F: sp.Matrix
    exact: bool


def _integrate_bounded(integrand: sp.Expr, a: sp.Expr, b: sp.Expr) -> tuple[sp.Expr, bool]:
    result = sp.integrate(integrand, (_X, a, b))
    return result, not result.has(sp.Integral)


def _symbolic_shape_functions(
    element_type: ElementType, a: sp.Expr, b: sp.Expr
) -> tuple[list[sp.Expr], list[sp.Expr]]:
    h = b - a
    xi_of_x = 2 * (_X - a) / h - 1
    n_x = [expr.subs(_XI, xi_of_x) for expr in shape_functions_symbolic(element_type)]
    dn_x = [sp.diff(n, _X) for n in n_x]
    return n_x, dn_x


def element_matrices_symbolic(
    element_type: ElementType,
    interval: tuple[sp.Expr, sp.Expr],
    p: sp.Expr,
    q: sp.Expr,
    r: sp.Expr,
    f: sp.Expr,
) -> ElementMatricesSymbolic:
    """Exact element matrices via SymPy ``integrate`` (docs/MATH_SPEC.md §5.2.1).

    ``exact`` is False for any entry where SymPy could not reach a closed form
    (the result still contains an unevaluated ``Integral``); the caller should
    then fall back to :func:`element_matrices` (numeric quadrature).
    """
    a, b = interval
    ndof = len(local_nodes(element_type))
    n_x, dn_x = _symbolic_shape_functions(element_type, a, b)

    K = sp.zeros(ndof, ndof)
    C = sp.zeros(ndof, ndof)
    M = sp.zeros(ndof, ndof)
    F = sp.zeros(ndof, 1)
    exact = True

    for i in range(ndof):
        for j in range(i, ndof):  # K, M symmetric in (i, j); compute once, mirror
            k_val, k_exact = _integrate_bounded(p * dn_x[i] * dn_x[j], a, b)
            K[i, j] = K[j, i] = k_val
            exact = exact and k_exact

            m_val, m_exact = _integrate_bounded(r * n_x[i] * n_x[j], a, b)
            M[i, j] = M[j, i] = m_val
            exact = exact and m_exact

        for j in range(ndof):
            c_val, c_exact = _integrate_bounded(q * n_x[i] * dn_x[j], a, b)
            C[i, j] = c_val
            exact = exact and c_exact

        f_val, f_exact = _integrate_bounded(f * n_x[i], a, b)
        F[i, 0] = f_val
        exact = exact and f_exact

    return ElementMatricesSymbolic(K=K, C=C, M=M, F=F, exact=exact)
