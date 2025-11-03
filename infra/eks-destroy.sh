#!/bin/bash
# EKS Cluster Destruction Script for Hackathon Profile
# WARNING: This will delete the EKS cluster and all resources!

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="investiq-cluster"
REGION="us-east-1"
PROFILE="hackathon"

echo -e "${RED}=== ⚠️  EKS Cluster Destruction ⚠️  ===${NC}"
echo -e "Cluster Name: ${CLUSTER_NAME}"
echo -e "Region: ${REGION}"
echo -e "AWS Profile: ${PROFILE}"
echo ""
echo -e "${RED}WARNING: This will DELETE the entire EKS cluster and all resources!${NC}"
echo -e "${RED}All data and deployments will be lost!${NC}"
echo ""

# Verify AWS profile
echo -e "${YELLOW}Checking AWS profile configuration...${NC}"
if ! aws configure list --profile ${PROFILE} &>/dev/null; then
    echo -e "${RED}ERROR: AWS profile '${PROFILE}' not found!${NC}"
    exit 1
fi

CURRENT_ACCOUNT=$(aws sts get-caller-identity --profile ${PROFILE} --query Account --output text 2>/dev/null || echo "unknown")
echo -e "${GREEN}Using AWS Account: ${CURRENT_ACCOUNT}${NC}"
echo ""

# Check for required tools
if ! command -v eksctl &> /dev/null; then
    echo -e "${RED}ERROR: eksctl not found!${NC}"
    echo "Install with: brew install eksctl"
    exit 1
fi

# Export AWS_PROFILE for eksctl (eksctl doesn't support --profile flag)
export AWS_PROFILE=${PROFILE}
export AWS_REGION=${REGION}

# Check if cluster exists
if ! aws eks describe-cluster --name ${CLUSTER_NAME} --region ${REGION} --profile ${PROFILE} &>/dev/null; then
    echo -e "${YELLOW}Cluster '${CLUSTER_NAME}' does not exist.${NC}"
    exit 0
fi

# Confirm deletion
echo -e "${RED}Are you ABSOLUTELY SURE you want to delete cluster '${CLUSTER_NAME}'?${NC}"
echo -e "Type 'DELETE' to confirm: "
read CONFIRMATION

if [ "$CONFIRMATION" != "DELETE" ]; then
    echo "Aborted."
    exit 0
fi

# Delete cluster
echo -e "${YELLOW}Deleting EKS cluster '${CLUSTER_NAME}'...${NC}"
eksctl delete cluster \
  --name ${CLUSTER_NAME} \
  --region ${REGION}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cluster deletion initiated${NC}"
    echo "Note: This may take 10-15 minutes to complete."
else
    echo -e "${RED}✗ Cluster deletion failed${NC}"
    exit 1
fi

