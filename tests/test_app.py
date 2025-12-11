"""
Test suite for Flask application endpoints
"""
import unittest
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app


class TestFlaskApp(unittest.TestCase):
    """Test cases for Flask application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_home_page(self):
        """Test that home page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_home_page_content(self):
        """Test that home page contains expected content"""
        response = self.client.get('/')
        self.assertIn(b'Swing', response.data)
    
    def tearDown(self):
        """Clean up after tests"""
        pass


if __name__ == '__main__':
    unittest.main()
