from app.extensions import ma
from app.models import Ticket
from marshmallow import fields, Schema
from app.blueprints.mechanics.schemas import MechanicSchema
#============ SCHEMAS =================

class TicketSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Int(required=True)
    mechanic_id = fields.Int(required=False, allow_none=True)
    mechanics = fields.Nested(MechanicSchema, many=True)
    
    class Meta:
        model = Ticket
        include_fk = True 
        
class EditTicketSchema(Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ('add_mechanic_ids', 'remove_mechanic_ids')

        
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
return_ticket_schema = TicketSchema(exclude=('id',))
edit_ticket_schema = EditTicketSchema()


