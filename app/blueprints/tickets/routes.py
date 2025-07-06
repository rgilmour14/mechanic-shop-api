from .schemas import ticket_schema, tickets_schema, edit_ticket_schema, return_ticket_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Ticket, Customer, Mechanic, Inventory, TicketParts, MechanicServiceTicket, db
from app.extensions import limiter, cache
from datetime import datetime
from . import tickets_bp

#============ ROUTES =================

# Create Ticket
@tickets_bp.route("/", methods=['POST'])
@limiter.limit("5 per hour")  # Limit to 5 requests per hour
def create_ticket():
    try:
        ticket_data = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer_id = ticket_data.get("customer_id")
    customer = db.session.query(Customer).get(customer_id)
    if not customer:
        return jsonify({"error": "Customer with this ID does not exist."}), 400
    
    new_ticket = Ticket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(ticket_schema.dump(new_ticket)), 201

# Assign Mechanic to Ticket
@tickets_bp.route("/<int:ticket_id>/assign_mechanic/<int:mechanic_id>", methods=['POST'])
def assign_mechanic(ticket_id, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    ticket = db.session.get(Ticket, ticket_id)
    
    if not mechanic or not ticket:
        return jsonify({"error": "Mechanic or Ticket not found."}), 404
    
    # Check if assignment already exists
    existing_assignment = db.session.query(MechanicServiceTicket).filter_by(
        mechanic_id=mechanic_id,
        ticket_id=ticket_id
    ).first()
    
    if existing_assignment:
        return jsonify({"message": "Mechanic already assigned to this ticket"}), 400
    
    # Create assignment with current datetime as start_date
    assignment = MechanicServiceTicket(
        mechanic_id=mechanic_id,
        ticket_id=ticket_id,
        start_date=datetime.utcnow()
    )
    db.session.add(assignment)
    db.session.commit()
    
    return jsonify({"message": "Successfully assigned mechanic to ticket"}), 200

# Remove Mechanic from Ticket
@tickets_bp.route("/<int:ticket_id>/remove_mechanic/<mechanic_id>", methods=['POST'])
def remove_mechanic(ticket_id, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    ticket = db.session.get(Ticket, ticket_id)
    
    if not mechanic or not ticket:
        return jsonify({"error": "Mechanic or Ticket not found."}), 404
    
    # Find assignment in MechanicServiceTicket
    assignment = db.session.query(MechanicServiceTicket).filter_by(
        mechanic_id=mechanic_id,
        ticket_id=ticket_id
    ).first()
    
    if not assignment:
        return jsonify({"message": "Mechanic not assigned to this ticket"}), 400
    
    # Delete the assignment
    db.session.delete(assignment)
    db.session.commit()
    
    return jsonify({"message": "Successfully removed mechanic from ticket"}), 200


# Get all Tickets
@tickets_bp.route("/", methods=['GET'])
@cache.cached(timeout=20)  # Cache for 20 seconds
def get_tickets():
    query = select(Ticket)
    tickets = db.session.execute(query).scalars().all()
    return tickets_schema.jsonify(tickets)


# Edit Ticket
@tickets_bp.route("/<int:ticket_id>/edit", methods=['PUT'])
def edit_ticket(ticket_id):
    try:
        ticket_edits = edit_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Retrieve ticket
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    # === ADD Mechanics ===
    for mechanic_id in ticket_edits.get("add_mechanic_ids", []):
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic:
            # Check if assignment exists
            existing_assignment = db.session.query(MechanicServiceTicket).filter_by(
                mechanic_id=mechanic_id,
                ticket_id=ticket_id
            ).first()
            if not existing_assignment:
                assignment = MechanicServiceTicket(
                    mechanic_id=mechanic_id,
                    ticket_id=ticket_id
                )
                db.session.add(assignment)

    # === REMOVE Mechanics ===
    for mechanic_id in ticket_edits.get("remove_mechanic_ids", []):
        assignment = db.session.query(MechanicServiceTicket).filter_by(
            mechanic_id=mechanic_id,
            ticket_id=ticket_id
        ).first()
        if assignment:
            db.session.delete(assignment)
    
    db.session.commit()
    
    return jsonify(return_ticket_schema.dump(ticket)), 200

# Add Part to Ticket
@tickets_bp.route("/<int:ticket_id>/add_part/<int:part_id>", methods=['POST'])
def add_part_to_ticket(ticket_id, part_id):
    ticket = db.session.get(Ticket, ticket_id)
    part = db.session.get(Inventory, part_id)
    
    if not ticket or not part:
        return jsonify({"error": "Part or Ticket not found."}), 404

    for part in ticket.ticket_parts:
        if part.part_id == part_id:
            return jsonify({"message": "Part already associated with ticket."}), 200

    ticket_part = TicketParts(ticket_id=ticket_id, part_id=part_id)
    db.session.add(ticket_part)
    db.session.commit()

    return jsonify({"message": "Successfully added part to ticket"}), 200