"""Error norms, convergence rates, diagnostics and sampling (steps M4.1-M4.3).

Formulas: docs/MATH_SPEC.md §6 (norms), §7 (rates), §8 (diagnostics). Finite-element functions
are evaluated with closed-form, vectorised Lagrange bases on the reference element
xi in [-1, 1]; tests check them against `fem1d.elements` and against hand-derived integrals.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from fem1d.mesh import ElementType, Mesh
from fem1d.quadrature import gauss_legendre

Array = NDArray[np.float64]
ScalarField = Callable[[Any], Any]

MACHINE_PRECISION_LIMIT = 1e-12
ASYMPTOTIC_TOLERANCE = 0.1
ERROR_QUADRATURE_POINTS = 10  # MATH_SPEC §6
MAX_SAMPLE_POINTS = 2048  # ARCHITECTURE §3


# ---------------------------------------------------------------------------- reference bases
def reference_basis(element_type: ElementType, xi: Array) -> tuple[Array, Array]:
    """Shape functions N (ndof, m) and derivatives dN/dxi (ndof, m) at points xi (m,)."""
    xi = np.asarray(xi, dtype=float)
    if element_type == "P1":
        n = np.array([(1 - xi) / 2, (1 + xi) / 2])
        dn = np.array([np.full_like(xi, -0.5), np.full_like(xi, 0.5)])
    else:
        n = np.array([xi * (xi - 1) / 2, 1 - xi**2, xi * (xi + 1) / 2])
        dn = np.array([xi - 0.5, -2 * xi, xi + 0.5])
    return n, dn


def fe_values(mesh: Mesh, U: Array, xi: Array) -> tuple[Array, Array, Array]:
    """x, u_h, u_h' at the reference points `xi` of every element; all shaped (n, m)."""
    n_ref, dn_ref = reference_basis(mesh.element_type, xi)
    coeff = U[mesh.connectivity]  # (n, ndof)
    left = mesh.nodes[mesh.connectivity[:, 0]][:, None]
    right = mesh.nodes[mesh.connectivity[:, -1]][:, None]
    h = right - left
    x = (left + right) / 2 + h / 2 * np.asarray(xi)[None, :]
    return x, coeff @ n_ref, (coeff @ dn_ref) * (2 / h)


def _field(fn: ScalarField, x: Array) -> Array:
    """Evaluate a user/analytic function so that constants broadcast to x's shape."""
    return np.asarray(fn(x), dtype=float) * np.ones_like(x)


# ------------------------------------------------------------------------------ error norms
@dataclass(frozen=True)
class ErrorNorms:
    l2: float
    h1: float
    max_nodal: float
    l2_rel: float | None  # None when ||u||_L2 = 0
    h1_rel: float | None


def vertex_dofs(mesh: Mesh) -> NDArray[np.int64]:
    """DOFs at element end points (P1: all nodes; P2: every second node, midpoints excluded)."""
    step = 1 if mesh.element_type == "P1" else 2
    return np.arange(0, len(mesh.nodes), step)


def compute_errors(
    mesh: Mesh, U: Array, u: ScalarField, du: ScalarField, points: int = ERROR_QUADRATURE_POINTS
) -> ErrorNorms:
    """L2, H1 semi-norm and element-end-point errors against a known solution (§6)."""
    rule = gauss_legendre(points)
    xi, w = np.asarray(rule.points, dtype=float), np.asarray(rule.weights, dtype=float)
    x, uh, duh = fe_values(mesh, U, xi)
    jac = (mesh.nodes[mesh.connectivity[:, -1]] - mesh.nodes[mesh.connectivity[:, 0]])[:, None] / 2
    weight = w[None, :] * jac
    exact, dexact = _field(u, x), _field(du, x)
    l2 = math.sqrt(float(np.sum(weight * (exact - uh) ** 2)))
    h1 = math.sqrt(float(np.sum(weight * (dexact - duh) ** 2)))
    v = vertex_dofs(mesh)
    nodal = float(np.max(np.abs(U[v] - _field(u, mesh.nodes[v]))))
    u_norm = math.sqrt(float(np.sum(weight * exact**2)))
    du_norm = math.sqrt(float(np.sum(weight * dexact**2)))
    return ErrorNorms(
        l2=l2,
        h1=h1,
        max_nodal=nodal,
        l2_rel=l2 / u_norm if u_norm > 0 else None,
        h1_rel=h1 / du_norm if du_norm > 0 else None,
    )


# ------------------------------------------------------------------------------ convergence
@dataclass(frozen=True)
class Convergence:
    """Successive rates rho_k = ln(e_k/e_{k+1}) / ln(h_k/h_{k+1}) (§7)."""

    rates: tuple[float | None, ...]  # None where an error is below the machine-precision floor
    theory: float | None
    asymptotic: bool
    machine_precision: bool


def theoretical_rate(norm: str, element_type: ElementType) -> float | None:
    """A priori orders (§6.1). The nodal error has no general a priori order."""
    k = 1 if element_type == "P1" else 2
    return {"L2": float(k + 1), "H1": float(k)}.get(norm)


