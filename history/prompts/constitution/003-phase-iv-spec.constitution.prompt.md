---
id: "003"
title: "Phase IV Specification JSON"
stage: "spec"
date_iso: "2026-02-04"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "user"
command: "create phase iv spec"
labels: ["specification", "json", "kubernetes", "agents", "minikube", "helm"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files_yaml: |
  - .specify/memory/phase-iv-spec.json
tests_yaml: |
  - none
prompt_text: |
  /specifyplus

  You are the Phase IV Specification Agent for the Cloud-Native Todo Chatbot project.

  Task:
  Generate a fully detailed, agent-executable specification for deploying the Todo Chatbot locally on Minikube using AI-driven DevOps.

  Requirements (follow the constitution strictly):
  1. Reference the Phase IV Agent Constitution for all rules, agents, workflow, and constraints.
  2. Output a JSON object that includes:
     - project_title
     - purpose
     - core_principles
     - tooling_canon
     - agents (with name, authority, inputs, outputs, rules)
     - workflow
     - acceptance_criteria
     - prohibitions
     - audit_evidence
     - amendment_process
  3. Include concrete details for each AI agent:
     - Specify what each agent will generate and execute
     - Specify dependencies between agents (e.g., Docker AI before Helm generation)
  4. Add execution constraints:
     - No manual coding
     - No handwritten YAML or Dockerfiles
     - Deployment strictly on Minikube
  5. Ensure the output is **strict JSON**:
     - All keys quoted
     - Values are strings, arrays, or objects
     - No comments or extra text
  6. Make the spec **agent-ready**, so it can directly drive:
     - Docker AI (Gordon)
     - kubectl-ai
     - kagent
     - Helm charts
     - Deployment & validation on Minikube
response_text: |
  Created a comprehensive JSON specification for the Phase IV Cloud-Native Todo Chatbot deployment with:

  - Detailed project title and purpose for the Kubernetes deployment
  - Six core principles following the constitution (Spec-Driven, No Manual Coding, etc.)
  - Complete tooling canon with all required tools (Docker Desktop, Gordon, Minikube, Helm, kubectl-ai, kagent)
  - Six agent definitions with specific authority, inputs, outputs, and rules
  - Clear workflow from Specification to Validation
  - Detailed acceptance criteria for deployment success
  - Prohibitions to ensure compliance with no-manual-coding and local-first principles
  - Audit and amendment processes defined

  The specification is fully agent-ready and executable by AI agents following the constitution.
outcome: "Successfully created a complete JSON specification for Phase IV deployment following all constitutional requirements."
evaluation: "JSON specification contains all required fields and is structured to be directly executable by AI agents."
---

# Prompt History Record: Phase IV Specification JSON

## Context
Creating a complete JSON specification for Phase IV Cloud-Native Todo Chatbot deployment following constitutional requirements.

## Changes Made
- Created a comprehensive JSON specification with all required fields
- Defined 6 agents with specific roles, authorities, inputs, outputs, and rules
- Established workflow from specification to validation
- Set clear acceptance criteria and prohibitions
- Ensured compliance with no-manual-coding and local-first principles

## Impact
The specification is agent-ready and executable by AI agents working on the Kubernetes deployment project.