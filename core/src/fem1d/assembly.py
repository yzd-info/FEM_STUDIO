"""Global assembly of the system matrix K and load vector F (docs/MATH_SPEC.md §3, §5; step M2.4).

The element matrices of every element are added into the global system at the
DOF indices given by the mesh connectivity. Every single addition is recorded
in an assembly log so the derivation document can show, for example,
K_11 = K^(1)_22 + K^(2)_11 with real numbers.

Naming note: as in docs/MATH_SPEC.md §5, the *global* matrix is called K and
equals the sum of the diffusion, convection and reaction parts (K + C + M).
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from fem1d.element_matrices import Coefficient, ElementMatrices, element_matrices
from fem1d.mesh import Mesh


@dataclass(frozen=True)
class Contribution:
    """One addition `value` into global entry (global_row, global_col) from one element."""

    element: int
    local_row: int
    local_col: int
    global_row: int
    global_col: int
    value: float


@dataclass(frozen=True)
class AssembledSystem:
    """Global system before boundary conditions: K U = F with K = K_diff + C + M."""

    mesh: Mesh
    K: NDArray[np.float64]
    F: NDArray[np.float64]
    per_element: tuple[ElementMatrices, ...]
    log: tuple[Contribution, ...]
    quadrature_approx: bool

    def contributions_to(self, row: int, col: int) -> tuple[Contribution, ...]:
        """All logged element contributions that were added into K[row, col]."""
        return tuple(c for c in self.log if c.global_row == row and c.global_col == col)


def assemble(
    mesh: Mesh,
    p: Coefficient,
    p_degree: int | None,
    q: Coefficient,
    q_degree: int | None,
    r: Coefficient,
    r_degree: int | None,
    f: Coefficient,
    f_degree: int | None,
    record_log: bool = True,
) -> AssembledSystem:
    """Assemble K and F for -(p u')' + q u' + r u = f on `mesh`.

    `*_degree` is the polynomial degree of the coefficient (or None when it is
    not a polynomial), which selects the quadrature rule (MATH_SPEC §5.2).
    """
    ndofs = len(mesh.nodes)
    K = np.zeros((ndofs, ndofs))
    F = np.zeros(ndofs)
    per_element: list[ElementMatrices] = []
    log: list[Contribution] = []
    approx = False

    for e, dofs in enumerate(mesh.connectivity):
        left = float(mesh.nodes[dofs[0]])
        right = float(mesh.nodes[dofs[-1]])
        em = element_matrices(
            mesh.element_type,
            (left, right),
            p,
            p_degree,
            q,
            q_degree,
            r,
            r_degree,
            f,
            f_degree,
        )
        per_element.append(em)
        approx = approx or em.quadrature_approx
        local = em.K + em.C + em.M
        for i, gi in enumerate(dofs):
            F[gi] += em.F[i]
            for j, gj in enumerate(dofs):
                K[gi, gj] += local[i, j]
                if record_log:
                    log.append(
                        Contribution(
                            element=e,
                            local_row=i,
                            local_col=j,
                            global_row=int(gi),
                            global_col=int(gj),
                            value=float(local[i, j]),
                        )
                    )

    return AssembledSystem(
        mesh=mesh,
        K=K,
        F=F,
        per_element=tuple(per_element),
        log=tuple(log),
        quadrature_approx=approx,
    )
