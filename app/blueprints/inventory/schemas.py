from app.extensions import ma
from app.models import Inventory

#============ SCHEMAS =================

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        
        
part_schema = InventorySchema()
parts_schema = InventorySchema(many=True)



