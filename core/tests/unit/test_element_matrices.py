"""M2.2: element matrices by quadrature, constant-coefficient case
(docs/MATH_SPEC.md §5.1-5.2)."""

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from fem1d.element_matrices import element_matrices

_COEFF = st.floats(min_value=-5, max_value=5, allow_nan=False, allow_infinity=False)
_H = st.floats(min_value=0.01, max_value=10, allow_nan=False, allow_infinity=False)


def _const(value):
    return lambda x: np.full_like(np.asarray(x, dtype=float), value)


@given(p=_COEFF, q=_COEFF, r=_COEFF, f=_COEFF, h=_H)
def test_p1_constant_coefficients_match_spec_closed_form(p, q, r, f, h) -> None:
    result = element_matrices(
        "P1", (0.0, h), _const(p), 0, _const(q), 0, _const(r), 0, _const(f), 0
    )
    expected_K = (p / h) * np.array([[1, -1], [-1, 1]])
    expected_C = (q / 2) * np.array([[-1, 1], [-1, 1]])
    expected_M = (r * h / 6) * np.array([[2, 1], [1, 2]])
    expected_F = (f * h / 2) * np.array([1, 1])
    assert np.allclose(result.K, expected_K, atol=1e-10)
    assert np.allclose(result.C, expected_C, atol=1e-10)
    assert np.allclose(result.M, expected_M, atol=1e-10)
    assert np.allclose(result.F, expected_F, atol=1e-10)
    assert result.quadrature_approx is False


@given(p=_COEFF, q=_COEFF, r=_COEFF, f=_COEFF, h=_H)
def test_p2_constant_coefficients_match_spec_closed_form(p, q, r, f, h) -> None:
    result = element_matrices(
        "P2", (0.0, h), _const(p), 0, _const(q), 0, _const(r), 0, _const(f), 0
    )
    expected_K = (p / (3 * h)) * np.array([[7, -8, 1], [-8, 16, -8], [1, -8, 7]])
    expected_C = (q / 6) * np.array([[-3, 4, -1], [-4, 0, 4], [1, -4, 3]])
    expected_M = (r * h / 30) * np.array([[4, 2, -1], [2, 16, 2], [-1, 2, 4]])
    expected_F = (f * h / 6) * np.array([1, 4, 1])
    assert np.allclose(result.K, expected_K, atol=1e-10)
    assert np.allclose(result.C, expected_C, atol=1e-10)
    assert np.allclose(result.M, expected_M, atol=1e-10)
    assert np.allclose(result.F, expected_F, atol=1e-10)
    assert result.quadrature_approx is False


@pytest.mark.parametrize("element_type", ["P1", "P2"])
@given(p=_COEFF, q=_COEFF, r=_COEFF, f=_COEFF, h=_H)
def test_row_sum_and_total_properties(element_type, p, q, r, f, h) -> None:
    result = element_matrices(
        element_type, (0.0, h), _const(p), 0, _const(q), 0, _const(r), 0, _const(f), 0
    )
    assert np.allclose(result.K.sum(axis=1), 0.0, atol=1e-10)
    assert np.allclose(result.C.sum(axis=1), 0.0, atol=1e-10)
    assert result.M.sum() == pytest.approx(r * h, abs=1e-10)
    assert result.F.sum() == pytest.approx(f * h, abs=1e-10)
    assert np.allclose(result.K, result.K.T, atol=1e-10)
    assert np.allclose(result.M, result.M.T, atol=1e-10)


def test_non_polynomial_coefficient_falls_back_to_quadrature_approx() -> None:
    result = element_matrices(
        "P1",
        (0.0, 1.0),
        lambda x: np.exp(np.asarray(x, dtype=float)),
        None,
        _const(0.0),
        0,
        _const(0.0),
        0,
        _const(1.0),
        0,
    )
    assert result.quadrature_approx is True
