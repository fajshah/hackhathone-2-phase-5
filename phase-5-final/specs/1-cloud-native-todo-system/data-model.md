# Data Model: Cloud-Native Todo Chatbot System

## Core Entities

### Task
**Description**: Represents a user's to-do item with associated metadata and status

**Fields**:
- `id` (UUID/string): Unique identifier for the task
- `title` (string): Task title/description (required, max 255 chars)
- `description` (string): Optional detailed description
- `status` (enum): One of ['pending', 'completed', 'in-progress'] (default: 'pending')
- `priority` (enum): One of ['low', 'medium', 'high', 'critical'] (default: 'medium')
- `due_date` (datetime): Optional deadline for task completion
- `created_at` (datetime): Timestamp of creation
- `updated_at` (datetime): Timestamp of last modification
- `user_id` (string/UUID): Reference to user who owns the task
- `assigned_to` (string/UUID): Reference to user assigned to task (optional)
- `tags` (array<string>): Array of string tags for categorization

**Validation Rules**:
- Title must be 1-255 characters
- Due date cannot be in the past when status is pending
- Status transitions: pending → in-progress → completed (no backward transitions allowed)

**Relationships**:
- One-to-many with User (owned_by)
- One-to-many with Reminder (has_reminders)

### Reminder
**Description**: Represents scheduled notifications for tasks

**Fields**:
- `id` (UUID/string): Unique identifier for the reminder
- `task_id` (string/UUID): Reference to associated task
- `user_id` (string/UUID): Reference to user receiving reminder
- `scheduled_time` (datetime): When reminder should be sent
- `status` (enum): One of ['scheduled', 'sent', 'cancelled'] (default: 'scheduled')
- `method` (enum): One of ['email', 'push', 'sms', 'in-app'] (default: 'in-app')
- `created_at` (datetime): Timestamp of creation
- `sent_at` (datetime): Timestamp when reminder was sent (nullable)

**Validation Rules**:
- Scheduled time must be in the future
- Task must exist and be in pending status
- Only one active reminder per task at a time

**Relationships**:
- Many-to-one with Task (belongs_to)
- Many-to-one with User (recipient)

### User Session
**Description**: Maintains conversational state for user interactions

**Fields**:
- `session_id` (string/UUID): Unique session identifier
- `user_id` (string/UUID): Reference to user
- `current_context` (string): Current conversational context
- `last_interaction` (datetime): Timestamp of last chat interaction
- `created_at` (datetime): Session creation time
- `expires_at` (datetime): Session expiration time

**Validation Rules**:
- Session expires after 24 hours of inactivity
- One active session per user

**Relationships**:
- Many-to-one with User (belongs_to)

### Event Log
**Description**: Records all system events for audit and replay

**Fields**:
- `id` (UUID/string): Unique event identifier
- `event_type` (string): Type of event (task-created, reminder-scheduled, etc.)
- `payload` (JSON): Event data in JSON format
- `timestamp` (datetime): When event occurred
- `source_service` (string): Which service generated the event
- `correlation_id` (string): For tracking related events

**Validation Rules**:
- All fields are required
- Event type must be from predefined list

**Relationships**:
- None (event sourced system)

## State Transitions

### Task State Transitions
- `pending` → `in-progress`: When user starts working on task
- `in-progress` → `completed`: When user marks task as done
- `completed` → `pending`: Only through explicit user action to reopen
- `pending` → `cancelled`: Through explicit user action (new state might be needed)

### Reminder State Transitions
- `scheduled` → `sent`: When reminder is delivered to user
- `scheduled` → `cancelled`: When user cancels reminder or task is completed
- `sent` → `reopened`: When user requests reminder again

## API Contract Overview

### Task Operations
- POST /tasks: Create new task
- GET /tasks: Retrieve user's tasks
- GET /tasks/{id}: Retrieve specific task
- PUT /tasks/{id}: Update task
- DELETE /tasks/{id}: Delete task
- POST /tasks/{id}/complete: Mark task as completed
- POST /tasks/{id}/assign: Assign task to user

### Reminder Operations
- POST /reminders: Schedule new reminder
- GET /reminders: Get user's upcoming reminders
- DELETE /reminders/{id}: Cancel scheduled reminder
- PUT /reminders/{id}/reschedule: Change reminder time

### Chat Operations
- POST /chat: Send message to chatbot
- GET /chat/session: Get current session state
- POST /chat/session/reset: Reset conversation context

## Database Schema Considerations

### Indexing Strategy
- Tasks: Index on user_id, status, due_date for efficient querying
- Reminders: Index on user_id, scheduled_time, status
- Sessions: Index on user_id, expires_at for cleanup
- Events: Index on event_type, timestamp for audit queries

### Partitioning Strategy
- Events table: Partition by date (monthly partitions)
- Tasks table: Partition by user_id hash if scale requires

### Constraints
- Foreign key relationships between entities
- Check constraints for enum values
- Unique constraints where appropriate (active sessions per user)