from .schemas import customer_schema, customers_schema, login_schema, tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import Select
from app.models import Customer, Ticket, db
from app.extensions import limiter, cache
from . import customers_bp
from app.utils.util import encode_token, token_required

#============ ROUTES =================

# customer log in
@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = Select(Customer).where(Customer.email == email) 
    customer = db.session.execute(query).scalar_one_or_none() #Query customer table for a customer with this email

    if customer and customer.password == password: #if we have a customer associated with the email, validate the password
        auth_token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 400

# Create Customer
@customers_bp.route("/", methods=['POST'])
@limiter.limit("5 per day")  # Limit to 5 requests per day
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'],email=customer_data['email'],
                            phone=customer_data['phone'], password=customer_data['password'])
    
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

# Get all Customers
@customers_bp.route("/", methods=['GET'])
@cache.cached(timeout=20)  # Cache for 20 seconds
def get_customers():
    query = Select(Customer)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)

# Get Customer by ID
@customers_bp.route("/<int:customer_id>", methods=['GET'])
@cache.cached(timeout=20)  # Cache for 20 seconds
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 400

# Update Customer
@customers_bp.route("/", methods=['PUT'])
@token_required
@limiter.limit("5 per month")  # Limit to 5 requests per month
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 400
    
    try:
        customer_data = customer_schema.load(request.json, partial=True) 
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

# Delete Customer
@customers_bp.route("/", methods=['DELETE'])
@token_required
@limiter.limit("5 per day")  # Limit to 5 requests per day
def delete_customer(customer_id):
    query = Select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted.'}), 200


# Get Customer's Tickets
@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    # Query all tickets belonging to the customer
    tickets = db.session.query(Ticket).filter_by(customer_id=customer_id).all()
    
    return jsonify({
        "status": "success",
        "tickets": tickets_schema.dump(tickets)
    }), 200