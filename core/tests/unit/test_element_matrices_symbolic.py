"""M2.3: exact element matrices via SymPy `integrate` (docs/MATH_SPEC.md §5.2.1)."""

import sympy as sp
from hypothesis import given, settings
from hypothesis import strategies as st

from fem1d.element_matrices import element_matrices, element_matrices_symbolic

_X = sp.Symbol("x")
_RATIONAL = st.fractions(min_value=-5, max_value=5, max_denominator=6)


def test_b3_element1_matches_fixture_closed_form() -> None:
    # docs/BENCHMARKS.md B3: p=1+x, q=0, r=0, f=1 on [0, 1], n=2 -> h=0.5.
    # core/tests/fixtures/B3_P1_n2.json gives K^(1)_11 = 5/2, F^(1)_1 = 1/4.
    result = element_matrices_symbolic(
        "P1",
        (sp.Integer(0), sp.Rational(1, 2)),
        1 + _X,
        sp.Integer(0),
        sp.Integer(0),
        sp.Integer(1),
    )
    assert result.K[0, 0] == sp.Rational(5, 2)
    assert result.F[0] == sp.Rational(1, 4)
    assert result.exact is True


@settings(deadline=None, max_examples=20)  # symbolic sp.integrate per entry is slow, not flaky
@given(p=_RATIONAL, q=_RATIONAL, r=_RATIONAL, f=_RATIONAL)
def test_symbolic_matches_numeric_for_constant_coefficients(p, q, r, f) -> None:
    p_e, q_e, r_e, f_e = sp.Rational(p), sp.Rational(q), sp.Rational(r), sp.Rational(f)
    symbolic = element_matrices_symbolic(
        "P2", (sp.Integer(0), sp.Rational(1, 3)), p_e, q_e, r_e, f_e
    )
    numeric = element_matrices(
        "P2",
        (0.0, 1 / 3),
        lambda x: float(p),
        0,
        lambda x: float(q),
        0,
        lambda x: float(r),
        0,
        lambda x: float(f),
        0,
    )
    assert symbolic.exact is True

    def relative_close(sym_matrix, num_matrix) -> bool:
        sym_arr = sym_matrix if hasattr(sym_matrix, "tolist") else sym_matrix
        import numpy as np

        sym_np = np.array([[float(v) for v in row] for row in sym_arr.tolist()])
        return bool(np.allclose(sym_np, num_matrix, rtol=1e-12, atol=1e-12))

    assert relative_close(symbolic.K, numeric.K)
    assert relative_close(symbolic.C, numeric.C)
    assert relative_close(symbolic.M, numeric.M)


def test_undefined_integrand_is_not_exact() -> None:
    g = sp.Function("g")(_X)
    result = element_matrices_symbolic(
        "P1", (sp.Integer(0), sp.Integer(1)), sp.Integer(1), sp.Integer(0), sp.Integer(0), g
    )
    assert result.exact is False
