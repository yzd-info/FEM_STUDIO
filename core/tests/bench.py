"""Test support (not part of the package).

* Benchmark definitions from docs/BENCHMARKS.md §1.
* `solve_fem`: assembly -> boundary conditions -> linear solve, using the package.
* `fe_gauss_data` / `error_norms`: an INDEPENDENT evaluation of finite-element functions and
  error norms (own Lagrange formulas and own Gauss rule; it does not import `fem1d.elements`
  or `fem1d.quadrature`), so errors reported by tests do not rely on the code under test.
* Random manufactured-solution problems: the right-hand side is derived with exact
  polynomial algebra (numpy.polynomial), never with the FEM code.
* `scipy_reference`: boundary value problem solved by a different algorithm (scipy.solve_bvp).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

import numpy as np
from numpy.polynomial import Polynomial
from numpy.typing import NDArray
from scipy.integrate import solve_bvp

from fem1d.assembly import assemble
from fem1d.boundary import BoundaryCondition, apply_boundary_conditions, expand_solution
from fem1d.mesh import ElementType, Mesh, build_mesh
from fem1d.solver import solve_linear_system

Fn = Callable[[float], float]


@dataclass(frozen=True)
class Problem:
    name: str
    domain: tuple[float, float]
    p: Fn
    q: Fn
    r: Fn
    f: Fn
    degrees: tuple[int | None, int | None, int | None, int | None]  # p, q, r, f
    left: BoundaryCondition
    right: BoundaryCondition
    u: Fn | None = None
    du: Fn | None = None


def _c(value: float) -> Fn:
    return lambda x: value + 0.0 * x


def _dirichlet(value: float) -> BoundaryCondition:
    return BoundaryCondition(0.0, 1.0, value)


_PI = np.pi
_EPS = 0.05
_K = 10.0


def benchmark(name: str) -> Problem:
    """Problems of docs/BENCHMARKS.md §1 (all on [0, 1])."""
    d = (0.0, 1.0)
    zero = _dirichlet(0.0)
    table: dict[str, Problem] = {
        "B1": Problem(
            "B1",
            d,
            _c(1),
            _c(0),
            _c(0),
            _c(1),
            (0, 0, 0, 0),
            zero,
            zero,
            lambda x: x * (1 - x) / 2,
            lambda x: 0.5 - x,
        ),
        "B2": Problem(
            "B2",
            d,
            _c(1),
            _c(0),
            _c(0),
            lambda x: _PI**2 * np.sin(_PI * x),
            (0, 0, 0, None),
            zero,
            zero,
            lambda x: np.sin(_PI * x),
            lambda x: _PI * np.cos(_PI * x),
        ),
        "B3": Problem(
            "B3",
            d,
            lambda x: 1 + x,
            _c(0),
            _c(0),
            _c(1),
            (1, 0, 0, 0),
            zero,
            zero,
            lambda x: np.log(1 + x) / np.log(2) - x,
            lambda x: 1 / ((1 + x) * np.log(2)) - 1,
        ),
        "B4": Problem(
            "B4",
            d,
            _c(1),
            _c(0),
            _c(1),
            lambda x: x,
            (0, 0, 0, 1),
            zero,
            zero,
            lambda x: x - np.sinh(x) / np.sinh(1),
            lambda x: 1 - np.cosh(x) / np.sinh(1),
        ),
        "B5": Problem(
            "B5",
            d,
            _c(_EPS),
            _c(1),
            _c(0),
            _c(0),
            (0, 0, 0, 0),
            zero,
            _dirichlet(1.0),
            lambda x: np.expm1(x / _EPS) / np.expm1(1 / _EPS),
            lambda x: np.exp(x / _EPS) / _EPS / np.expm1(1 / _EPS),
        ),
        "B6": Problem(
            "B6",
            d,
            _c(1),
            _c(0),
            _c(0),
            _c(2),
            (0, 0, 0, 0),
            zero,
            BoundaryCondition(1.0, 0.0, 0.0),
            lambda x: 2 * x - x * x,
            lambda x: 2 - 2 * x,
        ),
        "B7": Problem(
            "B7",
            d,
            _c(1),
            _c(0),
            _c(0),
            _c(1),
            (0, 0, 0, 0),
            zero,
            BoundaryCondition(1.0, 1.0, 1.0),
            lambda x: -x * x / 2 + 1.25 * x,
            lambda x: -x + 1.25,
        ),
        "B8": Problem(
            "B8",
            d,
            _c(1),
            _c(0),
            _c(-_K * _K),
            _c(0),
            (0, 0, 0, 0),
            zero,
            _dirichlet(1.0),
            lambda x: np.sin(_K * x) / np.sin(_K),
            lambda x: _K * np.cos(_K * x) / np.sin(_K),
        ),
        "B9": Problem(
            "B9",
            d,
            np.exp,
            _c(0),
            _c(0),
            lambda x: np.exp(x) * (1 + 2 * x),
            (None, 0, 0, None),
            zero,
            zero,
            lambda x: x * (1 - x),
            lambda x: 1 - 2 * x,
        ),
        "B10": Problem(
            "B10",
            d,
            _c(1),
            _c(1),
            _c(2),
            lambda x: 2 * np.exp(x),
            (0, 0, 0, None),
            BoundaryCondition(-1.0, 2.0, 1.0),
            _dirichlet(float(np.e)),
            np.exp,
            np.exp,
        ),
        "M2": Problem(
            "M2",
            d,
            _c(1),
            _c(0),
            _c(0),
            _c(-2),
            (0, 0, 0, 0),
            zero,
            _dirichlet(1.0),
            lambda x: x**2,
            lambda x: 2 * x,
        ),
        "M3": Problem(
            "M3",
            d,
            _c(1),
            _c(0),
            _c(0),
            lambda x: -6 * x,
            (0, 0, 0, 1),
            zero,
            _dirichlet(1.0),
            lambda x: x**3,
            lambda x: 3 * x**2,
        ),
        "M4": Problem(
            "M4",
            d,
            _c(1),
            _c(0),
            _c(0),
            lambda x: -12 * x**2,
            (0, 0, 0, 2),
            zero,
            _dirichlet(1.0),
            lambda x: x**4,
            lambda x: 4 * x**3,
        ),
    }
    return table[name]


def solve_fem(
    problem: Problem, n: int, element: ElementType, record_log: bool = False
) -> tuple[Mesh, NDArray[np.float64]]:
    """Full pipeline with the package: mesh -> assemble -> boundary conditions -> solve."""
    mesh = build_mesh(problem.domain, n, element)
    pd, qd, rd, fd = problem.degrees
    system = assemble(
        mesh, problem.p, pd, problem.q, qd, problem.r, rd, problem.f, fd, record_log=record_log
    )
    reduced = apply_boundary_conditions(system, problem.p, problem.left, problem.right)
    solution = solve_linear_system(reduced.K_ff, reduced.F_f, compute_condition=False)
    return mesh, expand_solution(reduced, solution.x)


# ----------------------------------------------------------------- independent FE evaluation
def fe_gauss_data(
    mesh: Mesh, U: NDArray[np.float64], m: int = 10
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Gauss points x, weights w, u_h(x), u_h'(x) of the FE function with nodal values U."""
    xg, wg = np.polynomial.legendre.leggauss(m)
    xs: list[NDArray[np.float64]] = []
    ws: list[NDArray[np.float64]] = []
    uh: list[NDArray[np.float64]] = []
    duh: list[NDArray[np.float64]] = []
    for dofs in mesh.connectivity:
        x0, x1 = mesh.nodes[dofs[0]], mesh.nodes[dofs[-1]]
        h = x1 - x0
        if len(dofs) == 2:
            N = np.array([(1 - xg) / 2, (1 + xg) / 2])
            dN = np.array([-0.5 + 0 * xg, 0.5 + 0 * xg])
        else:
            N = np.array([xg * (xg - 1) / 2, 1 - xg**2, xg * (xg + 1) / 2])
            dN = np.array([xg - 0.5, -2 * xg, xg + 0.5])
        c = U[dofs]
        xs.append((x0 + x1) / 2 + h / 2 * xg)
        ws.append(wg * h / 2)
        uh.append(c @ N)
        duh.append(c @ dN * 2 / h)
    return np.concatenate(xs), np.concatenate(ws), np.concatenate(uh), np.concatenate(duh)


