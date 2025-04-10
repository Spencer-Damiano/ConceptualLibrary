from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

def migrate_tasks():
    load_dotenv()
    
    # Connect to MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'conceptual_library')
    
    client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]
    
    # Find all tasks that don't have a taskType field
    tasks_to_update = list(db.tasks.find({'taskType': {'$exists': False}}))
    
    if not tasks_to_update:
        print("No tasks found that need migration.")
        return
    
    print(f"Found {len(tasks_to_update)} tasks to migrate.")
    
    # Update each task:
    # 1. Add taskType field (default to 'todo')
    # 2. Remove priority field
    for task in tasks_to_update:
        update_data = {
            'taskType': 'todo',  # Default all existing tasks to todo
            'updatedAt': datetime.now(timezone.utc)
        }
        
        # Use $unset to remove the priority field
        db.tasks.update_one(
            {'_id': task['_id']},
            {
                '$set': update_data,
                '$unset': {'priority': ''}
            }
        )
    
    print(f"Successfully migrated {len(tasks_to_update)} tasks.")

if __name__ == "__main__":
    migrate_tasks()