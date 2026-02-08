# Agentic Todo AI Chatbot Backend

This is a stateless, AI-powered Todo chatbot backend using OpenAI Agents SDK and MCP Server architecture, enabling users to manage tasks through natural language.

## Architecture

The system follows the Agentic Dev Stack architecture with five major layers:

### 1. Database Layer
- **Technology**: SQLModel + Neon PostgreSQL
- **Models**: Task, Conversation, Message, User
- **Responsibilities**: Persistent storage for all application state
- **Constraints**: No direct DB access by AI agent, only through MCP tools

### 2. MCP Server Layer
- **Technology**: Custom MCP registry with FastAPI
- **Tools Implemented**:
  - `add_task`: Create new tasks
  - `list_tasks`: Retrieve user's tasks with filtering
  - `complete_task`: Mark tasks as completed
  - `delete_task`: Remove tasks
  - `update_task`: Modify task properties
- **Constraints**: Stateless operations, input validation, JSON responses

### 3. AI Agent Layer
- **Technology**: OpenAI Agents SDK
- **Purpose**: Natural language understanding and tool orchestration
- **Components**:
  - Intent recognition using OpenAI functions
  - Tool selection and chaining
  - Response generation
- **Constraints**: No direct DB access, stateless operation

### 4. Backend API Layer
- **Technology**: FastAPI
- **Primary Endpoint**: POST `/api/v1/users/{user_id}/chat/`
- **Flow**:
  1. Receive user message
  2. Fetch conversation history from database
  3. Persist incoming user message
  4. Build agent input (history + new message)
  5. Run agent with MCP tools
  6. Persist agent response
  7. Return response to frontend
- **Constraints**: Stateless per request

### 5. Authentication Layer
- **Technology**: JWT-based authentication
- **Endpoints**: Register, login, user profile
- **Constraints**: Stateless, no session storage

## Conversation Lifecycle (Stateless)

1. User sends message
2. Backend fetches conversation history
3. Agent processes intent
4. MCP tools mutate database
5. Agent responds
6. Messages stored
7. Response returned

Server is ready for next request with no memory retained.

## Setup Instructions

1. Install dependencies:
```bash
poetry install
```

2. Set environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/v1/users/{user_id}/chat/` - Main chat endpoint
- `GET /api/v1/users/{user_id}/conversations/` - Get user's conversations
- `GET /api/v1/conversations/{conversation_id}/messages/` - Get conversation messages
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user info

## MCP & Agent Flow

The system uses an MCP (Model Context Protocol) server pattern where:

1. MCP tools provide standardized database operations
2. AI agent interprets natural language and selects appropriate tools
3. Tools execute database operations and return structured responses
4. Agent generates natural language responses based on tool results

This ensures the AI never directly accesses the database and all state changes go through validated tools.