import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db 
from models import Juegos 

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_juego_creation(self):
        j = Juegos(nombre='Test', descripcion='Desc', precio=9.99) 
        db.session.add(j)
        db.session.commit()
        self.assertEqual(Juegos.query.count(), 1)  

if __name__ == '__main__':
    unittest.main()