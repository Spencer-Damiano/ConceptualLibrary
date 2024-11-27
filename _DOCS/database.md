# Database Schema Documentation

## Collections Overview

### Users Collection
| Field Name    | Type         | Properties                | Description |
|---------------|--------------|---------------------------|-------------|
| _id           | ObjectId     | Primary Key              | Unique identifier |
| username      | String       | Unique, Required, Indexed | User's login name |
| passwordHash  | String       | Required                  | Hashed password |
| userType      | String       | Required, Enum           | User role (admin/user) |
| isActive      | Boolean      | Required, Default: true   | Soft delete flag |
| email         | String       | Unique, Required, Indexed | User's email |
| createdAt     | DateTime     | Required                  | Creation timestamp |
| updatedAt     | DateTime     | Required                  | Last update timestamp |
| lastLoginAt   | DateTime     | Optional                  | Last login timestamp |
| version       | Number       | Required, Default: 1      | Document version |

### Sessions Collection
| Field Name     | Type     | Properties                | Description |
|----------------|----------|---------------------------|-------------|
| _id            | ObjectId | Primary Key              | Unique identifier |
| userId         | ObjectId | Required, Indexed        | Reference to Users |
| timerTypeId    | ObjectId | Required, Indexed        | Reference to TimerTypes |
| startTime      | DateTime | Required, Indexed        | Session start time |
| endTime        | DateTime | Optional, Indexed        | Session end time |
| workDuration   | Number   | Required                 | Duration in minutes |
| breakDuration  | Number   | Required                 | Break time in minutes |
| status         | String   | Required, Enum, Indexed  | active/paused/completed |
| isActive       | Boolean  | Required, Default: true  | Soft delete flag |
| createdAt      | DateTime | Required                 | Creation timestamp |
| updatedAt      | DateTime | Required                 | Last update timestamp |
| version        | Number   | Required, Default: 1     | Document version |

### TimerTypes Collection
| Field Name  | Type     | Properties                | Description |
|-------------|----------|---------------------------|-------------|
| _id         | ObjectId | Primary Key              | Unique identifier |
| typeName    | String   | Unique, Required         | Timer type name |
| description | String   | Optional                 | Type description |
| isActive    | Boolean  | Required, Default: true  | Soft delete flag |
| createdAt   | DateTime | Required                 | Creation timestamp |
| updatedAt   | DateTime | Required                 | Last update timestamp |
| version     | Number   | Required, Default: 1     | Document version |

### Tasks Collection
| Field Name   | Type     | Properties                | Description |
|--------------|----------|---------------------------|-------------|
| _id          | ObjectId | Primary Key              | Unique identifier |
| userId       | ObjectId | Required, Indexed        | Reference to Users |
| description  | String   | Required                 | Task description |
| isCompleted  | Boolean  | Required, Default: false | Completion status |
| priority     | Number   | Required, Default: 1     | Priority level (1-5) |
| status       | String   | Required, Enum, Indexed  | pending/active/completed |
| isActive     | Boolean  | Required, Default: true  | Soft delete flag |
| createdAt    | DateTime | Required                 | Creation timestamp |
| updatedAt    | DateTime | Required                 | Last update timestamp |
| version      | Number   | Required, Default: 1     | Document version |

### Tags Collection
| Field Name | Type     | Properties                | Description |
|------------|----------|---------------------------|-------------|
| _id        | ObjectId | Primary Key              | Unique identifier |
| name       | String   | Unique, Required         | Tag name |
| color      | String   | Required                 | Tag color code |
| isActive   | Boolean  | Required, Default: true  | Soft delete flag |
| createdAt  | DateTime | Required                 | Creation timestamp |
| updatedAt  | DateTime | Required                 | Last update timestamp |
| version    | Number   | Required, Default: 1     | Document version |

### TaskTags Collection
| Field Name | Type     | Properties                | Description |
|------------|----------|---------------------------|-------------|
| _id        | ObjectId | Primary Key              | Unique identifier |
| taskId     | ObjectId | Required, Indexed        | Reference to Tasks |
| tagId      | ObjectId | Required, Indexed        | Reference to Tags |
| createdAt  | DateTime | Required                 | Creation timestamp |
| version    | Number   | Required, Default: 1     | Document version |

### AuditLogs Collection
| Field Name | Type     | Properties       | Description |
|------------|----------|------------------|-------------|
| _id        | ObjectId | Primary Key     | Unique identifier |
| userId     | ObjectId | Required, Indexed| Reference to Users |
| action     | String   | Required        | Action performed |
| entityType | String   | Required        | Collection name |
| entityId   | ObjectId | Required        | Referenced document |
| oldValue   | Object   | Optional        | Previous state |
| newValue   | Object   | Optional        | New state |
| createdAt  | DateTime | Required        | Action timestamp |
| ipAddress  | String   | Required        | User's IP address |
| userAgent  | String   | Required        | User's browser info |

## Key Improvements

1. **Added Indexes**
   - User queries: username, email
   - Session queries: startTime, endTime, status
   - Task queries: status, userId + isActive
   - Audit trail: userId + entityType

2. **Enhanced Data Integrity**
   - Added status enums for Sessions and Tasks
   - Implemented soft delete with isActive flag
   - Version tracking for all documents
   - Constraints through application validation

3. **New Features**
   - Separated Tags collection with color support
   - Comprehensive audit logging
   - User session tracking
   - Enhanced metadata (createdAt, updatedAt)

4. **MongoDB-Specific Optimizations**
   - Designed for document-based structure
   - Optimized for common query patterns
   - Proper index strategy
   - Version control for documents