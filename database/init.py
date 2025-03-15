from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def init_database():
    # Get MongoDB connection details from environment variables
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'conceptual_library')
    
    # Simple connection URI for local MongoDB without auth
    MONGO_URI = os.getenv('MONGO_URI', 'conceptual_library')
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        
        # Create collections with validators
        collections = ['users', 'sessions', 'timerTypes', 'tasks', 'tags', 'taskTags', 'auditLogs']
        for collection in collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
                print(f"Created collection: {collection}")
        
        # Create indexes
        db.users.create_index([('username', ASCENDING)], unique=True)
        db.users.create_index([('email', ASCENDING)], unique=True)
        
        db.sessions.create_index([('userId', ASCENDING)])
        db.sessions.create_index([('startTime', ASCENDING)])
        db.sessions.create_index([('status', ASCENDING)])
        
        db.tasks.create_index([('userId', ASCENDING)])
        db.tasks.create_index([('status', ASCENDING)])
        
        # Create initial timer types
        default_timer_types = [
            {
                'typeName': 'Pomodoro',
                'description': 'Standard 25/5 minute work/break cycle',
                'isActive': True,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                'version': 1
            }
        ]
        
        if db.timerTypes.count_documents({}) == 0:
            db.timerTypes.insert_many(default_timer_types)
            print("Added default timer types")
            
        print("Database initialization completed successfully!")
        return db
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()