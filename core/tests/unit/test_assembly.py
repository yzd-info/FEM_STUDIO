"""M2.4: global assembly with assembly log (docs/MATH_SPEC.md §3, §5)."""

import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
from numpy.polynomial import Polynomial

from bench import benchmark, fe_gauss_data, random_mms_problem
from fem1d.assembly import assemble
from fem1d.mesh import build_mesh

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _assemble(problem, n, element, record_log=True):
    mesh = build_mesh(problem.domain, n, element)
    pd, qd, rd, fd = problem.degrees
    return assemble(
        mesh, problem.p, pd, problem.q, qd, problem.r, rd, problem.f, fd, record_log=record_log
    )


@pytest.mark.parametrize(
    ("fixture_id", "problem"),
    [("B1_P1_n2", "B1"), ("B1_P1_n4", "B1"), ("B3_P1_n2", "B3")],
)
def test_assembled_system_equals_hand_computed_fixture(fixture_id, problem) -> None:
    data = json.loads((FIXTURES / f"{fixture_id}.json").read_text())
    system = _assemble(benchmark(problem), data["n"], data["element"])
    expected_K = np.array([[float(Fraction(v)) for v in row] for row in data["K"]])
    expected_F = np.array([float(Fraction(v)) for v in data["F"]])
    np.testing.assert_allclose(system.K, expected_K, rtol=0, atol=1e-13)
    np.testing.assert_allclose(system.F, expected_F, rtol=0, atol=1e-13)


def test_p2_shared_vertex_collects_two_elements_and_midpoint_only_one() -> None:
    # B1, P2, n=2, h=1/2: K^e = 1/(3h) [[7,-8,1],[-8,16,-8],[1,-8,7]] = (2/3) [...]
    system = _assemble(benchmark("B1"), 2, "P2")
    assert system.K[2, 2] == pytest.approx(2 * 7 * 2 / 3)  # vertex shared by both elements
    assert system.K[1, 1] == pytest.approx(16 * 2 / 3)  # midpoint belongs to one element
    assert len(system.contributions_to(2, 2)) == 2
    assert len(system.contributions_to(1, 1)) == 1


def test_log_shows_k11_as_sum_of_two_element_entries() -> None:
    # K_11 = K^(0)_22 + K^(1)_11 for B1, P1, n = 2 (both equal 2).
    system = _assemble(benchmark("B1"), 2, "P1")
    parts = system.contributions_to(1, 1)
    assert [(c.element, c.local_row, c.local_col) for c in parts] == [(0, 1, 1), (1, 0, 0)]
    assert sum(c.value for c in parts) == pytest.approx(4.0)


@pytest.mark.parametrize("element", ["P1", "P2"])
@pytest.mark.parametrize("seed", range(20))
def test_log_is_complete_and_consistent_with_matrix(seed, element) -> None:
    problem = random_mms_problem(seed, 3)
    n = 1 + seed % 6
    system = _assemble(problem, n, element)
    ndof = 2 if element == "P1" else 3
    assert len(system.log) == n * ndof * ndof
    rebuilt = np.zeros_like(system.K)
    buckets: dict[tuple[int, int], list[float]] = {}
    for c in system.log:
        dofs = system.mesh.connectivity[c.element]
        assert c.global_row == dofs[c.local_row]
        assert c.global_col == dofs[c.local_col]
        em = system.per_element[c.element]
        assert c.value == pytest.approx((em.K + em.C + em.M)[c.local_row, c.local_col], abs=1e-15)
        buckets.setdefault((c.global_row, c.global_col), []).append(c.value)
    for (i, j), values in buckets.items():
        rebuilt[i, j] = math.fsum(values)
    np.testing.assert_allclose(rebuilt, system.K, rtol=0, atol=1e-13)


def test_record_log_false_skips_the_log_but_not_the_matrix() -> None:
    with_log = _assemble(benchmark("B4"), 5, "P2", record_log=True)
    without = _assemble(benchmark("B4"), 5, "P2", record_log=False)
    assert without.log == ()
    np.testing.assert_array_equal(with_log.K, without.K)


