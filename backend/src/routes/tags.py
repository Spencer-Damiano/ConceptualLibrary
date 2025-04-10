from flask import Blueprint, request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime, timezone

# Create both blueprint and API namespace
tags_bp = Blueprint('tags', __name__)
tags_ns = Namespace('tags', description='Tag operations')

# Create route mappings
@tags_bp.route('/', methods=['GET'])
@jwt_required()
def list_tags():
    return TagList().get()

@tags_bp.route('/', methods=['POST'])
@jwt_required()
def create_tag():
    return TagList().post()

@tags_bp.route('/<tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    return Tag().delete(tag_id)

tag_model = tags_ns.model('Tag', {
    'name': fields.String(required=True, description='Tag name'),
    'color': fields.String(required=True, description='Tag color hex code', 
                         pattern='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
})

tag_response_model = tags_ns.inherit('TagResponse', tag_model, {
    '_id': fields.String(description='Tag ID'),
    'user_id': fields.String(description='User ID'),
    'is_active': fields.Boolean(description='Active status'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'version': fields.Integer(description='Document version')
})

@tags_ns.route('/')
class TagList(Resource):
    @tags_ns.doc('create_tag', security='jwt')
    @tags_ns.expect(tag_model)
    @tags_ns.marshal_with(tag_response_model, code=201)
    @tags_ns.response(400, 'Validation Error')
    @tags_ns.response(409, 'Tag already exists')
    def post(self):
        """Create a new tag"""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('name'):
            tags_ns.abort(400, 'Tag name is required')
        
        # Check if tag already exists for this user
        existing_tag = current_app.mongo.db.tags.find_one({
            'name': data['name'],
            'userId': ObjectId(user_id),
            'isActive': True
        })
        
        if existing_tag:
            tags_ns.abort(409, 'Tag already exists')
        
        # Use timezone-aware datetime objects
        now = datetime.now(timezone.utc)
        
        tag = {
            'name': data['name'],
            'color': data.get('color', '#000000'),
            'userId': ObjectId(user_id),
            'isActive': True,
            'createdAt': now,
            'updatedAt': now,
            'version': 1
        }
        
        result = current_app.mongo.db.tags.insert_one(tag)
        
        # Create a properly formatted response object
        response = {
            '_id': str(result.inserted_id),
            'name': tag['name'],
            'color': tag['color'],
            'user_id': str(tag['userId']),
            'is_active': tag['isActive'],
            'created_at': tag['createdAt'],
            'updated_at': tag['updatedAt'],
            'version': tag['version']
        }
        
        return response, 201

    @tags_ns.doc('list_tags', security='jwt')
    @tags_ns.marshal_list_with(tag_response_model)
    def get(self):
        """List all tags for the current user"""
        user_id = get_jwt_identity()
        tags = list(current_app.mongo.db.tags.find({
            'userId': ObjectId(user_id),
            'isActive': True
        }))
        
        # Transform each tag to match the response model
        transformed_tags = []
        for tag in tags:
            transformed_tags.append({
                '_id': str(tag['_id']),
                'name': tag['name'],
                'color': tag['color'],
                'user_id': str(tag['userId']),
                'is_active': tag['isActive'],
                'created_at': tag['createdAt'],
                'updated_at': tag['updatedAt'],
                'version': tag['version']
            })
        
        return transformed_tags

@tags_ns.route('/<tag_id>')
@tags_ns.param('tag_id', 'The tag identifier')
class Tag(Resource):
    @tags_ns.doc('delete_tag', security='jwt')
    @tags_ns.response(200, 'Success')
    @tags_ns.response(404, 'Tag not found')
    def delete(self, tag_id):
        """Delete a tag"""
        user_id = get_jwt_identity()
        
        # Soft delete by setting isActive to False
        result = current_app.mongo.db.tags.update_one(
            {
                '_id': ObjectId(tag_id),
                'userId': ObjectId(user_id),
                'isActive': True
            },
            {
                '$set': {
                    'isActive': False,
                    'updatedAt': datetime.now(timezone.utc),  # Use timezone-aware datetime
                    'updatedBy': ObjectId(user_id)  # Add updatedBy field
                }
            }
        )
        
        if result.modified_count:
            # Also remove this tag from all tasks
            current_app.mongo.db.taskTags.delete_many({'tagId': ObjectId(tag_id)})
            return {'message': 'Tag deleted successfully'}, 200
        tags_ns.abort(404, 'Tag not found')