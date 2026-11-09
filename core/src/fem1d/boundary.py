"""Boundary conditions alpha*u' + beta*u = gamma at both ends (docs/MATH_SPEC.md §2; step M2.5).

- Dirichlet (alpha == 0): the DOF is fixed to gamma/beta and eliminated (lifting, §2.4).
- Neumann / Robin (alpha != 0): natural terms are added to K and F (§2.2, §2.3):
    right end x = b:  K[N,N] += +p(b) beta/alpha,   F[N] += +p(b) gamma/alpha
    left  end x = a:  K[0,0] += -p(a) beta/alpha,    F[0] += -p(a) gamma/alpha
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from fem1d.assembly import AssembledSystem
from fem1d.element_matrices import Coefficient

BoundaryKind = Literal["dirichlet", "neumann", "robin"]

_SINGULAR_TOLERANCE = 1e-10


class SingularSystemError(ValueError):
    """The problem has no unique solution (e.g. pure Neumann with r = 0; MATH_SPEC §1.2)."""


@dataclass(frozen=True)
class BoundaryCondition:
    """alpha * u'(x0) + beta * u(x0) = gamma."""

    alpha: float
    beta: float
    gamma: float

    def __post_init__(self) -> None:
        if self.alpha == 0 and self.beta == 0:
            raise ValueError("boundary condition needs alpha != 0 or beta != 0")

    @property
    def kind(self) -> BoundaryKind:
        if self.alpha == 0:
            return "dirichlet"
        if self.beta == 0:
            return "neumann"
        return "robin"


@dataclass(frozen=True)
class ReducedSystem:
    """System after boundary conditions.

    `K_full`/`F_full` include the natural (Neumann/Robin) terms but still all DOFs.
    `fixed` maps Dirichlet DOF -> value. `K_ff U_f = F_f` is the reduced system with
    F_f = F_free - K_free,fixed U_fixed.
    """

    K_full: NDArray[np.float64]
    F_full: NDArray[np.float64]
    fixed: dict[int, float]
    free: NDArray[np.int64]
    K_ff: NDArray[np.float64]
    F_f: NDArray[np.float64]


def apply_boundary_conditions(
    system: AssembledSystem,
    p: Coefficient,
    left: BoundaryCondition,
    right: BoundaryCondition,
) -> ReducedSystem:
    """Apply the left/right boundary conditions to the assembled system."""
    ndofs = len(system.mesh.nodes)
    a, b = system.mesh.domain
    K = system.K.copy()
    F = system.F.copy()
    fixed: dict[int, float] = {}

    for dof, x0, bc, sign in ((0, a, left, -1.0), (ndofs - 1, b, right, 1.0)):
        if bc.kind == "dirichlet":
            fixed[dof] = bc.gamma / bc.beta
        else:
            weight = sign * float(p(x0)) / bc.alpha
            K[dof, dof] += weight * bc.beta
            F[dof] += weight * bc.gamma

    if not fixed and np.max(np.abs(K @ np.ones(ndofs))) <= _SINGULAR_TOLERANCE * np.max(np.abs(K)):
        raise SingularSystemError(
            "no Dirichlet or Robin condition pins the solution: "
            "u is only determined up to an additive constant"
        )

    free = np.array([i for i in range(ndofs) if i not in fixed], dtype=np.int64)
    fixed_idx = np.array(sorted(fixed), dtype=np.int64)
    u_fixed = np.array([fixed[i] for i in fixed_idx], dtype=float)
    K_ff = K[np.ix_(free, free)]
    F_f = F[free] - K[np.ix_(free, fixed_idx)] @ u_fixed
    return ReducedSystem(K_full=K, F_full=F, fixed=fixed, free=free, K_ff=K_ff, F_f=F_f)


def expand_solution(reduced: ReducedSystem, u_free: NDArray[np.float64]) -> NDArray[np.float64]:
    """Insert the free-DOF solution and the prescribed Dirichlet values into a full vector."""
    u = np.zeros(len(reduced.K_full))
    u[reduced.free] = u_free
    for dof, value in reduced.fixed.items():
        u[dof] = value
    return u
