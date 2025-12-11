"""
Test suite for swing score component calculations
"""
import unittest
import sys
import os
import pandas as pd

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.swing_score import compute_swing_components, normalize_series


class TestSwingComponents(unittest.TestCase):
    """Test cases for swing score component calculations"""
    
    def test_compute_swing_components_structure(self):
        """Test that compute_swing_components returns expected structure"""
        # Create sample aggregated data
        data = {
            'state_code': ['PA', 'PA', 'PA', 'PA'],
            'county_fips': ['42001', '42001', '42003', '42003'],
            'county_name': ['Adams', 'Adams', 'Allegheny', 'Allegheny'],
            'year': [2016, 2020, 2016, 2020],
            'dem_votes': [90, 100, 450, 500],
            'rep_votes': [150, 150, 450, 450],
            'total_votes': [240, 250, 900, 950],
            'margin': [-60, -50, 0, 50],
            'margin_pct': [-0.25, -0.20, 0.0, 0.053]
        }
        df = pd.DataFrame(data)
        
        result = compute_swing_components(df, year_prev=2016, year_latest=2020)
        
        # Check that result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check for expected columns (using actual column names from the function)
        expected_cols = ['county_name', 'margin_change_abs', 'closeness_latest', 
                        'turnout_latest', 'votes_latest', 'swing_score']
        for col in expected_cols:
            self.assertIn(col, result.columns)
    
    def test_normalize_series_range(self):
        """Test that normalized values are between 0 and 1"""
        s = pd.Series([5, 10, 15, 20, 25, 30])
        result = normalize_series(s)
        
        # All values should be between 0 and 1
        self.assertTrue((result >= 0).all())
        self.assertTrue((result <= 1).all())
    
    def test_normalize_series_empty(self):
        """Test normalize_series with empty series"""
        s = pd.Series([], dtype=float)
        result = normalize_series(s)
        
        # Should return empty series
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()
