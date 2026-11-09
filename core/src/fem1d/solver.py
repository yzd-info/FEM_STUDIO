"""Linear solvers for the reduced system (step M2.6).

`thomas` is the tridiagonal algorithm of docs/LATEX_STYLE.md step 10; its forward-elimination
quantities are recorded so the derivation can print them. `solve_linear_system` uses it
automatically for tridiagonal matrices (P1) and falls back to LAPACK otherwise (P2, or
non-tridiagonal structure).
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

ILL_CONDITIONED_LIMIT = 1e10
_PIVOT_TOLERANCE = 1e-14


@dataclass(frozen=True)
class ThomasStep:
    """Forward-elimination row i: pivot b'_i, c'_i = c_i / b'_i and d'_i."""

    index: int
    pivot: float
    c_prime: float
    d_prime: float


@dataclass(frozen=True)
class LinearSolution:
    x: NDArray[np.float64]
    method: Literal["dense", "thomas"]
    condition_number: float | None
    ill_conditioned: bool
    thomas_steps: tuple[ThomasStep, ...] | None


def is_tridiagonal(matrix: NDArray[np.float64]) -> bool:
    """True when every entry further than one off the diagonal is exactly zero."""
    n = matrix.shape[0]
    if n <= 2:
        return True
    return not np.any(np.triu(matrix, 2)) and not np.any(np.tril(matrix, -2))


def thomas(
    lower: NDArray[np.float64],
    diag: NDArray[np.float64],
    upper: NDArray[np.float64],
    rhs: NDArray[np.float64],
) -> tuple[NDArray[np.float64], tuple[ThomasStep, ...]]:
    """Solve a tridiagonal system. lower/upper have length n-1, diag/rhs length n."""
    n = len(diag)
    if len(lower) != n - 1 or len(upper) != n - 1 or len(rhs) != n:
        raise ValueError("inconsistent tridiagonal dimensions")
    c_prime = np.zeros(n)
    d_prime = np.zeros(n)
    steps: list[ThomasStep] = []
    scale = float(np.max(np.abs(diag))) if n else 1.0

    for i in range(n):
        pivot = diag[i] - (lower[i - 1] * c_prime[i - 1] if i > 0 else 0.0)
        if abs(pivot) <= _PIVOT_TOLERANCE * scale:
            raise np.linalg.LinAlgError("zero pivot in Thomas algorithm")
        c_prime[i] = (upper[i] / pivot) if i < n - 1 else 0.0
        previous = d_prime[i - 1] if i > 0 else 0.0
        d_prime[i] = (rhs[i] - (lower[i - 1] * previous if i > 0 else 0.0)) / pivot
        steps.append(
            ThomasStep(
                index=i, pivot=float(pivot), c_prime=float(c_prime[i]), d_prime=float(d_prime[i])
            )
        )

    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = d_prime[i] - (c_prime[i] * x[i + 1] if i < n - 1 else 0.0)
    return x, tuple(steps)


def solve_linear_system(
    K: NDArray[np.float64],
    F: NDArray[np.float64],
    method: Literal["auto", "dense", "thomas"] = "auto",
    compute_condition: bool = True,
    condition_max_dofs: int = 2049,
) -> LinearSolution:
    """Solve K x = F; reports the 2-norm condition number for sizes up to `condition_max_dofs`."""
    n = K.shape[0]
    if n == 0:
        return LinearSolution(np.zeros(0), "dense", None, False, None)

    use_thomas = method == "thomas" or (method == "auto" and is_tridiagonal(K))
    steps: tuple[ThomasStep, ...] | None = None
    if use_thomas:
        lower = np.diagonal(K, -1).copy()
        upper = np.diagonal(K, 1).copy()
        x, steps = thomas(lower, np.diagonal(K).copy(), upper, F)
        used: Literal["dense", "thomas"] = "thomas"
    else:
        x = np.linalg.solve(K, F)
        used = "dense"

    cond: float | None = None
    if compute_condition and n <= condition_max_dofs:
        cond = float(np.linalg.cond(K))
    return LinearSolution(
        x=x,
        method=used,
        condition_number=cond,
        ill_conditioned=cond is not None and cond > ILL_CONDITIONED_LIMIT,
        thomas_steps=steps,
    )
