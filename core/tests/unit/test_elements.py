"""M1.3: P1/P2 reference shape functions, numeric and symbolic (docs/MATH_SPEC.md §4.1-4.2)."""

import numpy as np
import pytest
import sympy as sp
from hypothesis import given
from hypothesis import strategies as st

from fem1d.elements import (
    local_nodes,
    shape_function_derivatives,
    shape_functions,
    shape_functions_symbolic,
)


@pytest.mark.parametrize("element_type", ["P1", "P2"])
@given(xi=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_shape_functions_partition_of_unity(element_type, xi) -> None:
    n = shape_functions(element_type, xi)
    assert np.sum(n) == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("element_type", ["P1", "P2"])
@given(xi=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_shape_function_derivatives_sum_to_zero(element_type, xi) -> None:
    dn = shape_function_derivatives(element_type, xi)
    assert np.sum(dn) == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize("element_type", ["P1", "P2"])
def test_shape_functions_are_kronecker_delta_at_nodes(element_type) -> None:
    nodes = local_nodes(element_type)
    m = len(nodes)
    for i, xi_i in enumerate(nodes):
        n = shape_functions(element_type, xi_i)
        expected = np.zeros(m)
        expected[i] = 1.0
        assert np.allclose(n, expected, atol=1e-12)


def test_local_nodes_values() -> None:
    assert np.allclose(local_nodes("P1"), [-1.0, 1.0])
    assert np.allclose(local_nodes("P2"), [-1.0, 0.0, 1.0])


@pytest.mark.parametrize("element_type", ["P1", "P2"])
@given(xi=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_symbolic_matches_numeric(element_type, xi) -> None:
    sym_exprs = shape_functions_symbolic(element_type)
    xi_sym = sp.Symbol("xi")
    sym_values = np.array([float(expr.subs(xi_sym, xi)) for expr in sym_exprs])
    numeric_values = shape_functions(element_type, xi)
    assert np.allclose(sym_values, numeric_values, atol=1e-12)


def test_symbolic_derivatives_match_numeric_derivatives() -> None:
    xi_sym = sp.Symbol("xi")
    for element_type in ("P1", "P2"):
        sym_exprs = shape_functions_symbolic(element_type)
        sym_derivs = [sp.diff(expr, xi_sym) for expr in sym_exprs]
        for xi in (-1.0, -0.3, 0.0, 0.7, 1.0):
            expected = np.array([float(d.subs(xi_sym, xi)) for d in sym_derivs])
            actual = shape_function_derivatives(element_type, xi)
            assert np.allclose(expected, actual, atol=1e-12)
