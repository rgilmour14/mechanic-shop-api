from .schemas import ticket_schema, tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Ticket, Customer, Mechanic, db
from . import tickets_bp

#============ ROUTES =================

# Create Ticket
@tickets_bp.route("/", methods=['POST'])
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
@tickets_bp.route("/<int:ticket_id>/assign_mechanic/<mechanic_id>", methods=['POST'])
def assign_mechanic(mechanic_id, ticket_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    ticket = db.session.get(Ticket, ticket_id)
    
    if mechanic and ticket:
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify({"Message": "Successfully assigned mechanic to ticket"}), 200
        else:
            return jsonify({"Message": "Mechanic already assigned to this ticket"}), 400
    else:
        return jsonify({"error": "Mechanic or Ticket not found."}), 404

# Remove Mechanic from Ticket
@tickets_bp.route("/<int:ticket_id>/remove_mechanic/<mechanic_id>", methods=['POST'])
def remove_mechanic(mechanic_id, ticket_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    ticket = db.session.get(Ticket, ticket_id)
    
    if mechanic and ticket:
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify({"Message": "Successfully removed mechanic from ticket"}), 200
        else:
            return jsonify({"Message": "Mechanic not assigned to this ticket"}), 400
    else:
        return jsonify({"error": "Mechanic or Ticket not found."}), 404


# Get all Tickets
@tickets_bp.route("/", methods=['GET'])
def get_tickets():
    query = select(Ticket)
    tickets = db.session.execute(query).scalars().all()

    return tickets_schema.jsonify(tickets)