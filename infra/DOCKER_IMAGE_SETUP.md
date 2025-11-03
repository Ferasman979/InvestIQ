# Docker Image Setup Guide

## Overview

The backend deployment needs a Docker image. You have several options depending on your deployment strategy.

## Option 1: AWS ECR (Recommended for EKS) ✅

**Best for production EKS deployments** - Uses AWS's container registry which integrates seamlessly with EKS.

### Setup Steps:

1. **Create ECR Repository:**
```bash
# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile hackathon --query Account --output text)
AWS_REGION=us-east-1

# Create ECR repository
aws ecr create-repository \
  --repository-name investiq-backend \
  --region $AWS_REGION \
  --profile hackathon
```

2. **Build and Push Image:**
```bash
# Login to ECR
aws ecr get-login-password --region $AWS_REGION --profile hackathon | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build image
docker build -t investiq-backend:latest -f infra/docker/backend.Dockerfile .

# Tag for ECR
docker tag investiq-backend:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/investiq-backend:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/investiq-backend:latest
```

3. **Update Deployment:**
```bash
# Update backend-deployment.yaml line 28:
image: <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/investiq-backend:latest
```

Example:
```yaml
image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/investiq-backend:latest
```

## Option 2: Docker Hub

**Alternative option** - Use public/private Docker Hub registry.

### Setup Steps:

1. **Build and Push Image:**
```bash
# Login to Docker Hub
docker login

# Build image
docker build -t <your-dockerhub-username>/investiq-backend:latest -f infra/docker/backend.Dockerfile .

# Push to Docker Hub
docker push <your-dockerhub-username>/investiq-backend:latest
```

2. **Update Deployment:**
```bash
# Update backend-deployment.yaml line 28:
image: <your-dockerhub-username>/investiq-backend:latest
```

## Option 3: Local Testing (Current Default)

**For local development/testing only** - Requires manually loading image into Kubernetes.

### Setup Steps:

1. **Build Image Locally:**
```bash
docker build -t investiq-backend:latest -f infra/docker/backend.Dockerfile .
```

2. **Load into Kind/minikube:**
```bash
# For Kind
kind load docker-image investiq-backend:latest

# For minikube
minikube image load investiq-backend:latest
```

3. **For EKS: Use ImagePullPolicy: Never (not recommended for production)**

## Current Configuration

The deployment file (`infra/kubernetes/backend-deployment.yaml`) is currently set to:

```yaml
image: investiq-backend:latest
imagePullPolicy: IfNotPresent
```

**Before deploying to EKS, you should:**
1. Choose Option 1 (ECR) or Option 2 (Docker Hub)
2. Build and push your image
3. Update line 28 in `backend-deployment.yaml` with your image URL

## Quick Setup Script

Create `infra/build-and-push-ecr.sh`:

```bash
#!/bin/bash
set -e

AWS_REGION=us-east-1
AWS_PROFILE=hackathon
IMAGE_NAME=investiq-backend
ECR_REPO=investiq-backend

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)

# Create ECR repo if it doesn't exist
aws ecr describe-repositories --repository-names $ECR_REPO --region $AWS_REGION --profile $AWS_PROFILE 2>/dev/null || \
  aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION --profile $AWS_PROFILE

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build image
echo "Building image..."
docker build -t $IMAGE_NAME:latest -f infra/docker/backend.Dockerfile .

# Tag for ECR
ECR_IMAGE=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
docker tag $IMAGE_NAME:latest $ECR_IMAGE

# Push to ECR
echo "Pushing to ECR..."
docker push $ECR_IMAGE

echo "✅ Image pushed: $ECR_IMAGE"
echo ""
echo "Update backend-deployment.yaml with:"
echo "  image: $ECR_IMAGE"
```

## GitHub Actions Integration

The project already has GitHub Actions configured (`.github/workflows/deploy.yml`) that builds and pushes to Docker Hub. You can modify it to push to ECR instead.

