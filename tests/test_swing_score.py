"""
Test suite for swing score calculations
"""
import unittest
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.swing_score import normalize_series
import pandas as pd


class TestSwingScore(unittest.TestCase):
    """Test cases for swing score calculation logic"""
    
    def test_normalize_series_basic(self):
        """Test basic normalize_series functionality"""
        s = pd.Series([10, 20, 30, 40, 50])
        result = normalize_series(s)
        
        # Check that min is 0 and max is 1
        self.assertAlmostEqual(result.min(), 0.0)
        self.assertAlmostEqual(result.max(), 1.0)
        self.assertEqual(len(result), 5)
    
    def test_normalize_series_all_same(self):
        """Test normalize_series when all values are equal"""
        s = pd.Series([5, 5, 5, 5])
        result = normalize_series(s)
        
        # Should return 0.5 for all values
        for val in result:
            self.assertAlmostEqual(val, 0.5)


if __name__ == '__main__':
    unittest.main()
