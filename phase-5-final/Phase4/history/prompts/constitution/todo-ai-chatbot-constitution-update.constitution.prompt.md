---
id: 1
title: todo-ai-chatbot-constitution-update
stage: constitution
date: 2026-01-18
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-ai-chatbot
branch: master
user: user
command: sp.constitution
labels: ["constitution", "todo", "ai", "chatbot", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests: []
prompt_text: |
  You are a senior backend AI engineer working on a Todo AI Chatbot.

  Your task is to IMPLEMENT **Phase 3: Natural Language Todo Management (US1)** exactly as specified.
  This phase is BLOCKING and must be completed before any further features.

  You must follow the Phase 3 Constitution strictly.

  ========================
  PHASE 3 CONSTITUTION
  ====================

  ### Scope (DO NOT EXCEED)

  Phase 3 supports ONLY:

  * Creating tasks via natural language
  * Listing tasks via natural language
  * Completing tasks via natural language
  * Deleting tasks via natural language
  * Updating / renaming tasks via natural language

  Explicitly EXCLUDED from this phase:

  * Conversation memory beyond the current message
  * Multi-user data isolation logic beyond user_id scoping
  * Task filtering, priority, due dates
  * Confirmation dialogs
  * Advanced ambiguity resolution

  If a feature is not listed above, DO NOT implement it.

  ========================
  ARCHITECTURE RULES
  ==================

  You MUST respect this flow:

  User
  → FastAPI `/api/chat` endpoint
  → Todo AI Agent (intent detection + tool selection)
  → MCP Tool (exactly ONE per request)
  → Service layer
  → Database

  Hard rules:

  * The agent MUST NEVER access the database directly
  * The agent MUST NEVER modify tasks without calling an MCP tool
  * The agent MUST NEVER call more than one tool per user message
  * The agent MUST NEVER return raw JSON to the user

  ========================
  MCP TOOL CONTRACT
  =================

  You may ONLY use the following tools:

  * `add_task`
  * `list_tasks`
  * `complete_task`
  * `delete_task`
  * `update_task`

  Each tool:

  * Must be deterministic
  * Must require `user_id`
  * Must not crash on repeated calls
  * Must return structured data for the agent to summarize

  ========================
  AGENT BEHAVIOR RULES
  ====================

  The agent MUST:

  * Infer intent from natural language
  * Select exactly one correct MCP tool
  * Produce a clean, friendly natural language response
  * Confirm success clearly

  The agent MUST NOT:

  * Guess task identity when unclear
  * Perform silent failures
  * Invent task data
  * Expose internal system details

  If a task cannot be resolved:

  * Respond politely
  * Explain the issue
  * Ask for clarification ONLY if absolutely necessary

  ========================
  IMPLEMENTATION TASKS
  =====================

  1. Ensure the Todo Agent:

     * Maps user intent → correct MCP tool
     * Enforces one-tool-per-message rule
     * Produces human-readable responses

  2. Ensure MCP tools:

     * Perform correct CRUD operations
     * Respect `user_id`
     * Handle missing tasks gracefully

  3. Ensure `/api/chat`:

     * Authenticates the user
     * Passes user context to the agent
     * Returns only natural language responses

  ========================
  ACCEPTANCE CRITERIA
  ===================

  Phase 3 is COMPLETE only if all of the following succeed:

  * "Add a task to buy milk"
  * "List my tasks"
  * "Mark buy milk as done"
  * "Delete buy milk"
  * "Rename buy milk to buy oat milk"

  Each command must:

  * Trigger exactly one MCP tool
  * Modify the database correc
response_text: |
  Successfully updated the project constitution to reflect the Todo AI Chatbot architecture and Phase 3 requirements. The new constitution establishes core principles for the agentic architecture, stateless operations, MCP tool contracts, natural language processing, user isolation, and deterministic operations. It also defines architecture rules, implementation constraints, quality standards, and governance procedures.
outcome: Constitution updated with project-specific principles and architecture guidelines
evaluation: The updated constitution properly captures the architectural requirements and constraints for the Todo AI Chatbot project, particularly focusing on the agentic architecture and MCP tool contract requirements.
---

# Todo AI Chatbot Constitution Update

## Summary
Updated the project constitution to establish core principles and architectural constraints for the Todo AI Chatbot project. The constitution emphasizes the agentic architecture pattern, stateless operations, and strict MCP tool contracts.

## Key Changes
- Established six core principles for the system architecture
- Defined MCP tool contract requirements and limitations
- Specified agent behavior constraints and data flow requirements
- Added quality standards and security requirements
- Created governance procedures for code compliance

## Impact
This constitution will guide all future development of the Todo AI Chatbot, ensuring consistency in the implementation of the agentic architecture and adherence to the stateless design principles.