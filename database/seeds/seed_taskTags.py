from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import random
import re

def create_sample_task_tags():
    load_dotenv()
    
    # Connect to MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'productivity_app')
    
    client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]
    
    # Get existing tasks and tags
    tasks = list(db.tasks.find())
    tags = list(db.tags.find())
    
    if not tasks or not tags:
        raise Exception("Please ensure tasks and tags exist before creating task-tag relationships")
    
    # Create a dictionary of tag names to their IDs for easy lookup
    tag_dict = {tag['name']: tag['_id'] for tag in tags}
    
    # Rules for automatic tag assignment
    tag_rules = {
        r'presentation|meeting': ['Meeting'],
        r'documentation|test cases': ['Work', 'Research'],
        r'debug|issue': ['Urgent'],
        r'deploy|backup': ['Important'],
        r'refactor|update': ['Project'],
        r'training|review': ['Study'],
        r'Frontend|Backend|API': ['Project', 'Work'],
    }
    
    sample_task_tags = []
    task_tag_count = {}  # To keep track of how many tags each task has
    
    for task in tasks:
        task_tags = set()  # Use set to avoid duplicate tags for the same task
        
        # Apply tag rules based on task description
        description = task['description'].lower()
        for pattern, tag_names in tag_rules.items():
            if re.search(pattern, description, re.IGNORECASE):
                task_tags.update(tag_names)
        
        # Always add at least one tag if none were added by rules
        if not task_tags:
            task_tags.add(random.choice(['Work', 'Personal', 'Project']))
        
        # Add "Urgent" tag to high priority tasks if not already tagged
        if task['priority'] >= 4 and 'Urgent' not in task_tags:
            task_tags.add('Urgent')
        
        # Create task-tag relationships
        for tag_name in task_tags:
            task_tag = {
                "taskId": task['_id'],
                "tagId": tag_dict[tag_name],
                "createdAt": datetime.utcnow(),
                "version": 1
            }
            sample_task_tags.append(task_tag)
            
        task_tag_count[str(task['_id'])] = len(task_tags)
    
    try:
        # Insert task-tag relationships
        if sample_task_tags:
            result = db.taskTags.insert_many(sample_task_tags)
            print(f"Created {len(result.inserted_ids)} task-tag relationships")
            
            # Print statistics
            print("\nTask-Tag Statistics:")
            print(f"Average tags per task: {sum(task_tag_count.values()) / len(task_tag_count):.1f}")
            print(f"Total task-tag relationships: {len(sample_task_tags)}")
            
            # Print tag usage statistics
            tag_usage = {}
            for task_tag in sample_task_tags:
                tag_name = next(tag['name'] for tag in tags if tag['_id'] == task_tag['tagId'])
                tag_usage[tag_name] = tag_usage.get(tag_name, 0) + 1
            
            print("\nTag Usage:")
            for tag_name, count in sorted(tag_usage.items(), key=lambda x: x[1], reverse=True):
                print(f"{tag_name}: {count} tasks")
            
    except Exception as e:
        print(f"Error creating task-tag relationships: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_task_tags()