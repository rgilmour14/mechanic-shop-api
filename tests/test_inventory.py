from app import create_app
from app.models import db, Inventory
import unittest
from app.utils.util import encode_token

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.part = Inventory(name="test_part", price=100.00)
            db.session.add(self.part)
            db.session.commit()
        
        
    def test_create_part(self):
        part_payload = {
            "name": "Brake Pad",
            "price": 150.00
        }

        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Brake Pad")
        
    def test_invalid_creation(self):
        part_payload = {
            "name": "Brake Pad"        }

        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Missing data for required field.'])
        
    def test_update_part(self):
        update_payload = {
            "price": 110.00,
        }

        response = self.client.put('/inventory/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'test_part')
        self.assertEqual(response.json['price'], 110.00)

        
    def test_get_all_parts(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_part')
        
    def test_get_part_by_id(self):
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'test_part')
    
        
    def test_delete_part(self):
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)
        