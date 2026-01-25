#!/bin/bash
set -e

echo "AI-PAWS Production Deployment Script"
echo "====================================="

# Configuration - UPDATE THESE AFTER INFRASTRUCTURE SETUP
AWS_REGION="eu-central-1"
ECR_REPOSITORY="542585190596.dkr.ecr.eu-central-1.amazonaws.com/ai-paws-prod"
ECS_CLUSTER="ai-paws-cluster"
SERVICE_NAME="ai-paws-prod-service"
TASK_DEFINITION_FAMILY="ai-paws-prod"
ALB_DNS=""  # Set this after ALB creation, e.g., "ai-paws-prod-alb-123456789.eu-central-1.elb.amazonaws.com"

# Check if ALB_DNS is set
if [ -z "$ALB_DNS" ]; then
    echo "WARNING: ALB_DNS is not set. Update this script after creating the ALB."
fi

# Get current task definition revision
CURRENT_REVISION=$(aws ecs describe-services \
    --cluster "${ECS_CLUSTER}" \
    --services "${SERVICE_NAME}" \
    --region "${AWS_REGION}" \
    --query 'services[0].taskDefinition' \
    --output text 2>/dev/null || echo "No existing service")

echo "Current task definition: ${CURRENT_REVISION}"

echo "Building Docker image for production..."
cd backend
docker buildx build --platform linux/amd64 -t ai-paws-prod .

echo "Logging into ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin 542585190596.dkr.ecr.eu-central-1.amazonaws.com

echo "Pushing to ECR..."
docker tag ai-paws-prod:latest "${ECR_REPOSITORY}:latest"
docker push "${ECR_REPOSITORY}:latest"

# Also tag with timestamp for rollback capability
TIMESTAMP=$(date +%Y%m%d%H%M%S)
docker tag ai-paws-prod:latest "${ECR_REPOSITORY}:${TIMESTAMP}"
docker push "${ECR_REPOSITORY}:${TIMESTAMP}"
echo "Tagged image with: ${TIMESTAMP}"

echo "Updating ECS service with force new deployment..."
cd ..

aws ecs update-service \
    --cluster "${ECS_CLUSTER}" \
    --service "${SERVICE_NAME}" \
    --force-new-deployment \
    --region "${AWS_REGION}"

echo "Waiting for deployment to complete..."
echo "This may take 2-3 minutes..."

aws ecs wait services-stable \
    --cluster "${ECS_CLUSTER}" \
    --services "${SERVICE_NAME}" \
    --region "${AWS_REGION}"

echo ""
echo "DEPLOYMENT SUCCESSFUL!"
echo "======================"

if [ ! -z "$ALB_DNS" ]; then
    echo "API Endpoint: http://${ALB_DNS}"
    echo "Health Check: http://${ALB_DNS}/health"
    echo "API Docs: http://${ALB_DNS}/documentation"

    echo ""
    echo "Testing health endpoint..."
    curl -f "http://${ALB_DNS}/health" || echo "Health check failed - service may still be starting"
fi

echo ""
echo "Useful commands:"
echo "aws ecs describe-services --cluster ${ECS_CLUSTER} --services ${SERVICE_NAME} --region ${AWS_REGION}"
echo "aws logs tail /ecs/ai-paws-prod --region ${AWS_REGION} --since 10m"
echo "aws elbv2 describe-target-health --target-group-arn <TARGET_GROUP_ARN> --region ${AWS_REGION}"
