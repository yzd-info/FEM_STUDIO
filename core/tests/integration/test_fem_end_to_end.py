"""M2 end-to-end: mesh -> assembly -> boundary conditions -> solve, against independent checks.

Independent means: exact fractions (fixtures), published reference numbers (BENCHMARKS §3),
scipy.solve_bvp (another algorithm), and error norms computed by tests/bench.py without the
package's own elements or quadrature.
"""

import numpy as np
import pytest

from bench import (
    CASES,
    REFERENCE,
    benchmark,
    error_norms,
    fe_gauss_data,
    observed_rates,
    random_mms_problem,
    scipy_reference,
    shifted,
    solve_fem,
)

ALL_BENCHMARKS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "M2", "M3", "M4"]


def _errors(name, element, ns):
    problem = benchmark(name)
    out = []
    for n in ns:
        mesh, U = solve_fem(problem, n, element)
        out.append(error_norms(mesh, U, problem.u, problem.du))
    return out


@pytest.mark.parametrize("name", sorted(REFERENCE))
def test_reference_error_table(name) -> None:
    problem = benchmark(name)
    for (element, n), expected in zip(CASES, REFERENCE[name], strict=True):
        mesh, U = solve_fem(problem, n, element)
        l2, h1, _ = error_norms(mesh, U, problem.u, problem.du)
        if expected is None:  # exact representation: below 1e-11 (H1 amplifies round-off by ~h^-1)
            assert l2 < 1e-11
            assert h1 < 1e-11
        else:
            assert l2 == pytest.approx(expected[0], rel=1e-2), (name, element, n)
            assert h1 == pytest.approx(expected[1], rel=1e-2), (name, element, n)


@pytest.mark.parametrize("name", ["B2", "B3", "B4", "B10", "M3", "M4"])
def test_theoretical_rates_for_smooth_problems(name) -> None:
    for element, l2_window, h1_window in (
        ("P1", (1.95, 2.05), (0.95, 1.05)),
        ("P2", (2.9, 3.1), (1.9, 2.1)),
    ):
        errs = _errors(name, element, (8, 16, 32, 64))
        l2 = observed_rates([e[0] for e in errs])
        h1 = observed_rates([e[1] for e in errs])
        assert all(l2_window[0] <= r <= l2_window[1] for r in l2), (name, element, l2)
        assert all(h1_window[0] <= r <= h1_window[1] for r in h1), (name, element, h1)


@pytest.mark.parametrize("name", ["B1", "B6", "B7", "M2"])
def test_p1_rates_and_p2_exactness_for_polynomial_solutions_of_degree_le_2(name) -> None:
    errs = _errors(name, "P1", (8, 16, 32, 64))
    assert all(1.95 <= r <= 2.05 for r in observed_rates([e[0] for e in errs]))
    assert all(0.95 <= r <= 1.05 for r in observed_rates([e[1] for e in errs]))
    for n in (2, 5, 16):
        l2, h1, nodal = _errors(name, "P2", (n,))[0]
        assert max(l2, h1, nodal) < 1e-11


def test_b9_p1_rates_and_p2_machine_precision() -> None:
    errs = _errors("B9", "P1", (8, 16, 32, 64))
    assert all(1.95 <= r <= 2.05 for r in observed_rates([e[0] for e in errs]))
    assert all(0.95 <= r <= 1.05 for r in observed_rates([e[1] for e in errs]))
    assert max(_errors("B9", "P2", (7,))[0]) < 1e-11


def test_b5_and_b8_asymptotic_windows() -> None:
    for name, p1_h1, p2_l2 in (("B5", (0.95, 1.05), (2.9, 3.1)), ("B8", (0.95, 1.1), (2.95, 3.15))):
        p1 = _errors(name, "P1", (64, 128, 256))
        p2 = _errors(name, "P2", (32, 64, 128, 256))
        assert all(1.95 <= r <= 2.05 for r in observed_rates([e[0] for e in p1])), name
        assert all(p1_h1[0] <= r <= p1_h1[1] for r in observed_rates([e[1] for e in p1])), name
        assert all(p2_l2[0] <= r <= p2_l2[1] for r in observed_rates([e[0] for e in p2])), name
        assert all(1.9 <= r <= 2.1 for r in observed_rates([e[1] for e in p2])), name


def test_b8_helmholtz_is_pre_asymptotic_for_coarse_p1() -> None:
    errs = _errors("B8", "P1", (8, 16))
    assert observed_rates([e[0] for e in errs])[0] > 4.0  # documented: about 6, not 2


def test_b5_central_discretisation_oscillates_for_large_peclet_number() -> None:
    problem = benchmark("B5")
    minima = {n: float(np.min(solve_fem(problem, n, "P1")[1])) for n in (8, 16, 64)}
    assert minima[8] == pytest.approx(-0.111, abs=2e-3)
    assert minima[16] >= -1e-12
    assert minima[64] >= -1e-12


