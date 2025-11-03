#!/bin/bash
# ONE-COMMAND DEMO START - Run this and you're ready!

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Demo Environment...${NC}"
echo ""

# Ensure Docker Compose services are up
docker-compose up -d postgres redis

# Set environment variables
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
export REDIS_URL=redis://localhost:6379/0

cd backend

# Initialize database if needed (suppress errors if already exists)
poetry run python scripts/init_database.py 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ Database ready!${NC}"
echo ""
echo -e "${YELLOW}Starting backend server...${NC}"
echo "📝 Access at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start backend
poetry run uvicorn app:app --host 0.0.0.0 --port 8000

