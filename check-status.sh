#!/bin/bash
# Quick status check script for EKS database setup

echo "🔍 Checking EKS Database Status..."
echo ""

# Check pods
echo "📦 Pods:"
kubectl get pods -n investiq
echo ""

# Check EBS CSI driver
echo "💾 EBS CSI Driver Status:"
DRIVER_STATUS=$(aws eks describe-addon --cluster-name investiq-cluster --addon-name aws-ebs-csi-driver --profile hackathon --region us-east-1 --query 'addon.status' --output text 2>&1)
echo "  Status: $DRIVER_STATUS"

if [ "$DRIVER_STATUS" = "ACTIVE" ]; then
    echo "  ✅ EBS CSI driver is ready!"
else
    echo "  ⏳ EBS CSI driver is still installing..."
fi
echo ""

# Check PostgreSQL status
PG_STATUS=$(kubectl get pod postgres-0 -n investiq -o jsonpath='{.status.phase}' 2>/dev/null)
if [ "$PG_STATUS" = "Running" ]; then
    echo "✅ PostgreSQL is running!"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Port-forward: kubectl port-forward -n investiq svc/postgres 5432:5432"
    echo "  2. Initialize: cd backend && poetry run python scripts/init_database.py"
else
    echo "⏳ PostgreSQL is still pending (waiting for EBS CSI driver)"
fi