@pytest.mark.parametrize("name", ["B1", "B2", "B6", "B7", "M2", "M3", "M4"])
@pytest.mark.parametrize("element", ["P1", "P2"])
def test_nodal_superconvergence_when_p_constant_and_q_r_zero(name, element) -> None:
    for n in (4, 9, 16):
        assert _errors(name, element, (n,))[0][2] < 1e-12, (name, element, n)


@pytest.mark.parametrize("name", ["B3", "B4", "B10"])
def test_nodal_values_are_not_exact_when_assumptions_fail(name) -> None:
    # Negative control: the test above would be meaningless if it passed for everything.
    assert _errors(name, "P1", (8,))[0][2] > 1e-6
    assert _errors(name, "P2", (4,))[0][2] > 1e-9


@pytest.mark.parametrize("name", ALL_BENCHMARKS)
@pytest.mark.parametrize("element", ["P1", "P2"])
def test_fem_agrees_with_independent_bvp_solver(name, element) -> None:
    """FEM at n=256 vs scipy.solve_bvp: the distance must equal the FEM error already known."""
    problem = benchmark(name)
    mesh, U = solve_fem(problem, 256, element)
    x, _, uh, _ = fe_gauss_data(mesh, U)
    ref = scipy_reference(problem, x)
    exact = problem.u(x)
    assert np.max(np.abs(ref - exact)) < 5e-11  # the oracle itself is right
    assert np.max(np.abs(uh - ref)) <= np.max(np.abs(uh - exact)) + 5e-11


@pytest.mark.parametrize("seed", range(30))
def test_random_smooth_coefficients_against_scipy_oracle_without_exact_solution(seed) -> None:
    """No manufactured solution involved: sin/exp coefficients, mixed boundary conditions."""
    rng = np.random.default_rng(5000 + seed)
    a1, a2, a3, a4 = rng.uniform(0.2, 1.0, 4)
    base = random_mms_problem(seed, 2)
    problem = base.__class__(
        f"smooth-{seed}",
        (0.0, 1.0),
        lambda x: 2.0 + a1 * np.sin(3 * x),
        lambda x: a2 * np.cos(2 * x),
        lambda x: 0.5 + a3 * x**2,
        lambda x: np.exp(a4 * x) * np.cos(4 * x),
        (None, None, None, None),
        base.left,
        base.right,
    )
    mesh, U = solve_fem(problem, 512, "P2")
    x, _, uh, _ = fe_gauss_data(mesh, U)
    assert np.max(np.abs(uh - scipy_reference(problem, x))) < 5e-8


@pytest.mark.parametrize("element", ["P1", "P2"])
@pytest.mark.parametrize("seed", range(60))
def test_random_polynomial_mms_is_exact_when_solution_lies_in_the_space(seed, element) -> None:
    """Patch test: u in P1 (resp. P2) is reproduced to round-off for ANY coefficients/BCs."""
    degree = 1 if element == "P1" else 2
    problem = random_mms_problem(seed, degree)
    for n in (1, 3, 8):
        mesh, U = solve_fem(problem, n, element)
        l2, h1, _ = error_norms(mesh, U, problem.u, problem.du)
        assert max(l2, h1) < 1e-10, (seed, n, l2, h1)


@pytest.mark.parametrize("element", ["P1", "P2"])
@pytest.mark.parametrize("seed", range(20))
def test_random_polynomial_mms_converges_at_theoretical_rate(seed, element) -> None:
    degree = 3 if element == "P1" else 4
    problem = random_mms_problem(100 + seed, degree)
    errs = [
        error_norms(*solve_fem(problem, n, element), problem.u, problem.du) for n in (16, 32, 64)
    ]
    l2 = observed_rates([e[0] for e in errs])
    h1 = observed_rates([e[1] for e in errs])
    k = 1 if element == "P1" else 2
    # Windows are theory +/- 0.3: random coefficients make constants differ, rates must not.
    assert all(k + 1 - 0.3 <= r <= k + 1 + 0.3 for r in l2), (seed, l2)
    assert all(k - 0.3 <= r <= k + 0.3 for r in h1), (seed, h1)


@pytest.mark.parametrize("element", ["P1", "P2"])
def test_translation_invariance_of_the_discretisation(element) -> None:
    """B1 (-u''=1 with u=0 at both ends) on [2,5] has u=(x-2)(5-x)/2; M3-like shift too."""
    base = benchmark("B1")
    problem = shifted(base, (2.0, 5.0), lambda x: (x - 2) * (5 - x) / 2, lambda x: (7 - 2 * x) / 2)
    problem = problem.__class__(
        **{
            **problem.__dict__,
            "left": base.left.__class__(0.0, 1.0, 0.0),
            "right": base.right.__class__(0.0, 1.0, 0.0),
        }
    )
    for n in (3, 10):
        mesh, U = solve_fem(problem, n, element)
        l2, h1, nodal = error_norms(mesh, U, problem.u, problem.du)
        assert nodal < 1e-12
        if element == "P2":
            assert max(l2, h1) < 1e-11
