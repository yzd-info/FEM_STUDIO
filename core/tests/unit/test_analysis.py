"""M4.1-M4.3: error norms, convergence rates, diagnostics, sampling (MATH_SPEC §6-§8)."""

import math

import numpy as np
import pytest

from bench import benchmark, error_norms, fe_gauss_data, random_mms_problem, solve_fem
from fem1d.analysis import (
    basis_functions,
    coercivity_minimum,
    compute_errors,
    diagnose_run,
    estimate_convergence,
    fe_values,
    peclet_number,
    points_per_element,
    reference_basis,
    sample_fields,
    theoretical_rate,
)
from fem1d.elements import shape_function_derivatives, shape_functions
from fem1d.mesh import build_mesh


# ------------------------------------------------------------------------------- bases
@pytest.mark.parametrize("element", ["P1", "P2"])
def test_reference_basis_matches_package_elements(element) -> None:
    xi = np.linspace(-1, 1, 7)
    n, dn = reference_basis(element, xi)
    for j, x in enumerate(xi):
        np.testing.assert_allclose(n[:, j], shape_functions(element, float(x)), atol=1e-14)
        np.testing.assert_allclose(
            dn[:, j], shape_function_derivatives(element, float(x)), atol=1e-14
        )


@pytest.mark.parametrize("element", ["P1", "P2"])
def test_partition_of_unity_and_zero_derivative_sum(element) -> None:
    xi = np.random.default_rng(0).uniform(-1, 1, 20)
    n, dn = reference_basis(element, xi)
    np.testing.assert_allclose(n.sum(axis=0), 1.0, atol=1e-14)
    np.testing.assert_allclose(dn.sum(axis=0), 0.0, atol=1e-14)


@pytest.mark.parametrize("seed", range(20))
@pytest.mark.parametrize("element", ["P1", "P2"])
def test_interpolant_reproduces_polynomials_of_the_element_degree(seed, element) -> None:
    rng = np.random.default_rng(seed)
    degree = 1 if element == "P1" else 2
    coef = rng.uniform(-2, 2, degree + 1)
    a = rng.uniform(-3, 0)
    b = a + rng.uniform(0.5, 4)
    mesh = build_mesh((a, b), 1 + seed % 5, element)
    poly = np.polynomial.Polynomial(coef)
    x, uh, duh = fe_values(mesh, poly(mesh.nodes), np.linspace(-1, 1, 5))
    np.testing.assert_allclose(uh, poly(x), atol=1e-12)
    np.testing.assert_allclose(duh, poly.deriv()(x), atol=1e-11)


# -------------------------------------------------------------------------- error norms
def test_errors_of_the_zero_function_against_u_equals_x() -> None:
    mesh = build_mesh((0.0, 1.0), 4, "P1")
    e = compute_errors(mesh, np.zeros(5), lambda x: x, lambda x: 1.0 + 0 * x)
    assert e.l2 == pytest.approx(1 / math.sqrt(3), rel=1e-14)  # int x^2 = 1/3
    assert e.h1 == pytest.approx(1.0, rel=1e-14)  # int 1 = 1
    assert e.max_nodal == pytest.approx(1.0)
    assert e.l2_rel == pytest.approx(1.0)  # error equals u itself
    assert e.h1_rel == pytest.approx(1.0)


@pytest.mark.parametrize("n", [1, 2, 5, 17])
def test_p1_interpolation_error_of_x_squared_matches_closed_form(n) -> None:
    # Error on one element is (x-a)(x-b): int e^2 = h^5/30; e' = 2s with s = x - midpoint, so
    # int e'^2 = h^3/3 (hand derived).
    mesh = build_mesh((0.0, 1.0), n, "P1")
    h = 1 / n
    e = compute_errors(mesh, mesh.nodes**2, lambda x: x**2, lambda x: 2 * x)
    assert e.l2 == pytest.approx(math.sqrt(n * h**5 / 30), rel=1e-12)
    assert e.h1 == pytest.approx(math.sqrt(n * h**3 / 3), rel=1e-12)
    assert e.max_nodal < 1e-15


