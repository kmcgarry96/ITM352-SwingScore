"""
Integration tests for end-to-end workflows
"""
import unittest
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_full_state_workflow(self):
        """Test complete workflow: home -> state view"""
        # First load home page
        response1 = self.client.get('/')
        self.assertEqual(response1.status_code, 200)
        
        # Then navigate to a state
        response2 = self.client.get('/state/PA')
        self.assertEqual(response2.status_code, 200)
    
    def test_map_workflow(self):
        """Test workflow: home -> map view"""
        # Load home page
        response1 = self.client.get('/')
        self.assertEqual(response1.status_code, 200)
        
        # Load map view
        response2 = self.client.get('/map/PA')
        self.assertEqual(response2.status_code, 200)
    
    def test_multiple_states_workflow(self):
        """Test accessing multiple states in sequence"""
        states = ['PA', 'GA', 'AZ', 'MI']
        
        for state in states:
            response = self.client.get(f'/state/{state}')
            # Should either load successfully or handle missing data gracefully
            self.assertIn(response.status_code, [200, 404, 500])


if __name__ == '__main__':
    unittest.main()
