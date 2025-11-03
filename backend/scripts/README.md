# Database Setup Scripts

This directory contains scripts for database initialization and data loading.

## Prerequisites

1. **PostgreSQL Running** (local or in Kubernetes)
2. **Environment Variables** - Set `DATABASE_URL` in `.env`:

   ```bash
   # For local PostgreSQL
   DATABASE_URL=postgresql://user:password@localhost:5432/investiq

   # For Kubernetes PostgreSQL
   DATABASE_URL=postgresql://investiq:password@postgres.investiq.svc.cluster.local:5432/investiq_db

   # For local SQLite (development)
   DATABASE_URL=sqlite:///./app.db
   ```

## Database Initialization

### Step 1: Initialize Database Tables

This script creates all database tables from SQLAlchemy models:

```bash
cd backend
poetry run python scripts/init_database.py
```

**What it does:**

- Connects to PostgreSQL database
- Creates all tables defined in `models/` directory:
  - `transactions` table (TransactionDB model)
  - `transaction_ledger` table (TransactionLedger model)
- Verifies tables were created

### Step 2: Load CSV Data

Load transaction data from CSV file:

```bash
cd backend
poetry run python scripts/load_csv_data.py path/to/transactions.csv
```

**Options:**

```bash
# Skip first N lines (if header is not first line)
--skip-lines 1

# Limit number of rows to process (for testing)
--max-rows 1000

# Dry run - validate CSV without inserting
--dry-run
```

**CSV Format:**
The script automatically detects common column names:

- `amount`, `Amount` - Transaction amount
- `vendor`, `merchant`, `description` - Vendor/merchant name
- `category`, `type` - Transaction category
- `date`, `transaction_date`, `tx_date` - Transaction date
- `status` - Transaction status (pending, approved, verified, failed)

**Supported Date Formats:**

- `YYYY-MM-DD`
- `YYYY-MM-DD HH:MM:SS`
- `MM/DD/YYYY`
- `DD/MM/YYYY`

**Supported Amount Formats:**

- `1234.56`
- `$1,234.56`
- `1,234.56`

## Example Workflow

### Local Development

```bash
# 1. Start PostgreSQL (using Docker Compose)
docker-compose up -d postgres

# 2. Set environment variable
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db

# 3. Initialize database
cd backend
poetry run python scripts/init_database.py

# 4. Load CSV data
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

### Kubernetes Deployment

```bash
# 1. Ensure PostgreSQL is deployed
kubectl get pods -n investiq | grep postgres

# 2. Port-forward to access database locally (if needed)
kubectl port-forward -n investiq svc/postgres 5432:5432

# 3. Set DATABASE_URL for Kubernetes database
export DATABASE_URL=postgresql://investiq:changeme@localhost:5432/investiq_db

# 4. Run initialization (from your local machine)
cd backend
poetry run python scripts/init_database.py

# 5. Load CSV data
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

### Or use kubectl exec to run inside pod

```bash
# Copy CSV file to pod
kubectl cp data/transactions.csv investiq/postgres-0:/tmp/transactions.csv

# Copy scripts to pod
kubectl cp backend/scripts postgres-0:/tmp/scripts -n investiq

# Exec into pod and run script
kubectl exec -it postgres-0 -n investiq -- python /tmp/scripts/load_csv_data.py /tmp/transactions.csv
```

## Database Connection

### Direct Connection (Recommended)

**NOT using boto3** - boto3 is for AWS services, not databases.

Instead, use direct PostgreSQL connection via:

- **psycopg2** (Python PostgreSQL adapter) - already included via SQLAlchemy
- Connection string in `DATABASE_URL` environment variable

### Connection Details

**Local PostgreSQL:**

```
postgresql://username:password@localhost:5432/database_name
```

**Kubernetes PostgreSQL:**

```
postgresql://username:password@postgres.investiq.svc.cluster.local:5432/investiq_db
```

**Environment Variables:**
The application reads `DATABASE_URL` from:

1. Environment variable (highest priority)
2. `.env` file in backend directory
3. Defaults to SQLite for local development

## Troubleshooting

### Connection Errors

```bash
# Test connection
psql $DATABASE_URL -c "SELECT version();"

# Check if PostgreSQL is running (local)
docker-compose ps postgres

# Check PostgreSQL pod (Kubernetes)
kubectl get pods -n investiq | grep postgres
kubectl logs postgres-0 -n investiq
```

### Table Creation Errors

```bash
# Check if tables exist
psql $DATABASE_URL -c "\dt"

# Drop and recreate (CAUTION: deletes all data!)
# Edit init_database.py to uncomment drop_all()
```

### CSV Loading Errors

```bash
# Validate CSV structure
head -5 transactions.csv

# Dry run to check for errors
poetry run python scripts/load_csv_data.py transactions.csv --dry-run

# Load with row limit for testing
poetry run python scripts/load_csv_data.py transactions.csv --max-rows 100
```

## Notes

- The scripts use SQLAlchemy ORM, so you don't need raw SQL
- All database models are automatically registered when imported
- CSV loader supports flexible column names (auto-detection)
- Data is committed in batches (every 100 rows) for performance
- Invalid rows are skipped with warnings, not fatal errors
