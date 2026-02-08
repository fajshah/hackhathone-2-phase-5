---
id: "001"
title: "Phase IV Constitution Update"
stage: "constitution"
date_iso: "2026-02-04"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "user"
command: "sp.constitution"
labels: ["constitution", "governance", "kubernetes", "agents"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files_yaml: |
  - .specify/memory/constitution.md
tests_yaml: |
  - none
prompt_text: |
  /specifyplus

  You are the SpecificationPlus Constitution Agent.

  Task:
  Create a strict, agent-executable constitution for Phase IV of the Cloud-Native Todo Chatbot project.
  This constitution will govern all AI agents (Specification, Planning, Docker AI, Helm Generation, Kubernetes Ops, Deployment & Validation).

  Requirements:
  1. Define **Project Title** and **Purpose**.
  2. Define **Core Principles** (e.g., Spec-Driven, No Manual Coding, Local-First, Reproducibility, Observability, Safety).
  3. List **Tooling Canon** (Docker Desktop, Gordon, Minikube, Helm, kubectl-ai, kagent).
  4. Define **Agent Roles & Authority**:
     - Agent A: Specification Agent
     - Agent B: Planning Agent
     - Agent C: Docker AI Agent (Gordon)
     - Agent D: Helm Generation Agent (kubectl-ai)
     - Agent E: Kubernetes Ops Agent (kagent)
     - Agent F: Deployment & Validation Agent
     - For each agent, include: Authority, Inputs, Outputs, Rules / Constraints
  5. Define **Execution Workflow**: Step-by-step spec → plan → tasks → deploy → validate
  6. Define **Acceptance Criteria**: e.g., pods ready, frontend accessible, Helm install success
  7. Define **Prohibitions**: No manual Dockerfiles, YAML, cloud usage
  8. Define **Audit & Evidence**: All specs, plans, and commands retained
  9. Define **Amendment Process**: Spec Agent revision + Planning Agent approval
  10. Output MUST be in **JSON format** suitable for AI execution, with keys:
     - project_title
     - purpose
     - core_principles (array)
     - tooling_canon (array)
     - agents (array of objects)
     - workflow (array)
     - acceptance_criteria (array)
     - prohibitions (array)
     - audit_evidence (string)
     - amendment_process (string)
response_text: |
  Updated the project constitution to govern Phase IV Cloud-Native Todo Chatbot deployment on Kubernetes. The new constitution defines:

  - Core principles for spec-driven, no-manual-coding approach
  - Tooling canon including Docker Desktop, Gordon, Minikube, Helm, kubectl-ai, kagent
  - Six distinct agent roles with specific authorities and responsibilities
  - Execution workflow from specification to validation
  - Clear acceptance criteria for deployment success
  - Prohibitions against manual coding and cloud deployment
  - Audit and amendment processes

  The constitution now governs all AI agents working on the Kubernetes deployment phase.
outcome: "Successfully updated constitution to govern Phase IV Kubernetes deployment agents and processes."
evaluation: "Constitution aligns with user requirements for governing AI agents in Kubernetes deployment with proper authority distribution."
---

# Prompt History Record: Phase IV Constitution Update

## Context
Updating the project constitution to govern Phase IV Cloud-Native Todo Chatbot deployment on Kubernetes using AI agents.

## Changes Made
- Replaced Phase 3 constitution with Phase IV constitution
- Defined new core principles for Kubernetes deployment
- Established six agent roles with specific authorities
- Outlined execution workflow for spec-driven deployment
- Set clear acceptance criteria and prohibitions
- Established governance and amendment processes

## Impact
The constitution now properly governs AI agents working on the Kubernetes deployment phase, ensuring adherence to spec-driven principles, no manual coding, and local-first deployment strategy.