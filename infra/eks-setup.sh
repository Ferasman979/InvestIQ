#!/bin/bash
# EKS Cluster Setup Script for Hackathon Profile
# This script ensures we use the correct AWS profile (hackathon) when creating the EKS cluster

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
NODE_TYPE="t3.small"
NODES=2
MIN_NODES=1
MAX_NODES=3

echo -e "${GREEN}=== InvestIQ EKS Cluster Setup ===${NC}"
echo -e "Cluster Name: ${CLUSTER_NAME}"
echo -e "Region: ${REGION}"
echo -e "AWS Profile: ${PROFILE}"
echo -e "Node Type: ${NODE_TYPE}"
echo -e "Nodes: ${NODES} (min: ${MIN_NODES}, max: ${MAX_NODES})"
echo ""

# Check for required tools
echo -e "${YELLOW}Checking for required tools...${NC}"
MISSING_TOOLS=()

if ! command -v aws &> /dev/null; then
    MISSING_TOOLS+=("aws-cli")
fi

if ! command -v eksctl &> /dev/null; then
    MISSING_TOOLS+=("eksctl")
fi

if ! command -v kubectl &> /dev/null; then
    MISSING_TOOLS+=("kubectl")
fi

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo -e "${RED}ERROR: Missing required tools: ${MISSING_TOOLS[*]}${NC}"
    echo ""
    echo "Installation instructions:"
    echo ""
    for tool in "${MISSING_TOOLS[@]}"; do
        case $tool in
            "aws-cli")
                echo "  AWS CLI:"
                echo "    macOS: brew install awscli"
                echo "    or: curl \"https://awscli.amazonaws.com/awscli-exe-macos.zip\" -o \"awscliv2.zip\" && unzip awscliv2.zip && sudo ./aws/install"
                ;;
            "eksctl")
                echo "  eksctl:"
                echo "    macOS: brew install eksctl"
                echo "    or: curl --silent --location \"https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_Darwin_amd64.tar.gz\" | tar xz -C /tmp && sudo mv /tmp/eksctl /usr/local/bin"
                ;;
            "kubectl")
                echo "  kubectl:"
                echo "    macOS: brew install kubectl"
                echo "    or: curl -LO \"https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl\" && sudo install -o root -g wheel -m 0755 kubectl /usr/local/bin/kubectl"
                ;;
        esac
        echo ""
    done
    exit 1
fi

echo -e "${GREEN}✓ All required tools are installed${NC}"
echo ""

# Verify AWS profile is set correctly
echo -e "${YELLOW}Checking AWS profile configuration...${NC}"
if ! aws configure list --profile ${PROFILE} &>/dev/null; then
    echo -e "${RED}ERROR: AWS profile '${PROFILE}' not found!${NC}"
    echo "Please configure it with: aws configure --profile ${PROFILE}"
    exit 1
fi

CURRENT_ACCOUNT=$(aws sts get-caller-identity --profile ${PROFILE} --query Account --output text 2>/dev/null || echo "unknown")
echo -e "${GREEN}Using AWS Account: ${CURRENT_ACCOUNT}${NC}"
echo ""

# Export AWS_PROFILE for eksctl (eksctl doesn't support --profile flag)
export AWS_PROFILE=${PROFILE}
export AWS_REGION=${REGION}

# Check if cluster already exists
echo -e "${YELLOW}Checking if cluster '${CLUSTER_NAME}' already exists...${NC}"
if aws eks describe-cluster --name ${CLUSTER_NAME} --region ${REGION} --profile ${PROFILE} &>/dev/null; then
    echo -e "${GREEN}Cluster '${CLUSTER_NAME}' already exists!${NC}"
    echo ""
    echo "Current cluster status:"
    aws eks describe-cluster --name ${CLUSTER_NAME} --region ${REGION} --profile ${PROFILE} --query 'cluster.status' --output text
    
    echo ""
    read -p "Do you want to proceed with updating kubeconfig? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Updating kubeconfig...${NC}"
        aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${REGION} --profile ${PROFILE}
        echo -e "${GREEN}✓ Kubeconfig updated${NC}"
        echo ""
        echo "To verify:"
        echo "  kubectl get nodes"
        echo "  kubectl get pods --all-namespaces"
    fi
    exit 0
fi

# Confirm before creating
echo -e "${YELLOW}⚠️  WARNING: This will create a new EKS cluster!${NC}"
echo -e "This may incur AWS charges (free tier: $100 credit for hackathon)"
echo ""
read -p "Continue with cluster creation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Create EKS cluster
echo -e "${GREEN}Creating EKS cluster '${CLUSTER_NAME}'...${NC}"
echo -e "${YELLOW}Note: This may take 15-20 minutes...${NC}"
eksctl create cluster \
  --name ${CLUSTER_NAME} \
  --region ${REGION} \
  --nodegroup-name standard-workers \
  --node-type ${NODE_TYPE} \
  --nodes ${NODES} \
  --nodes-min ${MIN_NODES} \
  --nodes-max ${MAX_NODES} \
  --managed \
  --with-oidc \
  --full-ecr-access

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cluster created successfully!${NC}"
    echo ""
    
    # Update kubeconfig
    echo -e "${YELLOW}Updating kubeconfig...${NC}"
    aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${REGION} --profile ${PROFILE}
    
    echo -e "${GREEN}✓ Kubeconfig updated${NC}"
    echo ""
    
    # Verify cluster access
    echo -e "${YELLOW}Verifying cluster access...${NC}"
    kubectl get nodes
    
    echo ""
    echo -e "${GREEN}=== Setup Complete! ===${NC}"
    echo "Next steps:"
    echo "  1. Deploy infrastructure: kubectl apply -f infra/kubernetes/"
    echo "  2. Create secrets: See SECURITY.md"
    echo "  3. Verify: kubectl get pods -n investiq"
else
    echo -e "${RED}✗ Cluster creation failed${NC}"
    exit 1
fi

