# src/routes/users.py
from flask import Blueprint, request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime

# Create both blueprint and API namespace
users_bp = Blueprint('users', __name__)
users_ns = Namespace('users', description='User operations')

# Create route mappings
@users_bp.route('/me')
@jwt_required()
def get_current_user():
    return CurrentUser().get()

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    return UserProfile().put()

# Define models for swagger documentation
user_response_model = users_ns.model('UserResponse', {
    '_id': fields.String(description='User ID'),
    'email': fields.String(description='User email'),
    'username': fields.String(description='Username'),
    'name': fields.String(description='User name'),
    'user_type': fields.String(description='User type', enum=['user', 'admin']),
    'is_active': fields.Boolean(description='Active status'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'last_login_at': fields.DateTime(description='Last login timestamp'),
    'version': fields.Integer(description='Document version')
})

profile_update_model = users_ns.model('ProfileUpdate', {
    'name': fields.String(required=True, description='User name'),
    'username': fields.String(required=True, description='Username')
})

@users_ns.route('/me')
class CurrentUser(Resource):
    @users_ns.doc('get_current_user', security='jwt')
    @users_ns.marshal_with(user_response_model)
    def get(self):
        """Get current user profile"""
        try:
            user_id = get_jwt_identity()
            user = current_app.mongo.db.users.find_one({'_id': ObjectId(user_id)})
            
            if not user:
                users_ns.abort(404, 'User not found')
            
            # Transform the document to match the response model
            transformed_user = {
                '_id': str(user['_id']),
                'email': user['email'],
                'username': user['username'],
                'name': user['name'],
                'user_type': user['userType'],
                'is_active': user['isActive'],
                'created_at': user['createdAt'],
                'updated_at': user['updatedAt'],
                'last_login_at': user['lastLoginAt'],
                'version': user['version']
            }
            
            return transformed_user
            
        except Exception as e:
            users_ns.abort(500, str(e))

@users_ns.route('/profile')
class UserProfile(Resource):
    @users_ns.doc('update_profile', security='jwt')
    @users_ns.expect(profile_update_model)
    @users_ns.response(200, 'Success')
    @users_ns.response(400, 'Validation Error')
    @users_ns.response(409, 'Username already exists')
    def put(self):
        """Update user profile"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Check if username exists (if username is being updated)
            if 'username' in data:
                existing_user = current_app.mongo.db.users.find_one({
                    'username': data['username'],
                    '_id': {'$ne': ObjectId(user_id)}
                })
                if existing_user:
                    return {'message': 'Username already taken'}, 409
            
            # Don't allow email/password/userType updates through this endpoint
            allowed_updates = ['name', 'username']
            update_data = {
                to_camel_case(k): v 
                for k, v in data.items() 
                if k in allowed_updates
            }
            
            # Add metadata updates
            current_user = current_app.mongo.db.users.find_one({'_id': ObjectId(user_id)})
            update_data.update({
                'updatedAt': datetime.utcnow(),
                'version': current_user['version'] + 1
            })
            
            result = current_app.mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count:
                return {'message': 'Profile updated successfully'}, 200
            return {'message': 'No changes made'}, 200
            
        except Exception as e:
            users_ns.abort(500, str(e))

# Helper function
def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])