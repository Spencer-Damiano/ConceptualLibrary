from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import random

def create_sample_tasks():
    load_dotenv()
    
    # Connect to MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'productivity_app')
    
    client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]
    
    # Get existing users
    users = list(db.users.find({"userType": "user"}))
    
    if not users:
        raise Exception("Please ensure users exist before creating tasks")
    
    # Sample task templates
    task_templates = [
        "Review {project} documentation",
        "Prepare presentation for {topic}",
        "Update weekly report for {project}",
        "Schedule meeting with {team}",
        "Complete {type} training module",
        "Debug {project} issue",
        "Write test cases for {feature}",
        "Refactor {component} code",
        "Create backup of {system}",
        "Deploy {project} to staging"
    ]
    
    # Variables to fill in templates
    projects = ["Frontend", "Backend", "Database", "API", "Mobile App"]
    topics = ["Q4 Goals", "Product Launch", "Team Updates", "Technical Review"]
    teams = ["Development", "Design", "Marketing", "Management"]
    types = ["Security", "Performance", "DevOps", "Agile"]
    features = ["Authentication", "Dashboard", "Reports", "User Profile"]
    components = ["Login", "Navigation", "Data Processing", "File Upload"]
    systems = ["Production", "Development", "Testing", "Staging"]
    
    # Task types for our application
    task_types = ['todo', 'distraction']
    
    # Create sample tasks
    sample_tasks = []
    
    for user in users:
        # Create 10-15 tasks per user
        num_tasks = random.randint(10, 15)
        
        for _ in range(num_tasks):
            template = random.choice(task_templates)
            
            # Replace template variables
            description = template.format(
                project=random.choice(projects),
                topic=random.choice(topics),
                team=random.choice(teams),
                type=random.choice(types),
                feature=random.choice(features),
                component=random.choice(components),
                system=random.choice(systems)
            )
            
            # Decide if this is a todo or distraction (80% todo, 20% distraction)
            task_type = random.choices(task_types, weights=[0.8, 0.2])[0]
            
            task = {
                "userId": user['_id'],
                "description": description,
                "isCompleted": random.choice([True, False, False, False]),  # 25% completion rate
                "taskType": task_type, 
                "status": random.choice(['pending', 'active', 'completed']),
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "version": 1
            }
            
            # Ensure completed tasks have isCompleted=True
            if task["status"] == "completed":
                task["isCompleted"] = True
            
            sample_tasks.append(task)
    
    try:
        # Insert tasks
        if sample_tasks:
            result = db.tasks.insert_many(sample_tasks)
            print(f"Created {len(result.inserted_ids)} sample tasks")
            
            # Print task statistics
            print("\nTask Statistics:")
            for user in users:
                total_tasks = db.tasks.count_documents({"userId": user['_id']})
                completed_tasks = db.tasks.count_documents({
                    "userId": user['_id'],
                    "isCompleted": True
                })
                todo_tasks = db.tasks.count_documents({
                    "userId": user['_id'],
                    "taskType": "todo"
                })
                distraction_tasks = db.tasks.count_documents({
                    "userId": user['_id'],
                    "taskType": "distraction"
                })
                
                print(f"User {user['username']}:")
                print(f"  Total tasks: {total_tasks}")
                print(f"  Completed tasks: {completed_tasks}")
                print(f"  Completion rate: {(completed_tasks/total_tasks*100):.1f}%")
                print(f"  Todo tasks: {todo_tasks}")
                print(f"  Distraction tasks: {distraction_tasks}")
        
            return result.inserted_ids
            
    except Exception as e:
        print(f"Error creating sample tasks: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_tasks()