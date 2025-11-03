#!/bin/bash
# Quick demo script - starts everything locally for presentation

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Local Demo Environment...${NC}"
echo ""

# Start Docker Compose services
echo -e "${YELLOW}1. Starting PostgreSQL and Redis...${NC}"
docker-compose up -d postgres redis

# Wait for services
sleep 5

# Check if backend directory exists
if [ -d "backend" ]; then
    cd backend
    
    # Set environment variables
    export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
    export REDIS_URL=redis://localhost:6379/0
    
    echo -e "${YELLOW}2. Initializing database...${NC}"
    poetry run python scripts/init_database.py 2>/dev/null || echo "Database might already be initialized"
    
    echo ""
    echo -e "${GREEN}✅ Services are ready!${NC}"
    echo ""
    echo "📝 To start backend:"
    echo "   poetry run uvicorn app:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "📝 To start LLM service (in another terminal):"
    echo "   cd backend/llm-service"
    echo "   poetry run uvicorn main:app --host 0.0.0.0 --port 8001"
    echo ""
    echo "🌐 Endpoints:"
    echo "   - Backend API: http://localhost:8000/docs"
    echo "   - LLM Service: http://localhost:8001/docs"
    echo ""
else
    echo -e "${RED}❌ Backend directory not found${NC}"
fi

