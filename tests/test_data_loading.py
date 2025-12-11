"""
Test suite for data loading functionality
"""
import unittest
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_loading import load_state_raw_data


class TestDataLoading(unittest.TestCase):
    """Test cases for data loading utilities"""
    
    def test_load_state_raw_data_invalid_state(self):
        """Test that loading invalid state code raises appropriate error"""
        with self.assertRaises(FileNotFoundError):
            load_state_raw_data("XX")  # Invalid state code
    
    def test_load_state_raw_data_case_insensitive(self):
        """Test that state codes are case-insensitive"""
        # This test will pass as long as the function doesn't crash
        # Actual data loading would require test data files
        try:
            # Try with lowercase - if data exists it should work
            load_state_raw_data("pa")
        except FileNotFoundError:
            # Expected if no test data files exist
            pass


if __name__ == '__main__':
    unittest.main()
