import unittest
from taxes import calc_multiplier  # Adjust this import as necessary

class TestCalcMultiplier(unittest.TestCase):
    def test_below_cutoff(self):
        """Test weight below the cut_off."""
        self.assertEqual(calc_multiplier(800), 0)

    def test_at_cutoff(self):
        """Test weight exactly at the cut_off."""
        self.assertEqual(calc_multiplier(900), 0)

    def test_one_step_above(self):
        """Test weight just one step above the cut_off."""
        self.assertEqual(calc_multiplier(1000), 1)

    def test_multiple_steps_above(self):
        """Test weight multiple steps above the cut_off."""
        self.assertEqual(calc_multiplier(1200), 3)

    def test_large_number(self):
        """Test with a large number."""
        self.assertEqual(calc_multiplier(1900), 10)

    def test_custom_cutoff_and_step(self):
        """Test with custom cut_off and step values."""
        self.assertEqual(calc_multiplier(1300, cut_off=1000, step=50), 6)

    def test_edge_case(self):
        """Test on the edge case where result is just below adding another tax."""
        self.assertEqual(calc_multiplier(999), 0)

if __name__ == '__main__':
    unittest.main()
