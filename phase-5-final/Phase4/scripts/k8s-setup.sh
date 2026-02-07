#!/bin/bash

# Comprehensive setup script for Todo Chatbot Kubernetes deployment
# This script orchestrates the complete setup: environment validation,
# image building, deployment, and validation

set -e  # Exit on any error

echo "🚀 Starting Todo Chatbot Kubernetes Deployment Setup"
echo "=================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Validate prerequisites
echo "🔍 Validating prerequisites..."

MISSING_TOOLS=()
if ! command_exists minikube; then
    MISSING_TOOLS+=("minikube")
fi

if ! command_exists kubectl; then
    MISSING_TOOLS+=("kubectl")
fi

if ! command_exists helm; then
    MISSING_TOOLS+=("helm")
fi

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo "❌ Missing required tools: ${MISSING_TOOLS[*]}"
    echo "Please install the missing tools and try again."
    exit 1
fi

echo "✅ All required tools are available"

# Check Docker AI Agent (Gordon) availability
if command_exists docker && docker ai "help" &> /dev/null; then
    echo "✅ Docker AI Agent (Gordon) is available"
    echo "💡 Using Docker AI Agent for container optimization"

    # Analyze and optimize Dockerfiles with Gordon
    echo "🔧 Optimizing Dockerfiles with Docker AI Agent..."
    cd frontend
    docker ai "analyze the Dockerfile and suggest optimizations"
    cd ../backend
    docker ai "analyze the Dockerfile and suggest optimizations"
    cd ..
else
    echo "⚠️  Docker AI Agent (Gordon) is not available in this environment"
    echo "   Continuing with standard Docker operations"
fi

# Start Minikube if not already running
echo "📍 Checking Minikube status..."
if ! minikube status &> /dev/null; then
    echo "☸️  Starting Minikube cluster..."
    minikube start --cpus=4 --memory=8192 --disk-size=20g

    # Enable addons that might be useful
    minikube addons enable ingress
    minikube addons enable metrics-server
else
    echo "✅ Minikube is already running"
fi

# Build and deploy
echo "🏗️  Building and deploying Todo Chatbot..."
chmod +x scripts/deploy-k8s.sh
./scripts/deploy-k8s.sh

# Validate deployment
echo "✅ Validating deployment..."
chmod +x scripts/validate-deployment.sh
./scripts/validate-deployment.sh

# Show AI operations guide
echo "🤖 AI-Assisted Operations Available:"
echo "Run the following command to see available AI operations:"
echo "  chmod +x scripts/ai-operations.sh && ./scripts/ai-operations.sh"

echo ""
echo "🎉 Todo Chatbot Kubernetes Deployment Setup Complete!"
echo "==================================================="
echo ""
echo "Access the application at: $(minikube service todo-chatbot-frontend-service -n todo-app --url)"
echo ""
echo "Useful commands:"
echo "  # Check all resources"
echo "  kubectl get all -n todo-app"
echo ""
echo "  # View logs"
echo "  kubectl logs -l app=todo-frontend -n todo-app"
echo "  kubectl logs -l app=todo-backend -n todo-app"
echo "  kubectl logs -l app=todo-postgres -n todo-app"
echo ""
echo "  # Port forward for local access"
echo "  kubectl port-forward svc/todo-chatbot-frontend-service -n todo-app 8080:80"
echo ""
echo "  # Scale deployments"
echo "  kubectl scale deployment todo-chatbot-frontend -n todo-app --replicas=2"
echo "  kubectl scale deployment todo-chatbot-backend -n todo-app --replicas=2"
echo ""
echo "  # Uninstall"
echo "  helm uninstall todo-chatbot -n todo-app"
echo ""
echo "💡 Next steps:"
echo "  - Explore AI-assisted operations with kubectl-ai and Kagent"
echo "  - Customize values in charts/todo-chatbot/values.yaml for your needs"
echo "  - Add monitoring and observability tools"
echo "  - Set up CI/CD pipeline for automated deployments"