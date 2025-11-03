# Deploy InvestIQ to EKS - Step by Step Guide

## Prerequisites ✅

- [x] EKS cluster is created (`investiq-cluster`)
- [x] `kubectl` is configured (run `kubectl get nodes` to verify)
- [ ] CSV transaction file is available

## Step 1: Deploy Kubernetes Infrastructure

### 1.1 Create Namespace

```bash
kubectl apply -f infra/kubernetes/namespace.yaml
```

### 1.2 Create ConfigMap

```bash
kubectl apply -f infra/kubernetes/configmap.yaml
```

### 1.3 Create Secrets

**IMPORTANT**: Create secrets with your actual credentials.

**Note**: DATABASE_URL is now stored in secrets (more secure). Make sure DATABASE_PASSWORD matches the password in DATABASE_URL!

```bash
# IMPORTANT: Replace <secure-password> with a strong password
# Make sure DATABASE_PASSWORD matches the password in DATABASE_URL!
kubectl create secret generic investiq-secrets \
  --from-literal=DATABASE_USER=investiq \
  --from-literal=DATABASE_PASSWORD=<secure-password> \
  --from-literal=DATABASE_URL=postgresql://investiq:<secure-password>@postgres.investiq.svc.cluster.local:5432/investiq_db \
  --from-literal=GEMINI_API_KEY=your-gemini-api-key \
  --from-literal=SMTP_HOST=smtp.gmail.com \
  --from-literal=SMTP_PORT=587 \
  --from-literal=SMTP_USERNAME=your-email@gmail.com \
  --from-literal=SMTP_PASSWORD=your-app-password \
  --from-literal=EMAIL_FROM=noreply@investiq.com \
  --namespace=investiq
```

**Note**:

- Replace `<secure-password>` with a strong password
- **DATABASE_PASSWORD must match the password in DATABASE_URL** (consistency is ensured this way)
- DATABASE_URL is now stored in secrets (more secure than ConfigMap)

### 1.4 Deploy PostgreSQL

```bash
kubectl apply -f infra/kubernetes/postgres-deployment.yaml
```

Wait for PostgreSQL to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=postgres -n investiq --timeout=300s
```

Verify:

```bash
kubectl get pods -n investiq | grep postgres
```

### 1.5 Deploy Redis

```bash
kubectl apply -f infra/kubernetes/redis-deployment.yaml
```

Wait for Redis to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=redis -n investiq --timeout=300s
```

### 1.6 Deploy Backend Services

```bash
# Deploy backend
kubectl apply -f infra/kubernetes/backend-deployment.yaml

# Deploy agents (optional for now)
kubectl apply -f infra/kubernetes/payment-agent-deployment.yaml
kubectl apply -f infra/kubernetes/security-agent-deployment.yaml
kubectl apply -f infra/kubernetes/credit-agent-deployment.yaml
```

Verify all pods are running:

```bash
kubectl get pods -n investiq
```

## Step 2: Initialize Database

### Option A: Port-Forward and Run Locally (Recommended)

1. **Port-forward PostgreSQL** (in one terminal):

```bash
kubectl port-forward -n investiq svc/postgres 5432:5432
```

2. **In another terminal, set DATABASE_URL** (use the password from your secrets):

```bash
cd backend
# Use the same password you set in secrets
export DATABASE_URL=postgresql://investiq:<your-secret-password>@localhost:5432/investiq_db
```

3. **Initialize tables**:

```bash
poetry run python scripts/init_database.py
```

You should see:

```
✅ Database connection successful!
✅ Database tables created successfully!
Created tables: transactions, transaction_ledger
```

### Option B: Run Inside Backend Pod

```bash
# Find backend pod name
BACKEND_POD=$(kubectl get pods -n investiq -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Exec into pod
kubectl exec -it $BACKEND_POD -n investiq -- bash

# Inside pod:
cd /app
python scripts/init_database.py
exit
```

## Step 3: Load CSV Transaction Data

### Find Your CSV File

Place your CSV file somewhere accessible, for example:

