import importlib.util
import json
import unittest
from pathlib import Path

from motorrijtuigenbelasting import EnergySource

ROOT = Path(__file__).parent.parent


def load_generator():
    spec = importlib.util.spec_from_file_location(
        "generate_output", ROOT / "scripts" / "generate_output.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGeneratedOutput(unittest.TestCase):
    def test_benzine_output_is_up_to_date(self):
        """Run `python scripts/generate_output.py benzine` after changing tax data"""
        with open(ROOT / "output" / "benzine.json", encoding="utf-8") as f:
            committed = json.load(f)
        self.assertEqual(committed, load_generator().generate(EnergySource.BENZINE))
