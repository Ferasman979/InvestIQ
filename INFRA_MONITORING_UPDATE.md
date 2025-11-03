# Infrastructure & Monitoring Updates

## Summary

Updated all infrastructure and monitoring configurations to align with the current setup, including:

- PostgreSQL database with EBS CSI driver
- Redis cache
- Backend API
- **LLM Service** (newly added)
- All agent services (payment, security, credit)

## Changes Made

### 1. LLM Service Infrastructure

#### New Files Created:

- **`infra/docker/llm-service.Dockerfile`**

  - Multi-stage Docker build for LLM service
  - Based on Python 3.12-slim
  - Health check endpoint: `/docs`
  - Port: 8000

- **`infra/kubernetes/llm-service-deployment.yaml`**
  - Kubernetes Deployment for LLM service
  - Replicas: 1 (auto-scales via HPA)
  - Environment variables:
    - `DATABASE_URL` from secrets
    - `GOOGLE_API_KEY` from secrets (mapped from `GEMINI_API_KEY`)
  - Health checks: liveness and readiness probes
  - Resource limits: 1Gi memory, 1000m CPU
  - Service: ClusterIP on port 8000

### 2. Monitoring Updates

#### Prometheus Configuration (`monitoring/prometheus-config.yaml` & `monitoring/prometheus-deployment.yaml`):

- ✅ Added LLM service scraping job
  - Job: `llm-service`
  - Port: 8000
  - Namespace: `investiq`
- ✅ Added PostgreSQL scraping job (ready for postgres_exporter)
- ✅ Updated existing scrape configs for consistency

#### Grafana Dashboards (`monitoring/dashboards/system-health.json`):

- ✅ Added LLM service to "Pod Status" panel
- ✅ Added "LLM Service Request Rate" panel
- ✅ Added "LLM Service CPU Usage" panel
- ✅ Added "LLM Service Memory Usage" panel

### 3. Auto-Scaling

#### Horizontal Pod Autoscaler (`infra/kubernetes/hpa.yaml`):

- ✅ Added `llm-service-hpa`:
  - Min replicas: 1
  - Max replicas: 3
  - CPU target: 70% utilization
  - Memory target: 80% utilization
  - Scale-up policy: 1 pod per 60 seconds
  - Scale-down window: 300 seconds

### 4. Ingress Configuration (`infra/kubernetes/ingress.yaml`):

- ✅ Added LLM service route:
  - Path: `/llm`
  - Service: `llm-service`
  - Port: 8000

### 5. Deployment Scripts

#### `infra/deploy-all.sh`:

- ✅ Added LLM service deployment step
- ✅ Added LLM service readiness check
- ✅ Updated secrets creation instructions to include `DATABASE_URL`

### 6. Documentation

#### `infra/README.md`:

- ✅ Updated deployment steps to include LLM service
- ✅ Updated secrets creation to match current format (with `DATABASE_URL`)

#### `infra/kubernetes/secrets.yaml.template`:

- ✅ Added documentation for `GEMINI_API_KEY` with link to API key generation
- ✅ Clarified that `GEMINI_API_KEY` is required for LLM service

### 7. Bug Fixes

#### `infra/kubernetes/backend-deployment.yaml`:

- ✅ Fixed missing `requests:` in resources section

## Deployment Checklist

### Prerequisites:

1. ✅ EKS cluster running
2. ✅ EBS CSI driver installed and configured
3. ✅ Storage class `ebs-csi` available
4. ✅ PostgreSQL database initialized with schema
5. ✅ Google Gemini API key obtained

### Deployment Steps:

1. **Create secrets** (if not already done):

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

2. **Deploy infrastructure**:

   ```bash
   # Option 1: Use deploy script
   ./infra/deploy-all.sh

   # Option 2: Manual deployment
   kubectl apply -f infra/kubernetes/namespace.yaml
   kubectl apply -f infra/kubernetes/configmap.yaml
   kubectl apply -f infra/kubernetes/postgres-deployment.yaml
   kubectl apply -f infra/kubernetes/redis-deployment.yaml
   kubectl apply -f infra/kubernetes/backend-deployment.yaml
   kubectl apply -f infra/kubernetes/llm-service-deployment.yaml
   kubectl apply -f infra/kubernetes/payment-agent-deployment.yaml
   kubectl apply -f infra/kubernetes/security-agent-deployment.yaml
   kubectl apply -f infra/kubernetes/credit-agent-deployment.yaml
   ```

3. **Deploy monitoring**:

   ```bash
   kubectl apply -f monitoring/prometheus-deployment.yaml
   kubectl apply -f monitoring/grafana-deployment.yaml
   kubectl apply -f monitoring/prometheus-config.yaml
   ```

4. **Enable auto-scaling**:

   ```bash
   kubectl apply -f infra/kubernetes/hpa.yaml
   ```

5. **Configure ingress** (optional):
   ```bash
   kubectl apply -f infra/kubernetes/ingress.yaml
   ```

## Verification

### Check Pod Status:

```bash
kubectl get pods -n investiq
```

Expected services:

- ✅ `postgres-0` (StatefulSet)
- ✅ `redis-*`
- ✅ `backend-*`
- ✅ `llm-service-*` (new)
- ✅ `payment-agent-*`
- ✅ `security-agent-*`
- ✅ `credit-agent-*`

### Check Services:

```bash
kubectl get svc -n investiq
```

### Test LLM Service:

```bash
# Port forward
kubectl port-forward -n investiq svc/llm-service 8000:8000

# Test endpoint
curl -X POST http://localhost:8000/generate-security-question \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Check Monitoring:

```bash
# Port forward Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Port forward Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Access:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

## Files Changed

### New Files:

- `infra/docker/llm-service.Dockerfile`
- `infra/kubernetes/llm-service-deployment.yaml`
- `INFRA_MONITORING_UPDATE.md` (this file)

### Updated Files:

- `infra/kubernetes/backend-deployment.yaml` (fixed resources)
- `infra/kubernetes/hpa.yaml` (added LLM service HPA)
- `infra/kubernetes/ingress.yaml` (added LLM service route)
- `infra/kubernetes/secrets.yaml.template` (documented GEMINI_API_KEY)
- `infra/deploy-all.sh` (added LLM service deployment)
- `infra/README.md` (updated deployment steps)
- `monitoring/prometheus-config.yaml` (added LLM service scraping)
- `monitoring/prometheus-deployment.yaml` (added LLM service scraping)
- `monitoring/dashboards/system-health.json` (added LLM service metrics)

## Next Steps

1. **Build and push LLM service Docker image**:

   ```bash
   docker build -f infra/docker/llm-service.Dockerfile -t investiq-llm-service:latest .
   # Push to ECR or Docker Hub
   ```

2. **Update image reference** in `llm-service-deployment.yaml` if using ECR/Docker Hub

3. **Deploy and verify** all services are running

4. **Set up monitoring alerts** in Prometheus (optional)

5. **Configure Grafana dashboards** to monitor LLM service performance

## Notes

- LLM service uses the same PostgreSQL database as the backend
- LLM service requires `GOOGLE_API_KEY` (stored as `GEMINI_API_KEY` in secrets)
- LLM service is configured to auto-scale based on CPU and memory usage
- All monitoring metrics are automatically collected by Prometheus via Kubernetes service discovery
