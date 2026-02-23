#!/bin/bash
set -e

echo "🚀 AI-PAWS PROD Deployment Script"
echo "==================================="

# Configuration
# Note: you need to setup your AWS credentials before this
# For example i have a setup in my aws profile ~/.aws/credentials file
AWS_REGION="eu-central-1"
ECR_REPOSITORY="542585190596.dkr.ecr.eu-central-1.amazonaws.com/ai-paws-prod"
ECS_CLUSTER="ai-paws-cluster"
SERVICE_NAME="ai-paws-prod-service"
TASK_DEFINITION_FAMILY="ai-paws-prod"

# Get current task definition revision
CURRENT_REVISION=$(aws ecs describe-services \
    --cluster $ECS_CLUSTER \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'services[0].taskDefinition' \
    --output text)

echo "📋 Current task definition: $CURRENT_REVISION"

echo "📦 Building Docker image..."
cd backend
docker buildx build --platform linux/amd64 -t ai-paws-prod .

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin 542585190596.dkr.ecr.eu-central-1.amazonaws.com

echo "📤 Pushing to ECR..."
docker tag ai-paws-prod:latest "${ECR_REPOSITORY}:latest"
docker push "${ECR_REPOSITORY}:latest"

echo "🔄 Updating service with force new deployment..."
cd ..

# Force new deployment to pull the latest image
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $SERVICE_NAME \
    --force-new-deployment \
    --region $AWS_REGION

echo "⏳ Waiting for deployment to complete..."
echo "This may take 2-3 minutes..."

# Wait for service to stabilize
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $SERVICE_NAME \
    --region $AWS_REGION

echo "🔍 Checking prod health via ALB..."
ALB_DNS="ai-paws-alb-665099486.eu-central-1.elb.amazonaws.com"

echo "🧪 Testing health endpoint..."
if curl -sf "http://$ALB_DNS/health"; then
    echo ""
    echo "🎉 PROD DEPLOYMENT SUCCESSFUL!"
    echo "========================="
    echo "🌐 API Endpoint: http://$ALB_DNS"
    echo "🏥 Health Check: http://$ALB_DNS/health"
    echo "📚 API Docs: http://$ALB_DNS/docs"
else
    echo ""
    echo "⚠️  Health check failed via ALB. Checking task status..."

    RUNNING_TASKS=$(aws ecs list-tasks \
        --cluster $ECS_CLUSTER \
        --service-name $SERVICE_NAME \
        --region $AWS_REGION \
        --query 'taskArns' \
        --output text)

    if [ ! -z "$RUNNING_TASKS" ] && [ "$RUNNING_TASKS" != "None" ]; then
        echo "Tasks are running. Check logs:"
        echo "aws logs tail /ecs/ai-paws --region $AWS_REGION --since 10m"
    else
        echo "❌ No running tasks found"
    fi
fi

echo ""
echo "📊 Useful commands:"
echo "aws ecs describe-services --cluster $ECS_CLUSTER --services $SERVICE_NAME --region $AWS_REGION"
echo "aws logs tail /ecs/ai-paws --region $AWS_REGION --since 10m"
echo "aws ecs list-tasks --cluster $ECS_CLUSTER --service-name $SERVICE_NAME --region $AWS_REGION"
