from flask import Blueprint, request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime, timezone

# Create both blueprint and API namespace
sessions_bp = Blueprint('sessions', __name__)
sessions_ns = Namespace('sessions', description='Session operations')

# Create route mappings
@sessions_bp.route('/', methods=['GET'])
@jwt_required()
def list_sessions():
    return SessionList().get()

@sessions_bp.route('/', methods=['POST'])
@jwt_required()
def create_session():
    return SessionList().post()

@sessions_bp.route('/<session_id>/stop', methods=['POST'])
@jwt_required()
def stop_session(session_id):
    return SessionStop().post(session_id)

session_model = sessions_ns.model('Session', {
    'task_id': fields.String(required=False, description='Associated task ID'),
    'timer_type_id': fields.String(required=True, description='Associated timer type ID'),
    'status': fields.String(required=True, description='Session status', enum=['active', 'paused', 'completed']),
    'start_time': fields.DateTime(description='Session start time'),
    'end_time': fields.DateTime(description='Session end time'),
    'work_duration': fields.Integer(required=True, description='Work duration in minutes'),
    'break_duration': fields.Integer(required=True, description='Break duration in minutes')
})

session_response_model = sessions_ns.inherit('SessionResponse', session_model, {
    '_id': fields.String(description='Session ID'),
    'user_id': fields.String(description='User ID'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'version': fields.Integer(description='Document version')
})

@sessions_ns.route('/')
class SessionList(Resource):
    @sessions_ns.doc('list_sessions', security='jwt')
    @sessions_ns.marshal_list_with(session_response_model)
    def get(self):
        """List all sessions for the current user"""
        user_id = get_jwt_identity()
        sessions = list(current_app.mongo.db.sessions.find({
            'userId': ObjectId(user_id),
            'isActive': True
        }))
        
        # Transform each session to match the response model
        transformed_sessions = []
        for session in sessions:
            transformed_sessions.append({
                '_id': str(session['_id']),
                'user_id': str(session['userId']),
                'task_id': str(session['taskId']) if session.get('taskId') else None,
                'timer_type_id': str(session['timerTypeId']) if session.get('timerTypeId') else None,
                'status': session.get('status', ''),
                'start_time': session.get('startTime'),
                'end_time': session.get('endTime') if 'endTime' in session else None,
                'work_duration': session.get('workDuration', 0),
                'break_duration': session.get('breakDuration', 0),
                'created_at': session.get('createdAt'),
                'updated_at': session.get('updatedAt'),
                'version': session.get('version', 1)
            })
        
        return transformed_sessions

    @sessions_ns.doc('start_session', security='jwt')
    @sessions_ns.expect(session_model)
    @sessions_ns.marshal_with(session_response_model, code=201)
    def post(self):
        """Start a new session"""
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Use timezone-aware datetime objects
        now = datetime.now(timezone.utc)
        
        session = {
            'userId': ObjectId(user_id),
            'startTime': now,
            'timerTypeId': ObjectId(data['timer_type_id']),
            'taskId': ObjectId(data['task_id']) if data.get('task_id') else None,
            'workDuration': data['work_duration'],
            'breakDuration': data['break_duration'],
            'status': 'active',
            'isActive': True,
            'createdAt': now,
            'updatedAt': now,
            'version': 1
        }
        
        result = current_app.mongo.db.sessions.insert_one(session)
        
        # Create a properly formatted response object with mapped fields
        response = {
            '_id': str(result.inserted_id),
            'user_id': str(session['userId']),
            'task_id': str(session['taskId']) if session.get('taskId') else None,
            'timer_type_id': str(session['timerTypeId']) if session.get('timerTypeId') else None,
            'status': session.get('status', ''),
            'start_time': session.get('startTime'),
            'end_time': session.get('endTime') if 'endTime' in session else None,
            'work_duration': session.get('workDuration', 0),
            'break_duration': session.get('breakDuration', 0),
            'created_at': session.get('createdAt'),
            'updated_at': session.get('updatedAt'),
            'version': session.get('version', 1)
        }
        
        return response, 201

@sessions_ns.route('/<session_id>/stop')
@sessions_ns.param('session_id', 'The session identifier')
class SessionStop(Resource):
    @sessions_ns.doc('stop_session', security='jwt')
    def post(self, session_id):
        """Stop an active session"""
        user_id = get_jwt_identity()
        end_time = datetime.now(timezone.utc)
        
        session = current_app.mongo.db.sessions.find_one({'_id': ObjectId(session_id)})
        if not session:
            sessions_ns.abort(404, 'Session not found')
            
        duration = (end_time - session['startTime']).total_seconds() / 60  # Convert to minutes
        
        result = current_app.mongo.db.sessions.update_one(
            {
                '_id': ObjectId(session_id),
                'userId': ObjectId(user_id),
                'status': 'active'
            },
            {
                '$set': {
                    'endTime': end_time,
                    'status': 'completed',
                    'duration': duration,
                    'updatedAt': datetime.now(timezone.utc),
                    'version': session['version'] + 1
                }
            }
        )
        
        if result.modified_count:
            return {'message': 'Session stopped successfully'}, 200
        sessions_ns.abort(404, 'Session not found or already stopped')