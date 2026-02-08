# Quickstart Guide: Cloud-Native Todo Chatbot System

## Prerequisites

- Docker Desktop (with Kubernetes enabled) or Minikube
- kubectl
- Helm 3+
- Dapr CLI
- Python 3.11+
- Node.js 18+

## Local Development Setup

### 1. Environment Preparation

```bash
# Start Minikube
minikube start

# Install Dapr in Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k
```

### 2. Clone and Navigate

```bash
git clone [repository-url]
cd [repository-name]

# Navigate to specs directory
cd specs/1-cloud-native-todo-system
```

### 3. Initialize Local Development

```bash
# Create virtual environment for backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend service
dapr run --app-id backend --app-port 8000 -- python src/main.py

# In a new terminal, start frontend
cd frontend
npm install
npm run dev
```

### 4. Local Kafka Setup

```bash
# Start Kafka locally using Docker Compose
docker-compose -f docker/kafka-local.yml up -d

# Create required topics
kafka-topics --create --topic task-events --bootstrap-server localhost:9092
kafka-topics --create --topic reminders --bootstrap-server localhost:9092
kafka-topics --create --topic task-updates --bootstrap-server localhost:9092
```

### 5. Verify Components

```bash
# Check Dapr components
dapr components -k

# Verify services are running
kubectl get pods

# Check if Kafka topics are created
kafka-topics --list --bootstrap-server localhost:9092
```

## Running the Full System Locally

### 1. Deploy with Helm

```bash
# Navigate to charts directory
cd charts/todo-chatbot

# Install the application
helm install todo-chatbot . --namespace todo-app --create-namespace

# Verify deployment
kubectl get pods -n todo-app
kubectl get svc -n todo-app
```

### 2. Access the Application

```bash
# Port forward to access services
kubectl port-forward svc/todo-chatbot-frontend 3000:80 -n todo-app
kubectl port-forward svc/todo-chatbot-backend 8000:80 -n todo-app
```

Visit `http://localhost:3000` for the frontend and test the todo chatbot.

## Development Workflow

### 1. Service Development

```bash
# Develop backend service
cd backend
dapr run --app-id backend --app-port 8000 --dapr-http-port 3500 -- python -m src.main

# In a new terminal, develop frontend
cd frontend
npm run dev
```

### 2. Testing Changes

```bash
# Run backend tests
cd backend
python -m pytest tests/

# Run frontend tests
cd frontend
npm test

# Run integration tests
cd backend
python -m pytest tests/integration/
```

### 3. Dapr Component Development

Create Dapr components for pub/sub, state, and secrets:

```yaml
# dapr/components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: authRequired
    value: "false"
```

## Troubleshooting

### Common Issues

1. **Dapr not found**: Run `dapr uninstall --all` and `dapr init -k`

2. **Kafka connection errors**: Ensure Kafka is running and accessible:
   ```bash
   telnet localhost 9092
   ```

3. **Helm installation fails**: Check namespace and resource availability:
   ```bash
   kubectl get nodes
   kubectl describe namespace todo-app
   ```

### Useful Commands

```bash
# View application logs
kubectl logs -l app=backend -n todo-app
kubectl logs -l app=frontend -n todo-app

# Scale services
kubectl scale deployment todo-chatbot-backend --replicas=3 -n todo-app

# View Dapr sidecar logs
kubectl logs -l app=backend -c daprd -n todo-app

# Check service connectivity
dapr status -k
kubectl get services -n todo-app
```

## Next Steps

1. Follow the tasks in `tasks.md` to implement specific features
2. Review the API contracts in the `contracts/` directory
3. Check out the full system documentation in the main repository
4. Connect to NeonDB and set up the initial schema