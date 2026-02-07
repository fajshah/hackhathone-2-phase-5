# Quickstart Guide: Todo Chatbot Kubernetes Deployment

## Prerequisites

### System Requirements
- Docker Desktop with AI features enabled (for Docker AI Agent)
- Minikube installed (v1.20+)
- Helm 3.x installed
- kubectl installed
- kubectl-ai plugin installed (optional)
- Kagent installed (optional)

### Local Resource Requirements
- At least 4 CPU cores
- 8GB RAM (recommended: 12GB+)
- 20GB free disk space

## Setup Instructions

### 1. Start Minikube Cluster
```bash
# Start Minikube with adequate resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Verify cluster is running
kubectl cluster-info
```

### 2. Prepare Container Images
```bash
# Navigate to project root
cd D:\phase-4

# Build frontend image
cd frontend
docker build -t todo-frontend:latest .

# Build backend image
cd ../backend
docker build -t todo-backend:latest .

# Optionally use Docker AI Agent (Gordon) to optimize
docker ai "analyze the Dockerfile in current directory and suggest optimizations"
```

### 3. Install and Configure Helm
```bash
# Verify Helm is installed
helm version

# Create namespace for the application
kubectl create namespace todo-app
```

### 4. Deploy Using Helm
```bash
# Navigate to Helm charts directory (will be created in next step)
cd ..

# Install the application
helm install todo-chatbot ./charts/todo-chatbot \
  --namespace todo-app \
  --create-namespace \
  --set frontend.image.tag=latest \
  --set backend.image.tag=latest
```

## Helm Chart Creation

### 1. Create Helm Chart Structure
```bash
# Create charts directory
mkdir -p charts/todo-chatbot

# Create basic chart structure
helm create charts/todo-chatbot

# Remove default templates
rm -rf charts/todo-chatbot/templates/*
```

### 2. Create Custom Templates (these will be populated during implementation)

The following templates will be created:
- `charts/todo-chatbot/templates/frontend-deployment.yaml`
- `charts/todo-chatbot/templates/backend-deployment.yaml`
- `charts/todo-chatbot/templates/database-statefulset.yaml`
- `charts/todo-chatbot/templates/frontend-service.yaml`
- `charts/todo-chatbot/templates/backend-service.yaml`
- `charts/todo-chatbot/templates/database-service.yaml`
- `charts/todo-chatbot/templates/configmap.yaml`
- `charts/todo-chatbot/templates/secrets.yaml`

### 3. Customize values.yaml
```yaml
# Default values for the application
frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    pullPolicy: IfNotPresent
    tag: "latest"
  service:
    type: NodePort
    port: 80
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi

backend:
  replicaCount: 1
  image:
    repository: todo-backend
    pullPolicy: IfNotPresent
    tag: "latest"
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 150m
      memory: 256Mi
    limits:
      cpu: 300m
      memory: 512Mi

database:
  enabled: true
  image:
    repository: postgres
    tag: "13"
  service:
    port: 5432
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  persistence:
    enabled: true
    size: 1Gi
    storageClass: ""
```

## Deployment Verification

### 1. Check Deployment Status
```bash
# Check all resources in the namespace
kubectl get all -n todo-app

# Check pod statuses
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app
```

### 2. View Application Logs
```bash
# View backend logs
kubectl logs -l app=todo-backend -n todo-app

# View frontend logs
kubectl logs -l app=todo-frontend -n todo-app

# View database logs
kubectl logs -l app=todo-postgres -n todo-app
```

### 3. Access the Application
```bash
# Get frontend service external IP and port
kubectl get svc todo-frontend-service -n todo-app

# Or use minikube tunnel to expose the service
minikube tunnel

# Access the application at:
# http://<node-ip>:<nodeport>
```

## AI-Assisted Operations

### Using kubectl-ai
```bash
# Deploy frontend with 2 replicas
kubectl-ai "scale the frontend deployment to 2 replicas in todo-app namespace"

# Check why pods are failing
kubectl-ai "show me why the backend pods are failing in todo-app namespace"

# Get resource usage overview
kubectl-ai "show me resource usage for all pods in todo-app namespace"
```

### Using Kagent
```bash
# Analyze cluster health
kagent "analyze the health of my cluster"

# Optimize resource allocation
kagent "suggest optimizations for resource allocation in todo-app namespace"
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Pods stuck in Pending state
```bash
# Check events for more details
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check if nodes have sufficient resources
kubectl describe nodes
```

#### Issue: Service not accessible
```bash
# Check service configuration
kubectl describe svc todo-frontend-service -n todo-app

# Verify pod IP and service endpoints
kubectl get endpoints todo-frontend-service -n todo-app
```

#### Issue: Database connection problems
```bash
# Check database logs
kubectl logs -l app=todo-postgres -n todo-app

# Verify database service is running
kubectl get svc todo-postgres-service -n todo-app

# Test connectivity from backend pod
kubectl exec -it -l app=todo-backend -n todo-app -- telnet todo-postgres-service 5432
```

## Cleanup

### Uninstall the Application
```bash
# Uninstall the Helm release
helm uninstall todo-chatbot -n todo-app

# Delete the namespace (optional)
kubectl delete namespace todo-app
```

### Stop Minikube
```bash
# Stop the Minikube cluster
minikube stop

# Delete the Minikube cluster (to free resources)
minikube delete
```