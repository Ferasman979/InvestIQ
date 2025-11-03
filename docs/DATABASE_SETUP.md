# Database Setup Guide

## Overview

InvestIQ uses **PostgreSQL** as the production database (deployed in Kubernetes/EKS). The database is managed as a Kubernetes StatefulSet and accessed directly by the application services.

## Database Architecture

### ✅ What Database?

- **PostgreSQL 15** (production)
- **SQLite** (local development only)

**NOT MySQL** - The architecture is designed for PostgreSQL.

### Database Location

1. **Local Development**: PostgreSQL in Docker Compose (`docker-compose.yml`)
2. **Kubernetes/EKS**: PostgreSQL StatefulSet (`infra/kubernetes/postgres-deployment.yaml`)

### Database Access

**❌ NOT using boto3** - boto3 is for AWS services (S3, DynamoDB, etc.), not PostgreSQL.

**✅ Direct PostgreSQL Connection** - The application connects directly to PostgreSQL using:

- **psycopg2** (PostgreSQL adapter) - via SQLAlchemy
- Connection string in `DATABASE_URL` environment variable

### How It Works

```
Application (FastAPI)
    ↓
SQLAlchemy ORM
    ↓
psycopg2 (PostgreSQL driver)
    ↓
PostgreSQL Database
```

**In Kubernetes:**

```
Backend Pod → PostgreSQL Service (ClusterIP) → PostgreSQL Pod
```

The PostgreSQL service is internal to the Kubernetes cluster and accessible via:

```
postgresql://user:password@postgres.investiq.svc.cluster.local:5432/investiq_db
```

## Database Setup Steps

### 1. Initialize Database Tables

Create all tables from SQLAlchemy models:

```bash
cd backend
poetry run python scripts/init_database.py
```

This creates:

- `transactions` table (from `TransactionDB` model)
- `transaction_ledger` table (from `TransactionLedger` model)

### 2. Load CSV Data

Load transaction data from CSV file:

```bash
cd backend
poetry run python scripts/load_csv_data.py /path/to/your/transactions.csv
```

**CSV Format Support:**

- Auto-detects column names (amount, vendor, category, date, status)
- Supports multiple date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
- Handles currency formats ($1,234.56 or 1234.56)
- Commits in batches (every 100 rows)

**Options:**

```bash
# Dry run (validate without inserting)
--dry-run

# Limit rows (for testing)
--max-rows 1000

# Skip header lines
--skip-lines 1
```

## Setup Scenarios

### Scenario 1: Local Development

```bash
# 1. Start PostgreSQL
docker-compose up -d postgres

# 2. Set DATABASE_URL
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db

# 3. Initialize tables
cd backend
poetry run python scripts/init_database.py

# 4. Load CSV data
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

### Scenario 2: Kubernetes/EKS Deployment

**Option A: Run from local machine (port-forward)**

```bash
# 1. Ensure PostgreSQL is deployed
kubectl get pods -n investiq | grep postgres

# 2. Port-forward PostgreSQL service
kubectl port-forward -n investiq svc/postgres 5432:5432

# 3. Set DATABASE_URL (in another terminal)
export DATABASE_URL=postgresql://investiq:changeme@localhost:5432/investiq_db

# 4. Initialize and load data
cd backend
poetry run python scripts/init_database.py
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

**Option B: Run inside Kubernetes pod**

```bash
# 1. Copy CSV file to PostgreSQL pod
kubectl cp data/transactions.csv investiq/postgres-0:/tmp/transactions.csv

# 2. Copy scripts directory to pod
kubectl cp backend/scripts investiq/postgres-0:/tmp/scripts -n investiq

# 3. Exec into pod and run
kubectl exec -it postgres-0 -n investiq -- bash

# Inside pod:
cd /tmp/scripts
python3 init_database.py
python3 load_csv_data.py /tmp/transactions.csv
```

**Option C: Use kubectl exec from backend pod**

```bash
# Find backend pod
kubectl get pods -n investiq | grep backend

# Copy CSV to backend pod
kubectl cp data/transactions.csv investiq/<backend-pod-name>:/tmp/transactions.csv

# Exec into backend pod
kubectl exec -it <backend-pod-name> -n investiq -- bash

# Inside pod:
cd /app
python scripts/init_database.py
python scripts/load_csv_data.py /tmp/transactions.csv
```

## Environment Variables

The application reads `DATABASE_URL` from:

1. **Environment variable** (highest priority)
2. **`.env` file** in backend directory
3. **Default** to SQLite for local development

**Format:**

```
postgresql://username:password@host:port/database_name
```

**Examples:**

```bash
# Local PostgreSQL
DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db

# Kubernetes PostgreSQL
DATABASE_URL=postgresql://investiq:changeme@postgres.investiq.svc.cluster.local:5432/investiq_db

# SQLite (development)
DATABASE_URL=sqlite:///./app.db
```

## Database Models

The database schema includes:

### `transactions` table

- `id` (primary key)
- `amount` (numeric)
- `vendor` (string, max 120 chars)
- `category` (string, max 80 chars)
- `tx_date` (date)
- `status` (enum: pending, verified, failed, approved)
- `created_at`, `updated_at` (timestamps)

### `transaction_ledger` table

- `id` (primary key)
- `tx_id` (foreign key to transactions)
- `amount`, `vendor`, `category`, `tx_date` (copied from transaction)
- `provider_ref` (external payment reference)
- `approved_at` (timestamp)

## Troubleshooting

### Connection Issues

```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT version();"

# Check if PostgreSQL is running (local)
docker-compose ps postgres

# Check PostgreSQL pod (Kubernetes)
kubectl get pods -n investiq | grep postgres
kubectl logs postgres-0 -n investiq
```

### Table Creation Issues

```bash
# Check if tables exist
psql $DATABASE_URL -c "\dt"

# List all tables
psql $DATABASE_URL -c "\dt investiq.*"

# Describe table structure
psql $DATABASE_URL -c "\d transactions"
```

### CSV Loading Issues

```bash
# Validate CSV structure
head -5 transactions.csv

# Dry run to check errors
poetry run python scripts/load_csv_data.py transactions.csv --dry-run

# Load with row limit for testing
poetry run python scripts/load_csv_data.py transactions.csv --max-rows 100
```

## Summary

1. ✅ **Database**: PostgreSQL (in Kubernetes StatefulSet)
2. ✅ **Access**: Direct connection via psycopg2/SQLAlchemy (NOT boto3)
3. ✅ **Initialization**: Run `scripts/init_database.py` to create tables
4. ✅ **Data Loading**: Run `scripts/load_csv_data.py` with your CSV file
5. ✅ **Connection**: Via `DATABASE_URL` environment variable

The database is **managed by Kubernetes** (PostgreSQL StatefulSet), but applications connect to it **directly** using standard PostgreSQL drivers, not through AWS services.
