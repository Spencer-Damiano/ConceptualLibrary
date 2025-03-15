# src/app.py
from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()

# Create API with prefix to avoid conflicts
authorizations = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

api = Api(
    title='Productivity API',
    version='1.0',
    description='A productivity tracking API with tasks, tags, and time sessions',
    doc='/swagger',  # Swagger UI will be available at /swagger
    authorizations=authorizations,
    security='jwt'
)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    
    # Initialize CORS and extensions
    CORS(app)
    mongo.init_app(app)
    jwt.init_app(app)
    
    # Add this line to attach mongo to app
    app.mongo = mongo
    
    # Import namespaces
    from routes.auth import auth_bp, auth_ns
    from routes.users import users_bp, users_ns
    from routes.tasks import tasks_bp, tasks_ns
    from routes.tags import tags_bp, tags_ns
    from routes.sessions import sessions_bp, sessions_ns
    
    # Add namespaces to API
    api.add_namespace(auth_ns)
    api.add_namespace(users_ns)
    api.add_namespace(tasks_ns)
    api.add_namespace(tags_ns)
    api.add_namespace(sessions_ns)
    
    # Initialize API
    api.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
    
    # Root endpoint using standard Flask route
    @app.route("/")
    def hello_world():
        return "<p>Hello, World! The API documentation is available at <a href='/swagger'>Swagger UI</a></p>"
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 5000)))