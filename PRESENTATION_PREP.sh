#!/bin/bash
# Emergency Presentation Prep Script - 35 min countdown
# This script checks what's running and gives you quick recovery options

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 PRESENTATION PREP - QUICK STATUS CHECK${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if kubectl is available and cluster is accessible
echo -e "${YELLOW}1️⃣ Checking Kubernetes/EKS...${NC}"
if command -v kubectl &> /dev/null; then
    if kubectl cluster-info &>/dev/null 2>&1; then
        echo -e "${GREEN}✅ kubectl is connected${NC}"
        echo ""
        echo "📦 Kubernetes Pods Status:"
        kubectl get pods -n investiq 2>/dev/null || echo -e "${RED}❌ No pods in investiq namespace or namespace doesn't exist${NC}"
        echo ""
        echo "🌐 Kubernetes Services:"
        kubectl get svc -n investiq 2>/dev/null || echo -e "${RED}❌ No services in investiq namespace${NC}"
        echo ""
        
        # Check if any pods are running
        RUNNING_PODS=$(kubectl get pods -n investiq --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l | tr -d ' ')
        if [ "$RUNNING_PODS" -gt 0 ]; then
            echo -e "${GREEN}✅ $RUNNING_PODS pod(s) are running in Kubernetes${NC}"
        else
            echo -e "${RED}❌ No pods are running in Kubernetes${NC}"
        fi
    else
        echo -e "${RED}❌ kubectl is not configured or cluster is not accessible${NC}"
    fi
else
    echo -e "${RED}❌ kubectl is not installed${NC}"
fi

echo ""
echo -e "${YELLOW}2️⃣ Checking Local Docker Compose...${NC}"
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    if [ -f "docker-compose.yml" ]; then
        echo "🐳 Docker Compose Services:"
        docker-compose ps 2>/dev/null || echo -e "${RED}❌ Docker Compose not running${NC}"
        echo ""
        
        # Check specific services
        if docker-compose ps postgres 2>/dev/null | grep -q "Up"; then
            echo -e "${GREEN}✅ PostgreSQL is running locally${NC}"
        else
            echo -e "${RED}❌ PostgreSQL is NOT running locally${NC}"
        fi
        
        if docker-compose ps redis 2>/dev/null | grep -q "Up"; then
            echo -e "${GREEN}✅ Redis is running locally${NC}"
        else
            echo -e "${RED}❌ Redis is NOT running locally${NC}"
        fi
    else
        echo -e "${RED}❌ docker-compose.yml not found${NC}"
    fi
else
    echo -e "${RED}❌ Docker/Docker Compose not available${NC}"
fi

echo ""
echo -e "${YELLOW}3️⃣ Checking Local Backend Process...${NC}"
if pgrep -f "uvicorn.*app:app" > /dev/null; then
    echo -e "${GREEN}✅ Backend is running locally (uvicorn)${NC}"
    BACKEND_PID=$(pgrep -f "uvicorn.*app:app" | head -1)
    echo "   PID: $BACKEND_PID"
else
    echo -e "${RED}❌ Backend is NOT running locally${NC}"
fi

echo ""
echo -e "${YELLOW}4️⃣ Checking Local LLM Service Process...${NC}"
if pgrep -f "uvicorn.*llm-service.*main:app" > /dev/null || pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo -e "${GREEN}✅ LLM Service might be running locally${NC}"
else
    echo -e "${RED}❌ LLM Service is NOT running locally${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📋 QUICK RECOVERY OPTIONS${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}Option 1: Start Local Services (FASTEST - 2 min)${NC}"
echo "   cd backend"
echo "   docker-compose up -d postgres redis"
echo "   export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db"
echo "   poetry run uvicorn app:app --host 0.0.0.0 --port 8000"
echo ""

echo -e "${GREEN}Option 2: Use Kubernetes (if configured)${NC}"
echo "   ./check-status.sh"
echo "   kubectl port-forward -n investiq svc/backend 8000:8000"
echo "   kubectl port-forward -n investiq svc/llm-service 8001:8000"
echo ""

echo -e "${GREEN}Option 3: Quick Local Demo Mode${NC}"
echo "   # Terminal 1:"
echo "   docker-compose up -d"
echo "   # Terminal 2:"
echo "   cd backend && poetry run uvicorn app:app --host 0.0.0.0 --port 8000"
echo "   # Terminal 3:"
echo "   cd backend/llm-service && poetry run uvicorn main:app --host 0.0.0.0 --port 8001"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📊 WHAT TO SAY IN PRESENTATION${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "✅ If things are running:"
echo "   - 'We have a microservices architecture deployed on EKS'"
echo "   - 'Backend API, LLM service, and agents are containerized'"
echo "   - 'Monitoring with Prometheus and Grafana'"
echo ""
echo "⚠️  If things are NOT running:"
echo "   - 'We have a complete microservices architecture ready'"
echo "   - 'Currently deployed on AWS EKS with Kubernetes'"
echo "   - 'Includes: Backend API, LLM service, security agents, monitoring'"
echo "   - 'Can demonstrate locally or show deployment configs'"
echo ""
echo -e "${YELLOW}💡 DEMO SCRIPT (if backend is running):${NC}"
echo "   curl http://localhost:8000/api/healthcheck"
echo "   curl http://localhost:8000/docs  # Swagger UI"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}⏰ TIME CHECKLIST (35 min)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "   [ ] Check status (1 min) - YOU ARE HERE"
echo "   [ ] Decide: Local or Kubernetes? (1 min)"
echo "   [ ] Start services (2-5 min)"
echo "   [ ] Prepare demo commands (2 min)"
echo "   [ ] Test endpoints (2 min)"
echo "   [ ] Prepare slides/talking points (25 min)"
echo ""

echo -e "${GREEN}Good luck! 🚀${NC}"