def vertex_dofs(mesh: Mesh) -> NDArray[np.int64]:
    """DOFs at element end points (P1: all nodes; P2: every second node)."""
    step = 1 if mesh.element_type == "P1" else 2
    return np.arange(0, len(mesh.nodes), step)


def error_norms(mesh: Mesh, U: NDArray[np.float64], u: Fn, du: Fn) -> tuple[float, float, float]:
    """(L2 error, H1 semi-norm error, max error at element end points)."""
    x, w, uh, duh = fe_gauss_data(mesh, U)
    l2 = float(np.sqrt(np.sum(w * (u(x) - uh) ** 2)))
    h1 = float(np.sqrt(np.sum(w * (du(x) - duh) ** 2)))
    v = vertex_dofs(mesh)
    nodal = float(np.max(np.abs(U[v] - u(mesh.nodes[v]))))
    return l2, h1, nodal


def observed_rates(errors: list[float]) -> list[float]:
    """log2 ratios of successive errors (meshes are successively halved)."""
    return [float(np.log2(a / b)) for a, b in zip(errors[:-1], errors[1:], strict=True)]


# ------------------------------------------------------------------ random manufactured problems
def random_mms_problem(seed: int, u_degree: int) -> Problem:
    """Random polynomial coefficients and exact solution of given degree on [0, 1].

    f is derived exactly: f = -(p u')' + q u' + r u with polynomial algebra. p >= 0.5, r >= 0.1,
    so every boundary-condition combination below is well posed.
    """
    rng = np.random.default_rng(seed)
    u_coef = rng.uniform(-1.0, 1.0, u_degree + 1)
    u_coef[-1] = rng.choice([-1.0, 1.0]) * rng.uniform(0.5, 1.5)
    u = Polynomial(u_coef)
    p = Polynomial([rng.uniform(1.5, 2.5), rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)])
    q = Polynomial([rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0)])
    r = Polynomial([rng.uniform(0.5, 1.5), rng.uniform(-0.4, 0.4)])
    du = u.deriv()
    f = -(p * du).deriv() + q * du + r * u

    def boundary(x0: float, alpha: float) -> BoundaryCondition:
        kind = rng.choice(["dirichlet", "neumann", "robin"])
        if kind == "dirichlet":
            beta = float(rng.uniform(0.5, 2.0))
            return BoundaryCondition(0.0, beta, beta * float(u(x0)))
        if kind == "neumann":
            return BoundaryCondition(alpha, 0.0, alpha * float(du(x0)))
        sigma = float(rng.uniform(0.5, 3.0))
        return BoundaryCondition(alpha, sigma, alpha * float(du(x0)) + sigma * float(u(x0)))

    left = boundary(0.0, -1.0)
    right = boundary(1.0, 1.0)
    return Problem(
        f"random-mms-{seed}-deg{u_degree}",
        (0.0, 1.0),
        p,
        q,
        r,
        f,
        (p.degree(), q.degree(), r.degree(), f.degree()),
        left,
        right,
        u,
        du,
    )


