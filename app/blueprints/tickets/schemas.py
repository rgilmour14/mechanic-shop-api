from app.extensions import ma
from app.models import Ticket
from marshmallow import fields

#============ SCHEMAS =================

class TicketSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Int(required=True)
    mechanic_id = fields.Int(required=False, allow_none=True)
    
    class Meta:
        model = Ticket
        include_fk = True  # Include foreign keys = customer_id
        
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

