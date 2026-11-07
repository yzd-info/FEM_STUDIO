"""M1.2: uniform mesh with P1/P2 connectivity (docs/MATH_SPEC.md §4)."""

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from fem1d.mesh import build_mesh


@given(
    domain=st.tuples(
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
    ).filter(lambda ab: ab[1] - ab[0] > 1e-6),
    n=st.integers(min_value=1, max_value=20),
)
def test_p1_node_count_and_endpoints(domain, n) -> None:
    a, b = domain
    mesh = build_mesh(domain, n, "P1")
    assert len(mesh.nodes) == n + 1
    assert mesh.nodes[0] == pytest.approx(a)
    assert mesh.nodes[-1] == pytest.approx(b)
    assert np.all(np.diff(mesh.nodes) > 0)


@given(
    domain=st.tuples(
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
    ).filter(lambda ab: ab[1] - ab[0] > 1e-6),
    n=st.integers(min_value=1, max_value=20),
)
def test_p2_node_count_and_endpoints(domain, n) -> None:
    a, b = domain
    mesh = build_mesh(domain, n, "P2")
    assert len(mesh.nodes) == 2 * n + 1
    assert mesh.nodes[0] == pytest.approx(a)
    assert mesh.nodes[-1] == pytest.approx(b)
    assert np.all(np.diff(mesh.nodes) > 0)


def test_p1_connectivity_is_consecutive_pairs() -> None:
    mesh = build_mesh((0.0, 1.0), 4, "P1")
    assert mesh.connectivity.shape == (4, 2)
    for k in range(4):
        assert list(mesh.connectivity[k]) == [k, k + 1]


def test_p2_connectivity_matches_spec_formula() -> None:
    mesh = build_mesh((0.0, 1.0), 4, "P2")
    assert mesh.connectivity.shape == (4, 3)
    for k in range(4):
        assert list(mesh.connectivity[k]) == [2 * k, 2 * k + 1, 2 * k + 2]


def test_p2_midpoint_nodes_lie_between_element_boundaries() -> None:
    mesh = build_mesh((0.0, 2.0), 2, "P2")
    for k in range(2):
        left, mid, right = mesh.connectivity[k]
        x_left, x_mid, x_right = mesh.nodes[[left, mid, right]]
        assert x_mid == pytest.approx((x_left + x_right) / 2)


def test_uniform_spacing_matches_h() -> None:
    a, b, n = -1.0, 3.0, 8
    h = (b - a) / n
    mesh = build_mesh((a, b), n, "P1")
    assert np.allclose(np.diff(mesh.nodes), h)


@pytest.mark.parametrize("element_type", ["P1", "P2"])
def test_rejects_non_positive_element_count(element_type) -> None:
    with pytest.raises(ValueError):
        build_mesh((0.0, 1.0), 0, element_type)
