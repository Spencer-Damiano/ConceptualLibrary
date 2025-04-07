from flask import Blueprint, request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime

# Create both blueprint and API namespace
tasks_bp = Blueprint('tasks', __name__)
tasks_ns = Namespace('tasks', description='Task operations')

# Create route mappings
@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def list_tasks():
    return TaskList().get()

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    return TaskList().post()

# Define models for swagger documentation
task_model = tasks_ns.model('Task', {
    'title': fields.String(required=True, description='Task title'),
    'description': fields.String(required=False, description='Task description'),
    'status': fields.String(required=False, description='Task status', enum=['pending', 'active', 'completed']),
    'task_type': fields.String(required=True, description='Task type', enum=['todo', 'distraction']),
    }
)

task_response_model = tasks_ns.inherit('TaskResponse', task_model, {
    '_id': fields.String(description='Task ID'),
    'user_id': fields.String(description='User ID'),
    'is_active': fields.Boolean(description='Active status'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'version': fields.Integer(description='Document version')
})

@tasks_ns.route('/')
class TaskList(Resource):
    @tasks_ns.doc('list_tasks', security='jwt')
    @tasks_ns.marshal_list_with(task_response_model)
    def get(self):
        """List all tasks for the current user"""
        user_id = get_jwt_identity()
        tasks = list(current_app.mongo.db.tasks.find({
            'userId': ObjectId(user_id),
            'isActive': True
        }))
        
        for task in tasks:
            task['_id'] = str(task['_id'])
            task['user_id'] = str(task['userId'])
            
        return tasks

    @tasks_ns.doc('create_task', security='jwt')
    @tasks_ns.expect(task_model)
    @tasks_ns.marshal_with(task_response_model, code=201)
    @tasks_ns.response(400, 'Validation Error')
    def post(self):
        """Create a new task"""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('title'):
            tasks_ns.abort(400, 'Task title is required')
        
        task = {
            'title': data['title'],
            'description': data.get('description', ''),
            'taskType': data['task_type'],
            'status': data.get('status', 'pending'),
            'userId': ObjectId(user_id),
            'isActive': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'version': 1
        }
        
        result = current_app.mongo.db.tasks.insert_one(task)
        task['_id'] = str(result.inserted_id)
        task['user_id'] = str(task['userId'])
        
        return task, 201
    
@tasks_ns.route('/todos')
class TodoList(Resource):
    @tasks_ns.doc('list_todos', security='jwt')
    @tasks_ns.marshal_list_with(task_response_model)
    def get(self):
        """List all todo tasks for the current user"""
        user_id = get_jwt_identity()
        tasks = list(current_app.mongo.db.tasks.find({
            'userId': ObjectId(user_id),
            'isActive': True,
            'taskType': 'todo'
        }))
        
        for task in tasks:
            task['_id'] = str(task['_id'])
            task['user_id'] = str(task['userId'])
            
        return tasks

@tasks_ns.route('/distractions')
class DistractionList(Resource):
    @tasks_ns.doc('list_distractions', security='jwt')
    @tasks_ns.marshal_list_with(task_response_model)
    def get(self):
        """List all distraction tasks for the current user"""
        user_id = get_jwt_identity()
        tasks = list(current_app.mongo.db.tasks.find({
            'userId': ObjectId(user_id),
            'isActive': True,
            'taskType': 'distraction'
        }))
        
        for task in tasks:
            task['_id'] = str(task['_id'])
            task['user_id'] = str(task['userId'])
            
        return tasks