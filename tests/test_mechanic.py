from app import create_app
from app.models import db, Mechanic
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.mechanic = Mechanic(name="test_mechanic", email="test@email.com", phone="1234567899", salary="50000")
            db.session.add(self.mechanic)
            db.session.commit() 
        
        
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1234567890",
            "salary": 60000
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")
        
    def test_invalid_creation(self):
        mechanic_payload = {
            "name": "John Doe",
            "phone": "1234567890",
            "salary": 60000
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])
        
        
    def test_update_mechanic(self):
        update_payload = {
            "name": "Peter",
        }

        response = self.client.put('/mechanics/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter') 
        self.assertEqual(response.json['email'], 'test@email.com')
        
    def test_get_all_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')
        
        
    def test_delete_mechanic(self):
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)

    def test_mechanic_ticket_list(self):
        response = self.client.get('/mechanics/mechanic-ticket-list')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')
    
    def test_search_mechanic(self):
        with self.app.app_context():
            mechanic = Mechanic(
                name="Peter Parker",
                email="peter@email.com",
                phone="111-222-3333",
                salary=50000
            )
            db.session.add(mechanic)
            db.session.commit()
            
        response = self.client.get('/mechanics/search?name=Peter')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('Peter' in m['name'] for m in response.json))
