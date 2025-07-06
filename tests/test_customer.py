from app import create_app
from app.models import db, Customer, Ticket
import unittest
from app.utils.util import encode_token

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customer(name="test_customer", email="test@email.com", phone="1234567899", password="test")
            db.session.add(self.customer)
            db.session.commit()
            self.auth_token = encode_token(self.customer.id)    
        
        
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1234567890",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")
        
    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "1234567890",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])
        
    def test_login(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['message'], 'Successfully Logged In')
        self.assertIn('auth_token', response.json)
        return response.json['auth_token']
    
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['messages'], 'Invalid email or password')
        
    def test_update_customer(self):
        update_payload = {
            "name": "Peter",
        }

        headers = {'Authorization': "Bearer " + self.test_login()}

        response = self.client.put('/customers/', json=update_payload, headers=headers)
        print(response.json) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter') 
        self.assertEqual(response.json['email'], 'test@email.com')
        
    def test_get_all_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_customer')
        
    def test_get_customer_by_id(self):
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'test_customer')
        
    def test_get_my_tickets(self):
        with self.app.app_context():
            ticket1 = Ticket(
                vin="1HGCM82633",
                service_date="01-01-2023",
                service_desc="Sample description",
                customer_id=self.customer.id
            )
            ticket2 = Ticket(
                vin="1HGCM82634",
                service_date="01-02-2023",
                service_desc="Another description",
                customer_id=self.customer.id
            )

            db.session.add_all([ticket1, ticket2])
            db.session.commit()
        
        headers = {'Authorization': "Bearer " + self.test_login()}
        response = self.client.get('/customers/my-tickets', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('tickets', response.json)
        self.assertEqual(len(response.json['tickets']), 2)
        self.assertEqual(response.json['tickets'][0]['vin'], '1HGCM82633')
        self.assertEqual(response.json['tickets'][0]['service_desc'], 'Sample description')
        
    def test_delete_customer(self):
        headers = {'Authorization': "Bearer " + self.test_login()}
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)
        
    