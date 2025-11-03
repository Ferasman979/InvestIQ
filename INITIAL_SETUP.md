# Initial Setup Guide - Complete Workflow

This guide walks you through setting up the entire infrastructure from scratch.

## Prerequisites Check

Before starting, verify:

```bash
# 1. AWS profile is set to hackathon
export AWS_PROFILE=hackathon
aws sts get-caller-identity --profile hackathon

# 2. Required tools are installed
aws --version
kubectl version --client
eksctl version
docker --version
```

## Step-by-Step Setup

### Step 1: Create EKS Cluster

**This will take 10-20 minutes and use AWS credits (~$5-10 for a few hours)**

```bash
# Run the EKS setup script
./infra/eks-setup.sh
```

**What it does:**
- Creates EKS cluster named `investiq-cluster`
- Sets up 2x t3.small worker nodes (auto-scales 1-3 nodes)
- Configures kubectl for the cluster
- Uses hackathon AWS account

**Wait for:** Cluster creation to complete (you'll see "Setup Complete!")

**Expected output:**
```
✓ Cluster created successfully!
✓ Kubeconfig updated
✓ Nodes ready
```

**Verify:**
```bash
kubectl get nodes
# Should show 2 nodes in Ready state
```

---

### Step 2: Deploy Infrastructure (PostgreSQL, Redis)

**Deploy the base infrastructure:**

```bash
# 1. Create namespace
kubectl apply -f infra/kubernetes/namespace.yaml

# 2. Create ConfigMap (environment variables)
kubectl apply -f infra/kubernetes/configmap.yaml

# 3. Create Secrets (you'll need to create this manually - see below)
```

**Create database secrets:**

```bash
# Create the secrets in Kubernetes
kubectl create secret generic investiq-secrets \
  --from-literal=gemini-api-key=<your-gemini-key> \
  --from-literal=smtp-host=smtp.gmail.com \
  --from-literal=smtp-port=587 \
  --from-literal=smtp-username=<your-email> \
  --from-literal=smtp-password=<your-app-password> \
  --from-literal=email-from=noreply@investiq.com \
  --from-literal=database-user=investiq \
  --from-literal=database-password=<strong-password-here> \
  --namespace=investiq
```

**Deploy PostgreSQL and Redis:**

```bash
# Deploy PostgreSQL StatefulSet
kubectl apply -f infra/kubernetes/postgres-deployment.yaml

# Deploy Redis
kubectl apply -f infra/kubernetes/redis-deployment.yaml
```

**Wait for PostgreSQL to be ready:**
```bash
# Check PostgreSQL pod status
kubectl get pods -n investiq | grep postgres

# Wait until STATUS shows "Running" (takes 1-2 minutes)
kubectl wait --for=condition=ready pod -l app=postgres -n investiq --timeout=300s
```

**Verify services:**
```bash
kubectl get pods -n investiq
kubectl get services -n investiq
```

---

### Step 3: Set Up Database (Create Tables)

**Option A: From your local machine (Recommended)**

```bash
# 1. Port-forward PostgreSQL service to access from local
kubectl port-forward -n investiq svc/postgres 5432:5432 &
PF_PID=$!

# 2. Set DATABASE_URL (use the password you set in secrets)
export DATABASE_URL=postgresql://investiq:<your-db-password>@localhost:5432/investiq_db

# 3. Go to backend directory
cd backend

# 4. Install dependencies (including psycopg2)
poetry install

# 5. Initialize database tables
poetry run python scripts/init_database.py

# Expected output:
# ✅ Database connection successful!
# ✅ Database tables created successfully!
# Created tables: transactions, transaction_ledger
```

**Option B: Run inside a temporary pod**

```bash
# Use a PostgreSQL client pod
kubectl run -it --rm psql-client \
  --image=postgres:15-alpine \
  --restart=Never \
  --env="PGPASSWORD=<your-db-password>" \
  -n investiq \
  -- psql -h postgres -U investiq -d investiq_db

# Then run SQL commands inside:
# CREATE TABLE transactions (...);
# Or use the Python script approach (Option A)
```

---

### Step 4: Load CSV Data

**Now that tables are created, load your CSV data:**

```bash
# 1. Make sure port-forward is still running (from Step 3)
# If not, restart it:
kubectl port-forward -n investiq svc/postgres 5432:5432 &

# 2. Ensure DATABASE_URL is set
export DATABASE_URL=postgresql://investiq:<your-db-password>@localhost:5432/investiq_db

# 3. Load CSV data
cd backend
poetry run python scripts/load_csv_data.py /path/to/your/transactions.csv

# Expected output:
# ✅ Database connection successful!
# CSV columns detected: amount, vendor, category, date, ...
# Processed 100 transactions...
# ✅ Successfully loaded X transactions
```

**Verify data was loaded:**
```bash
# Using psql client pod
kubectl run -it --rm psql-client \
  --image=postgres:15-alpine \
  --restart=Never \
  --env="PGPASSWORD=<your-db-password>" \
  -n investiq \
  -- psql -h postgres -U investiq -d investiq_db \
  -c "SELECT COUNT(*) FROM transactions;"
```

---

### Step 5: Deploy Backend and Agents

**Now deploy the application:**

```bash
# 1. Update deployment files with your Docker Hub username
# Edit these files and replace <dockerhub-username>:
# - infra/kubernetes/backend-deployment.yaml
# - infra/kubernetes/payment-agent-deployment.yaml
# - infra/kubernetes/security-agent-deployment.yaml
# - infra/kubernetes/credit-agent-deployment.yaml

# 2. Deploy backend
kubectl apply -f infra/kubernetes/backend-deployment.yaml

# 3. Deploy agents (when ready)
kubectl apply -f infra/kubernetes/payment-agent-deployment.yaml
kubectl apply -f infra/kubernetes/security-agent-deployment.yaml
kubectl apply -f infra/kubernetes/credit-agent-deployment.yaml

# 4. Check deployment status
kubectl get pods -n investiq
kubectl get services -n investiq
```

---

## Quick Reference: Complete Sequence

```bash
# 1. Create EKS cluster
./infra/eks-setup.sh

# 2. Deploy infrastructure
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/configmap.yaml
kubectl create secret generic investiq-secrets ...  # (create secrets)

# 3. Deploy PostgreSQL and Redis
kubectl apply -f infra/kubernetes/postgres-deployment.yaml
kubectl apply -f infra/kubernetes/redis-deployment.yaml

# 4. Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n investiq --timeout=300s

# 5. Set up database (port-forward + initialize)
kubectl port-forward -n investiq svc/postgres 5432:5432 &
export DATABASE_URL=postgresql://investiq:<password>@localhost:5432/investiq_db
cd backend && poetry install && poetry run python scripts/init_database.py

# 6. Load CSV data
poetry run python scripts/load_csv_data.py /path/to/transactions.csv

# 7. Deploy backend and agents (when ready)
kubectl apply -f infra/kubernetes/backend-deployment.yaml
```

---

## Troubleshooting

### EKS Cluster Creation Fails

```bash
# Check AWS credentials
aws sts get-caller-identity --profile hackathon

# Check region
aws configure list --profile hackathon

# Check for existing clusters
aws eks list-clusters --profile hackathon --region us-east-1
```

### PostgreSQL Pod Not Starting

```bash
# Check pod logs
kubectl logs postgres-0 -n investiq

# Check pod events
kubectl describe pod postgres-0 -n investiq

# Check if secrets exist
kubectl get secrets -n investiq
```

### Database Connection Fails

```bash
# Verify PostgreSQL is accessible
kubectl port-forward -n investiq svc/postgres 5432:5432 &
psql postgresql://investiq:<password>@localhost:5432/investiq_db -c "SELECT version();"

# Test from inside cluster
kubectl run -it --rm psql-test \
  --image=postgres:15-alpine \
  --restart=Never \
  --env="PGPASSWORD=<password>" \
  -n investiq \
  -- psql -h postgres -U investiq -d investiq_db -c "SELECT 1;"
```

---

## Important Notes

1. **EKS Cluster Creation**: Takes 10-20 minutes - be patient!
2. **PostgreSQL Setup**: Must be done BEFORE loading CSV data
3. **Port-Forwarding**: Keep the port-forward running while setting up database
4. **Secrets**: Create secrets BEFORE deploying PostgreSQL
5. **Docker Images**: Update deployment files with your Docker Hub username
6. **Costs**: EKS cluster costs ~$0.10/hour + EC2 node costs (~$0.02/hour per node)

---

## Next Steps After Setup

1. ✅ Database tables created
2. ✅ CSV data loaded
3. ⏳ Deploy backend API
4. ⏳ Deploy agents
5. ⏳ Set up monitoring (Prometheus/Grafana)
6. ⏳ Configure CI/CD pipeline

