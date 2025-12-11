"""
Test suite for input validation and edge cases
"""
import unittest
import sys
import os
import pandas as pd

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_loading import load_state_raw_data
from backend.swing_score import normalize_series


class TestValidation(unittest.TestCase):
    """Test cases for input validation and edge cases"""
    
    def test_invalid_state_code(self):
        """Test that invalid state codes raise FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            load_state_raw_data("INVALID")
    
    def test_empty_state_code(self):
        """Test that empty state code raises error"""
        with self.assertRaises(FileNotFoundError):
            load_state_raw_data("")
    
    def test_normalize_single_value(self):
        """Test normalize_series with single value"""
        s = pd.Series([42])
        result = normalize_series(s)
        
        # Single value should normalize to 0.5
        self.assertAlmostEqual(result.iloc[0], 0.5)
    
    def test_normalize_negative_values(self):
        """Test normalize_series with negative values"""
        s = pd.Series([-10, -5, 0, 5, 10])
        result = normalize_series(s)
        
        # Should still normalize to 0-1 range
        self.assertAlmostEqual(result.min(), 0.0)
        self.assertAlmostEqual(result.max(), 1.0)
    
    def test_normalize_with_nan(self):
        """Test normalize_series behavior with NaN values"""
        s = pd.Series([1, 2, None, 4, 5])
        result = normalize_series(s)
        
        # Result should have same length
        self.assertEqual(len(result), len(s))


if __name__ == '__main__':
    unittest.main()
