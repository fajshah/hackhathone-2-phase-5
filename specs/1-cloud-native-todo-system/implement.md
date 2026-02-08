# Implementation Guide: Cloud-Native Todo Chatbot System

**Feature**: Cloud-Native Todo Chatbot System
**Date**: 2026-02-05
**Spec**: [specs/1-cloud-native-todo-system/spec.md](./spec.md)
**Plan**: [specs/1-cloud-native-todo-system/plan.md](./plan.md)
**Tasks**: [specs/1-cloud-native-todo-system/tasks.md](./tasks.md)

## 1. Implementation Objective

This document translates Tasks into real system implementation. It defines HOW agents should build services, infrastructure, and integrations to ensure production-grade, stable, and scalable output. It minimizes errors, rework, and guesswork by providing clear, step-by-step implementation guidance that follows the exact sequence defined in the task breakdown.

## 2. Implementation Authority Rules

Strict execution hierarchy: Constitution > Specify > Plan > Tasks > Implement > Code

Agents MUST:
* Follow tasks strictly in the defined order and sequence
* Respect architecture decisions made in previous phases
* Avoid deviation from the approved technology stack
* Implement only components defined in the tasks

Agents MUST NOT:
* Add unplanned services beyond those specified
* Change infrastructure choices already decided
* Modify system design independently

## 3. Global Implementation Strategy

Build the system incrementally following this approach:
* Service-by-service development
* Layer-by-layer construction
* Fully containerized deployment
* Kubernetes-first mindset
* Event-driven communication first

Follow this exact order:
1. Core infrastructure (T001-T009, T010-T018)
2. Backend services (T019-T038)
3. Event system (T039-T062)
4. Frontend implementation (T063-T070)
5. Containerization (T071-T075)
6. Kubernetes deployment (T076-T083)
7. Helm packaging (T084-T088)
8. CI/CD integration (T089-T094)
9. Testing & validation (T095-T100)
10. Polish & production readiness (T101-T108)

## 4. Backend Implementation Guidelines

### FastAPI Structure
* Organize code in backend/src/ following the planned structure:
  - models/: Data models and database schemas
  - services/: Business logic and service classes
  - api/: API route handlers and request/response models
  - kafka/: Kafka integration and event handling
  - dapr/: Dapr integration and service invocation

### Clean Folder Architecture
* Keep separation of concerns with distinct modules
* Use consistent naming conventions
* Implement proper error handling and logging

### API Standards
* Create async-first endpoints for performance
* Implement proper request/response validation
* Add health check endpoint at `/health`
* Include proper status codes and error responses

### Dapr Integration
* Initialize Dapr sidecars as part of the service startup
* Use Dapr clients for pub/sub, state, and secrets
* Implement service invocation for inter-service communication

## 5. Frontend Implementation Guidelines

### API Integration Standards
* Create service layer for backend API communication
* Implement proper error handling for network requests
* Handle loading states and user feedback appropriately

### Environment Configuration
* Use environment variables for different deployment targets
* Implement proper CORS configuration for local/production
* Ensure frontend can communicate with backend via Kubernetes services

### Production Build
* Optimize bundle size and loading performance
* Implement proper asset caching strategies
* Ensure responsive design for different screen sizes

## 6. Event System Implementation (Kafka + Dapr)

### Producer Logic (T036, T045, T050)
* Create dedicated Kafka producers for each event type
* Implement proper serialization (JSON preferred)
* Add error handling and retry mechanisms
* Ensure events are published after successful business operations

### Consumer Services (T054-T058, T049)
* Create event loop that continuously polls Kafka topics
* Implement proper deserialization
* Add error handling to prevent consumer crashes
* Implement acknowledgment after successful processing

### Topic Implementation
* Create three mandatory topics as specified:
  - task-events: For task lifecycle events
  - reminders: For reminder scheduling and notifications
  - task-updates: For task status change events

