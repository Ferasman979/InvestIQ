#!/bin/bash
# Quick deployment script for InvestIQ to EKS
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying InvestIQ to EKS...${NC}"
echo ""

# Check if kubectl is configured
if ! kubectl cluster-info &>/dev/null; then
    echo -e "${RED}❌ Error: kubectl is not configured or cluster is not accessible${NC}"
    exit 1
fi

# Deploy infrastructure
echo -e "${YELLOW}📦 Deploying Kubernetes resources...${NC}"
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/configmap.yaml
kubectl apply -f infra/kubernetes/postgres-deployment.yaml
kubectl apply -f infra/kubernetes/redis-deployment.yaml
kubectl apply -f infra/kubernetes/backend-deployment.yaml
kubectl apply -f infra/kubernetes/llm-service-deployment.yaml

echo ""
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres -n investiq --timeout=300s || {
    echo -e "${RED}❌ PostgreSQL failed to start${NC}"
    kubectl logs -l app=postgres -n investiq --tail=50
    exit 1
}

echo ""
echo -e "${YELLOW}⏳ Waiting for Redis to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=redis -n investiq --timeout=300s || {
    echo -e "${RED}❌ Redis failed to start${NC}"
    kubectl logs -l app=redis -n investiq --tail=50
    exit 1
}

echo ""
echo -e "${YELLOW}⏳ Waiting for Backend to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=backend -n investiq --timeout=300s || {
    echo -e "${RED}❌ Backend failed to start${NC}"
    kubectl logs -l app=backend -n investiq --tail=50
    exit 1
}

echo ""
echo -e "${YELLOW}⏳ Waiting for LLM Service to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=llm-service -n investiq --timeout=300s || {
    echo -e "${RED}❌ LLM Service failed to start${NC}"
    kubectl logs -l app=llm-service -n investiq --tail=50
    exit 1
}

echo ""
echo -e "${GREEN}✅ Infrastructure deployed successfully!${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: You still need to:${NC}"
echo ""
echo "  1. Create secrets:"
echo "     kubectl create secret generic investiq-secrets \\"
echo "       --from-literal=DATABASE_USER=investiq \\"
echo "       --from-literal=DATABASE_PASSWORD=changeme \\"
echo "       --from-literal=DATABASE_URL=postgresql://investiq:changeme@postgres.investiq.svc.cluster.local:5432/investiq_db \\"
echo "       --from-literal=GEMINI_API_KEY=your-key \\"
echo "       --from-literal=SMTP_HOST=smtp.gmail.com \\"
echo "       --from-literal=SMTP_PORT=587 \\"
echo "       --from-literal=SMTP_USERNAME=your-email@gmail.com \\"
echo "       --from-literal=SMTP_PASSWORD=your-app-password \\"
echo "       --from-literal=EMAIL_FROM=noreply@investiq.com \\"
echo "       --namespace=investiq"
echo ""
echo "  2. Initialize database:"
echo "     kubectl port-forward -n investiq svc/postgres 5432:5432"
echo "     # In another terminal:"
echo "     cd backend"
echo "     export DATABASE_URL=postgresql://investiq:changeme@localhost:5432/investiq_db"
echo "     poetry run python scripts/init_database.py"
echo ""
echo "  3. Load CSV data:"
echo "     poetry run python scripts/load_csv_data.py /path/to/your/transactions.csv"
echo ""
echo -e "${GREEN}📊 Check status:${NC}"
echo "  kubectl get pods -n investiq"
echo "  kubectl get services -n investiq"

