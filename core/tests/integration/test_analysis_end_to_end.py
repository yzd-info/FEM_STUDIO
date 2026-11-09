"""M4 end-to-end: package error analysis on the benchmarks (BENCHMARKS §3.1-§3.4)."""

import numpy as np
import pytest

from bench import CASES, REFERENCE, benchmark, singular_s1, solve_fem
from fem1d.analysis import (
    coercivity_minimum,
    compute_errors,
    diagnose_run,
    estimate_convergence,
    peclet_number,
    theoretical_rate,
)
from fem1d.assembly import assemble
from fem1d.mesh import build_mesh


def _series(problem, element, ns):
    errs = []
    for n in ns:
        mesh, U = solve_fem(problem, n, element)
        errs.append(compute_errors(mesh, U, problem.u, problem.du))
    return [1.0 / n for n in ns], errs


@pytest.mark.parametrize("name", sorted(REFERENCE))
def test_package_errors_reproduce_reference_table(name) -> None:
    problem = benchmark(name)
    for (element, n), expected in zip(CASES, REFERENCE[name], strict=True):
        mesh, U = solve_fem(problem, n, element)
        e = compute_errors(mesh, U, problem.u, problem.du)
        if expected is None:
            assert max(e.l2, e.h1) < 1e-11
        else:
            assert e.l2 == pytest.approx(expected[0], rel=1e-2)
            assert e.h1 == pytest.approx(expected[1], rel=1e-2)


@pytest.mark.parametrize("name", ["B2", "B3", "B4", "B10", "M3", "M4"])
@pytest.mark.parametrize("element", ["P1", "P2"])
def test_smooth_problems_are_flagged_asymptotic_with_theoretical_rates(name, element) -> None:
    h, errs = _series(benchmark(name), element, (8, 16, 32, 64))
    for norm, pick in (("L2", lambda e: e.l2), ("H1", lambda e: e.h1)):
        c = estimate_convergence(h, [pick(e) for e in errs], theoretical_rate(norm, element))
        assert c.asymptotic is True, (name, element, norm, c.rates)
        assert c.machine_precision is False


@pytest.mark.parametrize("name", ["B1", "B6", "B7", "M2", "B9"])
def test_exact_representation_in_p2_is_reported_as_machine_precision(name) -> None:
    h, errs = _series(benchmark(name), "P2", (4, 8, 16, 32))
    c = estimate_convergence(h, [max(e.l2, e.h1, e.max_nodal) for e in errs], 3.0, floor=1e-11)
    assert c.machine_precision is True
    assert c.asymptotic is False


def test_singular_solution_rates_do_not_improve_with_p2() -> None:
    """S1 (BENCHMARKS §3.2): L2 ~ 1.25, H1 ~ 0.25 for P1 AND P2; theory is not reached."""
    problem = singular_s1()
    for element, l2_window in (("P1", (1.15, 1.35)), ("P2", (1.1, 1.35))):
        ns = (16, 32, 64, 128, 256) if element == "P1" else (16, 32, 64, 128)
        h, errs = _series(problem, element, ns)
        c_l2 = estimate_convergence(h, [e.l2 for e in errs], theoretical_rate("L2", element))
        c_h1 = estimate_convergence(h, [e.h1 for e in errs], theoretical_rate("H1", element))
        assert all(l2_window[0] <= r <= l2_window[1] for r in c_l2.rates if r), c_l2.rates
        assert all(0.2 <= r <= 0.3 for r in c_h1.rates if r), c_h1.rates
        assert c_l2.asymptotic is False  # the flag compares with the SMOOTH theory
        assert c_h1.asymptotic is False


def test_singular_solution_nodal_values_are_not_exact_with_numerical_quadrature() -> None:
    h, errs = _series(singular_s1(), "P1", (16, 32))
    assert all(e.max_nodal > 1e-6 for e in errs)  # §3.3: quadrature error spoils nodal exactness


def _diagnostics(name, n, element="P1"):
    problem = benchmark(name)
    mesh = build_mesh(problem.domain, n, element)
    pd, qd, rd, fd = problem.degrees
    system = assemble(mesh, problem.p, pd, problem.q, qd, problem.r, rd, problem.f, fd)
    pe = peclet_number(problem.p, problem.q, problem.domain, 1.0 / n)
    cmin = coercivity_minimum(problem.q, problem.r, problem.domain)
    return {
        d.code: d
        for d in diagnose_run(n, 1.0 / n, pe, cmin, system.quadrature_approx, 10.0, False, None)
    }


def test_b5_peclet_warning_only_while_the_mesh_is_too_coarse() -> None:
    assert "PECLET" in _diagnostics("B5", 8)
    assert _diagnostics("B5", 8)["PECLET"].data["Pe"] == pytest.approx(1.25)
    assert "PECLET" not in _diagnostics("B5", 16)
    # and the warning is justified by the solution: oscillation with negative values at n = 8
    assert float(np.min(solve_fem(benchmark("B5"), 8, "P1")[1])) < -0.1


def test_helmholtz_b8_is_non_coercive_and_polynomial_problems_have_no_quadrature_warning() -> None:
    assert "NON_COERCIVE" in _diagnostics("B8", 16)
    assert "QUADRATURE_APPROX" in _diagnostics("B2", 8)  # f = pi^2 sin(pi x)
    assert "QUADRATURE_APPROX" not in _diagnostics("B4", 8)
    assert _diagnostics("B3", 8) == {}
