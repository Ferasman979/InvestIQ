# When You Return - Quick Resume Guide

## ✅ Current State (Safe to Pause)

**Everything is in a stable state - you can safely leave:**

1. ✅ **EKS Cluster**: Running and stable
2. ✅ **Namespace**: Created (`investiq`)
3. ✅ **ConfigMap**: Created and configured
4. ✅ **Secrets**: Created with database credentials
5. ✅ **Redis**: Running and ready (1/1)
6. ⏳ **PostgreSQL**: Pending (will start automatically when EBS CSI driver is ready)
7. ⏳ **EBS CSI Driver**: Installing in background (will finish automatically)

**Nothing will break while you're away!** PostgreSQL will automatically start once the EBS CSI driver finishes installing (this happens in the background).

## 🚀 When You Return (5 Minutes)

### Step 1: Check Status (30 seconds)

```bash
# Check if PostgreSQL is ready
kubectl get pods -n investiq

# If postgres-0 shows "1/1 Ready" - you're good to go!
# If it's still Pending, check EBS CSI driver:
aws eks describe-addon \
  --cluster-name investiq-cluster \
  --addon-name aws-ebs-csi-driver \
  --profile hackathon \
  --region us-east-1 \
  --query 'addon.status' \
  --output text
```

### Step 2: Initialize Database (if PostgreSQL is ready)

Once PostgreSQL shows `1/1 Ready`:

```bash
# Port-forward PostgreSQL
kubectl port-forward -n investiq svc/postgres 5432:5432

# In another terminal:
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
poetry run python scripts/init_database.py
```

### Step 3: Load CSV Data (if you have it)

```bash
# Keep port-forward running, in another terminal:
cd backend
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

## 📋 Quick Status Check Commands

```bash
# Overall status
kubectl get pods,pvc,svc -n investiq

# PostgreSQL details
kubectl describe pod postgres-0 -n investiq

# Check if database is accessible
kubectl exec -it postgres-0 -n investiq -- psql -U investiq -d investiq_db -c "SELECT version();"
```

## 💰 Cost Note

While you're away:
- ✅ **EKS Cluster**: Minimal cost (just running nodes)
- ✅ **EBS Volumes**: Not created yet (waiting for PostgreSQL to start)
- ✅ **Redis**: Running (minimal cost)
- ⚠️ **Note**: EKS nodes continue running (~$0.10/hour per t3.small node × 2 = ~$0.20/hour)

**Total while away (~1 hour)**: ~$0.20 (very minimal)

## 🆘 If Something Went Wrong

If PostgreSQL still isn't ready when you return:

1. **Check EBS CSI driver**:
   ```bash
   aws eks describe-addon \
     --cluster-name investiq-cluster \
     --addon-name aws-ebs-csi-driver \
     --profile hackathon \
     --region us-east-1
   ```

2. **Check pod events**:
   ```bash
   kubectl describe pod postgres-0 -n investiq
   kubectl describe pvc postgres-storage-postgres-0 -n investiq
   ```

3. **See detailed status**: `EKS_DATABASE_STATUS.md`

## ✨ What's Ready Now

- ✅ Redis is fully operational
- ✅ Database credentials are set
- ✅ All Kubernetes resources are deployed
- ✅ Backend team can connect to Redis now if needed

## 📝 Next Steps After Return

1. Wait for PostgreSQL to be ready (check with `kubectl get pods -n investiq`)
2. Initialize database tables
3. Load CSV data (if you have it)
4. Deploy backend (when ready)

---

**Everything is safe to pause here!** See you when you get back! 🏥

