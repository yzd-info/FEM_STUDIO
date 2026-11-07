"""Gauss-Legendre quadrature on the reference interval [-1, 1].

See docs/MATH_SPEC.md §4 and §5.2: an m-point rule integrates polynomials
up to degree 2m-1 exactly.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.polynomial.legendre import leggauss
from numpy.typing import NDArray


@dataclass(frozen=True)
class QuadratureRule:
    """An m-point Gauss-Legendre rule on the reference interval [-1, 1]."""

    points: NDArray[np.float64]
    weights: NDArray[np.float64]


def gauss_legendre(m: int) -> QuadratureRule:
    """Build the m-point Gauss-Legendre rule on [-1, 1]."""
    if m < 1:
        raise ValueError(f"m must be >= 1, got {m}")
    points, weights = leggauss(m)
    return QuadratureRule(points=points, weights=weights)


def integrate(
    f: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    rule: QuadratureRule,
    interval: tuple[float, float],
) -> float:
    """Integrate f over [x0, x1] by mapping `rule` from [-1, 1] via the Jacobian h/2."""
    x0, x1 = interval
    jacobian = (x1 - x0) / 2
    x = (x0 + x1) / 2 + jacobian * rule.points
    return float(np.sum(rule.weights * f(x)) * jacobian)
