from .schemas import part_schema, parts_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import Select
from app.models import Inventory, db
from . import inventory_bp
from app.utils.util import encode_token, token_required

#============ ROUTES =================

# Create Part
@inventory_bp.route("/", methods=['POST'])
def create_part():
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_part = Inventory(name=part_data['name'], price=part_data['price'])
    
    db.session.add(new_part)
    db.session.commit()
    return part_schema.jsonify(new_part), 201

# Get all Parts
@inventory_bp.route("/", methods=['GET'])
def get_parts():
    query = Select(Inventory)
    parts = db.session.execute(query).scalars().all()

    return parts_schema.jsonify(parts)

# Get Part by ID
@inventory_bp.route("/<int:part_id>", methods=['GET'])
def get_part(part_id):
    part = db.session.get(Inventory, part_id)

    if part:
        return part_schema.jsonify(part), 200
    return jsonify({"error": "Part not found."}), 400

# Update Part
@inventory_bp.route("/<int:part_id>", methods=['PUT'])
def update_part(part_id):
    part = db.session.get(Inventory, part_id)

    if not part:
        return jsonify({"error": "Part not found."}), 400
    
    try:
        part_data = part_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in part_data.items():
        setattr(part, key, value)

    db.session.commit()
    return part_schema.jsonify(part), 200

# Delete Part
@inventory_bp.route("/<int:part_id>", methods=['DELETE'])
def delete_part(part_id):
    query = Select(Inventory).where(Inventory.id == part_id)
    part = db.session.execute(query).scalars().first()

    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f'Part id: {part_id}, successfully deleted.'}), 200

