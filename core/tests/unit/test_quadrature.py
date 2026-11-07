"""M1.1: m-point Gauss-Legendre rule is exact up to degree 2m-1, and
generically inexact at degree 2m (docs/MATH_SPEC.md §5.2)."""

import numpy as np
from hypothesis import given
from hypothesis import strategies as st

from fem1d.quadrature import gauss_legendre, integrate


def _poly_integral_exact(coeffs: list[float], interval: tuple[float, float]) -> float:
    """Analytic integral of sum(c_k * x^k) over [x0, x1]."""
    x0, x1 = interval
    total = 0.0
    for k, c in enumerate(coeffs):
        total += c * (x1 ** (k + 1) - x0 ** (k + 1)) / (k + 1)
    return total


@given(
    m=st.integers(min_value=1, max_value=6),
    interval=st.tuples(
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
    ).filter(lambda ab: ab[1] - ab[0] > 1e-6),
    coeffs=st.data(),
)
def test_m_point_rule_is_exact_up_to_degree_2m_minus_1(m, interval, coeffs) -> None:
    degree = 2 * m - 1
    poly_coeffs = coeffs.draw(
        st.lists(
            st.floats(min_value=-5, max_value=5, allow_nan=False, allow_infinity=False),
            min_size=degree + 1,
            max_size=degree + 1,
        )
    )
    rule = gauss_legendre(m)
    approx = integrate(
        lambda x, c=poly_coeffs: sum(c[k] * x**k for k in range(len(c))),
        rule,
        interval,
    )
    exact = _poly_integral_exact(poly_coeffs, interval)
    assert abs(approx - exact) < 1e-9 * max(1.0, abs(exact))


def test_m_point_rule_is_not_exact_for_monomial_of_degree_2m() -> None:
    interval = (-1.0, 1.0)
    for m in range(1, 7):
        degree = 2 * m
        rule = gauss_legendre(m)
        approx = integrate(lambda x, d=degree: x**d, rule, interval)
        exact = _poly_integral_exact([0.0] * degree + [1.0], interval)
        assert abs(approx - exact) > 1e-6, f"m={m} unexpectedly exact for degree {degree}"


def test_gauss_legendre_rejects_non_positive_point_count() -> None:
    import pytest

    with pytest.raises(ValueError):
        gauss_legendre(0)


def test_gauss_legendre_point_count_matches_m() -> None:
    for m in range(1, 8):
        rule = gauss_legendre(m)
        assert len(rule.points) == m
        assert len(rule.weights) == m
        assert np.all(rule.points >= -1.0) and np.all(rule.points <= 1.0)
