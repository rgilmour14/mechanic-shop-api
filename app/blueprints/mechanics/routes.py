from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import Select
from app.models import Mechanic, db
from app.extensions import limiter, cache
from . import mechanics_bp

#============ ROUTES =================

# Create Mechanic
@mechanics_bp.route("/", methods=['POST'])
@limiter.limit("5 per hour")  # Limit to 5 requests per hour
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    
    new_mechanic = Mechanic(name=mechanic_data['name'],email=mechanic_data['email'],
                            phone=mechanic_data['phone'], salary=mechanic_data['salary'])
    
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

# Get all Mechanics
@mechanics_bp.route("/", methods=['GET'])
# @cache.cached(timeout=20)  # Cache for 20 seconds
def get_mechanics():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = Select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)
        return mechanics_schema.jsonify(mechanics), 200
    except:    
        query = Select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()
        return mechanics_schema.jsonify(mechanics), 200

# Update Mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
@limiter.limit("5 per hour")  # Limit to 5 requests per hour
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 400
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# Delete Mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
@limiter.limit("5 per hour")  # Limit to 5 requests per hour
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 400
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'Mechanic id: {mechanic_id}, successfully deleted.'}), 200

# Sort Mechanics by Ticket Count
@mechanics_bp.route("/mechanic-ticket-list", methods=['GET'])
def mechanic_ticket_list():
    query = Select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    mechanics.sort(key=lambda mechanic: len(mechanic.tickets), reverse=True)
    
    return mechanics_schema.jsonify(mechanics), 200

# Search Mechanic by Name
@mechanics_bp.route("/search", methods=['GET'])
def search_mechanic():
    name = request.args.get('name')
    
    query = Select(Mechanic).where(Mechanic.name.like(f'%{name}%'))
    mechanics = db.session.execute(query).scalars().all()
    
    return mechanics_schema.jsonify(mechanics), 200
