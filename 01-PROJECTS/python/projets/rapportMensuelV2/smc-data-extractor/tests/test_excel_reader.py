import unittest
from src.core.excel_reader import ExcelReader

class TestExcelReader(unittest.TestCase):

    def setUp(self):
        self.reader = ExcelReader()

    def test_read_valid_file(self):
        # Test reading a valid Excel file
        data = self.reader.read('tests/fixtures/sample_data.xlsx')
        self.assertIsNotNone(data)
        self.assertIn('Convergences', data)
        self.assertIn('Déplacements', data)

    def test_read_invalid_file(self):
        # Test reading an invalid Excel file
        with self.assertRaises(FileNotFoundError):
            self.reader.read('tests/fixtures/non_existent_file.xlsx')

    def test_parse_dates(self):
        # Test parsing various date formats
        dates = ['2023-08-01', '01/08/2023', '2023-08-01 12:00:00']
        parsed_dates = [self.reader.parse_date(date) for date in dates]
        self.assertEqual(parsed_dates[0], '2023-08-01')
        self.assertEqual(parsed_dates[1], '2023-08-01')
        self.assertEqual(parsed_dates[2], '2023-08-01')

    def test_extract_convergences(self):
        # Test extracting convergence data
        data = self.reader.read('tests/fixtures/sample_data.xlsx')
        convergences = self.reader.extract_convergences(data)
        self.assertGreater(len(convergences), 0)

    def test_extract_deplacements(self):
        # Test extracting displacement data
        data = self.reader.read('tests/fixtures/sample_data.xlsx')
        deplacements = self.reader.extract_deplacements(data)
        self.assertGreater(len(deplacements), 0)

if __name__ == '__main__':
    unittest.main()