### Dapr Pub/Sub Integration
* Configure Dapr components to connect to Kafka
* Use Dapr's pub/sub building blocks rather than direct Kafka clients where possible
* Implement proper topic and subscription configurations

## 7. State & Database Implementation

### Neon/Postgres Connection
* Implement connection pooling for optimal performance
* Use environment variables for database credentials
* Implement proper error handling for connection failures
* Add retry logic for transient database issues

### DB Schema & Models
* Create models that match the data-model.md specifications
* Implement proper indexing strategies as defined
* Add validation rules at the model level
* Create migration scripts for schema evolution

### Dapr State Integration
* Use Dapr state store for session and temporary data
* Implement proper key naming conventions
* Add TTL for temporary state when applicable
* Ensure state operations are idempotent

### Idempotent Operations
* Design all data operations to handle duplicates safely
* Implement unique constraints where needed
* Add correlation IDs to track related operations
* Use optimistic locking for concurrent updates

## 8. Reminder System Implementation

### Dapr Jobs API Usage (T042, T044)
* Register scheduled jobs with Dapr Jobs API
* Include proper job identifiers and metadata
* Implement job cancellation for reminder updates
* Add error handling for job scheduling failures

### Scheduled Triggers
* Calculate execution times based on user requests
* Store reminder metadata for processing
* Implement proper timezone handling
* Add grace periods for system delays

### Non-blocking Execution
* Schedule reminders without blocking the main thread
* Implement callback mechanisms for completed jobs
* Handle missed or delayed reminders appropriately
* Log reminder execution status for debugging

## 9. Kubernetes Implementation Standards

### Deployment YAMLs
* Use proper resource limits and requests
* Include health checks (readiness and liveness probes)
* Configure proper service accounts and RBAC if needed
* Add labels and annotations for proper identification

### Service Configuration
* Create ClusterIP services for internal communication
* Configure external access through LoadBalancer or Ingress
* Set up proper port mappings
* Enable service discovery through Kubernetes DNS

### Configuration Management
* Use ConfigMaps for non-sensitive configuration
* Use Secrets for sensitive data (credentials, keys)
* Parameterize values through environment variables
* Ensure no hardcoded dependencies in manifests

### Infrastructure Requirements
* No localhost dependencies - use service names for inter-service communication
* No hardcoded IPs - rely on Kubernetes DNS
* Services must be discoverable within the cluster
* Implement proper namespace isolation

## 10. Helm Implementation Standards

### Chart Structure
* Organize templates in charts/todo-chatbot/templates/
* Maintain proper Chart.yaml metadata
* Use values.yaml for configurable parameters
* Implement subcharts if services become complex

### Parameterization
* Make environment-specific values configurable
* Allow customization of resource limits
* Enable/disable features through values
* Provide sensible defaults for all parameters

### Multi-environment Support
* Parameterize environment-specific settings
* Support for dev, staging, and production configurations
* Allow different configurations for each environment
* Include environment-specific best practices

## 11. CI/CD Implementation Guidelines

### GitHub Actions Structure
* Create separate workflow files for each service
* Implement proper build, test, and deployment stages
* Use proper branch protection and approval processes
* Add notifications for deployment success/failure

### Docker Build Automation
* Implement multi-stage Docker builds
* Use proper tagging strategies (git tag, commit SHA)
* Scan images for security vulnerabilities
* Push to container registry after successful builds

### Deployment Automation
* Deploy via Helm charts for consistency
* Implement blue-green or rolling deployment strategies
* Add proper health checks before completing deployments
* Implement rollback procedures for failed deployments

## 12. Reliability Implementation Rules

### Health Checks (T035, T105)
* Implement liveness and readiness probes
* Check internal dependencies (database, Kafka, Dapr)
* Monitor service-specific metrics
* Include application-specific health indicators

### Retry Mechanisms (T029, T053)
* Implement exponential backoff for retries
* Use circuit breaker pattern for failing services
* Set appropriate retry limits to prevent infinite loops
* Log retry attempts for monitoring and debugging

