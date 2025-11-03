# EKS Database Setup Status

## Current Status

✅ **Namespace created**: `investiq`
✅ **ConfigMap created**: `investiq-config`
✅ **Secrets created**: `investiq-secrets`
✅ **Redis deployed and running**: `redis-56d5d797df-7r9cr` (1/1 Ready)
⏳ **PostgreSQL deploying**: `postgres-0` (0/1 Ready, waiting for EBS CSI driver)

## Issue

PostgreSQL is waiting for the **EBS CSI driver addon** to finish installing. The driver is currently in `CREATING` status.

## What's Happening

1. ✅ Storage class `ebs-csi` created and configured
2. ✅ PostgreSQL StatefulSet using `ebs-csi` storage class
3. ⏳ EBS CSI driver addon is installing (this can take 5-10 minutes)
4. ⏳ Once driver is ACTIVE, the volume will be provisioned and PostgreSQL will start

## Next Steps

### Option 1: Wait for EBS CSI Driver (Recommended)

The driver should be ready in a few minutes. Check status:

```bash
aws eks describe-addon \
  --cluster-name investiq-cluster \
  --addon-name aws-ebs-csi-driver \
  --profile hackathon \
  --region us-east-1 \
  --query 'addon.status' \
  --output text
```

When status is `ACTIVE`, PostgreSQL should start automatically.

### Option 2: Check Progress

```bash
# Check PostgreSQL pod status
kubectl get pods -n investiq

# Check PVC status
kubectl get pvc -n investiq

# Check EBS CSI driver pods (once addon is active)
kubectl get pods -n kube-system | grep ebs-csi
```

### Option 3: Initialize Database (Once PostgreSQL is Ready)

Once PostgreSQL is running (pod shows `1/1 Ready`):

```bash
# Port-forward PostgreSQL
kubectl port-forward -n investiq svc/postgres 5432:5432

# In another terminal:
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
poetry run python scripts/init_database.py
```

## Connection Details

**Database Name**: `investiq_db`
**Username**: `investiq`
**Password**: `investiq123` (from secrets)
**Connection String** (in-cluster): `postgresql://investiq:investiq123@postgres.investiq.svc.cluster.local:5432/investiq_db`

## Services Status

| Service    | Status     | Ready | Notes                      |
| ---------- | ---------- | ----- | -------------------------- |
| Redis      | ✅ Running | 1/1   | Fully operational          |
| PostgreSQL | ⏳ Pending | 0/1   | Waiting for EBS CSI driver |

## Troubleshooting

If PostgreSQL doesn't start after EBS CSI driver is ACTIVE:

```bash
# Check pod events
kubectl describe pod postgres-0 -n investiq

# Check PVC events
kubectl describe pvc postgres-storage-postgres-0 -n investiq

# Check EBS CSI driver pods
kubectl get pods -n kube-system | grep ebs-csi

# Check storage class
kubectl get storageclass ebs-csi -o yaml
```
