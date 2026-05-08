import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_access(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302) 

    def test_profile_requires_login(self):
        resp = self.client.get('/profile')
        self.assertEqual(resp.status_code, 404)  

if __name__ == '__main__':
    unittest.main()