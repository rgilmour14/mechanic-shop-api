from app import create_app
from app.models import db, Ticket, Customer, Mechanic, MechanicServiceTicket, Inventory, TicketParts
import unittest

class TestTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            customer = Customer(
                name="test_customer",
                email="test@email.com",
                phone="1234567890",
                password="test"
            )
            
            db.session.add(customer)
            db.session.commit()
            
            self.ticket = Ticket(vin="test_vin", service_date="01-01-2023", service_desc="Test Service", customer_id=1)
            
            db.session.add(self.ticket)
            db.session.commit()
        
        
    def test_create_ticket(self):
        ticket_payload = {
            "vin": "1HGCM82633",
            "service_date": "2023-01-01",
            "service_desc": "Sample description",
            "customer_id": 1
        }

        response = self.client.post('/tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['vin'], "1HGCM82633")
        
    def test_invalid_creation(self):
        ticket_payload = {
            "vin": "1HGCM82633",
            "service_desc": "Sample description",
            "customer_id": 1
        }

        response = self.client.post('/tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['service_date'], ['Missing data for required field.'])
        
    def test_assign_mechanic(self):
        with self.app.app_context():
            mechanic = Mechanic(
                name="Bob Ross",
                email="bross@email.com",
                phone="999-999-9999",
                salary= 50000
            )
            db.session.add(mechanic)
            db.session.commit()
            
        response = self.client.post('/tickets/1/assign_mechanic/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully assigned mechanic to ticket")
        
        with self.app.app_context():
            assigned = db.session.query(MechanicServiceTicket).filter_by(
                mechanic_id=1,
                ticket_id=1
            ).first()
            self.assertIsNotNone(assigned)
        
    def test_remove_mechanic(self):
        with self.app.app_context():
            mechanic = Mechanic(
                name="Bob Ross",
                email="bross@email.com",
                phone="999-999-9999",
                salary= 50000
            )
            db.session.add(mechanic)
            db.session.commit()
            
            mechanic_ticket = MechanicServiceTicket(
            mechanic_id=1,
            ticket_id=1
            )
            db.session.add(mechanic_ticket)
            db.session.commit()
            
        response = self.client.post('/tickets/1/remove_mechanic/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully removed mechanic from ticket")
        
    def test_get_all_tickets(self):
        response = self.client.get('/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)
            
    def test_edit_ticket(self):
        with self.app.app_context():
            mechanic = Mechanic(
                name="Bob Ross",
                email="bobross@email.com",
                phone="999-999-9999",
                salary=50000
            )
            db.session.add(mechanic)
            db.session.commit()

        edit_payload = {
            "add_mechanic_ids": [1],
            "remove_mechanic_ids": []
            }
        response = self.client.put('/tickets/1/edit', json=edit_payload)
        self.assertEqual(response.status_code, 200)
        
    def test_add_part_to_ticket(self):
        with self.app.app_context():
            part = Inventory(
                name="brake pad",
                price=100.0
            )
            db.session.add(part)
            db.session.commit()

        response = self.client.post(f'/tickets/1/add_part/1')
        print(response.json) 

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully added part to ticket")
