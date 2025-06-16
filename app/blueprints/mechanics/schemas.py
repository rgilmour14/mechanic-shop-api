from app.extensions import ma
from app.models import Mechanic

#============ SCHEMAS =================

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
