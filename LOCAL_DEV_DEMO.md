# Local Development - Complete Demo

## ✅ What Just Happened

I just set up your **local development environment** with the database. Here's what's running:

### Services Running Locally:

1. **PostgreSQL** - Running in Docker (port 5432)
2. **Redis** - Running in Docker (port 6379)
3. **Database Tables** - Initialized and ready

---

## 🚀 How Backend Team Uses This

### Quick Start (3 commands):

```bash
# 1. Start services (if not already running)
docker-compose up -d postgres redis

# 2. Set environment variable
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db

# 3. Run backend
cd backend
poetry run uvicorn app:app --reload --port 8000
```

### Using .env File (Recommended):

```bash
# 1. Create .env file (if not exists)
cd backend
cp .env.example .env

# 2. Edit .env - it already has the local connection string:
# DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db

# 3. Run backend (reads .env automatically)
poetry run uvicorn app:app --reload --port 8000
```

The backend code (`backend/db/db.py`) automatically:

- ✅ Loads `.env` file using `python-dotenv`
- ✅ Reads `DATABASE_URL` from environment
- ✅ Connects to PostgreSQL using SQLAlchemy
- ✅ Creates database sessions for FastAPI

---

## 🔍 How It Works

### 1. Database Connection Flow

```
Backend Code (app.py)
    ↓
db/db.py: load_dotenv() → reads .env file
    ↓
os.getenv("DATABASE_URL") → gets connection string
    ↓
create_engine(DATABASE_URL) → SQLAlchemy engine
    ↓
PostgreSQL (localhost:5432) → Docker container
```

### 2. Example: Creating a Transaction

```python
# In your backend code
from db.db import get_db
from models.Transcation import TransactionDB

# FastAPI dependency automatically gets database session
def create_transaction(db: Session = Depends(get_db)):
    transaction = TransactionDB(
        amount=100.00,
        vendor="Amazon",
        category="Shopping",
        tx_date=date.today()
    )
    db.add(transaction)
    db.commit()
    return transaction
```

The `get_db()` function:

- ✅ Gets session from `SessionLocal` (connected to your PostgreSQL)
- ✅ Works exactly the same for local, EKS (port-forward), or production
- ✅ Only difference is the `DATABASE_URL` connection string

---

## 📝 Complete Workflow Example

### Terminal 1: Start Services

```bash
cd /Users/zamanu/Documents/Projects/InvestIQ

# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Check they're running
docker-compose ps
```

**Output:**

```
NAME                STATUS    PORTS
investiq-postgres   Up        5432/tcp, 0.0.0.0:5432->5432/tcp
investiq-redis      Up        6379/tcp, 0.0.0.0:6379->6379/tcp
```

### Terminal 2: Run Backend

```bash
cd backend

# Set DATABASE_URL (or use .env file)
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db

# Run backend
poetry run uvicorn app:app --reload --port 8000
```

**Output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Test It:

```bash
# Health check
curl http://localhost:8000/api/healthcheck

# API docs
open http://localhost:8000/docs
```

---

## 🔄 Database Operations

### Initialize Database (First Time)

```bash
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
poetry run python scripts/init_database.py
```

### Load CSV Data

```bash
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

### Query Database Directly

```bash
# Using psql
psql postgresql://investiq:investiq123@localhost:5432/investiq_db

# Or using docker exec
docker exec -it investiq-postgres psql -U investiq -d investiq_db
```

---

## 🎯 Key Points

1. **Same Code, Different Connection String**

   - Local: `postgresql://...@localhost:5432/...`
   - EKS: `postgresql://...@postgres.investiq.svc.cluster.local:5432/...`
   - Backend code doesn't change!

2. **Environment Variables**

   - Backend reads `DATABASE_URL` from environment
   - `.env` file is loaded automatically
   - Can override with `export DATABASE_URL=...`

3. **Isolated Development**

   - Each developer has their own local database
   - Won't affect others
   - Can reset anytime: `docker-compose down -v`

4. **Fast Iteration**
   - No network dependency
   - Runs on your machine
   - Fast database operations

---

## 🛠️ Troubleshooting

### PostgreSQL Not Starting?

```bash
# Check logs
docker-compose logs postgres

# Restart
docker-compose restart postgres

# Full reset (WARNING: deletes data)
docker-compose down -v
docker-compose up -d postgres redis
```

### Can't Connect?

```bash
# Test connection
psql postgresql://investiq:investiq123@localhost:5432/investiq_db -c "SELECT version();"

# Check if port is in use
lsof -i :5432

# Check Docker container
docker-compose ps postgres
```

### Database Connection Error?

```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Should be: postgresql://investiq:investiq123@localhost:5432/investiq_db

# Test with Python
python3 -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://investiq:investiq123@localhost:5432/investiq_db'); print('Connected!')"
```

---

## ✅ Current Status

**Your local environment is now set up:**

- ✅ PostgreSQL running on `localhost:5432`
- ✅ Redis running on `localhost:6379`
- ✅ Database tables created (`transactions`, `transaction_ledger`)
- ✅ Ready to run backend!

**Next:** Backend team can start coding immediately using this local setup!