@pytest.mark.parametrize("element", ["P1", "P2"])
@pytest.mark.parametrize("seed", range(25))
def test_diffusion_convection_rows_sum_to_zero_when_r_is_zero(seed, element) -> None:
    # A constant has zero derivative, so K 1 = M 1 only; with r = 0 the rows sum to 0.
    problem = random_mms_problem(seed, 3)
    problem = problem.__class__(
        **{
            **problem.__dict__,
            "r": lambda x: 0.0 * x,
            "degrees": (problem.degrees[0], problem.degrees[1], 0, problem.degrees[3]),
        }
    )
    system = _assemble(problem, 4, element)
    np.testing.assert_allclose(system.K @ np.ones(len(system.K)), 0.0, atol=1e-12)


@pytest.mark.parametrize("element", ["P1", "P2"])
def test_symmetric_without_convection_and_not_symmetric_with_it(element) -> None:
    symmetric = _assemble(benchmark("B4"), 6, element).K  # q = 0
    np.testing.assert_allclose(symmetric, symmetric.T, rtol=0, atol=1e-13)
    nonsymmetric = _assemble(benchmark("B5"), 6, element).K  # q = 1
    assert np.max(np.abs(nonsymmetric - nonsymmetric.T)) > 1e-3


@pytest.mark.parametrize("element", ["P1", "P2"])
@pytest.mark.parametrize("seed", range(30))
def test_load_vector_integrates_the_source(seed, element) -> None:
    # sum_i F_i = integral of f, because the shape functions sum to 1 (exact polynomial algebra).
    problem = random_mms_problem(seed, 4)
    system = _assemble(problem, 1 + seed % 7, element)
    antiderivative = problem.f.integ()
    exact = float(antiderivative(1.0) - antiderivative(0.0))
    assert system.F.sum() == pytest.approx(exact, rel=1e-12, abs=1e-12)


@pytest.mark.parametrize("element", ["P1", "P2"])
@pytest.mark.parametrize("seed", range(40))
def test_bilinear_form_matches_independent_quadrature(seed, element) -> None:
    """v^T K u = B(u_h, v_h) and v^T F = (f, v_h), evaluated without the package's elements.

    This is the defining property of the Galerkin matrix (MATH_SPEC §3): K_ij = B(phi_j, phi_i).
    """
    rng = np.random.default_rng(1000 + seed)
    problem = random_mms_problem(seed, 3)
    n = 1 + seed % 5
    system = _assemble(problem, n, element)
    u = rng.uniform(-1, 1, len(system.K))
    v = rng.uniform(-1, 1, len(system.K))
    x, w, uh, duh = fe_gauss_data(system.mesh, u, m=12)
    _, _, vh, dvh = fe_gauss_data(system.mesh, v, m=12)
    p, q, r, f = (np.asarray(fn(x)) for fn in (problem.p, problem.q, problem.r, problem.f))
    bilinear = float(np.sum(w * (p * duh * dvh + q * duh * vh + r * uh * vh)))
    load = float(np.sum(w * f * vh))
    scale = max(1.0, abs(bilinear), abs(load))
    assert v @ system.K @ u == pytest.approx(bilinear, abs=1e-11 * scale)
    assert v @ system.F == pytest.approx(load, abs=1e-11 * scale)


def test_non_polynomial_coefficients_flag_quadrature_approximation() -> None:
    assert _assemble(benchmark("B2"), 3, "P1").quadrature_approx is True  # f = pi^2 sin(pi x)
    assert _assemble(benchmark("B4"), 3, "P1").quadrature_approx is False  # polynomial data


def test_polynomial_helper_is_really_polynomial() -> None:
    # guards the test-support assumption used above: degrees reported to the quadrature rule
    problem = random_mms_problem(3, 5)
    assert isinstance(problem.f, Polynomial)
    assert problem.degrees[3] == problem.f.degree()
