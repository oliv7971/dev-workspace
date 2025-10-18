import unittest
from src.core.data_extractor import DataExtractor

class TestDataExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = DataExtractor()

    def test_extract_convergences(self):
        # Test extraction of convergence data from a sample Excel file
        sample_file = 'tests/fixtures/sample_data.xlsx'
        result = self.extractor.extract_convergences(sample_file)
        self.assertIsInstance(result, dict)
        self.assertIn('BG', result)
        self.assertIn('HG', result)

    def test_extract_displacements(self):
        # Test extraction of displacement data from a sample Excel file
        sample_file = 'tests/fixtures/sample_data.xlsx'
        result = self.extractor.extract_displacements(sample_file)
        self.assertIsInstance(result, dict)
        self.assertIn('DPM', result)
        self.assertIn('DH', result)

    def test_handle_missing_data(self):
        # Test how the extractor handles missing data
        sample_file = 'tests/fixtures/sample_data_missing.xlsx'
        result = self.extractor.extract_convergences(sample_file)
        self.assertEqual(result, {})

    def test_invalid_file_format(self):
        # Test how the extractor handles invalid file formats
        sample_file = 'tests/fixtures/invalid_file.txt'
        with self.assertRaises(ValueError):
            self.extractor.extract_convergences(sample_file)

if __name__ == '__main__':
    unittest.main()