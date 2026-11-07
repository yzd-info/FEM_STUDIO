"""M2.1: hand-computed reference systems (docs/BENCHMARKS.md §4), at fraction level.

These fixtures are not yet compared against the solver (that starts in M2.2+);
this test only proves each fixture is internally consistent: the assembled
K U = F holds exactly at every interior (non-Dirichlet) node.
"""

import json
from fractions import Fraction
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

FIXTURE_IDS = ["B1_P1_n2", "B1_P1_n4", "B3_P1_n2"]


def _load(fixture_id: str) -> dict:
    with open(FIXTURES_DIR / f"{fixture_id}.json") as fh:
        return json.load(fh)


def _as_fraction_matrix(rows: list[list[str]]) -> list[list[Fraction]]:
    return [[Fraction(v) for v in row] for row in rows]


def _as_fraction_vector(values: list[str]) -> list[Fraction]:
    return [Fraction(v) for v in values]


@pytest.mark.parametrize("fixture_id", FIXTURE_IDS)
def test_fixture_dimensions_match_p1_dof_count(fixture_id) -> None:
    data = _load(fixture_id)
    assert data["element"] == "P1"
    expected_dofs = data["n"] + 1
    assert len(data["K"]) == expected_dofs
    assert all(len(row) == expected_dofs for row in data["K"])
    assert len(data["F"]) == expected_dofs
    assert len(data["U"]) == expected_dofs


@pytest.mark.parametrize("fixture_id", FIXTURE_IDS)
def test_fixture_dirichlet_boundary_values_are_zero(fixture_id) -> None:
    data = _load(fixture_id)
    U = _as_fraction_vector(data["U"])
    assert U[0] == Fraction(0)
    assert U[-1] == Fraction(0)


@pytest.mark.parametrize("fixture_id", FIXTURE_IDS)
def test_fixture_is_symmetric(fixture_id) -> None:
    data = _load(fixture_id)
    K = _as_fraction_matrix(data["K"])
    for i, row in enumerate(K):
        for j, value in enumerate(row):
            assert value == K[j][i]


@pytest.mark.parametrize("fixture_id", FIXTURE_IDS)
def test_fixture_satisfies_KU_equals_F_at_interior_nodes(fixture_id) -> None:
    data = _load(fixture_id)
    K = _as_fraction_matrix(data["K"])
    F = _as_fraction_vector(data["F"])
    U = _as_fraction_vector(data["U"])
    n_dofs = len(F)
    for i in range(1, n_dofs - 1):
        lhs = sum(K[i][j] * U[j] for j in range(n_dofs))
        assert lhs == F[i], f"{fixture_id}: row {i} mismatch ({lhs} != {F[i]})"
