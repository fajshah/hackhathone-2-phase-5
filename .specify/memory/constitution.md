<!--
SYNC IMPACT REPORT:
Version change: N/A → 1.0.0
Added sections: Core Principles (6), Architecture Rules, Implementation Constraints, Quality Standards, Governance
Removed sections: Template placeholders
Templates requiring updates: N/A (this is the first version)
Follow-up TODOs: None
-->
# Todo AI Chatbot Constitution

## Core Principles

### I. Agentic Architecture
The system MUST use an AI agent to interpret natural language and orchestrate deterministic tools. The agent acts as the orchestration layer between user input and state-changing operations.

### II. Stateless Operations
All server components MUST be stateless. All state (conversations, tasks, messages) MUST be persisted in the database. No session state on the server between requests.

### III. MCP Tool Contract
All operations that modify data MUST go through MCP tools. The agent MUST NOT access the database directly. Each user message triggers EXACTLY ONE MCP tool call.

### IV. Natural Language First
The system MUST prioritize natural language interaction. Users can express their intent in plain English (e.g., "Add a task to buy milk", "List my tasks").

### V. User Isolation
Each user's data MUST be isolated by user_id. No user MAY access another user's tasks, conversations, or messages.

### VI. Deterministic Operations
MCP tools MUST be deterministic and idempotent where appropriate. Tools MUST NOT fail silently and MUST return structured data for the agent to process.

## Architecture Rules

### Data Flow Requirements
The system MUST follow this exact flow: User → FastAPI endpoint → Todo AI Agent → MCP Tool → Service Layer → Database. No shortcuts or alternative paths are allowed.

### Agent Constraints
The agent MUST NOT access the database directly. The agent MUST NOT modify tasks without calling an MCP tool. The agent MUST NOT call more than one tool per user message. The agent MUST NOT return raw JSON to the user.

### Tool Contract Requirements
MCP tools MUST accept user context and perform user validation. Tools MUST require user_id for all operations. Tools MUST handle missing resources gracefully and return appropriate error messages.

## Implementation Constraints

### Phase 3 Scope
Phase 3 supports ONLY: creating tasks, listing tasks, completing tasks, deleting tasks, and updating tasks via natural language. All other features (conversation memory, filtering, confirmation dialogs, etc.) are explicitly excluded from this phase.

### MCP Tool Limitations
Only the following tools are allowed: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`. No additional tools may be created without explicit approval.

### Response Format
All API responses MUST be natural language summaries. Raw JSON or technical error messages MUST NOT be exposed to users.

## Quality Standards

### Error Handling
All operations MUST handle errors gracefully. Missing tasks MUST result in clear user-facing messages. Invalid user input MUST be handled with appropriate feedback.

### Test Coverage
All MCP tools MUST have comprehensive unit tests. The agent's intent detection MUST be validated against sample user inputs. API endpoints MUST have integration tests.

### Security Requirements
All database operations MUST validate user ownership of resources. Authentication MUST be verified for every request. No user data MAY be exposed to unauthorized users.

## Governance

All code changes MUST comply with these principles. Any deviation requires explicit approval and documentation. New features MUST NOT violate the stateless architecture or bypass the MCP tool contract. Code reviews MUST verify compliance with all architectural constraints.

**Version**: 1.0.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-18