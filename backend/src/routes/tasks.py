from flask import Blueprint, request, current_app, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime, timezone

# Create both blueprint and API namespace
tasks_bp = Blueprint('tasks', __name__)
tasks_ns = Namespace('tasks', description='Task operations')

# Helper function to transform tasks
def transform_task(task):
    return {
        '_id': str(task['_id']),
        'title': task['title'],
        'description': task.get('description', ''),
        'status': task.get('status', 'pending'),
        'task_type': task.get('taskType', ''),
        'user_id': str(task['userId']),
        'is_active': task.get('isActive', True),
        'created_at': task.get('createdAt'),
        'updated_at': task.get('updatedAt'),
        'version': task.get('version', 1)
    }

# Create route mappings with EXPLICIT blueprint routes
@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def list_tasks():
    return TaskList().get()

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    return TaskList().post()

# Add explicit blueprint routes for todos and distractions
@tasks_bp.route('/todos', methods=['GET'])
@jwt_required()
def list_todos():
    user_id = get_jwt_identity()
    tasks = list(current_app.mongo.db.tasks.find({
        'userId': ObjectId(user_id),
        'isActive': True,
        'taskType': 'todo'
    }))
    
    transformed_tasks = [transform_task(task) for task in tasks]
    return transformed_tasks

@tasks_bp.route('/distractions', methods=['GET'])
@jwt_required()
def list_distractions():
    user_id = get_jwt_identity()
    tasks = list(current_app.mongo.db.tasks.find({
        'userId': ObjectId(user_id),
        'isActive': True,
        'taskType': 'distraction'
    }))
    
    transformed_tasks = [transform_task(task) for task in tasks]
    return transformed_tasks

# Add new route for completing a task
@tasks_bp.route('/complete/<task_id>', methods=['POST'])
@jwt_required()
def complete_task(task_id):
    return CompleteTask().post(task_id)

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
        
        transformed_tasks = [transform_task(task) for task in tasks]
        return transformed_tasks

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
        
        # Use timezone-aware datetime objects
        now = datetime.now(timezone.utc)
        
        task = {
            'title': data['title'],
            'description': data.get('description', ''),
            'taskType': data['task_type'],
            'status': data.get('status', 'pending'),
            'userId': ObjectId(user_id),
            'isActive': True,
            'createdAt': now,
            'updatedAt': now,
            'version': 1
        }
        
        result = current_app.mongo.db.tasks.insert_one(task)
        
        # Create a properly formatted response object with mapped fields
        response = transform_task({
            '_id': result.inserted_id,
            **task
        })
        
        return response, 201
    
# Keep the namespace routes for Swagger documentation
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
        
        transformed_tasks = [transform_task(task) for task in tasks]
        return transformed_tasks

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
        
        transformed_tasks = [transform_task(task) for task in tasks]
        return transformed_tasks

# Add new namespace route for completing a task
@tasks_ns.route('/complete/<task_id>')
@tasks_ns.param('task_id', 'The task identifier')
class CompleteTask(Resource):
    @tasks_ns.doc('complete_task', security='jwt')
    @tasks_ns.response(200, 'Task completed successfully')
    @tasks_ns.response(404, 'Task not found')
    def post(self, task_id):
        """Mark a task as completed"""
        user_id = get_jwt_identity()
        
        # Find the task first to check if it exists and get its current version
        task = current_app.mongo.db.tasks.find_one({
            '_id': ObjectId(task_id),
            'userId': ObjectId(user_id),
            'isActive': True
        })
        
        if not task:
            return {'message': 'Task not found'}, 404
        
        # Update the task to mark it as completed
        now = datetime.now(timezone.utc)
        
        result = current_app.mongo.db.tasks.update_one(
            {
                '_id': ObjectId(task_id),
                'userId': ObjectId(user_id),
                'isActive': True
            },
            {
                '$set': {
                    'status': 'completed',
                    'updatedAt': now,
                    'version': task['version'] + 1
                }
            }
        )
        
        if result.modified_count:
            return {'message': 'Task completed successfully'}, 200
        
        return {'message': 'Task not updated. No changes made.'}, 400