def shifted(problem: Problem, new_domain: tuple[float, float], u: Fn, du: Fn) -> Problem:
    """Same coefficients on another interval with a given exact solution."""
    return replace(problem, domain=new_domain, u=u, du=du)


# ------------------------------------------------------------------------------ scipy oracle
def scipy_reference(problem: Problem, x_eval: NDArray[np.float64]) -> NDArray[np.float64]:
    """Solve the same BVP with scipy.solve_bvp (flux form y = [u, p u']) and evaluate."""
    a, b = problem.domain

    def rhs(x: NDArray[np.float64], y: NDArray[np.float64]) -> NDArray[np.float64]:
        p = problem.p(x)
        return np.vstack([y[1] / p, problem.q(x) * y[1] / p + problem.r(x) * y[0] - problem.f(x)])

    def residual(ya: NDArray[np.float64], yb: NDArray[np.float64]) -> NDArray[np.float64]:
        pa, pb = float(problem.p(a)), float(problem.p(b))
        lb, rb = problem.left, problem.right
        return np.array(
            [
                lb.alpha * ya[1] / pa + lb.beta * ya[0] - lb.gamma,
                rb.alpha * yb[1] / pb + rb.beta * yb[0] - rb.gamma,
            ]
        )

    x0 = np.linspace(a, b, 2000)
    result = solve_bvp(rhs, residual, x0, np.zeros((2, x0.size)), tol=1e-9, max_nodes=10**6)
    if not result.success:
        raise RuntimeError(f"scipy.solve_bvp failed for {problem.name}: {result.message}")
    return np.asarray(result.sol(x_eval)[0])


def singular_s1() -> Problem:
    """S1 of docs/BENCHMARKS.md: u = x^(3/4), -u'' = (3/16) x^(-5/4); not in H^2 (§6.4)."""
    a = 0.75
    return Problem(
        "S1",
        (0.0, 1.0),
        _c(1),
        _c(0),
        _c(0),
        lambda x: a * (1 - a) * x ** (a - 2),
        (0, 0, 0, None),
        _dirichlet(0.0),
        _dirichlet(1.0),
        lambda x: x**a,
        lambda x: a * x ** (a - 1),
    )


# BENCHMARKS.md §3.1: (P1 n=8, P1 n=64, P2 n=8, P2 n=64), each as (L2, H1); tolerance 1 %.
REFERENCE = {
    "B2": [
        (9.921e-03, 2.512e-01),
        (1.555e-04, 3.148e-02),
        (2.457e-04, 1.274e-02),
        (4.809e-07, 1.995e-04),
    ],
    "B3": [
        (1.175e-03, 2.805e-02),
        (1.843e-05, 3.514e-03),
        (1.418e-05, 7.346e-04),
        (2.786e-08, 1.155e-05),
    ],
    "B4": [
        (7.363e-04, 1.954e-02),
        (1.153e-05, 2.448e-03),
        (1.133e-05, 5.874e-04),
        (2.214e-08, 9.183e-06),
    ],
    "B10": [
        (1.885e-03, 6.447e-02),
        (2.945e-05, 8.062e-03),
        (2.004e-05, 1.040e-03),
        (3.921e-08, 1.626e-05),
    ],
    "M3": [
        (4.932e-03, 1.248e-01),
        (7.720e-05, 1.562e-02),
        (6.739e-05, 3.494e-03),
        (1.316e-07, 5.459e-05),
    ],
    "M4": [
        (7.616e-03, 1.928e-01),
        (1.196e-04, 2.420e-02),
        (1.553e-04, 8.054e-03),
        (3.040e-07, 1.261e-04),
    ],
    "B1": [(1.426e-03, 3.608e-02), (2.229e-05, 4.511e-03), None, None],
    "B7": [(1.426e-03, 3.608e-02), (2.229e-05, 4.511e-03), None, None],
}
CASES = [("P1", 8), ("P1", 64), ("P2", 8), ("P2", 64)]
