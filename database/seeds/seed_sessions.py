from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import random

def create_sample_sessions():
    load_dotenv()
    
    # Connect to MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'productivity_app')
    
    client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]
    
    # Get existing users and timer types
    users = list(db.users.find({"userType": "user"}))
    timer_types = list(db.timerTypes.find())
    
    if not users or not timer_types:
        raise Exception("Please ensure users and timer types exist before creating sessions")
    
    # Sample session statuses
    statuses = ['completed', 'completed', 'completed', 'paused', 'active']  # More completed for realism
    
    # Create sample sessions for the past week
    sample_sessions = []
    for user in users:
        # Create 3-5 sessions per user per day for the past 7 days
        for days_ago in range(7):
            num_sessions = random.randint(3, 5)
            base_date = datetime.utcnow() - timedelta(days=days_ago)
            
            for session_num in range(num_sessions):
                status = random.choice(statuses)
                start_time = base_date.replace(
                    hour=random.randint(9, 17),
                    minute=random.randint(0, 59)
                )
                
                session = {
                    "userId": user['_id'],
                    "timerTypeId": random.choice(timer_types)['_id'],
                    "startTime": start_time,
                    "workDuration": 25,  # Standard Pomodoro duration
                    "breakDuration": 5,
                    "status": status,
                    "isActive": True,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow(),
                    "version": 1
                }
                
                # Add endTime for completed sessions
                if status == 'completed':
                    session["endTime"] = start_time + timedelta(minutes=25)
                
                sample_sessions.append(session)
    
    try:
        if sample_sessions:
            # Insert sessions
            result = db.sessions.insert_many(sample_sessions)
            print(f"Created {len(result.inserted_ids)} sample sessions")
            
            # Print some session statistics
            print("\nSession Statistics:")
            for user in users:
                user_sessions = db.sessions.count_documents({"userId": user['_id']})
                print(f"User {user['username']}: {user_sessions} sessions")
                
    except Exception as e:
        print(f"Error creating sample sessions: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_sessions()