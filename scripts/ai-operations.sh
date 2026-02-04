#!/bin/bash

# Script to demonstrate AI-assisted Kubernetes operations for Todo Chatbot

echo "AI-Assisted Kubernetes Operations for Todo Chatbot"
echo "================================================="

# Check if kubectl-ai is available
if command -v kubectl-ai &> /dev/null; then
    echo "✓ kubectl-ai is available"

    echo ""
    echo "Examples of kubectl-ai commands for Todo Chatbot:"
    echo "  kubectl-ai \"show me all pods in the todo-app namespace\""
    echo "  kubectl-ai \"scale the frontend deployment to 2 replicas in todo-app namespace\""
    echo "  kubectl-ai \"find pods with high memory usage in todo-app namespace\""
    echo "  kubectl-ai \"restart the backend deployment in todo-app namespace\""
    echo "  kubectl-ai \"show me resource usage for all deployments in todo-app namespace\""
    echo "  kubectl-ai \"check why pods are failing in todo-app namespace\""
    echo "  kubectl-ai \"get logs from the backend pod in todo-app namespace\""
    echo "  kubectl-ai \"explain why the service is not accessible\""
    echo "  kubectl-ai \"show me all services and their endpoints in todo-app namespace\""
    echo "  kubectl-ai \"find deployment with the most restarts in todo-app namespace\""
else
    echo "⚠️  kubectl-ai is not available. Please install kubectl-ai plugin to use AI-assisted operations."
    echo "Installation: kubectl krew install ai"
fi

echo ""

# Check if Kagent is available
if command -v kagent &> /dev/null; then
    echo "✓ Kagent is available"

    echo ""
    echo "Examples of Kagent commands for Todo Chatbot:"
    echo "  kagent \"analyze the health of todo-app namespace\""
    echo "  kagent \"show me recommendations for resource optimization in todo-app namespace\""
    echo "  kagent \"identify potential issues in the todo-chatbot deployments\""
    echo "  kagent \"analyze cluster resource utilization\""
    echo "  kagent \"suggest improvements for the todo-chatbot application performance\""
    echo "  kagent \"provide insights about pod scheduling in todo-app namespace\""
    echo "  kagent \"review security posture of todo-chatbot deployments\""
    echo "  kagent \"analyze network policies for todo-chatbot services\""
else
    echo "⚠️  Kagent is not available. Please install Kagent to use advanced AI-assisted operations."
    echo "Kagent typically comes with kubectl-ai installation or as a standalone tool."
fi

echo ""

# Docker AI Agent (Gordon) examples
echo "Docker AI Agent (Gordon) capabilities:"
echo "  To analyze Dockerfile optimization: docker ai \"analyze the Dockerfile and suggest optimizations\""
echo "  To explain container issues: docker ai \"explain why my container is failing to start\""
echo "  To optimize multi-stage builds: docker ai \"optimize this multi-stage Dockerfile for size\""
echo "  To debug build issues: docker ai \"debug why my build is taking too long\""
echo "  To suggest security improvements: docker ai \"improve security of this Dockerfile\""

echo ""
echo "AI-assisted operations documentation:"
echo "1. kubectl-ai: Natural language Kubernetes commands"
echo "2. Kagent: Advanced cluster analysis and optimization"
echo "3. Docker AI Agent (Gordon): Intelligent container operations"
echo ""
echo "Note: Some AI tools may require API keys or specific access permissions depending on your environment."