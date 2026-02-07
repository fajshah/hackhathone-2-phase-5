# Data Model: Kubernetes Resources for Todo Chatbot

## Overview
This document defines the Kubernetes resources and their relationships for the Todo Chatbot application deployment.

## Core Kubernetes Resources

### 1. Deployments

#### Frontend Deployment
- **apiVersion**: apps/v1
- **kind**: Deployment
- **name**: todo-frontend
- **replicas**: 1 (scalable)
- **selector**: Match labels for frontend
- **template**:
  - **containers**:
    - **name**: frontend
    - **image**: todo-frontend:{tag}
    - **ports**: 80
    - **resources**:
      - requests: cpu=100m, memory=128Mi
      - limits: cpu=200m, memory=256Mi
    - **envFrom**: ConfigMap, Secrets

#### Backend Deployment
- **apiVersion**: apps/v1
- **kind**: Deployment
- **name**: todo-backend
- **replicas**: 1 (scalable)
- **selector**: Match labels for backend
- **template**:
  - **containers**:
    - **name**: backend
    - **image**: todo-backend:{tag}
    - **ports**: 8000
    - **resources**:
      - requests: cpu=150m, memory=256Mi
      - limits: cpu=300m, memory=512Mi
    - **envFrom**: ConfigMap, Secrets
    - **livenessProbe**: HTTP GET on /health
    - **readinessProbe**: HTTP GET on /ready

#### Database Deployment (StatefulSet)
- **apiVersion**: apps/v1
- **kind**: StatefulSet
- **name**: todo-postgres
- **replicas**: 1
- **selector**: Match labels for postgres
- **template**:
  - **containers**:
    - **name**: postgres
    - **image**: postgres:13
    - **ports**: 5432
    - **env**:
      - POSTGRES_DB: todo_db
      - POSTGRES_USER: postgres
      - POSTGRES_PASSWORD: (from secret)
    - **volumeMounts**:
      - name: postgres-storage
      - mountPath: /var/lib/postgresql/data
- **volumeClaimTemplates**:
  - name: postgres-storage
  - spec:
    - accessModes: ["ReadWriteOnce"]
    - resources:
      - requests:
        - storage: 1Gi

### 2. Services

#### Frontend Service
- **apiVersion**: v1
- **kind**: Service
- **name**: todo-frontend-service
- **type**: NodePort (or LoadBalancer)
- **selector**: app=todo-frontend
- **ports**:
  - port: 80
  - targetPort: 80
  - nodePort: (dynamic)

#### Backend Service
- **apiVersion**: v1
- **kind**: Service
- **name**: todo-backend-service
- **type**: ClusterIP
- **selector**: app=todo-backend
- **ports**:
  - port: 8000
  - targetPort: 8000

#### Database Service
- **apiVersion**: v1
- **kind**: Service
- **name**: todo-postgres-service
- **type**: ClusterIP
- **selector**: app=todo-postgres
- **ports**:
  - port: 5432
  - targetPort: 5432

### 3. ConfigMaps

#### Application ConfigMap
- **apiVersion**: v1
- **kind**: ConfigMap
- **name**: todo-app-config
- **data**:
  - FRONTEND_URL: http://todo-frontend-service
  - BACKEND_URL: http://todo-backend-service:8000
  - DATABASE_URL: postgresql://postgres:password@todo-postgres-service:5432/todo_db
  - OPENAI_API_KEY: (reference from Secret)

### 4. Secrets

#### Application Secrets
- **apiVersion**: v1
- **kind**: Secret
- **name**: todo-app-secrets
- **type**: Opaque
- **data**:
  - POSTGRES_PASSWORD: (base64 encoded)
  - OPENAI_API_KEY: (base64 encoded)

## Relationships and Dependencies

### Deployment Dependencies
1. **Database** must be available before **Backend** starts
2. **Backend** must be ready before **Frontend** starts
3. Services must be available for their respective Deployments

### Volume Relationships
1. **PostgreSQL StatefulSet** uses **PersistentVolumeClaim** for data persistence
2. Volume is dynamically provisioned based on StorageClass

## Validation Rules

### Deployment Validation
- Each Deployment must have matching Service
- Resource requests/limits must be within cluster capacity
- Health checks must be properly configured

### Service Validation
- Service selectors must match Deployment labels
- Port mappings must be consistent between Deployments and Services

### Configuration Validation
- All referenced ConfigMaps/Secrets must exist before Pod startup
- Environment variable names must follow Kubernetes naming conventions

## State Transitions

### Pod Lifecycle States
1. Pending → Running → Terminating (normal flow)
2. Pending → Failed (configuration error)
3. Running → CrashLoopBackOff (application error)

### Scaling Transitions
- Deployment replica count can be adjusted dynamically
- Horizontal Pod Autoscaler can trigger scaling based on metrics