@pytest.mark.parametrize("n", [1, 3, 8])
def test_p2_interpolation_error_of_x_cubed_matches_closed_form(n) -> None:
    # Error s(s^2-(h/2)^2): int e^2 = h^7/840, int e'^2 = h^5/20 per element (hand derived).
    mesh = build_mesh((0.0, 1.0), n, "P2")
    h = 1 / n
    e = compute_errors(mesh, mesh.nodes**3, lambda x: x**3, lambda x: 3 * x**2)
    assert e.l2 == pytest.approx(math.sqrt(n * h**7 / 840), rel=1e-12)
    assert e.h1 == pytest.approx(math.sqrt(n * h**5 / 20), rel=1e-12)


def test_nodal_error_ignores_p2_midpoints_and_uses_vertices() -> None:
    mesh = build_mesh((0.0, 1.0), 2, "P2")
    U = mesh.nodes.copy()
    U[1] += 5.0  # a midpoint: must not count
    assert compute_errors(mesh, U, lambda x: x, lambda x: 1 + 0 * x).max_nodal == 0.0
    U[2] += 0.25  # a vertex
    assert compute_errors(mesh, U, lambda x: x, lambda x: 1 + 0 * x).max_nodal == pytest.approx(
        0.25
    )


def test_relative_errors_are_none_for_the_zero_solution() -> None:
    mesh = build_mesh((0.0, 1.0), 2, "P1")
    e = compute_errors(mesh, np.ones(3), lambda x: 0 * x, lambda x: 0 * x)
    assert e.l2_rel is None
    assert e.h1_rel is None
    assert e.l2 == pytest.approx(1.0)


@pytest.mark.parametrize("seed", range(30))
@pytest.mark.parametrize("element", ["P1", "P2"])
def test_errors_agree_with_independent_implementation_on_random_solutions(seed, element) -> None:
    problem = random_mms_problem(seed, 4)
    mesh, U = solve_fem(problem, 1 + seed % 9, element)
    ours = compute_errors(mesh, U, problem.u, problem.du)
    l2, h1, nodal = error_norms(mesh, U, problem.u, problem.du)
    assert (ours.l2, ours.h1, ours.max_nodal) == pytest.approx(
        (l2, h1, nodal), rel=1e-11, abs=1e-14
    )


# ---------------------------------------------------------------------------- convergence
def test_exact_power_law_gives_the_exact_rate() -> None:
    h = [0.5**k for k in range(1, 6)]
    c = estimate_convergence(h, [3.0 * x**2 for x in h], theory=2.0)
    assert c.rates == pytest.approx((2.0,) * 4)
    assert c.asymptotic is True
    assert c.machine_precision is False


def test_rates_use_the_actual_h_ratio_not_a_fixed_factor_two() -> None:
    h = [1 / 3, 1 / 9, 1 / 27]
    c = estimate_convergence(h, [h_**3 for h_ in h], theory=3.0)
    assert c.rates == pytest.approx((3.0, 3.0))


def test_asymptotic_flag_requires_last_two_rates_within_tenth() -> None:
    h = [0.5, 0.25, 0.125, 0.0625]
    errors = [1.0, 1.0 / 6.0, 1.0 / 6.0 / 4.0, 1.0 / 6.0 / 16.0]  # rates: 2.585, 2, 2
    assert estimate_convergence(h, errors, 2.0).asymptotic is True
    off = [1.0, 0.25, 0.25 / 4.5, 0.25 / 4.5 / 3.0]  # last rates 2.17 and 1.585
    assert estimate_convergence(h, off, 2.0).asymptotic is False


def test_single_pair_is_never_called_asymptotic() -> None:
    c = estimate_convergence([0.5, 0.25], [1.0, 0.25], 2.0)
    assert c.rates == pytest.approx((2.0,))
    assert c.asymptotic is False


def test_errors_below_floor_give_machine_precision_and_no_rates() -> None:
    c = estimate_convergence([0.5, 0.25, 0.125], [1e-15, 3e-14, 1e-14], 3.0)
    assert c.machine_precision is True
    assert c.rates == (None, None)
    assert c.asymptotic is False


