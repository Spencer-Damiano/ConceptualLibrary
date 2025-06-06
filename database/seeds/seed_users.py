from pymongo import MongoClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

def create_sample_users():
    load_dotenv()
    
    # Connect to MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'productivity_app')
    
    client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]
    
    # Sample users data
    sample_users = [
        {
            "username": "admin_user",
            "password": generate_password_hash("admin123"),
            "userType": "admin",
            "isActive": True,
            "email": "admin@example.com",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
            "lastLoginAt": None,
            "version": 1
        },
        {
            "username": "test_user1",
            "password": generate_password_hash("test123"),
            "userType": "user",
            "isActive": True,
            "email": "user1@example.com",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
            "lastLoginAt": None,
            "version": 1
        },
        {
            "username": "test_user2",
            "password": generate_password_hash("test456"),
            "userType": "user",
            "isActive": True,
            "email": "user2@example.com",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
            "lastLoginAt": None,
            "version": 1
        }
    ]
    
    try:
        # Insert users if they don't exist
        for user in sample_users:
            db.users.update_one(
                {"username": user["username"]},
                {"$setOnInsert": user},
                upsert=True
            )
        print("Sample users created successfully!")
        
        # Return the user IDs for use in other sample data
        return {user["username"]: db.users.find_one({"username": user["username"]})["_id"] 
                for user in sample_users}
        
    except Exception as e:
        print(f"Error creating sample users: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_users()