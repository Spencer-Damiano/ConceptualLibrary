from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import time

# Import all seed scripts
from seeds.seed_users import create_sample_users
from seeds.seed_tags import create_sample_tags
from seeds.seed_sessions import create_sample_sessions
from seeds.seed_tasks import create_sample_tasks
from seeds.seed_task_tags import create_sample_task_tags

def clear_database():
    """Clear all collections from the database"""
    load_dotenv()
    
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'productivity_app')
    
    client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]
    
    collections = ['users', 'sessions', 'timerTypes', 'tasks', 'tags', 'taskTags', 'auditLogs']
    
    for collection in collections:
        if collection in db.list_collection_names():
            db[collection].delete_many({})
            print(f"Cleared collection: {collection}")

def seed_database(clear_first=False):
    """
    Run all seed scripts in the correct order.
    
    Args:
        clear_first (bool): Whether to clear the database before seeding
    """
    start_time = time.time()
    
    try:
        print("=== Starting Database Seeding Process ===")
        
        if clear_first:
            print("\n--- Clearing existing data ---")
            clear_database()
        
        print("\n--- Creating Users ---")
        user_ids = create_sample_users()
        
        print("\n--- Creating Tags ---")
        tag_ids = create_sample_tags()
        
        print("\n--- Creating Sessions ---")
        create_sample_sessions()
        
        print("\n--- Creating Tasks ---")
        create_sample_tasks()
        
        print("\n--- Creating Task-Tag Relationships ---")
        create_sample_task_tags()
        
        end_time = time.time()
        print(f"\n=== Database Seeding Completed Successfully ===")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"\nError during database seeding: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed the database with sample data')
    parser.add_argument('--clear', action='store_true', 
                      help='Clear the database before seeding')
    args = parser.parse_args()
    
    seed_database(clear_first=args.clear)