def test_partially_floored_series_skips_only_the_affected_pairs() -> None:
    c = estimate_convergence([0.5, 0.25, 0.125, 0.0625], [1e-2, 1e-3, 1e-4, 1e-13], 3.0)
    assert c.machine_precision is False
    assert c.rates[0] is not None
    assert c.rates[2] is None


def test_convergence_input_validation() -> None:
    with pytest.raises(ValueError):
        estimate_convergence([0.5], [1.0], 2.0)
    with pytest.raises(ValueError):
        estimate_convergence([0.25, 0.5], [1.0, 2.0], 2.0)
    with pytest.raises(ValueError):
        estimate_convergence([0.5, 0.25], [1.0], 2.0)


def test_theoretical_rates() -> None:
    assert [theoretical_rate(n, "P1") for n in ("L2", "H1", "maxNodal")] == [2.0, 1.0, None]
    assert [theoretical_rate(n, "P2") for n in ("L2", "H1", "maxNodal")] == [3.0, 2.0, None]


# ---------------------------------------------------------------------------- diagnostics
def test_peclet_number_matches_the_documented_b5_values() -> None:
    b5 = benchmark("B5")
    assert peclet_number(b5.p, b5.q, b5.domain, 1 / 8) == pytest.approx(1.25)
    assert peclet_number(b5.p, b5.q, b5.domain, 1 / 16) == pytest.approx(0.625)
    assert peclet_number(b5.p, b5.q, b5.domain, 1 / 64) == pytest.approx(0.15625)


def test_peclet_uses_the_maximum_over_the_domain() -> None:
    value = peclet_number(lambda x: 1.0 + 0 * x, lambda x: 4 * x, (0.0, 1.0), 0.5)
    assert value == pytest.approx(1.0)  # max |q| = 4 at x = 1: 4 * 0.5 / 2


def test_coercivity_minimum_for_helmholtz_and_convection() -> None:
    b8 = benchmark("B8")
    assert coercivity_minimum(b8.q, b8.r, b8.domain) == pytest.approx(float(b8.r(0.3)), rel=1e-12)
    assert coercivity_minimum(b8.q, b8.r, b8.domain) < 0
    # r = 1, q = 4x  ->  r - q'/2 = 1 - 2 = -1, with the exact and the numerical derivative
    r, q = (lambda x: 1.0 + 0 * x), (lambda x: 4 * x)
    assert coercivity_minimum(q, r, (0.0, 1.0)) == pytest.approx(-1.0, abs=1e-6)
    assert coercivity_minimum(q, r, (0.0, 1.0), dq=lambda x: 4.0 + 0 * x) == pytest.approx(-1.0)


def _codes(**kw):
    base = {
        "n": 8,
        "h": 0.125,
        "peclet": 0.1,
        "coercivity_min": 1.0,
        "quadrature_approx": False,
        "condition_number": 10.0,
        "ill_conditioned": False,
        "errors": None,
    }
    return [d.code for d in diagnose_run(**{**base, **kw})]


def test_diagnostics_fire_exactly_on_their_conditions() -> None:
    assert _codes() == []
    assert _codes(peclet=1.25) == ["PECLET"]
    assert _codes(peclet=1.0) == []  # the condition is strictly greater than 1
    assert _codes(coercivity_min=-0.5) == ["NON_COERCIVE"]
    assert _codes(quadrature_approx=True) == ["QUADRATURE_APPROX"]
    assert _codes(ill_conditioned=True, condition_number=3e11) == ["ILL_CONDITIONED"]


def test_machine_precision_diagnostic_needs_all_three_errors_tiny() -> None:
    from fem1d.analysis import ErrorNorms

    tiny = ErrorNorms(1e-15, 1e-14, 1e-16, None, None)
    assert _codes(errors=tiny) == ["MACHINE_PRECISION"]
    not_tiny = ErrorNorms(1e-15, 1e-9, 1e-16, None, None)
    assert _codes(errors=not_tiny) == []


def test_diagnostic_payload_carries_n_and_pe() -> None:
    (d,) = diagnose_run(8, 0.125, 1.25, 1.0, False, 10.0, False, None)
    assert d.data == {"n": 8, "Pe": 1.25}


