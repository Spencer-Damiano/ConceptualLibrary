from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

def create_sample_tags():
    load_dotenv()
    
    # Connect to MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'productivity_app')
    
    client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]
    
    # Sample tags data with color codes
    sample_tags = [
        {
            "name": "Work",
            "color": "#FF4444",  # Red
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "version": 1
        },
        {
            "name": "Study",
            "color": "#4444FF",  # Blue
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "version": 1
        },
        {
            "name": "Personal",
            "color": "#44FF44",  # Green
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "version": 1
        },
        {
            "name": "Urgent",
            "color": "#FF0000",  # Bright Red
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "version": 1
        },
        {
            "name": "Important",
            "color": "#FFA500",  # Orange
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "version": 1
        },
        {
            "name": "Meeting",
            "color": "#800080",  # Purple
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "version": 1
        },
        {
            "name": "Project",
            "color": "#008080",  # Teal
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "version": 1
        },
        {
            "name": "Research",
            "color": "#FFD700",  # Gold
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "version": 1
        }
    ]
    
    try:
        # Insert tags if they don't exist
        for tag in sample_tags:
            db.tags.update_one(
                {"name": tag["name"]},
                {"$setOnInsert": tag},
                upsert=True
            )
        
        # Count and print the number of tags
        tag_count = db.tags.count_documents({})
        print(f"Sample tags created successfully! Total tags: {tag_count}")
        
        # Return tag IDs for use in task tags
        return {tag["name"]: db.tags.find_one({"name": tag["name"]})["_id"] 
                for tag in sample_tags}
        
    except Exception as e:
        print(f"Error creating sample tags: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_tags()