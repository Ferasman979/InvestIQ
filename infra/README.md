# InvestIQ DevOps Infrastructure

This directory contains all DevOps/MLOps/SRE infrastructure configurations for the InvestIQ project.

## Directory Structure

```
infra/
├── docker/                    # Dockerfiles for all services
│   ├── backend.Dockerfile
│   ├── payment-agent.Dockerfile
│   ├── security-agent.Dockerfile
│   └── credit-agent.Dockerfile
├── kubernetes/                 # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml.template
│   ├── postgres-deployment.yaml
│   ├── redis-deployment.yaml
│   ├── backend-deployment.yaml
│   ├── payment-agent-deployment.yaml
│   ├── security-agent-deployment.yaml
│   ├── credit-agent-deployment.yaml
│   ├── ingress.yaml
│   └── hpa.yaml               # HorizontalPodAutoscaler
└── README.md                  # This file
```

## ⚠️ AWS Profile Notice

**IMPORTANT**: This project uses the **hackathon** AWS profile. Always verify you're using the correct account:

```bash
export AWS_PROFILE=hackathon
aws sts get-caller-identity --profile hackathon
```

See [AWS_PROFILE_NOTES.md](./AWS_PROFILE_NOTES.md) for details.

## Quick Start

### EKS Cluster Setup

**First time setup - Create EKS cluster:**

```bash
# Ensure you're using hackathon profile
export AWS_PROFILE=hackathon

# Run setup script (uses hackathon profile automatically)
./infra/eks-setup.sh
```

This will:
- Verify hackathon profile is configured
- Create EKS cluster with 2x t3.small nodes
- Update kubeconfig for local kubectl access
- Cost: Uses hackathon $100 AWS credit

### Local Development with Docker Compose

```bash
# Start all services locally
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes Deployment

1. **Create namespace and configs:**
   ```bash
   kubectl apply -f infra/kubernetes/namespace.yaml
   kubectl apply -f infra/kubernetes/configmap.yaml
   ```

2. **Create secrets:**
   ```bash
   kubectl create secret generic investiq-secrets \
     --from-literal=DATABASE_USER=investiq \
     --from-literal=DATABASE_PASSWORD=<secure-password> \
     --from-literal=DATABASE_URL=postgresql://investiq:<secure-password>@postgres.investiq.svc.cluster.local:5432/investiq_db \
     --from-literal=GEMINI_API_KEY=<your-key> \
     --from-literal=SMTP_HOST=smtp.gmail.com \
     --from-literal=SMTP_PORT=587 \
     --from-literal=SMTP_USERNAME=<your-email> \
     --from-literal=SMTP_PASSWORD=<app-password> \
     --from-literal=EMAIL_FROM=noreply@investiq.com \
     --namespace=investiq
   ```

3. **Deploy infrastructure:**
   ```bash
   kubectl apply -f infra/kubernetes/postgres-deployment.yaml
   kubectl apply -f infra/kubernetes/redis-deployment.yaml
   ```

4. **Deploy services:**
   ```bash
   kubectl apply -f infra/kubernetes/backend-deployment.yaml
   kubectl apply -f infra/kubernetes/llm-service-deployment.yaml
   kubectl apply -f infra/kubernetes/payment-agent-deployment.yaml
   kubectl apply -f infra/kubernetes/security-agent-deployment.yaml
   kubectl apply -f infra/kubernetes/credit-agent-deployment.yaml
   ```

5. **Enable auto-scaling:**
   ```bash
   kubectl apply -f infra/kubernetes/hpa.yaml
   ```

6. **Configure ingress:**
   ```bash
   kubectl apply -f infra/kubernetes/ingress.yaml
   ```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) automatically:

1. **Tests**: Runs pytest and linting on pull requests
2. **Builds**: Creates Docker images for all services
3. **Pushes**: Uploads images to Docker Hub
4. **Deploys**: Updates Kubernetes deployments on main branch
5. **Verifies**: Runs health checks after deployment

### Required GitHub Secrets

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`
- `GEMINI_API_KEY`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`

## Monitoring

See the `monitoring/` directory for Prometheus and Grafana configurations.

### Deploy Monitoring Stack

```bash
kubectl apply -f monitoring/prometheus-deployment.yaml
kubectl apply -f monitoring/grafana-deployment.yaml
```

### Access Grafana

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

Then open http://localhost:3000 (admin/admin123)

## Auto-Scaling

The HPA configuration automatically scales services based on CPU and memory usage:

- **Backend**: 2-10 replicas (70% CPU, 80% memory)
- **Payment Agent**: 1-5 replicas (70% CPU)
- **Security Agent**: 1-5 replicas (70% CPU)
- **Credit Agent**: 1-5 replicas (70% CPU)

## Resource Limits

All services have resource requests and limits configured:

- **Requests**: 256Mi memory, 250m CPU
- **Limits**: 512Mi memory, 500m CPU

## Health Checks

All services implement health checks:

- **Backend**: `GET /api/healthcheck`
- **Agents**: `GET /health`

## Notes

- Update `<dockerhub-username>` in deployment files with your Docker Hub username
- Secrets should be managed via Kubernetes Secrets or AWS Secrets Manager
- Ingress configuration assumes NGINX ingress controller and cert-manager
- Prometheus requires proper RBAC permissions (included in manifests)

