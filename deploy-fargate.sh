#!/bin/bash
set -e

echo "🚀 AI-PAWS Fast Deployment Script"
echo "=================================="

# Configuration
# Note: you need to setup your AWSA credentials before this
# For example i have a setup in my ~/.aws/credentials file 
AWS_REGION="eu-central-1"
ECR_REPOSITORY="542585190596.dkr.ecr.eu-central-1.amazonaws.com/ai-paws-staging"
ECS_CLUSTER="ai-paws-cluster"
SERVICE_NAME="ai-paws-secrets-service-jtufapgh"
TASK_DEFINITION_FAMILY="ai-paws-secrets"

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
docker buildx build --platform linux/amd64 -t ai-paws-staging .

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin 542585190596.dkr.ecr.eu-central-1.amazonaws.com

echo "📤 Pushing to ECR..."
docker tag ai-paws-staging:latest "${ECR_REPOSITORY}:latest"
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

echo "🔍 Getting service endpoint..."

# Get the service details
SERVICE_INFO=$(aws ecs describe-services \
    --cluster $ECS_CLUSTER \
    --services $SERVICE_NAME \
    --region $AWS_REGION)


RUNNING_TASKS=$(aws ecs list-tasks \
    --cluster $ECS_CLUSTER \
    --service-name $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'taskArns' \
    --output text)

if [ ! -z "$RUNNING_TASKS" ] && [ "$RUNNING_TASKS" != "None" ]; then
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "========================="
    
    for task in $RUNNING_TASKS; do
        echo "🔍 Getting public IP for task: $task"
        
        ENI_ID=$(aws ecs describe-tasks \
            --cluster $ECS_CLUSTER \
            --tasks $task \
            --region $AWS_REGION \
            --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
            --output text)
        
        if [ "$ENI_ID" != "None" ] && [ ! -z "$ENI_ID" ]; then
            PUBLIC_IP=$(aws ec2 describe-network-interfaces \
                --network-interface-ids $ENI_ID \
                --region $AWS_REGION \
                --query 'NetworkInterfaces[0].Association.PublicIp' \
                --output text)
            
            if [ ! -z "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "None" ]; then
                echo "🌐 API Endpoint: http://$PUBLIC_IP:8000"
                echo "🏥 Health Check: http://$PUBLIC_IP:8000/health"
                echo "📚 API Docs: http://$PUBLIC_IP:8000/docs"
                
                echo "🧪 Testing health endpoint..."
                curl -f http://$PUBLIC_IP:8000/health || echo "Health check failed"
                echo ""
            fi
        fi
    done
else
    echo "❌ No running tasks found
fi

echo ""
echo "📊 Useful commands:"
echo "aws ecs describe-services --cluster $ECS_CLUSTER --services $SERVICE_NAME --region $AWS_REGION"
echo "aws logs tail /ecs/ai-paws --region $AWS_REGION --since 10m"
echo "aws ecs list-tasks --cluster $ECS_CLUSTER --service-name $SERVICE_NAME --region $AWS_REGION"