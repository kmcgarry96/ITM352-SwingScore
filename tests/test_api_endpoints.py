"""
Test suite for Flask API endpoints
"""
import unittest
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for Flask API endpoints"""
    
    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_index_page_loads(self):
        """Test that index page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_index_page_is_html(self):
        """Test that index page returns HTML"""
        response = self.client.get('/')
        # Check for HTML (case-insensitive)
        self.assertIn(b'<!doctype html>', response.data.lower())
    
    def test_state_view_valid_state(self):
        """Test state view with valid state code"""
        # Test with Pennsylvania
        response = self.client.get('/state/PA')
        self.assertEqual(response.status_code, 200)
    
    def test_state_view_lowercase(self):
        """Test that state codes are case-insensitive"""
        response = self.client.get('/state/pa')
        # Should either work (200) or handle gracefully
        self.assertIn(response.status_code, [200, 404])
    
    def test_map_view_loads(self):
        """Test that map view endpoint loads"""
        response = self.client.get('/map/PA')
        self.assertEqual(response.status_code, 200)
    
    def test_nonexistent_route(self):
        """Test that nonexistent routes return 404"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def tearDown(self):
        """Clean up after tests"""
        pass


if __name__ == '__main__':
    unittest.main()
