# Fix EBS CSI Driver - Next Step

## 🔴 Problem Identified

**EBS CSI Driver is stuck in CREATING status (59+ minutes)**
- Controller pods are in `CrashLoopBackOff` (81 restarts!)
- This is preventing PostgreSQL from starting
- **Root cause**: IAM role missing required permissions

## ✅ Solution Steps (10 minutes)

### Step 1: Check Controller Logs (2 min)

```bash
kubectl logs -n kube-system -l app=ebs-csi-controller --tail=50
```

Look for IAM permission errors like:
- `AccessDenied`
- `UnauthorizedOperation`
- `InvalidUserID.NotFound`

### Step 2: Fix IAM Role Permissions (5 min)

The role exists but needs the AWS-managed policy attached:

```bash
# Get the role ARN
ROLE_ARN=$(aws eks describe-addon \
  --cluster-name investiq-cluster \
  --addon-name aws-ebs-csi-driver \
  --profile hackathon \
  --region us-east-1 \
  --query 'addon.serviceAccountRoleArn' \
  --output text)

echo "Role: $ROLE_ARN"

# Attach the AWS-managed policy for EBS CSI driver
aws iam attach-role-policy \
  --role-name AmazonEKS_EBS_CSI_DriverRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --profile hackathon
```

### Step 3: Restart the Addon (2 min)

After attaching the policy, restart the controller pods:

```bash
# Delete the controller pods (they'll restart automatically)
kubectl delete pods -n kube-system -l app=ebs-csi-controller

# Wait a few minutes and check status
kubectl get pods -n kube-system | grep ebs-csi
```

### Step 4: Verify Addon Status (1 min)

```bash
aws eks describe-addon \
  --cluster-name investiq-cluster \
  --addon-name aws-ebs-csi-driver \
  --profile hackathon \
  --region us-east-1 \
  --query 'addon.status' \
  --output text
```

Should change from `CREATING` to `ACTIVE` within 5-10 minutes.

## 🔄 Alternative: Delete and Recreate (If Step 2 doesn't work)

If the above doesn't work, delete and recreate with proper IAM role:

### Option A: Use AWS-managed IAM Role (Recommended)

```bash
# Delete the addon
aws eks delete-addon \
  --cluster-name investiq-cluster \
  --addon-name aws-ebs-csi-driver \
  --profile hackathon \
  --region us-east-1

# Wait for deletion (30-60 seconds)
sleep 60

# Recreate with AWS-managed role (recommended)
aws eks create-addon \
  --cluster-name investiq-cluster \
  --addon-name aws-ebs-csi-driver \
  --profile hackathon \
  --region us-east-1 \
  --service-account-role-arn arn:aws:iam::$(aws sts get-caller-identity --profile hackathon --query Account --output text):role/AmazonEKS_EBS_CSI_DriverRole
```

### Option B: Let EKS Create the Role Automatically

```bash
# Delete the addon
aws eks delete-addon \
  --cluster-name investiq-cluster \
  --addon-name aws-ebs-csi-driver \
  --profile hackathon \
  --region us-east-1

# Wait for deletion
sleep 60

# Recreate without specifying role (EKS will create it)
aws eks create-addon \
  --cluster-name investiq-cluster \
  --addon-name aws-ebs-csi-driver \
  --profile hackathon \
  --region us-east-1
```

## ✅ After Fix is Complete

Once EBS CSI driver shows `ACTIVE`:

1. **PostgreSQL will start automatically** (check with `kubectl get pods -n investiq`)
2. **Initialize database** (see `WHEN_YOU_RETURN.md`)
3. **Load CSV data** (if you have it)

## 🚨 Quick Check Commands

```bash
# Check addon status
aws eks describe-addon --cluster-name investiq-cluster --addon-name aws-ebs-csi-driver --profile hackathon --region us-east-1 --query 'addon.status' --output text

# Check controller pods
kubectl get pods -n kube-system | grep ebs-csi-controller

# Check PostgreSQL
kubectl get pods -n investiq | grep postgres
```

## 📝 Notes

- **Current role**: `arn:aws:iam::466650003123:role/AmazonEKS_EBS_CSI_DriverRole`
- **Missing policy**: `AmazonEBSCSIDriverPolicy` (AWS-managed)
- **Time to fix**: ~10 minutes once you start
- **PostgreSQL will start automatically** once driver is ACTIVE

---

**This is the next step when you return!** 🏥