- `data/transactions.csv` (create this directory if needed)
- Or anywhere on your local machine

### Option A: Load via Port-Forward (Recommended)

1. **Keep PostgreSQL port-forward running** (from Step 2):

```bash
kubectl port-forward -n investiq svc/postgres 5432:5432
```

2. **In another terminal** (use password from secrets):

```bash
cd backend
export DATABASE_URL=postgresql://investiq:<your-secret-password>@localhost:5432/investiq_db

# Load your CSV file (replace with your actual CSV path)
poetry run python scripts/load_csv_data.py /path/to/your/transactions.csv
```

**CSV Format**: The script automatically detects these columns:

- `amount`, `Amount`, `transaction_amount`
- `vendor`, `Vendor`, `merchant`, `description`
- `category`, `Category`, `type`
- `date`, `Date`, `transaction_date`, `tx_date`
- `status`, `Status` (optional, defaults to 'pending')

**Example CSV**:

```csv
amount,vendor,category,date,status
123.45,Amazon,Online Shopping,2024-01-15,pending
67.89,Starbucks,Food & Dining,2024-01-16,approved
```

### Option B: Load via Backend Pod

```bash
# Copy CSV to backend pod
kubectl cp /path/to/your/transactions.csv investiq/$BACKEND_POD:/tmp/transactions.csv

# Exec into pod and run script
kubectl exec -it $BACKEND_POD -n investiq -- bash
cd /app
python scripts/load_csv_data.py /tmp/transactions.csv
exit
```

## Step 4: Verify Everything Works

### Check Database Connection

```bash
# Port-forward PostgreSQL
kubectl port-forward -n investiq svc/postgres 5432:5432

# In another terminal, connect and verify
export PGPASSWORD=changeme
psql -h localhost -U investiq -d investiq_db -c "SELECT COUNT(*) FROM transactions;"
```

### Check Backend API

```bash
# Port-forward backend service
kubectl port-forward -n investiq svc/backend 8000:8000

# Test API (in another terminal)
curl http://localhost:8000/health
curl http://localhost:8000/api/transactions
```

### View Logs

```bash
# Backend logs
kubectl logs -f -n investiq -l app=backend

# PostgreSQL logs
kubectl logs -f postgres-0 -n investiq
```

## Quick Deploy Script

Create a file `infra/deploy-all.sh` to deploy everything at once:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying InvestIQ to EKS..."

# Deploy infrastructure
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/configmap.yaml
kubectl apply -f infra/kubernetes/postgres-deployment.yaml
kubectl apply -f infra/kubernetes/redis-deployment.yaml
kubectl apply -f infra/kubernetes/backend-deployment.yaml

# Wait for services
echo "⏳ Waiting for PostgreSQL..."
kubectl wait --for=condition=ready pod -l app=postgres -n investiq --timeout=300s

echo "⏳ Waiting for Redis..."
kubectl wait --for=condition=ready pod -l app=redis -n investiq --timeout=300s

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Create secrets: kubectl create secret ..."
echo "  2. Initialize database: poetry run python scripts/init_database.py"
echo "  3. Load CSV: poetry run python scripts/load_csv_data.py <csv-file>"
```

## Troubleshooting

### PostgreSQL Not Ready

```bash
# Check pod status
kubectl describe pod postgres-0 -n investiq

# Check logs
kubectl logs postgres-0 -n investiq

# Check persistent volume
kubectl get pvc -n investiq
```

### Database Connection Failed

```bash
# Verify secrets exist
kubectl get secret investiq-secrets -n investiq

# Check DATABASE_URL in ConfigMap
kubectl get configmap investiq-config -n investiq -o yaml

# Test connection via port-forward
kubectl port-forward -n investiq svc/postgres 5432:5432
```

### CSV Loading Issues

```bash
# Validate CSV format
head -5 your-transactions.csv

# Test with dry-run
poetry run python scripts/load_csv_data.py your-transactions.csv --dry-run

# Load limited rows for testing
poetry run python scripts/load_csv_data.py your-transactions.csv --max-rows 10
```
