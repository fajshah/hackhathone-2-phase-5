#!/bin/bash

# Script to deploy the Todo Chatbot application to Kubernetes using Helm

set -e  # Exit on any error

echo "Starting Kubernetes deployment for Todo Chatbot..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is required but not installed. Aborting."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "helm is required but not installed. Aborting."
    exit 1
fi

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "Minikube is not running. Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --disk-size=20g
fi

echo "Minikube is running."

# Create namespace if it doesn't exist
NAMESPACE="todo-app"
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE
fi

# Build Docker images and load them into Minikube
echo "Building Docker images and loading them into Minikube..."

# Set Docker environment to use Minikube's Docker daemon
eval $(minikube -p minikube docker-env)

# Build frontend image
echo "Building frontend image..."
cd ../frontend
docker build -t todo-frontend:latest .

# Build backend image
cd ../backend
echo "Building backend image..."
docker build -t todo-backend:latest .

# Revert to original Docker environment
eval $(minikube docker-env -u)

echo "Images built and loaded into Minikube."

# Install the Helm chart
echo "Installing Helm chart..."

# Check if the release already exists
if helm status todo-chatbot -n $NAMESPACE &> /dev/null; then
    echo "Updating existing release..."
    helm upgrade todo-chatbot ../charts/todo-chatbot \
        --namespace $NAMESPACE \
        --set frontend.image.tag=latest \
        --set backend.image.tag=latest
else
    echo "Installing new release..."
    helm install todo-chatbot ../charts/todo-chatbot \
        --namespace $NAMESPACE \
        --create-namespace \
        --set frontend.image.tag=latest \
        --set backend.image.tag=latest
fi

echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=Ready pods -l app=todo-frontend -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=Ready pods -l app=todo-backend -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=Ready pods -l app=todo-postgres -n $NAMESPACE --timeout=300s

echo "Deployment completed successfully!"
echo "Access the application at: $(minikube service todo-chatbot-frontend-service -n $NAMESPACE --url)"

echo "Deployment status:"
kubectl get pods,services,deployments,statefulsets -n $NAMESPACE