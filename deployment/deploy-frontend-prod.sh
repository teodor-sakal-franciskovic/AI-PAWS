#!/bin/bash
set -e

echo "AI-PAWS Frontend Production Deployment"
echo "======================================="

# Configuration - UPDATE THESE AFTER INFRASTRUCTURE SETUP
S3_BUCKET="ai-paws-production"
CLOUDFRONT_DIST_ID=""  # Set this after CloudFront creation
ALB_DNS=""  # Set this after ALB creation, e.g., "ai-paws-prod-alb-123456789.eu-central-1.elb.amazonaws.com"

# Validate configuration
if [ -z "$ALB_DNS" ]; then
    echo "ERROR: ALB_DNS is not set. Update this script with your ALB DNS name."
    exit 1
fi

if [ -z "$CLOUDFRONT_DIST_ID" ]; then
    echo "ERROR: CLOUDFRONT_DIST_ID is not set. Update this script with your CloudFront distribution ID."
    exit 1
fi

# Navigate to frontend directory
cd ../AI-PAWS-FE

echo "Installing dependencies..."
npm install

echo "Building for production with API endpoint: http://${ALB_DNS}/"
VITE_API_ADDRESS="http://${ALB_DNS}/" npm run build

echo "Deploying to S3..."
aws s3 sync build/ s3://${S3_BUCKET} --delete

echo "Invalidating CloudFront cache..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id ${CLOUDFRONT_DIST_ID} \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

echo "Invalidation created: ${INVALIDATION_ID}"

echo ""
echo "FRONTEND DEPLOYMENT SUCCESSFUL!"
echo "================================"
echo "CloudFront invalidation may take a few minutes to complete."
echo ""
echo "Useful commands:"
echo "aws cloudfront get-invalidation --distribution-id ${CLOUDFRONT_DIST_ID} --id ${INVALIDATION_ID}"
echo "aws cloudfront get-distribution --id ${CLOUDFRONT_DIST_ID} --query 'Distribution.DomainName' --output text"
