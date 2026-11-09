"""M2.7: independent oracle. scikit-fem assembles and solves the same weak form
with its own quadrature and sparse linear algebra; nodal values must agree with
fem1d (docs/BENCHMARKS.md §1 B1-B10) to within a relative difference of 1e-10.

Only the elementary Robin/Neumann corner-term algebra of docs/MATH_SPEC.md §2.2-2.3
(fem1d.boundary's weight = sign * p(x0) / alpha convention) is reused here, applied
to scikit-fem's own assembled matrix -- the discretisation itself (element matrices,
assembly, quadrature) is entirely independent of fem1d.
"""

import numpy as np
import pytest
from numpy.typing import NDArray
from skfem import (
    Basis,
    BilinearForm,
    ElementLineP1,
    ElementLineP2,
    LinearForm,
    MeshLine,
    condense,
    solve,
)

from bench import Problem, benchmark, solve_fem
from fem1d.mesh import ElementType

_BENCHMARK_NAMES = [f"B{i}" for i in range(1, 11)]


def _oracle_solve(problem: Problem, n: int, element: ElementType) -> dict[float, float]:
    """Solve `problem` with scikit-fem; return {x: u(x)} at every DOF."""
    mesh = MeshLine(np.linspace(*problem.domain, n + 1))
    basis = Basis(mesh, ElementLineP1() if element == "P1" else ElementLineP2(), intorder=20)

    @BilinearForm
    def bilinear(u, v, w):
        x = w.x[0]
        return (
            problem.p(x) * u.grad[0] * v.grad[0]
            + problem.q(x) * u.grad[0] * v
            + problem.r(x) * u * v
        )

    @LinearForm
    def linear(v, w):
        return problem.f(w.x[0]) * v

    A = bilinear.assemble(basis).tolil()
    b: NDArray[np.float64] = linear.assemble(basis)

    a, bnd = problem.domain
    x0 = basis.doflocs[0]
    left_dof, right_dof = int(np.argmin(x0)), int(np.argmax(x0))

    for dof, x_at, bc, sign in (
        (left_dof, a, problem.left, -1.0),
        (right_dof, bnd, problem.right, 1.0),
    ):
        if bc.alpha != 0:  # Neumann/Robin natural term, same formula as fem1d.boundary
            weight = sign * problem.p(x_at) / bc.alpha
            A[dof, dof] += weight * bc.beta
            b[dof] += weight * bc.gamma

    dirichlet_dofs = []
    dirichlet_values = np.zeros(A.shape[0])
    for dof, bc in ((left_dof, problem.left), (right_dof, problem.right)):
        if bc.alpha == 0:
            dirichlet_dofs.append(dof)
            dirichlet_values[dof] = bc.gamma / bc.beta

    D = np.array(dirichlet_dofs, dtype=np.int64)
    u = solve(*condense(A.tocsr(), b, D=D, x=dirichlet_values))
    return dict(zip(np.round(x0, 9), u, strict=True))


@pytest.mark.parametrize("name", _BENCHMARK_NAMES)
@pytest.mark.parametrize("element", ["P1", "P2"])
def test_nodal_values_match_scikit_fem_oracle(name: str, element: ElementType) -> None:
    problem = benchmark(name)
    n = 6
    mesh, U = solve_fem(problem, n, element)
    oracle = _oracle_solve(problem, n, element)

    for x, u_mine in zip(mesh.nodes, U, strict=True):
        u_oracle = oracle[round(float(x), 9)]
        denom = max(abs(u_mine), abs(u_oracle), 1e-12)
        assert abs(u_mine - u_oracle) / denom < 1e-10, (name, element, x, u_mine, u_oracle)
