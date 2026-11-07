import re

from fem1d import __version__


def test_version_is_semver_string() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
