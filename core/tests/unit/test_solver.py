"""M2.6: linear solvers including the Thomas algorithm (docs/LATEX_STYLE.md step 10)."""

import numpy as np
import pytest

from bench import benchmark, solve_fem
from fem1d.solver import (
    ILL_CONDITIONED_LIMIT,
    is_tridiagonal,
    solve_linear_system,
    thomas,
)


def _random_tridiagonal(rng, n, symmetric=False):
    diag = rng.uniform(4.0, 6.0, n)  # strictly diagonally dominant -> nonsingular, stable
    lower = rng.uniform(-1.5, 1.5, n - 1)
    upper = lower.copy() if symmetric else rng.uniform(-1.5, 1.5, n - 1)
    rhs = rng.uniform(-3.0, 3.0, n)
    dense = np.diag(diag) + np.diag(lower, -1) + np.diag(upper, 1)
    return lower, diag, upper, rhs, dense


@pytest.mark.parametrize("seed", range(100))
def test_thomas_matches_lapack_on_random_tridiagonal_systems(seed) -> None:
    rng = np.random.default_rng(seed)
    n = int(rng.integers(1, 80))
    lower, diag, upper, rhs, dense = _random_tridiagonal(rng, n, symmetric=bool(seed % 2))
    x, steps = thomas(lower, diag, upper, rhs)
    np.testing.assert_allclose(dense @ x, rhs, rtol=0, atol=1e-12)
    np.testing.assert_allclose(x, np.linalg.solve(dense, rhs), rtol=1e-11, atol=1e-12)
    assert len(steps) == n


def test_thomas_recorded_steps_follow_the_textbook_recurrences() -> None:
    rng = np.random.default_rng(7)
    lower, diag, upper, rhs, _ = _random_tridiagonal(rng, 6)
    x, steps = thomas(lower, diag, upper, rhs)
    c_prev = d_prev = 0.0
    for i, step in enumerate(steps):
        pivot = diag[i] - (lower[i - 1] * c_prev if i else 0.0)
        c = upper[i] / pivot if i < 5 else 0.0
        d = (rhs[i] - (lower[i - 1] * d_prev if i else 0.0)) / pivot
        assert (step.index, step.pivot, step.c_prime, step.d_prime) == pytest.approx(
            (i, pivot, c, d)
        )
        c_prev, d_prev = c, d
    for i in range(5):  # back substitution x_i = d'_i - c'_i x_{i+1}
        assert x[i] == pytest.approx(steps[i].d_prime - steps[i].c_prime * x[i + 1])
    assert x[5] == pytest.approx(steps[5].d_prime)


def test_thomas_single_unknown() -> None:
    x, steps = thomas(np.zeros(0), np.array([4.0]), np.zeros(0), np.array([2.0]))
    assert x.tolist() == [0.5]
    assert len(steps) == 1


def test_thomas_zero_pivot_raises() -> None:
    with pytest.raises(np.linalg.LinAlgError):
        thomas(np.array([1.0]), np.array([0.0, 1.0]), np.array([1.0]), np.array([1.0, 1.0]))


def test_thomas_rejects_inconsistent_dimensions() -> None:
    with pytest.raises(ValueError, match="dimensions"):
        thomas(np.zeros(3), np.ones(3), np.zeros(2), np.ones(3))


def test_is_tridiagonal() -> None:
    assert is_tridiagonal(np.diag([1.0, 2, 3]) + np.diag([1.0, 1], 1) + np.diag([1.0, 1], -1))
    assert not is_tridiagonal(np.array([[1.0, 0, 5], [0, 1, 0], [0, 0, 1]]))
    assert not is_tridiagonal(np.array([[1.0, 0, 0], [0, 1, 0], [5, 0, 1]]))
    assert is_tridiagonal(np.ones((2, 2)))


@pytest.mark.parametrize("element", ["P1", "P2"])
def test_auto_method_selects_thomas_for_p1_and_dense_for_p2(element) -> None:
    from fem1d.assembly import assemble
    from fem1d.boundary import apply_boundary_conditions
    from fem1d.mesh import build_mesh

    problem = benchmark("B4")
    mesh = build_mesh(problem.domain, 8, element)
    pd, qd, rd, fd = problem.degrees
    system = assemble(mesh, problem.p, pd, problem.q, qd, problem.r, rd, problem.f, fd)
    reduced = apply_boundary_conditions(system, problem.p, problem.left, problem.right)
    auto = solve_linear_system(reduced.K_ff, reduced.F_f)
    dense = solve_linear_system(reduced.K_ff, reduced.F_f, method="dense")
    assert auto.method == ("thomas" if element == "P1" else "dense")
    assert (auto.thomas_steps is not None) == (element == "P1")
    np.testing.assert_allclose(auto.x, dense.x, rtol=1e-11, atol=1e-13)


def test_forced_thomas_and_dense_agree_on_a_convection_problem() -> None:
    from fem1d.assembly import assemble
    from fem1d.boundary import apply_boundary_conditions
    from fem1d.mesh import build_mesh

    problem = benchmark("B5")
    mesh = build_mesh(problem.domain, 40, "P1")
    pd, qd, rd, fd = problem.degrees
    system = assemble(mesh, problem.p, pd, problem.q, qd, problem.r, rd, problem.f, fd)
    reduced = apply_boundary_conditions(system, problem.p, problem.left, problem.right)
    a = solve_linear_system(reduced.K_ff, reduced.F_f, method="thomas")
    b = solve_linear_system(reduced.K_ff, reduced.F_f, method="dense")
    np.testing.assert_allclose(a.x, b.x, rtol=1e-9, atol=1e-12)


def test_condition_number_and_ill_conditioned_flag() -> None:
    good = solve_linear_system(np.diag([1.0, 2.0]), np.array([1.0, 1.0]))
    assert good.condition_number == pytest.approx(2.0)
    assert good.ill_conditioned is False
    bad = solve_linear_system(np.diag([1.0, 1e12]), np.array([1.0, 1.0]))
    assert bad.condition_number == pytest.approx(1e12)
    assert bad.condition_number > ILL_CONDITIONED_LIMIT
    assert bad.ill_conditioned is True


def test_condition_number_can_be_skipped_or_is_skipped_for_large_systems() -> None:
    K, F = np.diag([1.0, 2.0, 3.0]), np.ones(3)
    assert solve_linear_system(K, F, compute_condition=False).condition_number is None
    assert solve_linear_system(K, F, condition_max_dofs=2).condition_number is None


def test_empty_system() -> None:
    solution = solve_linear_system(np.zeros((0, 0)), np.zeros(0))
    assert solution.x.size == 0


def test_singular_dense_system_raises() -> None:
    with pytest.raises(np.linalg.LinAlgError):
        solve_linear_system(np.ones((3, 3)), np.ones(3), method="dense")


def test_b1_hand_computed_nodal_values_n2_and_n4() -> None:
    # docs/BENCHMARKS.md §4: U_1 = 1/8 and U = [3/32, 1/8, 3/32]
    _, U2 = solve_fem(benchmark("B1"), 2, "P1")
    assert U2.tolist() == pytest.approx([0.0, 1 / 8, 0.0], abs=1e-15)
    _, U4 = solve_fem(benchmark("B1"), 4, "P1")
    assert U4.tolist() == pytest.approx([0.0, 3 / 32, 1 / 8, 3 / 32, 0.0], abs=1e-15)


def test_b3_hand_computed_nodal_value_n2() -> None:
    _, U = solve_fem(benchmark("B3"), 2, "P1")
    assert U[1] == pytest.approx(1 / 12, abs=1e-15)
