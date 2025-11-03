# Environment Variables Setup Guide

## ✅ Setup Complete

Your `.env` template and ignore files have been configured.

## Files Created/Updated

### 1. ✅ `.env.example` Template Created
**Location**: `backend/.env.example`

This template file includes all environment variables needed for the application:
- **Database**: `DATABASE_URL` (PostgreSQL/SQLite)
- **Redis**: `REDIS_URL`
- **API Keys**: `GEMINI_API_KEY`
- **Email/SMTP**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`
- **Application**: `APP_NAME`, `APP_ENV`, `LOG_LEVEL`
- **Optional**: AWS and CORS configuration

### 2. ✅ `.gitignore` Updated
**Location**: `.gitignore`

**Already configured:**
- ✅ `.env` files (line 132)
- ✅ `.env.local`, `.env.*.local` variants
- ✅ AWS credentials
- ✅ Secrets directories
- ✅ API keys files

**Added:**
- ✅ Kubernetes secrets files (`infra/kubernetes/secrets.yaml`)
- ✅ Monitoring secrets files (`monitoring/*secrets.yaml`)

### 3. ✅ `.dockerignore` Updated
**Location**: `.dockerignore`

**Already configured:**
- ✅ `.env` files
- ✅ Python cache files
- ✅ Git directories
- ✅ Documentation (except README.md)
- ✅ Kubernetes manifests (not needed in containers)

**Added:**
- ✅ More `.env` variants (`.env.production`, `.env.development`, `.env.test`)
- ✅ Data files (`data/`, `*.csv` - excludes sensitive transaction data)
- ✅ Secrets and credentials (`*.secret`, `*.key`, `*.pem`, `secrets.yaml`)

## Quick Start

### 1. Create Your `.env` File

```bash
cd backend
cp .env.example .env
```

### 2. Edit `.env` with Your Values

```bash
# Edit with your favorite editor
nano .env
# or
vim .env
# or
code .env
```

### 3. Fill in Required Values

**Minimum required for local development:**
```bash
DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
REDIS_URL=redis://localhost:6379/0
```

**For full functionality, also add:**
```bash
GEMINI_API_KEY=your-actual-key
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

## Environment Variables Reference

### Database (`DATABASE_URL`)

**Local Development (Docker Compose):**
```
DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
```

**Kubernetes/EKS (when port-forwarding):**
```
DATABASE_URL=postgresql://investiq:<your-secret-password>@localhost:5432/investiq_db
```

**Local SQLite (development only):**
```
DATABASE_URL=sqlite:///./app.db
```

### Redis (`REDIS_URL`)

**Local:**
```
REDIS_URL=redis://localhost:6379/0
```

**Kubernetes:**
```
REDIS_URL=redis://redis.investiq.svc.cluster.local:6379/0
```

### Email Configuration (Gmail)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the generated app password (not your regular password)

## Security Checklist

- ✅ `.env` is in `.gitignore` (will not be committed)
- ✅ `.env.example` is committed (template only, no secrets)
- ✅ Kubernetes secrets files are ignored
- ✅ Docker builds exclude sensitive files
- ✅ CSV transaction data excluded from Docker images
- ✅ AWS credentials and keys are ignored

## Verification

Check that your `.env` file won't be committed:

```bash
# Check if .env is ignored
git check-ignore backend/.env

# Verify it's not staged
git status | grep .env

# Should only show .env.example, not .env
```

## For Kubernetes/EKS

For Kubernetes deployment, use **Kubernetes Secrets**, not `.env` files:

```bash
# Create secrets instead
kubectl create secret generic investiq-secrets \
  --from-literal=DATABASE_URL=postgresql://... \
  --from-literal=GEMINI_API_KEY=... \
  # ... etc
```

See `infra/kubernetes/secrets.yaml.template` for reference.

## Troubleshooting

### `.env` file not being read?

1. **Check file location**: Should be in `backend/.env` (same directory as `app.py`)
2. **Check file name**: Must be exactly `.env` (not `.env.txt` or `env`)
3. **Restart application**: Changes to `.env` require restart
4. **Check for typos**: Variable names are case-sensitive

### Environment variable not found?

The application uses `python-dotenv` to load `.env` files. Make sure:
- `.env` file exists in `backend/` directory
- Variable names match exactly (case-sensitive)
- No extra spaces around `=` sign
- Values don't need quotes (unless containing spaces)

### Example `.env` Entry:
```bash
# ✅ Correct
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# ❌ Wrong (spaces)
DATABASE_URL = postgresql://user:pass@localhost:5432/db

# ❌ Wrong (quotes needed only for values with spaces)
DATABASE_URL="postgresql://user:pass@localhost:5432/db"
```

