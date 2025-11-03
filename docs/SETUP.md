# Setup Guide

This guide will walk you through setting up the InvestIQ project for local development and production deployment.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**
- **Poetry** (Python dependency manager)
- **Docker** and **Docker Compose**
- **Kubernetes CLI** (kubectl)
- **AWS CLI** (for EKS deployment)
- **Git**

### Optional Prerequisites

- **minikube** or **kind** (for local Kubernetes testing)
- **Terraform** (for infrastructure as code)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ravindrabhargava/InvestIQ.git
cd InvestIQ
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies using Poetry
poetry install

# Create environment file
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - DATABASE_URL
# - REDIS_URL
# - GEMINI_API_KEY
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/investiq
# Or for SQLite: sqlite:///./investiq.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Email/SMTP (for email notifications - use Gmail or SendGrid free tier)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Optional: Twilio for SMS (if needed later, costs money)
# TWILIO_ACCOUNT_SID=your_twilio_sid
# TWILIO_AUTH_TOKEN=your_twilio_token
# TWILIO_PHONE_NUMBER=+1234567890

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 4. Start Infrastructure Services

Using Docker Compose:

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 5. Initialize Database

```bash
cd backend
poetry run alembic upgrade head
# Or if using SQLAlchemy directly:
poetry run python scripts/init_db.py
```

### 6. Run the Backend

```bash
cd backend
poetry run uvicorn app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### 7. Frontend Setup (Optional)

If using Streamlit:

```bash
cd frontend
pip install streamlit
streamlit run app.py
```

If using Next.js:

```bash
cd frontend
npm install
npm run dev
```

## Docker Setup

### Build Docker Images

```bash
# Build backend image
docker build -t investiq-backend:latest -f infra/docker/backend.Dockerfile .

# Build payment agent
docker build -t investiq-payment-agent:latest -f infra/docker/payment-agent.Dockerfile ./agents/payment_agent

# Build security agent
docker build -t investiq-security-agent:latest -f infra/docker/security-agent.Dockerfile ./agents/security_agent

# Build credit agent
docker build -t investiq-credit-agent:latest -f infra/docker/credit-agent.Dockerfile ./agents/credit_agent
```

### Run with Docker Compose

```bash
docker-compose -f docker-compose.yml up -d
```

## Kubernetes (EKS) Deployment

### 1. Configure AWS CLI

```bash
# Set AWS profile (configured for hackathon profile)
export AWS_PROFILE=hackathon
export AWS_REGION=us-east-1

# Verify configuration
aws configure list
```

### 2. Create EKS Cluster

```bash
# Using AWS CLI
eksctl create cluster \
  --name investiq-cluster \
  --region us-east-1 \
  --node-type t3.small \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3

# Or using Terraform
cd infra/terraform
terraform init
terraform plan
terraform apply
```

### 3. Configure kubectl

```bash
aws eks update-kubeconfig --name investiq-cluster --region us-east-1

# Verify connection
kubectl get nodes
```

### 4. Deploy Services

```bash
# Apply Kubernetes manifests
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

### 5. Verify Deployment

```bash
# Check pod status
kubectl get pods -n investiq

# Check services
kubectl get services -n investiq

# Check logs
kubectl logs -f deployment/backend -n investiq
```

## CI/CD Setup (GitHub Actions)

### 1. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`
- `GEMINI_API_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`

### 2. Pipeline Workflow

The CI/CD pipeline (`.github/workflows/deploy.yml`) automatically:

1. **Build**: Tests code and builds Docker images
2. **Push**: Pushes images to Docker Hub
3. **Deploy**: Updates Kubernetes deployments
4. **Verify**: Runs health checks

## Monitoring Setup

### Prometheus

```bash
# Deploy Prometheus
kubectl apply -f monitoring/prometheus-config.yaml

# Access Prometheus UI
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

### Grafana

```bash
# Deploy Grafana
kubectl apply -f monitoring/grafana-deployment.yaml

# Access Grafana UI
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Default credentials: admin/admin
```

## Troubleshooting

### Backend won't start

- Check database connection: `DATABASE_URL` in `.env`
- Verify Redis is running: `docker-compose ps`
- Check logs: `poetry run uvicorn app:app --log-level debug`

### Agents not processing tasks

- Verify Redis queue connection
- Check agent logs: `kubectl logs -f <pod-name> -n investiq`
- Ensure Gemini API key is set correctly

### Database migration issues

```bash
# Reset database (CAUTION: deletes all data)
poetry run alembic downgrade base
poetry run alembic upgrade head
```

### Kubernetes deployment issues

```bash
# Check pod events
kubectl describe pod <pod-name> -n investiq

# Check resource limits
kubectl top pods -n investiq

# Restart deployment
kubectl rollout restart deployment/<deployment-name> -n investiq
```

## Development Tips

### Hot Reload

FastAPI supports hot reload during development:

```bash
poetry run uvicorn app:app --reload
```

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```

### Running Tests

```bash
cd backend
poetry run pytest

# With coverage
poetry run pytest --cov=. --cov-report=html
```

### Local Kubernetes Testing

```bash
# Start minikube
minikube start

# Load images into minikube
minikube image load investiq-backend:latest

# Deploy to minikube
kubectl apply -f infra/kubernetes/
```

## Next Steps

After setup:

1. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for system design details
2. Check [CONTEXT.md](./CONTEXT.md) for project context and guidelines
3. Start developing agents following the roadmap
4. Set up monitoring and alerts
5. Prepare for demo and pitch
