"""Make the shared test-support module `bench` importable from every test directory."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
