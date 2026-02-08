# ADR 001: Agentic Architecture for Todo AI Chatbot

## Status
Accepted

## Context
We needed to build an AI-powered todo management system that could interpret natural language commands, maintain conversation context, and provide reliable task management capabilities. Traditional rule-based systems would be insufficient for handling the variety of ways users might express their intentions.

## Decision
We chose an agentic architecture using OpenAI's Agent SDK with Model Context Protocol (MCP) tools. This approach allows us to:

1. Use AI for natural language understanding and intent recognition
2. Implement stateless tools for reliable operations
3. Maintain conversation context through database persistence
4. Separate concerns between AI decision-making and reliable execution

## Architecture Components

### Core Components
- **Todo AI Agent**: Processes natural language and decides which tools to call
- **MCP Tools**: Stateless functions for database operations (add_task, list_tasks, etc.)
- **Service Layer**: Business logic with user authorization
- **Database Layer**: PostgreSQL with SQLModel for type safety

### State Management
- Stateless server architecture (no session state on server)
- All conversation and task state persisted in database
- Context retrieval from database for each request

### Security Model
- User authentication through Better Auth
- Per-request user validation in all tools and services
- Data isolation enforced at service layer

## Consequences

### Positive
- Highly flexible natural language processing
- Scalable stateless architecture
- Clear separation between AI decision-making and reliable execution
- Strong security with per-request validation
- Good testability of individual components

### Negative
- Higher complexity than simple CRUD application
- Dependency on external AI services
- Potential latency for AI processing
- Need for careful error handling at AI/execution boundary

## Alternatives Considered

### Rule-Based Parser
- Pros: Predictable, fast, controllable
- Cons: Limited flexibility, maintenance burden, inability to handle varied user expressions

### Direct AI-to-Database
- Pros: Simpler architecture
- Cons: No transaction safety, harder to maintain consistency, security concerns

## Notes
This architecture proved effective for delivering the required functionality while maintaining scalability and security. The separation between AI decision-making and reliable execution provides both flexibility and reliability.