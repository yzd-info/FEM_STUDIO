"""M2.5: Dirichlet, Neumann and Robin conditions (docs/MATH_SPEC.md §2)."""

import numpy as np
import pytest

from bench import benchmark, random_mms_problem
from fem1d.assembly import assemble
from fem1d.boundary import (
    BoundaryCondition,
    SingularSystemError,
    apply_boundary_conditions,
    expand_solution,
)
from fem1d.mesh import build_mesh


def _system(problem, n=2, element="P1"):
    mesh = build_mesh(problem.domain, n, element)
    pd, qd, rd, fd = problem.degrees
    return assemble(mesh, problem.p, pd, problem.q, qd, problem.r, rd, problem.f, fd)


def _solve(problem, n=2, element="P1"):
    system = _system(problem, n, element)
    reduced = apply_boundary_conditions(system, problem.p, problem.left, problem.right)
    return reduced, expand_solution(reduced, np.linalg.solve(reduced.K_ff, reduced.F_f))


def test_kind_classification() -> None:
    assert BoundaryCondition(0, 1, 5).kind == "dirichlet"
    assert BoundaryCondition(2, 0, 5).kind == "neumann"
    assert BoundaryCondition(2, 3, 5).kind == "robin"


def test_alpha_and_beta_both_zero_is_rejected() -> None:
    with pytest.raises(ValueError, match="alpha"):
        BoundaryCondition(0.0, 0.0, 1.0)


def test_dirichlet_value_is_gamma_over_beta() -> None:
    problem = benchmark("B1")
    system = _system(problem)
    reduced = apply_boundary_conditions(
        system, problem.p, BoundaryCondition(0, 2, 4), BoundaryCondition(0, -4, 6)
    )
    assert reduced.fixed == {0: 2.0, 2: -1.5}


def test_dirichlet_lifting_moves_known_values_to_the_right_hand_side() -> None:
    # B1 n=2 with u(0)=1, u(1)=3: reduced equation 4 U1 = 1/2 - (-2*1 + -2*3) = 17/2.
    problem = benchmark("B1")
    system = _system(problem)
    reduced = apply_boundary_conditions(
        system, problem.p, BoundaryCondition(0, 1, 1), BoundaryCondition(0, 1, 3)
    )
    assert reduced.K_ff.tolist() == [[4.0]]
    assert reduced.F_f[0] == pytest.approx(8.5)
    U = expand_solution(reduced, reduced.F_f / reduced.K_ff[0, 0])
    # exact solution of -u'' = 1, u(0)=1, u(1)=3 is -x^2/2 + 5x/2 + 1; u(1/2) = 17/8
    assert U[1] == pytest.approx(17 / 8)
    assert U.tolist()[0::2] == [1.0, 3.0]


def test_right_robin_adds_p_beta_over_alpha_to_corner_and_p_gamma_over_alpha_to_load() -> None:
    problem = benchmark("B7")  # right: u' + u = 1
    system = _system(problem)
    reduced = apply_boundary_conditions(system, problem.p, problem.left, problem.right)
    assert reduced.K_full[2, 2] == pytest.approx(system.K[2, 2] + 1.0)
    assert reduced.F_full[2] == pytest.approx(system.F[2] + 1.0)
    # reduced system [[4,-2],[-2,3]] U = [1/2, 5/4]  ->  U = [1/2, 3/4] = exact u at 1/2 and 1
    assert reduced.K_ff.tolist() == [[4.0, -2.0], [-2.0, 3.0]]
    _, U = _solve(problem)
    assert U.tolist() == pytest.approx([0.0, 0.5, 0.75])


def test_left_robin_has_the_opposite_sign_B10_convention() -> None:
    # -u'(a) + 2 u(a) = 1  ->  alpha=-1, beta=2: K[0,0] += +p*2, F[0] += +p*1 (MATH_SPEC §2.3).
    problem = benchmark("B1")
    system = _system(problem)
    left = BoundaryCondition(-1.0, 2.0, 1.0)
    reduced = apply_boundary_conditions(system, problem.p, left, BoundaryCondition(0, 1, 0))
    assert reduced.K_full[0, 0] == pytest.approx(system.K[0, 0] + 2.0)
    assert reduced.F_full[0] == pytest.approx(system.F[0] + 1.0)


def test_neumann_adds_only_to_the_load_vector() -> None:
    problem = benchmark("B6")  # right: u' = 0 -> no change at all; use u'(1)=3 variant below
    system = _system(problem)
    right = BoundaryCondition(1.0, 0.0, 3.0)
    reduced = apply_boundary_conditions(system, problem.p, problem.left, right)
    np.testing.assert_array_equal(reduced.K_full, system.K)
    assert reduced.F_full[2] == pytest.approx(system.F[2] + 3.0)


