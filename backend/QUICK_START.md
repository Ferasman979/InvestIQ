# Backend Quick Start Guide

## Prerequisites

- Python 3.12+
- Poetry (Python dependency manager)
- Docker & Docker Compose (for local PostgreSQL/Redis)

## Setup Steps (5 minutes)

### 1. Install Dependencies

```bash
cd backend
poetry install
```

### 2. Create `.env` File

```bash
cp .env.example .env
# Edit .env with your values (see .env.example for details)
```

**Minimum for local dev:**
```bash
DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
REDIS_URL=redis://localhost:6379/0
```

### 3. Start PostgreSQL & Redis

```bash
# From project root
docker-compose up -d postgres redis

# Verify they're running
docker-compose ps
```

### 4. Initialize Database

```bash
cd backend
poetry run python scripts/init_database.py
```

You should see:
```
✅ Database connection successful!
✅ Database tables created successfully!
```

### 5. Run the Backend

```bash
poetry run uvicorn app:app --reload --port 8000
```

## Verify It's Working

- API: http://localhost:8000
- Health check: http://localhost:8000/api/healthcheck
- API docs: http://localhost:8000/docs

## Load Sample Data (Optional)

```bash
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

## Environment Variables

See `.env.example` for all available environment variables.

**Required for local dev:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Optional:**
- `GEMINI_API_KEY` - For AI features
- `SMTP_*` - For email notifications

## Troubleshooting

**Database connection failed?**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart if needed
docker-compose restart postgres
```

**Port already in use?**
```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
poetry run uvicorn app:app --reload --port 8001
```
