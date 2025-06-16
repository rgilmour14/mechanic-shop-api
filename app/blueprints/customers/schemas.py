from app.extensions import ma
from app.models import Customer

#============ SCHEMAS =================

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
