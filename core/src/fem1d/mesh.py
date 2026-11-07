"""Uniform 1D mesh with P1/P2 connectivity (docs/MATH_SPEC.md §4)."""

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

ElementType = Literal["P1", "P2"]


@dataclass(frozen=True)
class Mesh:
    """A uniform mesh of `n` elements over `domain`.

    `nodes` holds the coordinates of every global degree of freedom (DOF):
    n+1 for P1, 2n+1 for P2 (midpoints included). `connectivity[k]` lists the
    global DOF indices of element k, in local order (P1: [left, right];
    P2: [left, mid, right]).
    """

    domain: tuple[float, float]
    n: int
    element_type: ElementType
    nodes: NDArray[np.float64]
    connectivity: NDArray[np.int64]


def build_mesh(domain: tuple[float, float], n: int, element_type: ElementType) -> Mesh:
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    a, b = domain

    if element_type == "P1":
        nodes = np.linspace(a, b, n + 1)
        connectivity = np.array([[k, k + 1] for k in range(n)], dtype=np.int64)
    else:
        nodes = np.linspace(a, b, 2 * n + 1)
        connectivity = np.array([[2 * k, 2 * k + 1, 2 * k + 2] for k in range(n)], dtype=np.int64)

    return Mesh(
        domain=domain, n=n, element_type=element_type, nodes=nodes, connectivity=connectivity
    )
