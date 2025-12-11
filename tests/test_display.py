"""
Test suite for display and formatting functions
"""
import unittest
import sys
import os
import pandas as pd
from io import StringIO

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.display import show_ranked_counties, show_state_summary


class TestDisplay(unittest.TestCase):
    """Test cases for display and output formatting"""
    
    def test_show_ranked_counties_runs(self):
        """Test that show_ranked_counties executes without error"""
        # Create sample data with all required columns
        data = {
            'county_name': ['Adams', 'Allegheny', 'Beaver'],
            'swing_score': [85.5, 92.3, 78.1],
            'margin_change_abs': [0.08, 0.09, 0.07],
            'closeness_latest': [0.85, 0.95, 0.75],
            'turnout_latest': [0.65, 0.75, 0.60],
            'votes_latest': [10000, 50000, 8000]
        }
        df = pd.DataFrame(data)
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            show_ranked_counties(df, top=3)
            output = sys.stdout.getvalue()
            
            # Check that county names appear in output
            self.assertIn('Adams', output)
            self.assertIn('Allegheny', output)
        finally:
            sys.stdout = old_stdout
    
    def test_show_state_summary_runs(self):
        """Test that show_state_summary executes without error"""
        data = {
            'state_code': ['PA', 'PA', 'PA'],
            'county_name': ['Adams', 'Allegheny', 'Beaver'],
            'swing_score': [8550, 9230, 7810]
        }
        df = pd.DataFrame(data)
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            show_state_summary(df)
            output = sys.stdout.getvalue()
            
            # Check that output contains county count
            self.assertIn('3', output)
        finally:
            sys.stdout = old_stdout


if __name__ == '__main__':
    unittest.main()
