# 🎯 PRESENTATION CHEATSHEET - 35 MIN COUNTDOWN

## ✅ CURRENT STATUS (Just Checked)

- ✅ **PostgreSQL** - Running locally (Docker)
- ✅ **Redis** - Running locally (Docker)
- ✅ **Kubernetes** - Connected to EKS
- ❌ **Backend API** - NOT running (need to start)
- ❌ **LLM Service** - NOT running (optional for demo)

## 🚀 QUICK START (2 MINUTES)

### Option A: Start Backend (Recommended)
```bash
./START_DEMO.sh
```

This will:
1. Ensure PostgreSQL/Redis are running
2. Initialize database
3. Start backend on http://localhost:8000

### Option B: Manual Start
```bash
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
export REDIS_URL=redis://localhost:6379/0
poetry run uvicorn app:app --host 0.0.0.0 --port 8000
```

## 📊 DEMO ENDPOINTS

Once backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/healthcheck
- **API Root**: http://localhost:8000/api

## 💬 TALKING POINTS

### Architecture Overview
- "We built a microservices architecture for transaction verification"
- "Backend API handles transaction processing and verification"
- "LLM service provides intelligent security questions"
- "Deployed on AWS EKS with Kubernetes orchestration"
- "Monitoring with Prometheus and Grafana"

### What's Working
- ✅ Database (PostgreSQL) - running and ready
- ✅ Caching layer (Redis) - running
- ✅ Backend API - can start in 30 seconds
- ✅ Kubernetes deployment - configured and ready
- ✅ Monitoring stack - configured

### Demo Flow (if backend is running)
1. Show Swagger UI: "Here's our API documentation"
2. Show health check: "Service is healthy"
3. Show transaction endpoints: "We can process transactions"
4. Show verification flow: "Security question generation"

### If Backend Won't Start
- "We have a complete microservices architecture"
- "Backend API is containerized and ready to deploy"
- "Database and caching are running"
- "Can show deployment configurations"
- "Architecture is production-ready"

## 🎤 DEMO SCRIPT (Copy/Paste)

### If Backend is Running:
```bash
# 1. Health check
curl http://localhost:8000/api/healthcheck

# 2. Show Swagger UI
open http://localhost:8000/docs

# 3. Show transaction endpoint
curl -X GET http://localhost:8000/api/transactions
```

### Show Kubernetes (if needed):
```bash
# Show running pods
kubectl get pods -n investiq

# Show services
kubectl get svc -n investiq
```

## 📝 KEY FEATURES TO MENTION

1. **Microservices Architecture**
   - Separate services for backend, LLM, agents
   - Containerized with Docker
   - Kubernetes orchestration

2. **Database**
   - PostgreSQL for persistent storage
   - Redis for caching
   - Both running and ready

3. **API Design**
   - RESTful API with FastAPI
   - Swagger documentation
   - Health checks

4. **Deployment**
   - AWS EKS cluster
   - Kubernetes manifests
   - Monitoring stack

5. **Security**
   - Transaction verification
   - LLM-based security questions
   - Agent-based processing

## ⚠️ BACKUP PLAN

If nothing starts:
1. Show the code structure
2. Show Kubernetes manifests
3. Show Docker configurations
4. Explain the architecture
5. Show monitoring setup

## 🎯 TIME BREAKDOWN

- Check status: ✅ DONE (1 min)
- Start backend: [ ] (2 min)
- Test endpoints: [ ] (2 min)
- Prepare talking points: [ ] (30 min)

## 🚨 EMERGENCY COMMANDS

### Check what's running:
```bash
./PRESENTATION_PREP.sh
```

### Start everything:
```bash
./START_DEMO.sh
```

### Check if backend is responding:
```bash
curl http://localhost:8000/api/healthcheck
```

### View logs if backend crashes:
```bash
# Check backend logs (if running in terminal, you'll see them)
# Or check Docker logs:
docker-compose logs postgres
```

---

**Good luck! You've got this! 🚀**

