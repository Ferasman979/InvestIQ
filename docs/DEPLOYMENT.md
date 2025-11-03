# Deployment Guide

This guide covers deploying InvestIQ to AWS EKS (Elastic Kubernetes Service) using GitHub Actions for CI/CD.

## Prerequisites

- AWS account with EKS access
- GitHub repository with Actions enabled
- Docker Hub account (for container registry)
- kubectl configured for your cluster
- AWS CLI configured with appropriate credentials

## AWS Configuration

### 1. Set AWS Profile

```bash
# For InvestIQ project, hackathon profile is automatically set
# Check current profile
echo $AWS_PROFILE

# Should show: hackathon
```

### 2. Configure AWS Region

```bash
export AWS_REGION=us-east-1
```

## EKS Cluster Setup

### Option 1: Using eksctl

```bash
# Create EKS cluster with 2 nodes
eksctl create cluster \
  --name investiq-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.small \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed

# Update kubeconfig
aws eks update-kubeconfig --name investiq-cluster --region us-east-1
```

### Option 2: Using Terraform

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## Container Registry Setup

### Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag and push images
docker tag investiq-backend:latest <dockerhub-username>/investiq-backend:latest
docker push <dockerhub-username>/investiq-backend:latest
```

## Kubernetes Secrets

### Create Secrets Manually

```bash
kubectl create namespace investiq

# Create secrets for API keys
kubectl create secret generic investiq-secrets \
  --from-literal=gemini-api-key=$GEMINI_API_KEY \
  --from-literal=smtp-host=$SMTP_HOST \
  --from-literal=smtp-port=$SMTP_PORT \
  --from-literal=smtp-username=$SMTP_USERNAME \
  --from-literal=smtp-password=$SMTP_PASSWORD \
  --from-literal=email-from=$EMAIL_FROM \
  --namespace=investiq

# Create database credentials
kubectl create secret generic investiq-db \
  --from-literal=database-url=$DATABASE_URL \
  --namespace=investiq
```

### Using AWS Secrets Manager (Recommended)

```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name investiq/secrets \
  --secret-string file://secrets.json

# Reference in Kubernetes via External Secrets Operator
```

## GitHub Actions Setup

### 1. Configure Repository Secrets

Go to GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g., `us-east-1`)
- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`
- `GEMINI_API_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`

### 2. CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) includes:

1. **Build**: Run tests and build Docker images
2. **Push**: Push images to Docker Hub
3. **Deploy**: Update Kubernetes deployments
4. **Verify**: Run health checks

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and Push Docker Images
        # ... build steps

      - name: Deploy to EKS
        # ... deployment steps
```

## Deployment Process

### Manual Deployment

```bash
# Apply all Kubernetes manifests
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/configmap.yaml
kubectl apply -f infra/kubernetes/secrets.yaml
kubectl apply -f infra/kubernetes/backend-deployment.yaml
kubectl apply -f infra/kubernetes/payment-agent-deployment.yaml
kubectl apply -f infra/kubernetes/security-agent-deployment.yaml
kubectl apply -f infra/kubernetes/credit-agent-deployment.yaml
kubectl apply -f infra/kubernetes/services.yaml
kubectl apply -f infra/kubernetes/ingress.yaml
```

### Automated Deployment

The GitHub Actions pipeline automatically deploys when code is pushed to `main` branch.

## Verification

### Check Deployment Status

```bash
# Check all pods
kubectl get pods -n investiq

# Check services
kubectl get services -n investiq

# Check ingress
kubectl get ingress -n investiq
```

### Check Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -n investiq

# Payment agent logs
kubectl logs -f deployment/payment-agent -n investiq

# Security agent logs
kubectl logs -f deployment/security-agent -n investiq

# Credit agent logs
kubectl logs -f deployment/credit-agent -n investiq
```

### Test Endpoints

```bash
# Health check
curl https://api.investiq.example.com/healthcheck

# API documentation
curl https://api.investiq.example.com/docs
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=3 -n investiq

# Scale payment agent
kubectl scale deployment payment-agent --replicas=2 -n investiq
```

### Auto Scaling (HPA)

```bash
# Create HorizontalPodAutoscaler
kubectl apply -f infra/kubernetes/hpa.yaml

# Check HPA status
kubectl get hpa -n investiq
```

## Rollback

### Rollback Deployment

```bash
# Check rollout history
kubectl rollout history deployment/backend -n investiq

# Rollback to previous version
kubectl rollout undo deployment/backend -n investiq

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n investiq
```

## Monitoring Deployment

### View Metrics

```bash
# Port forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Port forward to Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

### Check Resource Usage

```bash
# Top pods
kubectl top pods -n investiq

# Top nodes
kubectl top nodes
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod for events
kubectl describe pod <pod-name> -n investiq

# Check pod logs
kubectl logs <pod-name> -n investiq

# Check previous container logs
kubectl logs <pod-name> -n investiq --previous
```

### Image Pull Errors

```bash
# Check image pull secrets
kubectl get secrets -n investiq

# Verify Docker Hub credentials
docker login
```

### Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql $DATABASE_URL
```

## Cleanup

### Delete Deployment

```bash
# Delete all resources in namespace
kubectl delete namespace investiq

# Or delete individually
kubectl delete -f infra/kubernetes/
```

### Delete EKS Cluster

```bash
# Using eksctl
eksctl delete cluster --name investiq-cluster --region us-east-1

# Or using Terraform
cd infra/terraform
terraform destroy
```