# ------------------------------------------------------------------------------ sampling
def test_points_per_element_and_the_cap() -> None:
    assert points_per_element(build_mesh((0, 1), 64, "P1")) == 2
    assert points_per_element(build_mesh((0, 1), 64, "P2")) == 9
    assert points_per_element(build_mesh((0, 1), 300, "P2")) == 5
    assert points_per_element(build_mesh((0, 1), 600, "P2")) == 3
    with pytest.raises(ValueError):
        points_per_element(build_mesh((0, 1), 700, "P2"))
    with pytest.raises(ValueError):
        points_per_element(build_mesh((0, 1), 1100, "P1"))


@pytest.mark.parametrize("element", ["P1", "P2"])
def test_sample_matches_independent_evaluation_and_error_definition(element) -> None:
    problem = benchmark("B2")
    mesh, U = solve_fem(problem, 8, element)
    s = sample_fields(mesh, U, problem.u)
    m = points_per_element(mesh)
    assert s.x.shape == (mesh.n * m,)
    assert s.x[0] == 0.0
    assert s.x[-1] == 1.0
    np.testing.assert_allclose(s.err, problem.u(s.x) - s.uh, atol=1e-15)
    # element end points coincide with the nodal values
    ends = np.ravel([[e * m, e * m + m - 1] for e in range(mesh.n)])
    np.testing.assert_allclose(s.uh[ends], U[mesh.connectivity[:, [0, -1]].ravel()], atol=1e-14)
    # an independent Gauss-data evaluation at the same element midpoints agrees
    xg, _, uh_g, duh_g = fe_gauss_data(mesh, U, m=1)
    mid = np.arange(mesh.n) * m + (m - 1) // 2 if m % 2 else None
    if mid is not None:
        np.testing.assert_allclose(s.uh[mid], uh_g, atol=1e-13)
        np.testing.assert_allclose(s.duh[mid], duh_g, atol=1e-12)


def test_p1_sample_keeps_the_derivative_jump_at_nodes() -> None:
    mesh = build_mesh((0.0, 1.0), 2, "P1")
    s = sample_fields(mesh, np.array([0.0, 1.0, 0.0]))
    assert s.x.tolist() == [0.0, 0.5, 0.5, 1.0]
    assert s.duh.tolist() == pytest.approx([2.0, 2.0, -2.0, -2.0])


def test_p2_sample_shows_curvature_inside_elements() -> None:
    mesh = build_mesh((0.0, 1.0), 1, "P2")
    s = sample_fields(mesh, np.array([0.0, 1.0, 0.0]), lambda x: 4 * x * (1 - x))
    assert len(s.x) == 9
    np.testing.assert_allclose(s.uh, 4 * s.x * (1 - s.x), atol=1e-14)  # exactly representable
    assert s.uh[4] == pytest.approx(1.0)  # the midpoint value


def test_sample_without_exact_solution_has_no_comparison_fields() -> None:
    mesh = build_mesh((0.0, 1.0), 2, "P1")
    s = sample_fields(mesh, np.zeros(3))
    assert s.u is None
    assert s.err is None


@pytest.mark.parametrize("element", ["P1", "P2"])
def test_basis_functions_for_visualisation(element) -> None:
    mesh = build_mesh((0.0, 2.0), 4, element)
    U = np.random.default_rng(3).uniform(-1, 1, len(mesh.nodes))
    x, phi, uh = basis_functions(mesh, U, per_element=11)
    assert phi.shape == (len(mesh.nodes), mesh.n * 11)
    np.testing.assert_allclose(phi.sum(axis=0), 1.0, atol=1e-14)  # partition of unity
    np.testing.assert_allclose(U @ phi, uh, atol=1e-14)  # u_h = sum U_i phi_i
    for i, xi in enumerate(mesh.nodes):  # phi_i(x_j) = delta_ij at the nodes
        hit = np.isclose(x, xi)
        assert hit.any()
        np.testing.assert_allclose(phi[i, hit], 1.0, atol=1e-14)
        others = np.delete(np.arange(len(mesh.nodes)), i)
        np.testing.assert_allclose(phi[np.ix_(others, np.where(hit)[0])], 0.0, atol=1e-14)
