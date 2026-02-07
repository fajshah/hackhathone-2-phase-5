# Oracle Cloud Deployment Guide for Todo AI Chatbot

This guide explains how to deploy the Todo AI Chatbot application on Oracle Cloud Infrastructure (OCI) with Dapr and Kafka.

## Prerequisites

1. Oracle Cloud account with appropriate permissions
2. OCI CLI installed and configured
3. kubectl installed
4. Docker installed for building images

## Step 1: Set up Oracle Container Engine for Kubernetes (OKE)

```bash
# Create a new compartment (optional)
oci iam compartment create --compartment-id <your_tenancy_ocid> \
  --name "todo-chatbot-compartment" \
  --description "Compartment for Todo Chatbot application"

# Create a new VCN
oci network vcn create --compartment-id <your_compartment_ocid> \
  --display-name "todo-chatbot-vcn" \
  --cidr-block "10.0.0.0/16"

# Create an OKE cluster
oci ce cluster create --name todo-chatbot-cluster \
  --kubernetes-version v1.26.2 \
  --vcn-id <your_vcn_id> \
  --service-lb-subnet-ids <subnet_ids> \
  --nodes-lb-subnet-ids <subnet_ids>
```

## Step 2: Get Kubeconfig

```bash
# Get the kubeconfig file to connect kubectl to your cluster
oci ce cluster generate-token --cluster-id <your_cluster_id> --file ~/.kube/config --region <your_region>
```

## Step 3: Install Dapr on the Cluster

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts
helm repo update

# Install Dapr
helm install dapr dapr/dapr --namespace dapr-system --create-namespace --wait

# Verify installation
kubectl get pods --namespace dapr-system
```

## Step 4: Deploy Kafka

```bash
# Create kafka namespace
kubectl create namespace kafka

# Apply Kafka deployment
kubectl apply -f kafka-deployment.yaml
```

## Step 5: Deploy Dapr Components

```bash
# Apply Dapr component configurations
kubectl apply -f dapr-components.yaml
```

## Step 6: Build and Push Application Images

```bash
# Navigate to the backend directory
cd Phase4/backend

# Build backend image
docker build -t <your_registry>/todo-backend:v1.0.0 .

# Push to container registry
docker push <your_registry>/todo-backend:v1.0.0

# Navigate to the frontend directory
cd ../../Phase4/frontend

# Build frontend image
docker build -t <your_registry>/todo-frontend:v1.0.0 .

# Push to container registry
docker push <your_registry>/todo-frontend:v1.0.0
```

## Step 7: Update Deployment Files

Update the k8s-deployment.yaml file with your actual image registry:

```yaml
# In the backend deployment
spec:
  containers:
  - name: backend
    image: <your_registry>/todo-backend:v1.0.0  # Replace with your actual registry

# In the frontend deployment
spec:
  containers:
  - name: frontend
    image: <your_registry>/todo-frontend:v1.0.0  # Replace with your actual registry
```

## Step 8: Deploy the Application

```bash
# Create secrets for authentication
kubectl create secret generic auth-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32)

# Apply the main deployment
kubectl apply -f k8s-deployment.yaml
```

## Step 9: Monitor the Deployment

```bash
# Check pod status
kubectl get pods

# Check services
kubectl get svc

# Check Dapr sidecars
kubectl get pods -l app=todo-backend -o yaml | grep dapr
```

## Step 10: Access the Application

```bash
# Get the external IP for the frontend service
kubectl get svc todo-frontend-service

# The application will be accessible at the EXTERNAL-IP on port 80
```

## Additional Oracle Cloud Services Integration

### 1. Oracle Cloud Infrastructure Registry (OCIR)

Use OCIR to store your container images securely:

```bash
# Tag images for OCIR
docker tag <local_image> <region-code>.ocir.io/<tenancy-name>/todo-backend:v1.0.0

# Push to OCIR
docker push <region-code>.ocir.io/<tenancy-name>/todo-backend:v1.0.0
```

### 2. Oracle Autonomous Database

For production, consider using Oracle Autonomous Database:

```bash
# Create an Autonomous Database
oci db autonomous-database create \
  --compartment-id <compartment_ocid> \
  --db-name tododb \
  --admin-password <password> \
  --cpu-core-count 1 \
  --data-storage-size-in-tbs 1 \
  --db-workload TRANSACTION_PROCESSING \
  --is-free-tier false
```

Then update your deployment to use the Autonomous Database connection string.

## Troubleshooting

1. **Pods not starting**: Check logs with `kubectl logs <pod-name>`
2. **Dapr sidecar issues**: Verify Dapr is running with `kubectl get pods -n dapr-system`
3. **Kafka connectivity**: Check Kafka pods status with `kubectl get pods -n kafka`
4. **Service accessibility**: Ensure load balancer is properly configured

## Scaling the Application

```bash
# Scale backend replicas
kubectl scale deployment todo-backend --replicas=3

# Add horizontal pod autoscaler
kubectl autoscale deployment todo-backend --cpu-percent=70 --min=1 --max=10
```

This deployment leverages Oracle Cloud's robust infrastructure with Dapr for microservices building blocks and Kafka for event streaming, providing a scalable and resilient architecture for the Todo AI Chatbot application.