def estimate_convergence(
    h: list[float],
    errors: list[float],
    theory: float | None,
    floor: float = MACHINE_PRECISION_LIMIT,
) -> Convergence:
    """Rates between successive meshes. Errors below `floor` are not used (§7).

    `asymptotic` holds when the last two available rates are within 0.1 of `theory`.
    """
    if len(h) != len(errors) or len(h) < 2:
        raise ValueError("need matching h and error lists with at least two meshes")
    if any(b >= a for a, b in zip(h[:-1], h[1:], strict=True)):
        raise ValueError("h must be strictly decreasing")
    machine = all(e < floor for e in errors)
    rates: list[float | None] = []
    for (h0, e0), (h1, e1) in zip(
        zip(h[:-1], errors[:-1], strict=True), zip(h[1:], errors[1:], strict=True), strict=True
    ):
        if e0 < floor or e1 < floor:
            rates.append(None)
        else:
            rates.append(math.log(e0 / e1) / math.log(h0 / h1))
    usable = [r for r in rates if r is not None]
    asymptotic = (
        theory is not None
        and len(usable) >= 2
        and rates[-1] is not None
        and rates[-2] is not None
        and all(abs(r - theory) <= ASYMPTOTIC_TOLERANCE for r in rates[-2:] if r is not None)
    )
    return Convergence(tuple(rates), theory, asymptotic, machine)


# ------------------------------------------------------------------------------- diagnostics
@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    data: dict[str, float | int | str]


def peclet_number(p: ScalarField, q: ScalarField, domain: tuple[float, float], h: float) -> float:
    """Pe = max |q| h / (2 p) over the domain (§8), maximised on a fine grid."""
    x = np.linspace(domain[0], domain[1], 1025)
    return float(np.max(np.abs(_field(q, x)) / (2.0 * _field(p, x))) * h)


def coercivity_minimum(
    q: ScalarField,
    r: ScalarField,
    domain: tuple[float, float],
    dq: ScalarField | None = None,
) -> float:
    """min over the domain of r - q'/2 (§8); q' by central differences when `dq` is absent."""
    x = np.linspace(domain[0], domain[1], 1025)
    if dq is not None:
        slope = _field(dq, x)
    else:
        step = 1e-6 * max(1.0, abs(domain[1] - domain[0]))
        slope = (_field(q, x + step) - _field(q, x - step)) / (2 * step)
    return float(np.min(_field(r, x) - slope / 2))


def diagnose_run(
    n: int,
    h: float,
    peclet: float,
    coercivity_min: float,
    quadrature_approx: bool,
    condition_number: float | None,
    ill_conditioned: bool,
    errors: ErrorNorms | None,
) -> list[Diagnostic]:
    """Warnings for a single mesh (§8). Messages are Turkish: they are shown to the user."""
    out: list[Diagnostic] = []
    if peclet > 1.0:
        out.append(
            Diagnostic(
                "PECLET",
                f"Péclet sayısı {peclet:.3g} > 1: standart Galerkin çözümünde düğüm "
                "salınımı beklenir; n'i artırın.",
                {"n": n, "Pe": peclet},
            )
        )
    if coercivity_min < 0:
        out.append(
            Diagnostic(
                "NON_COERCIVE",
                f"min(r − q′/2) = {coercivity_min:.3g} < 0: kararlılık garanti değil; "
                "asimptotik yakınsama geç başlayabilir.",
                {"n": n, "minimum": coercivity_min},
            )
        )
    if quadrature_approx:
        out.append(
            Diagnostic(
                "QUADRATURE_APPROX",
                "Katsayılardan biri polinom değil: integraller sayısal kareleme ile "
                "yaklaşık hesaplandı.",
                {"n": n},
            )
        )
    if ill_conditioned:
        out.append(
            Diagnostic(
                "ILL_CONDITIONED",
                f"Koşul sayısı {condition_number:.3g} > 1e10: yuvarlama hatası etkili olabilir.",
                {"n": n, "cond": condition_number if condition_number is not None else math.nan},
            )
        )
    if errors is not None and max(errors.l2, errors.h1, errors.max_nodal) < MACHINE_PRECISION_LIMIT:
        out.append(
            Diagnostic(
                "MACHINE_PRECISION",
                "Tam çözüm eleman uzayında: hata makine hassasiyetinde, yakınsama oranı "
                "hesaplanmaz.",
                {"n": n},
            )
        )
    return out


# ------------------------------------------------------------------------------------ sampling
@dataclass(frozen=True)
class Sample:
    """Fields on a common x grid (element end points appear twice: u' may jump there)."""

    x: Array
    uh: Array
    duh: Array
    u: Array | None
    err: Array | None


def points_per_element(mesh: Mesh, max_points: int = MAX_SAMPLE_POINTS) -> int:
    """2 for P1; 9 for P2, reduced to 5 or 3 when the cap would be exceeded (ARCHITECTURE §3)."""
    options = (2,) if mesh.element_type == "P1" else (9, 5, 3)
    for m in options:
        if mesh.n * m <= max_points:
            return m
    raise ValueError(f"mesh with {mesh.n} elements exceeds {max_points} sample points")


def sample_fields(
    mesh: Mesh,
    U: Array,
    u: ScalarField | None = None,
    max_points: int = MAX_SAMPLE_POINTS,
) -> Sample:
    m = points_per_element(mesh, max_points)
    x, uh, duh = fe_values(mesh, U, np.linspace(-1.0, 1.0, m))
    x, uh, duh = x.ravel(), uh.ravel(), duh.ravel()
    if u is None:
        return Sample(x, uh, duh, None, None)
    exact = _field(u, x)
    return Sample(x, uh, duh, exact, exact - uh)


def basis_functions(mesh: Mesh, U: Array, per_element: int = 41) -> tuple[Array, Array, Array]:
    """x grid, global basis functions phi (ndofs, npoints) and u_h = sum U_i phi_i (V3)."""
    xi = np.linspace(-1.0, 1.0, per_element)
    n_ref, _ = reference_basis(mesh.element_type, xi)
    x, uh, _ = fe_values(mesh, U, xi)
    phi = np.zeros((len(mesh.nodes), mesh.n * per_element))
    for e, dofs in enumerate(mesh.connectivity):
        cols = slice(e * per_element, (e + 1) * per_element)
        phi[dofs, cols] = n_ref
    return x.ravel(), phi, uh.ravel()
