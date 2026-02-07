---
id: "PHR-0001"
title: "Constitution Creation"
stage: "constitution"
date: "2026-02-05"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "unknown"
command: "/sp.phr"
labels: ["constitution", "specification", "governance", "architecture"]
links_spec: null
links_ticket: null
links_adr: null
links_pr: null
files_yaml:
  - ".specify/memory/constitution.md"
tests_yaml:
  - "none"
---

# Prompt History Record: Constitution Creation

## PROMPT TEXT
```
You are generating the **speckit.constitution** file for Phase V of an advanced cloud-native Todo Chatbot project. This constitution must be extremely detailed, production-grade, and written so clearly that it prevents repeated clarification, avoids architectural mistakes, and enables agents to complete large portions of work correctly in one pass.

Your objective is to define the NON-NEGOTIABLE engineering principles, constraints, and system rules that ALL agents must follow throughout development.

This is a Phase V (Advanced Cloud Deployment) system that includes:

* Kubernetes (Minikube → OKE)
* Helm deployments
* Dockerized microservices
* Kafka-based event-driven architecture
* Dapr (Pub/Sub, State, Jobs, Secrets, Service Invocation)
* FastAPI backend
* Frontend service
* Neon/Postgres database
* CI/CD via GitHub Actions
* Spec-Driven Development using Spec-KitPlus
* Agentic workflow (Claude Code + MCP)

The constitution must be written as a professional engineering governance document.

---

# Required Output Structure

Generate a full, well-structured constitution with the following sections:

## 1. Purpose

Explain that this document defines the core engineering laws of the system.
State that all agents MUST follow it before coding.

## 2. Core Development Philosophy

Define:

* Spec-Driven Development is mandatory
* No coding without tasks
* No architecture without plan
* No features without specification
* Deterministic, traceable engineering

## 3. Non-Negotiable Engineering Principles

Include strong, strict principles such as:

* Cloud-Native First
* Event-Driven First
* Loose Coupling Over Tight Coupling
* Scalability Over Simplicity
* Reliability Over Speed
* Security by Default
* Observability by Design
* Idempotent Operations
* Stateless Services
* Sidecar-Driven Integration via Dapr

Each principle must include:

* Why it exists
* How agents must apply it

## 4. Architecture Rules

Define strict architectural constraints:

* Microservices-based system
* Kubernetes is the primary runtime
* Docker is mandatory
* Helm is required for deployment
* Services must communicate via:

  * Dapr Pub/Sub
  * Service Invocation
* Direct service-to-service coupling must be avoided

## 5. Event-Driven System Mandate

Define that Kafka is the backbone of communication.

Agents must treat the system as:

* Producer → Topic → Consumer model
* Async processing only
* No blocking workflows

Include required topics:

* task-events
* reminders
* task-updates

## 6. Dapr Enforcement Rules

Agents must:

* Prefer Dapr over direct SDK integrations
* Use:

  * Pub/Sub for events
  * State store for conversation state
  * Jobs API for reminders
  * Secrets API for credentials
  * Service invocation for communication

Explain that infrastructure must be abstracted via Dapr.

## 7. Kubernetes Deployment Doctrine

Define:

* Minikube first
* Then production cluster
* Helm charts required
* Container resource awareness
* Namespace isolation
* No hardcoded IPs or localhost dependencies

## 8. Data & State Governance

Define:

* Stateless backend services
* Externalized state
* DB isolation
* Event-based state updates
* Audit trail via Kafka

## 9. Agent Behavior Rules

Agents MUST:

* Check constitution before planning
* Reference spec before coding
* Reference plan before implementing
* Reference tasks before writing files

Agents MUST NOT:

* Freestyle features
* Guess architecture
* Skip steps
* Change stack
* Modify services without updating plan

## 10. Quality & Reliability Standards

Define expectations:

* Production-grade code
* Clear service boundaries
* Retry-safe logic
* Failure-tolerant patterns
* Scalable design mindset

## 11. Performance Doctrine

* Async-first architecture
* Event streaming over polling
* Distributed workload handling
* Horizontal scaling ready

## 12. Security Doctrine

* Secrets never hardcoded
* Use Kubernetes/Dapr secrets
* Principle of least privilege
* Secure service communication

## 13. CI/CD Governance

* Automated builds required
* Versioned deployments
* Infrastructure as code mindset

## 14. Spec Hierarchy Law

Define strict authority order:

Constitution > Specify > Plan > Tasks > Code

If conflict occurs:
Agents must follow the higher-level document.

## 15. Completion Objective

State clearly:

This constitution exists to:

* Reduce errors
* Prevent rework
* Enable large multi-step execution
* Ensure agents complete multiple components correctly in one flow

---

# Writing Requirements

* Write in a strong, professional, authoritative tone
* Make it detailed and comprehensive
* Make it future-proof
* Avoid vague language
* Do not write short summaries
* Do not skip sections
* Do not leave placeholders
* Produce a complete ready-to-use speckit.constitution

This document must feel like it was written by a Senior Cloud Architect governing a production-grade distributed system.
```

## RESPONSE_TEXT
Created comprehensive speckit.constitution file for Phase V Advanced Cloud-Native Todo Chatbot project with all 15 required sections including purpose, core development philosophy, non-negotiable engineering principles, architecture rules, event-driven mandates, Dapr enforcement rules, Kubernetes deployment doctrine, data governance, agent behavior rules, quality standards, performance doctrine, security doctrine, CI/CD governance, spec hierarchy law, and completion objectives.

## OUTCOME_IMPACT
Successfully generated a production-grade constitution document that establishes engineering governance for the cloud-native todo chatbot system, defining mandatory principles for all agents to follow during development, ensuring consistent, reliable, and scalable implementation across all components of the distributed system architecture.

## TESTS_SUMMARY
none

## FILES_SUMMARY
- .specify/memory/constitution.md: Created comprehensive constitution file with 15 sections covering all required engineering principles and governance rules

## NEXT_PROMPTS
None needed - constitution is complete and follows all specified requirements

## REFLECTION_NOTE
Creating a comprehensive constitution upfront helps establish clear engineering governance that prevents architectural inconsistencies and ensures all agents follow the same principles during development.

## FAILURE MODES OBSERVED
The .specify/scripts/bash/create-phr.sh script did not exist, requiring fallback to manual PHR creation. The directory structure needed to be created manually before writing the PHR file.

## NEXT EXPERIMENT TO IMPROVE PROMPT QUALITY
Verify existence of PHR scripts before attempting to call them, and have better fallback procedures for manual PHR creation with proper ID sequencing.