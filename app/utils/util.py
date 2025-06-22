from datetime import datetime, timedelta, timezone
from jose import jwt
from functools import wraps
from flask import request, jsonify
import jose

SECRET_KEY = "a super secret, secret key"

def encode_token(customer_id): #using unique pieces of info to make our tokens user specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), #Setting the expiration time to an hour past now
        'iat': datetime.now(timezone.utc), #Issued at
        'sub':  str(customer_id) #This needs to be a string or the token will be malformed and won't be able to be decoded.
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                # Decode the token
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                print(data)
                customer_id = data['sub']  # Fetch the customer ID
            
            except jose.exceptions.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 401
            except jose.exceptions.JWTError:
                return jsonify({'message': 'Invalid token!'}), 401

            return f(customer_id, *args, **kwargs)
    
        else:
            return jsonify({'message': 'You must be logged in to access this.'}), 400

    return decorated