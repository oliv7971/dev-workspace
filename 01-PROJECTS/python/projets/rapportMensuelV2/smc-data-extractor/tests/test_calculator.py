import unittest
from src.core.calculator import Calculator

class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = Calculator()

    def test_periodic_calculation(self):
        last_in_month = 10.0
        last_before_month = 5.0
        expected_periodic = last_in_month - last_before_month
        result = self.calculator.calculate_periodic(last_in_month, last_before_month)
        self.assertEqual(result, expected_periodic)

    def test_cumulative_calculation(self):
        last_global = 20.0
        expected_cumulative = last_global
        result = self.calculator.calculate_cumulative(last_global)
        self.assertEqual(result, expected_cumulative)

    def test_periodic_calculation_no_previous(self):
        last_in_month = 10.0
        last_before_month = None
        expected_periodic = last_in_month  # If no previous value, periodic is just the last in month
        result = self.calculator.calculate_periodic(last_in_month, last_before_month)
        self.assertEqual(result, expected_periodic)

    def test_cumulative_calculation_no_values(self):
        last_global = None
        expected_cumulative = 0.0  # Assuming 0 if no global value
        result = self.calculator.calculate_cumulative(last_global)
        self.assertEqual(result, expected_cumulative)

if __name__ == '__main__':
    unittest.main()