### Event Handling Safety
* Implement idempotency for event processing
* Use dead letter queues for unprocessable events
* Add event deduplication mechanisms
* Include proper error handling in all event flows

### Observability
* Add structured logging with consistent formats
* Include request IDs for traceability
* Expose metrics for monitoring systems
* Implement distributed tracing where appropriate

## 13. Performance Implementation Doctrine

### Async-First Patterns
* Use async/await for I/O operations
* Implement non-blocking operations wherever possible
* Optimize database queries with proper indexing
* Cache frequently accessed data where appropriate

### Event Streaming Optimization
* Batch event processing where feasible
* Use appropriate serialization formats
* Implement proper partitioning strategies
* Monitor throughput and adjust as needed

### Scaling Compatibility
* Design services to handle varying loads
* Implement proper resource configuration
* Use horizontal pod autoscaling where appropriate
* Ensure stateless services where possible

## 14. Security Implementation Doctrine

### Credential Management
* Never hardcode credentials in source code
* Use Dapr secrets API for sensitive data
* Implement proper Kubernetes secrets for sensitive configuration
* Rotate credentials periodically

### Secure Connections
* Use TLS for all service-to-service communication
* Implement proper authentication and authorization
* Validate and sanitize all inputs
* Protect against common security vulnerabilities

### Access Control
* Implement principle of least privilege
* Use proper authentication mechanisms
* Log security-relevant events
* Regularly audit access controls

## 15. Integration Discipline

### Dapr Integration
* Every service must initialize Dapr sidecar
* Use Dapr building blocks for all infrastructure interactions
* Configure proper Dapr components for pub/sub, state, secrets
* Implement Dapr service invocation for service-to-service calls

### Kafka Integration
* All event communication must go through Kafka topics
* Implement proper topic producers and consumers
* Use Dapr Kafka binding when available
* Ensure event-driven communication patterns

### Kubernetes Compatibility
* Services must be deployable to Kubernetes
* Use proper Kubernetes service discovery
* Implement health checks and readiness probes
* Configure proper resource limits and requests

## 16. Error Prevention Guidelines

### Tight Coupling Prevention
* Use event-driven communication instead of direct calls
* Implement proper service boundaries
* Avoid shared databases between services
* Use asynchronous processing for inter-service communication

### Blocking Workflow Prevention
* Use async patterns for I/O operations
* Implement proper queuing mechanisms
* Avoid synchronous calls between services
* Design for eventual consistency

### State Duplication Prevention
* Maintain single source of truth for data
* Use event sourcing for audit trails
* Implement proper data consistency patterns
* Avoid storing the same data in multiple services

### Architecture Change Prevention
* Follow the planned architecture strictly
* Don't introduce unplanned services
* Maintain the defined technology stack
* Respect service boundaries and responsibilities

## 17. Implementation Completion Criteria

Implementation is considered complete when:
* All 108 tasks in tasks.md are marked as completed [X]
* All user stories (US1, US2, US3) are fully implemented
* All services can run independently in containerized environment
* Event-driven communication is working end-to-end
* Kubernetes deployment manifests are functional
* Helm charts are successfully deployable
* CI/CD pipelines execute without errors
* All acceptance criteria from user stories are met
* System can handle concurrent users and scale horizontally
* Security and reliability requirements are satisfied

## 18. Task Execution Checklist

This implementation guide is to be used in conjunction with the detailed task list in tasks.md. Each task should be executed in sequence, with proper verification of completion before proceeding to the next task. Use the following process:

1. Read the task description carefully
2. Understand the expected output
3. Implement the required changes
4. Test the implementation locally
5. Verify the output matches expectations
6. Mark the task as completed [X] in tasks.md
7. Move to the next task

For parallel tasks [P], multiple can be worked on simultaneously, but ensure proper coordination to avoid conflicts when modifying shared files.