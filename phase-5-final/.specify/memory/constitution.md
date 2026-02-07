<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0
Added sections: AI Agent Rules, Data Rules, Event System Requirements
Modified principles: Enhanced architecture rules and cloud native requirements
Removed sections: None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md - aligned with new principles
- ✅ .specify/templates/spec-template.md - aligned with new principles
- ✅ .specify/templates/tasks-template.md - aligned with new principles
- ⚠️ .specify/templates/commands/*.md - review for outdated references
- ⚠️ README.md - update references to new constitution
Follow-up TODOs: None
-->

# Speckit Constitution - Advanced Cloud-Native Todo Chatbot (Phase V)

## 1. Purpose

This document defines the core engineering laws and non-negotiable principles that govern the development, deployment, and operation of the Phase V Advanced Cloud-Native Todo Chatbot system. All agents, developers, and automated systems must strictly adhere to these rules before engaging in any coding, architectural, or deployment activities.

This constitution serves as the foundational authority that ensures consistent, reliable, and scalable development across all components of the distributed system architecture.

## 2. Core Development Philosophy

The following principles form the bedrock of all development activities:

**Spec-Driven Development is Mandatory**: No code shall be written without a corresponding specification that has been formally reviewed and approved. All features, modifications, and enhancements must originate from a documented specification.

**No Coding Without Tasks**: Every code change must correspond to a discrete, well-defined task that has been prioritized and assigned. Ad-hoc development is strictly prohibited.

**No Architecture Without Plan**: All architectural decisions must be preceded by a formal plan that addresses scalability, reliability, security, and operational concerns. Planning must occur before any implementation begins.

**No Features Without Specification**: Every feature must be comprehensively specified before any development work commences. Feature creep and speculative implementations are forbidden.

**Deterministic, Traceable Engineering**: All development activities must be traceable from specification through implementation, testing, and deployment. Non-deterministic or unpredictable development patterns are not acceptable.

## 3. Non-Negotiable Engineering Principles

### Cloud-Native First
All services must be designed and implemented with cloud-native principles at their core. This includes containerization, microservices architecture, and cloud-platform optimization. Why: To ensure portability, scalability, and resilience. How: Implement services as stateless, immutable containers that can run consistently across any Kubernetes environment.

### Event-Driven First
The system must be fundamentally event-driven with asynchronous processing as the default pattern. Why: To achieve loose coupling, improved scalability, and fault tolerance. How: Design all major business operations as events that flow through Kafka topics, avoiding synchronous request-response patterns where possible.

### Loose Coupling Over Tight Coupling
Services must interact through well-defined interfaces with minimal shared state or direct dependencies. Why: To enable independent deployment, scaling, and maintenance of services. How: Use Dapr service invocation and pub/sub patterns instead of direct HTTP calls between services.

### Scalability Over Simplicity
Design decisions must prioritize horizontal scalability even when it increases implementation complexity. Why: The system must handle variable loads and growth without degradation. How: Implement stateless services, use external state stores, and design for distributed processing.

### Reliability Over Speed
System reliability and data integrity must take precedence over performance optimizations. Why: Production systems must be dependable and trustworthy. How: Implement retry logic, circuit breakers, proper error handling, and transactional consistency where required.

### Security by Default
Security controls must be baked into every layer of the system, not added as an afterthought. Why: To protect sensitive data and prevent security vulnerabilities. How: Use Dapr secrets management, implement authentication and authorization at all service boundaries, and follow security best practices.

### Observability by Design
All services must include comprehensive logging, metrics, and tracing from the initial implementation phase. Why: To enable effective monitoring, debugging, and performance optimization. How: Implement structured logging, expose Prometheus metrics, and use distributed tracing across service boundaries.

### Idempotent Operations
All service operations must be designed to handle repeated requests safely without adverse side effects. Why: To ensure reliability in the face of retries and network failures. How: Design operations to check current state before applying changes, use optimistic locking where appropriate.

### Stateless Services
Backend services must not maintain client session state, relying on external state stores for persistence. Why: To enable horizontal scaling and improve resilience. How: Store all state externally using Dapr state stores, databases, or caches.

### Sidecar-Driven Integration via Dapr
All infrastructure integration must occur through Dapr sidecars rather than direct SDK usage. Why: To abstract infrastructure dependencies and improve portability. How: Use Dapr building blocks for all infrastructure interactions (pub/sub, state, secrets, service invocation).

## 4. Architecture Rules

### Microservices-Based System
The system must be architected as a collection of independently deployable services with bounded contexts. Each service must own its data and expose well-defined APIs.

### Kubernetes as Primary Runtime
Kubernetes must serve as the sole orchestration platform for all services. All deployments must be containerized and managed through Kubernetes resources.

### Docker Mandatory Requirement
All services must be packaged as Docker containers using standardized base images. Container images must be built with reproducible builds and tagged with version information.

### Helm Required for Deployment
All deployments must use Helm charts for packaging and deployment. Configuration must be externalized through values files, and deployments must support environment-specific overrides.

### Dapr-Based Service Communication
Services must communicate exclusively through Dapr building blocks:
- Use Dapr pub/sub for asynchronous event communication
- Use Dapr service invocation for synchronous service-to-service calls
- Direct HTTP connections between services are forbidden

### Avoid Direct Service Coupling
Direct dependencies between services must be eliminated in favor of event-driven or Dapr-managed communication patterns.

## 5. Event-Driven System Mandate

Kafka serves as the backbone of all system communication. All agents must treat the system as operating on a Producer → Topic → Consumer model with asynchronous processing as the default.

Blocking workflows are strictly prohibited. All major business operations must flow through Kafka topics as events.

Required Kafka topics:
- `task-events`: Contains all task lifecycle events (creation, update, deletion)
- `reminders`: Manages all reminder-related events and scheduling
- `task-updates`: Captures all task modification events for audit and synchronization

All event processing must be idempotent and designed to handle duplicate or out-of-order messages gracefully.

## 6. Dapr Enforcement Rules

### Preferred Infrastructure Abstraction
Dapr must be preferred over direct SDK integrations for all infrastructure interactions. This ensures platform independence and simplified configuration management.

### Building Block Usage Requirements
All agents must use the following Dapr building blocks appropriately:

- **Pub/Sub**: All event communication must use Dapr pub/sub for reliable message delivery
- **State Store**: Conversation state, user data, and service state must use Dapr state stores
- **Jobs API**: Reminder scheduling and background processing must leverage Dapr's job capabilities
- **Secrets API**: All sensitive configuration must be retrieved through Dapr secrets API
- **Service Invocation**: Inter-service communication must use Dapr service invocation for enhanced observability and reliability

### Infrastructure Abstraction Compliance
All infrastructure dependencies must be abstracted through Dapr building blocks. Direct database connections, message queue clients, or cloud service SDKs must not be used directly in application code.

## 7. Kubernetes Deployment Doctrine

### Progressive Deployment Strategy
Deployment follows a progressive strategy: Minikube for development → Staging cluster → Production cluster (OKE). No shortcuts are permitted in this progression.

### Helm Chart Mandate
All deployments must utilize Helm charts with standardized templates. Custom resource definitions and configuration must be managed through Helm value files.

### Resource Management Awareness
Container resources (requests and limits) must be carefully configured based on expected load patterns and performance requirements.

### Namespace Isolation Requirements
Services must be deployed in appropriately isolated namespaces with proper resource quotas and network policies.

### Elimination of Hardcoded Dependencies
No hardcoded IP addresses, localhost references, or environment-specific configurations are permitted. All configuration must be externalized and environment-aware.

## 8. Data & State Governance

### Stateless Service Design
Backend services must maintain no persistent state within their containers. All state must be externalized to designated storage systems.

### Externalized State Management
All state persistence must occur through external systems such as Neon Postgres database or Dapr state stores.

### Database Isolation Principles
Database access must be isolated behind well-defined data access layers with proper connection pooling and transaction management.

### Event-Based State Updates
State changes must be propagated through Kafka events rather than direct database manipulation across services.

### Audit Trail Through Kafka
All significant state changes must be recorded as events in Kafka for audit trail and system recovery purposes.

## 9. Agent Behavior Rules

### Mandatory Reference Checks
Agents MUST:
- Check the constitution before planning any significant changes
- Reference the specification before writing any code
- Reference the implementation plan before beginning implementation
- Reference task definitions before creating or modifying files

### Prohibited Activities
Agents MUST NOT:
- Implement features without proper specifications
- Guess architectural approaches without formal guidance
- Skip established development steps or phases
- Change the technology stack without explicit authorization
- Modify services without updating corresponding plans and specifications

## 10. Quality & Reliability Standards

### Production-Grade Code Expectations
All code must meet production-quality standards including proper error handling, logging, testing, and documentation.

### Clear Service Boundary Definition
Service responsibilities must be clearly defined with well-documented APIs and explicit data ownership.

### Retry-Safe Logic Implementation
All operations must be designed to handle retries safely without causing data inconsistency or unwanted side effects.

### Failure-Tolerant Pattern Adoption
Services must implement circuit breakers, timeouts, and graceful degradation patterns to handle partial system failures.

### Scalable Design Mindset
All implementations must consider horizontal scaling implications from the initial design phase.

## 11. Performance Doctrine

### Async-First Architecture
Asynchronous processing must be the default architectural pattern, with synchronous calls reserved for specific use cases only.

### Event Streaming Over Polling
Systems must prefer event-driven updates over polling mechanisms for improved efficiency and responsiveness.

### Distributed Workload Handling
Processing must be designed to distribute workloads across multiple instances and nodes effectively.

### Horizontal Scaling Readiness
All services must be designed to scale horizontally without requiring centralized coordination or state sharing.

## 12. Security Doctrine

### Zero Hardcoded Secrets
Secrets, passwords, and sensitive configuration values must never be hardcoded in source code or configuration files.

### Dapr/Kubernetes Secrets Management
All sensitive data must be stored and retrieved using Dapr secrets API or Kubernetes secrets, following security best practices.

### Principle of Least Privilege
Services must operate with minimal required permissions and access rights, following the principle of least privilege.

### Secure Service Communication
All inter-service communication must implement proper authentication and encryption as appropriate.

## 13. CI/CD Governance

### Automated Build Requirements
All code changes must pass through automated build processes with comprehensive testing and quality gates.

### Versioned Deployment Management
All deployments must use proper versioning schemes with clear rollback procedures and version tracking.

### Infrastructure as Code Discipline
All infrastructure provisioning and configuration must be managed through code with version control and peer review.

## 14. Spec Hierarchy Law

The following authority hierarchy is absolute and must be followed in case of conflicts:

**Constitution > Specification > Plan > Tasks > Code**

When conflicts arise between documents at different levels, the higher-level document takes precedence. Updates must flow downward through the hierarchy, never upward.

## 15. AI Agent Rules

All AI agents interacting with this system must follow strict behavioral guidelines:

Agents MUST:
- Follow the specification strictly without deviation
- Not change architecture without updating the specification first
- Explain all decisions and rationale in their responses
- Produce structured outputs following established templates
- Adhere to the mandated development workflow: Constitution → Specification → Plan → Tasks → Implementation

Allowed agents include:
- Claude Code
- kubectl-ai
- kagent
- Docker AI (Gordon)

## 16. Data Rules

### Primary Database Management
The system must use PostgreSQL or NeonDB as the primary database with strict access controls. Data access must occur exclusively through service layers, never through direct database calls from frontend components.

### Data Governance Principles
- No direct database access from client applications
- All data operations must go through the appropriate service layer
- Audit logging must be enabled for all data modification operations
- Data integrity and consistency must be maintained through proper transaction management

## 17. Event System Requirements

### Kafka as Message Broker
Apache Kafka must serve as the primary message broker for all system communications. All services must integrate with Kafka through Dapr's pub/sub building blocks.

### Required System Events
The system must support the following core events:
- task_created
- task_updated
- task_deleted
- reminder_triggered
- notification_sent

### Event-Driven Architecture
All business logic must follow event-driven patterns with asynchronous processing as the default approach. Services must be designed to handle events reliably and maintain eventual consistency.

## 18. DevOps and Observability Rules

### Deployment Requirements
Helm charts are mandatory for all deployments with support for dev, staging, and production environments. CI/CD pipelines must be implemented to support automated testing and deployment.

### Observability Standards
All services must implement comprehensive logging, metrics collection, and distributed tracing to ensure proper system observability and debugging capabilities.

## 19. Completion Objective

This constitution exists to:

- **Reduce Errors**: By establishing clear, unambiguous rules and patterns that prevent common architectural and implementation mistakes
- **Prevent Rework**: By ensuring all work aligns with agreed-upon principles and architecture from the outset
- **Enable Large Multi-Step Execution**: By providing sufficient guidance for agents to complete complex, multi-component tasks correctly in a single execution flow
- **Ensure Correct Component Implementation**: By establishing clear boundaries and interaction patterns that allow agents to develop multiple system components that work together reliably

The constitution serves as the definitive authority that governs all technical decisions, ensuring consistency, quality, and alignment across all development activities in the Phase V Advanced Cloud-Native Todo Chatbot project.