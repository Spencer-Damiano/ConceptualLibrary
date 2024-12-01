# src/routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_restx import Namespace, Resource, fields

# Create both blueprint and API namespace
auth_bp = Blueprint('auth', __name__)
auth_ns = Namespace('auth', description='Authentication operations')

# Define API models for Swagger documentation
register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'name': fields.String(description='User name')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# Blueprint routes (existing functionality)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    if current_app.mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'message': 'Email already registered'}), 409
    
    user = {
        'email': data['email'],
        'password': generate_password_hash(data['password']),
        'name': data.get('name', ''),
        'created_at': datetime.utcnow()
    }
    
    current_app.mongo.db.users.insert_one(user)
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    user = current_app.mongo.db.users.find_one({'email': data['email']})
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({'access_token': access_token}), 200

# Swagger documentation routes
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User registered successfully')
    @auth_ns.response(400, 'Validation Error')
    @auth_ns.response(409, 'Email already registered')
    def post(self):
        return register()

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(400, 'Validation Error')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        return login()