def test_natural_terms_scale_with_p_at_the_boundary() -> None:
    problem = benchmark("B3")  # p = 1 + x: p(0) = 1, p(1) = 2
    system = _system(problem)
    reduced = apply_boundary_conditions(
        system, problem.p, BoundaryCondition(1.0, 1.0, 0.0), BoundaryCondition(1.0, 1.0, 1.0)
    )
    assert reduced.K_full[2, 2] == pytest.approx(system.K[2, 2] + 2.0)  # + p(1) beta/alpha
    assert reduced.F_full[2] == pytest.approx(system.F[2] + 2.0)  # + p(1) gamma/alpha
    assert reduced.K_full[0, 0] == pytest.approx(system.K[0, 0] - 1.0)  # - p(0) beta/alpha


def test_input_system_is_not_modified() -> None:
    problem = benchmark("B7")
    system = _system(problem)
    K0, F0 = system.K.copy(), system.F.copy()
    apply_boundary_conditions(system, problem.p, problem.left, problem.right)
    np.testing.assert_array_equal(system.K, K0)
    np.testing.assert_array_equal(system.F, F0)


def test_pure_neumann_without_reaction_is_singular() -> None:
    problem = benchmark("B1")
    system = _system(problem)
    neumann = BoundaryCondition(1.0, 0.0, 0.0)
    with pytest.raises(SingularSystemError):
        apply_boundary_conditions(system, problem.p, neumann, neumann)


def test_pure_neumann_with_convection_but_no_reaction_is_still_singular() -> None:
    problem = benchmark("B5")  # q = 1, r = 0
    system = _system(problem, n=4)
    neumann = BoundaryCondition(1.0, 0.0, 0.0)
    with pytest.raises(SingularSystemError):
        apply_boundary_conditions(system, problem.p, neumann, neumann)


def test_pure_neumann_with_reaction_is_fine() -> None:
    problem = benchmark("B4")  # r = 1 > 0
    system = _system(problem)
    neumann = BoundaryCondition(1.0, 0.0, 0.0)
    reduced = apply_boundary_conditions(system, problem.p, neumann, neumann)
    assert reduced.fixed == {}
    assert len(reduced.free) == 3


def test_neumann_plus_robin_pins_the_solution() -> None:
    problem = benchmark("B1")
    system = _system(problem)
    reduced = apply_boundary_conditions(
        system, problem.p, BoundaryCondition(-1.0, 0.0, 0.0), BoundaryCondition(1.0, 1.0, 0.0)
    )
    assert reduced.fixed == {}


@pytest.mark.parametrize("element", ["P1", "P2"])
@pytest.mark.parametrize("seed", range(40))
def test_elimination_equals_row_replacement(seed, element) -> None:
    """Independent method: replace Dirichlet rows by identity rows and solve the full system."""
    problem = random_mms_problem(seed, 4)
    system = _system(problem, n=1 + seed % 6, element=element)
    reduced = apply_boundary_conditions(system, problem.p, problem.left, problem.right)
    U_elim = expand_solution(reduced, np.linalg.solve(reduced.K_ff, reduced.F_f))

    K, F = reduced.K_full.copy(), reduced.F_full.copy()
    for dof, value in reduced.fixed.items():
        K[dof, :] = 0.0
        K[dof, dof] = 1.0
        F[dof] = value
    U_rows = np.linalg.solve(K, F)
    np.testing.assert_allclose(U_elim, U_rows, rtol=1e-9, atol=1e-10)


@pytest.mark.parametrize("name", ["B1", "B2", "B3", "B4", "B6", "B7", "B9"])
@pytest.mark.parametrize("element", ["P1", "P2"])
def test_reduced_matrix_is_symmetric_positive_definite_without_convection(name, element) -> None:
    problem = benchmark(name)  # all have q = 0 and r >= 0
    system = _system(problem, n=6, element=element)
    reduced = apply_boundary_conditions(system, problem.p, problem.left, problem.right)
    np.testing.assert_allclose(reduced.K_ff, reduced.K_ff.T, rtol=0, atol=1e-13)
    assert np.min(np.linalg.eigvalsh(reduced.K_ff)) > 0


def test_expand_solution_places_free_and_fixed_values() -> None:
    problem = benchmark("B1")
    system = _system(problem, n=3)
    reduced = apply_boundary_conditions(
        system, problem.p, BoundaryCondition(0, 1, 7), BoundaryCondition(0, 1, -2)
    )
    U = expand_solution(reduced, np.array([10.0, 20.0]))
    assert U.tolist() == [7.0, 10.0, 20.0, -2.0]
