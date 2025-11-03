# AWS Profile Configuration - Hackathon Account

## ⚠️ Important: Always Use Hackathon Profile

This project uses the **hackathon** AWS profile to ensure we're working with the correct AWS account (hackathon $100 credit).

## Verify Current Profile

```bash
# Check current AWS profile
cat .aws-profile
# Should show: hackathon

# Verify AWS profile is configured
aws configure list --profile hackathon

# Check which account you're using
aws sts get-caller-identity --profile hackathon
```

## Setting AWS Profile

### Local Development

```bash
# Export for current session
export AWS_PROFILE=hackathon

# Or add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export AWS_PROFILE=hackathon' >> ~/.zshrc
source ~/.zshrc
```

### EKS Cluster Operations

The provided scripts automatically use the hackathon profile:

```bash
# Create cluster (uses hackathon profile)
./infra/eks-setup.sh

# Delete cluster (uses hackathon profile)
./infra/eks-destroy.sh
```

### Manual AWS CLI Commands

Always specify the profile:

```bash
# List EKS clusters
aws eks list-clusters --profile hackathon --region us-east-1

# Update kubeconfig
aws eks update-kubeconfig --name investiq-cluster --region us-east-1 --profile hackathon

# Describe cluster
aws eks describe-cluster --name investiq-cluster --region us-east-1 --profile hackathon
```

### Kubernetes Operations

kubectl uses the kubeconfig which should be configured for the hackathon account:

```bash
# Verify cluster context
kubectl config current-context

# Should show: arn:aws:eks:us-east-1:<hackathon-account-id>:cluster/investiq-cluster
```

## CI/CD Pipeline

The GitHub Actions workflow uses AWS credentials from GitHub Secrets:

- `AWS_ACCESS_KEY_ID` - Should be from hackathon account
- `AWS_SECRET_ACCESS_KEY` - Should be from hackathon account

**Verify these secrets are configured for the hackathon account!**

## Troubleshooting

### Wrong Account Error

If you see errors about wrong account or permissions:

1. **Check your profile:**
   ```bash
   echo $AWS_PROFILE
   ```

2. **Verify account:**
   ```bash
   aws sts get-caller-identity --profile hackathon
   ```

3. **Set profile explicitly:**
   ```bash
   export AWS_PROFILE=hackathon
   ```

### Profile Not Found

If hackathon profile doesn't exist:

```bash
# Configure the profile
aws configure --profile hackathon

# Enter:
# - AWS Access Key ID (from hackathon account)
# - AWS Secret Access Key (from hackathon account)
# - Default region: us-east-1
# - Default output format: json
```

## Account Information

- **Profile Name**: hackathon
- **Region**: us-east-1
- **Budget**: $100 AWS credit (hackathon budget)
- **Cluster Name**: investiq-cluster

## Safety Checks

Before any AWS operations, verify:

1. ✅ Profile is set to `hackathon`
2. ✅ Account ID matches hackathon account
3. ✅ Region is `us-east-1`
4. ✅ You're not accidentally using production account

