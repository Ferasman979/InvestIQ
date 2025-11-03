# Backend Team - How to Use the EKS Database

## Overview

The backend team can use the database in **three different ways** depending on their needs:

1. **Local Development** - Use local PostgreSQL (Docker Compose) - **Recommended for daily work**
2. **Testing Against EKS** - Connect to EKS database via port-forward - **For integration testing**
3. **Production Deployment** - Automatic connection when deployed to EKS - **For production**

---

## Scenario 1: Local Development (Recommended)

### Use Local PostgreSQL for Daily Development

**Why?** Faster, no network dependency, can reset anytime, uses your local machine.

### Setup:

```bash
# 1. Start local PostgreSQL & Redis
docker-compose up -d postgres redis

# 2. Create .env file in backend/
cd backend
cp .env.example .env

# 3. Edit .env - use local database
DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
REDIS_URL=redis://localhost:6379/0

# 4. Initialize local database
poetry run python scripts/init_database.py

# 5. Run backend
poetry run uvicorn app:app --reload --port 8000
```

**Connection String:**
```
postgresql://investiq:investiq123@localhost:5432/investiq_db
```

**Benefits:**
- ✅ Fast - runs on your machine
- ✅ Isolated - won't affect others
- ✅ Can reset anytime
- ✅ No network dependency

---

## Scenario 2: Testing Against EKS Database

### Connect to EKS PostgreSQL for Integration Testing

**Why?** To test against the actual production database schema, or share data with team.

### Setup:

```bash
# 1. Port-forward EKS PostgreSQL (in one terminal)
kubectl port-forward -n investiq svc/postgres 5432:5432

# 2. In another terminal, update .env
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db

# 3. Run backend (it will connect to EKS via port-forward)
poetry run uvicorn app:app --reload --port 8000
```

**Connection String:**
```
postgresql://investiq:investiq123@localhost:5432/investiq_db
```
*(Same as local, but kubectl port-forward routes it to EKS)*

**Benefits:**
- ✅ Test against actual EKS database
- ✅ Share data with team
- ✅ Test production-like environment

**Note:** Keep the port-forward running while using the backend.

---

## Scenario 3: Production Deployment (Automatic)

### When Backend is Deployed to EKS

**How it works:** The backend deployment automatically uses the EKS database - no configuration needed!

### Connection Details:

**In-Cluster Connection String:**
```
postgresql://investiq:investiq123@postgres.investiq.svc.cluster.local:5432/investiq_db
```

**How it's configured:**
- `infra/kubernetes/backend-deployment.yaml` reads `DATABASE_URL` from secrets
- Secrets are already configured with the correct connection string
- Backend pods automatically connect to PostgreSQL service

### Deploy Backend:

```bash
# Once backend image is built and pushed
kubectl apply -f infra/kubernetes/backend-deployment.yaml

# Backend will automatically connect to PostgreSQL
kubectl get pods -n investiq | grep backend
```

**Benefits:**
- ✅ Automatic - no configuration needed
- ✅ Secure - uses Kubernetes service discovery
- ✅ Production-ready - same database for all backend pods

---

## Connection Strings Reference

### Local Development
```
DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
```

### EKS (via port-forward)
```
DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
# (kubectl port-forward routes to EKS)
```

### EKS (in-cluster, production)
```
DATABASE_URL=postgresql://investiq:investiq123@postgres.investiq.svc.cluster.local:5432/investiq_db
```

---

## Database Credentials

**Username:** `investiq`  
**Password:** `investiq123` (matches docker-compose)  
**Database:** `investiq_db`

**⚠️ Note:** These are the same credentials for local and EKS (for consistency). In production, you should use stronger passwords.

---

## Quick Commands

### Check Database Connection

**Local:**
```bash
psql postgresql://investiq:investiq123@localhost:5432/investiq_db -c "SELECT version();"
```

**EKS (via port-forward):**
```bash
# Start port-forward first
kubectl port-forward -n investiq svc/postgres 5432:5432

# Then connect
psql postgresql://investiq:investiq123@localhost:5432/investiq_db -c "SELECT version();"
```

**EKS (direct from pod):**
```bash
kubectl exec -it postgres-0 -n investiq -- psql -U investiq -d investiq_db -c "SELECT version();"
```

### View Tables

```bash
# Local
psql postgresql://investiq:investiq123@localhost:5432/investiq_db -c "\dt"

# EKS (via port-forward)
psql postgresql://investiq:investiq123@localhost:5432/investiq_db -c "\dt"
```

### Load CSV Data

**Local:**
```bash
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

**EKS (via port-forward):**
```bash
# Terminal 1: Port-forward
kubectl port-forward -n investiq svc/postgres 5432:5432

# Terminal 2: Load data
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

---

## Recommended Workflow

### Daily Development:
1. ✅ Use **local PostgreSQL** (docker-compose)
2. ✅ Fast iteration, no network needed
3. ✅ Can reset database anytime

### Before Deploying:
1. ✅ Test against **EKS database** (port-forward)
2. ✅ Verify everything works with production schema
3. ✅ Load test data if needed

### After Deploying:
1. ✅ Backend automatically connects to EKS database
2. ✅ No configuration needed
3. ✅ All backend pods use same database

---

## Troubleshooting

### Can't Connect Locally?

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart if needed
docker-compose restart postgres
```

### Can't Connect to EKS?

```bash
# Check if port-forward is running
pgrep -f "kubectl port-forward.*postgres"

# Check PostgreSQL pod
kubectl get pods -n investiq | grep postgres

# Check PostgreSQL logs
kubectl logs postgres-0 -n investiq
```

### Connection String Not Working?

```bash
# Verify DATABASE_URL is set
echo $DATABASE_URL

# Test connection
python3 -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

---

## Summary

**For Backend Team:**
- 🏠 **Daily work:** Use local PostgreSQL (docker-compose)
- 🧪 **Testing:** Use EKS database via port-forward
- 🚀 **Production:** Automatic when deployed to EKS

**All connection strings are the same format, just different hosts!**

