from app.extensions import ma
from app.models import Customer, Ticket
from app.blueprints.tickets.schemas import TicketSchema, ticket_schema, tickets_schema

#============ SCHEMAS =================

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(only=('email', 'password'))


