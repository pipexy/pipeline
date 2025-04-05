# tests/test_csv_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import pandas as pd
import csv

# Import the adapter to test
sys.path.append('..')
from adapters.CSVAdapter import CSVAdapter


class CSVAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_dir = tempfile.mkdtemp()
        self.test_csv_content = """id,name,age
1,John Doe,30
2,Jane Smith,25
3,Bob Johnson,40"""

        # Create a test CSV file
        self.test_file = os.path.join(self.test_dir, "test.csv")
        with open(self.test_file, 'w') as f:
            f.write(self.test_csv_content)

    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test basic initialization of CSVAdapter"""
        adapter = CSVAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    def test_read_file(self):
        """Test reading a CSV file"""
        adapter = CSVAdapter({})
        adapter.read_file(self.test_file)
        result = adapter.execute()

        # Verify the CSV was read
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)  # 3 rows
        self.assertEqual(list(result.columns), ['id', 'name', 'age'])
        self.assertEqual(result.iloc[0]['name'], 'John Doe')

    def test_read_string(self):
        """Test reading CSV from a string"""
        adapter = CSVAdapter({})
        adapter.read_string(self.test_csv_content)
        result = adapter.execute()

        # Verify the CSV was read
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)  # 3 rows

    def test_filter_data(self):
        """Test filtering CSV data"""
        adapter = CSVAdapter({})
        adapter.read_file(self.test_file)

        # Get the data
        df = adapter.execute()

        # Filter for people older than 25
        filtered = df[df['age'].astype(int) > 25]

        # Verify filter results
        self.assertEqual(len(filtered), 2)
        self.assertTrue('John Doe' in filtered['name'].values)
        self.assertTrue('Bob Johnson' in filtered['name'].values)

    def test_write_file(self):
        """Test writing DataFrame to CSV file"""
        output_file = os.path.join(self.test_dir, "output.csv")

        # Create a sample DataFrame
        data = {
            'id': [4, 5],
            'name': ['Alice Brown', 'Charlie Davis'],
            'age': [35, 45]
        }
        df = pd.DataFrame(data)

        adapter = CSVAdapter({})
        adapter.dataframe(df)
        adapter.write_file(output_file)
        adapter.execute()

        # Verify the file was written
        self.assertTrue(os.path.exists(output_file))

        # Read it back to verify contents
        with open(output_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(rows[0], ['id', 'name', 'age'])
        self.assertEqual(rows[1], ['4', 'Alice Brown', '35'])

        # Clean up
        os.remove(output_file)

    def test_column_operations(self):
        """Test operations on CSV columns"""
        adapter = CSVAdapter({})
        adapter.read_file(self.test_file)
        df = adapter.execute()

        # Add a new column
        df['status'] = ['active', 'inactive', 'active']

        # Verify the new column
        self.assertTrue('status' in df.columns)
        self.assertEqual(df.iloc[0]['status'], 'active')

        # Calculate average age
        avg_age = df['age'].astype(int).mean()
        self.assertEqual(avg_age, (30 + 25 + 40) / 3)

    def test_sort_data(self):
        """Test sorting CSV data"""
        adapter = CSVAdapter({})
        adapter.read_file(self.test_file)
        df = adapter.execute()

        # Sort by age descending
        sorted_df = df.sort_values('age', ascending=False)

        # Verify sorting
        self.assertEqual(sorted_df.iloc[0]['name'], 'Bob Johnson')
        self.assertEqual(sorted_df.iloc[2]['name'], 'Jane Smith')

    def test_error_handling(self):
        """Test handling CSV reading errors"""
        # Non-existent file
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.csv")

        adapter = CSVAdapter({})
        adapter.read_file(nonexistent_file)

        # Should raise an exception
        with self.assertRaises(Exception):
            adapter.execute()


if __name__ == "__main__":
    unittest.main()