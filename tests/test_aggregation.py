"""
Test suite for data aggregation functionality
"""
import unittest
import sys
import os
import pandas as pd

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.aggregation import aggregate_to_county_year


class TestAggregation(unittest.TestCase):
    """Test cases for data aggregation utilities"""
    
    def test_aggregate_to_county_year_basic(self):
        """Test basic county-year aggregation"""
        # Create sample data
        data = {
            'state_code': ['PA', 'PA', 'PA', 'PA'],
            'county_fips': ['42001', '42001', '42003', '42003'],
            'county_name': ['Adams', 'Adams', 'Allegheny', 'Allegheny'],
            'year': [2020, 2020, 2020, 2020],
            'party_simplified': ['DEM', 'REP', 'DEM', 'REP'],
            'votes': [100, 150, 500, 450]
        }
        df = pd.DataFrame(data)
        
        result = aggregate_to_county_year(df)
        
        # Check that we have 2 counties
        self.assertEqual(len(result), 2)
        
        # Check that required columns exist
        required_cols = ['state_code', 'county_fips', 'county_name', 'year', 
                        'dem_votes', 'rep_votes', 'total_votes', 'margin']
        for col in required_cols:
            self.assertIn(col, result.columns)
    
    def test_aggregate_to_county_year_margins(self):
        """Test that margins are calculated correctly"""
        data = {
            'state_code': ['PA', 'PA'],
            'county_fips': ['42001', '42001'],
            'county_name': ['Adams', 'Adams'],
            'year': [2020, 2020],
            'party_simplified': ['DEM', 'REP'],
            'votes': [100, 150]
        }
        df = pd.DataFrame(data)
        
        result = aggregate_to_county_year(df)
        
        # margin should be dem_votes - rep_votes = 100 - 150 = -50
        self.assertEqual(result.iloc[0]['margin'], -50)
        
        # total_votes should be 250
        self.assertEqual(result.iloc[0]['total_votes'], 250)


if __name__ == '__main__':
    unittest.main()
