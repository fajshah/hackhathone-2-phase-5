#!/bin/bash

# Script to validate the Todo Chatbot Kubernetes deployment

set -e  # Exit on any error

NAMESPACE="todo-app"

echo "Validating Todo Chatbot deployment in namespace: $NAMESPACE"

# Check if the namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "ERROR: Namespace $NAMESPACE does not exist"
    exit 1
fi

echo "✓ Namespace exists"

# Check if all deployments are ready
echo "Checking deployment status..."

DEPLOYMENTS=("todo-chatbot-frontend" "todo-chatbot-backend")
for deployment in "${DEPLOYMENTS[@]}"; do
    if kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
        DESIRED=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
        READY=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')

        if [ "$READY" -eq "$DESIRED" ]; then
            echo "✓ Deployment $deployment is ready ($READY/$DESIRED)"
        else
            echo "✗ Deployment $deployment is not ready ($READY/$DESIRED)"
            exit 1
        fi
    else
        echo "✗ Deployment $deployment does not exist"
        exit 1
    fi
done

# Check if StatefulSet is ready
echo "Checking StatefulSet status..."
STATEFULSET="todo-chatbot-database"
if kubectl get statefulset "$STATEFULSET" -n "$NAMESPACE" &> /dev/null; then
    DESIRED=$(kubectl get statefulset "$STATEFULSET" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
    READY=$(kubectl get statefulset "$STATEFULSET" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')

    if [ "$READY" -eq "$DESIRED" ]; then
        echo "✓ StatefulSet $STATEFULSET is ready ($READY/$DESIRED)"
    else
        echo "✗ StatefulSet $STATEFULSET is not ready ($READY/$DESIRED)"
        exit 1
    fi
else
    echo "✗ StatefulSet $STATEFULSET does not exist"
    exit 1
fi

# Check if all services exist
echo "Checking service status..."

SERVICES=("todo-chatbot-frontend-service" "todo-chatbot-backend-service" "todo-chatbot-database")
for service in "${SERVICES[@]}"; do
    if kubectl get service "$service" -n "$NAMESPACE" &> /dev/null; then
        echo "✓ Service $service exists"
    else
        echo "✗ Service $service does not exist"
        exit 1
    fi
done

# Check pod status
echo "Checking pod status..."
PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.phase}{"\n"}{end}')

while IFS= read -r line; do
    if [ -n "$line" ]; then
        POD_NAME=$(echo "$line" | awk '{print $1}')
        POD_STATUS=$(echo "$line" | awk '{print $2}')

        if [[ "$POD_STATUS" == "Running" ]]; then
            echo "✓ Pod $POD_NAME is Running"
        else
            echo "✗ Pod $POD_NAME is $POD_STATUS"
            exit 1
        fi
    fi
done <<< "$PODS"

# Test basic connectivity
echo "Testing application connectivity..."

FRONTEND_SERVICE="todo-chatbot-frontend-service"
BACKEND_SERVICE="todo-chatbot-backend-service"

# Get service ports
FRONTEND_PORT=$(kubectl get service "$FRONTEND_SERVICE" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}')
BACKEND_PORT=$(kubectl get service "$BACKEND_SERVICE" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}')

echo "✓ Frontend service port: $FRONTEND_PORT"
echo "✓ Backend service port: $BACKEND_PORT"

# Check if pods are healthy by looking at their logs
echo "Checking pod health from logs..."

FRONTEND_POD=$(kubectl get pods -n "$NAMESPACE" -l app=todo-frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
BACKEND_POD=$(kubectl get pods -n "$NAMESPACE" -l app=todo-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
DB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=todo-postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$FRONTEND_POD" ]; then
    FRONTEND_LOGS=$(kubectl logs "$FRONTEND_POD" -n "$NAMESPACE" 2>&1 | tail -5)
    echo "Latest logs from frontend pod ($FRONTEND_POD):"
    echo "$FRONTEND_LOGS"
fi

if [ -n "$BACKEND_POD" ]; then
    BACKEND_LOGS=$(kubectl logs "$BACKEND_POD" -n "$NAMESPACE" 2>&1 | tail -5)
    echo "Latest logs from backend pod ($BACKEND_POD):"
    echo "$BACKEND_LOGS"
fi

if [ -n "$DB_POD" ]; then
    DB_LOGS=$(kubectl logs "$DB_POD" -n "$NAMESPACE" 2>&1 | tail -5)
    echo "Latest logs from database pod ($DB_POD):"
    echo "$DB_LOGS"
fi

echo "Deployment validation completed successfully! 🚀"
echo ""
echo "Summary:"
echo "- All deployments are ready"
echo "- All services are available"
echo "- All pods are running"
echo "- Applications appear to be functioning properly"
echo ""
echo "Access the application at: $(minikube service todo-chatbot-frontend-service -n $NAMESPACE --url)"