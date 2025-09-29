import json
import os
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logger = logging.getLogger(__name__)


class AWSSecretsManager:
    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "eu-central-1")
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.use_aws_secrets = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
        
        if self.use_aws_secrets:
            try:
                self.client = boto3.client("secretsmanager", region_name=self.region_name)
                logger.info(f"AWS Secrets Manager initialized for environment: {self.environment}")
            except NoCredentialsError:
                logger.warning("AWS credentials not found, falling back to local environment variables")
                self.use_aws_secrets = False
                self.client = None
        else:
            logger.info("Using local environment variables (USE_AWS_SECRETS=false)")
            self.client = None

    def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a secret from AWS Secrets Manager"""
        if not self.use_aws_secrets or not self.client:
            return None
            
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response.get("SecretString")
            if secret_string:
                return json.loads(secret_string)
        except ClientError as e:
            logger.error(f"Error retrieving secret {secret_name}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing secret {secret_name} as JSON: {e}")
            return None
        
        return None

    def get_all_secrets(self) -> Dict[str, Any]:
        """Retrieve all AI-PAWS secrets for the current environment"""
        if not self.use_aws_secrets:
            return {}
        
        secrets = {}
        secret_types = ["database", "application", "smtp", "google", "openai"]
        
        for secret_type in secret_types:
            secret_name = f"ai-paws-{secret_type}-{self.environment}"
            secret_data = self.get_secret(secret_name)
            if secret_data:
                secrets.update(secret_data)
                logger.debug(f"Retrieved {secret_type} secrets")
            else:
                logger.warning(f"Failed to retrieve {secret_type} secrets from {secret_name}")
        
        return secrets

    def get_config_value(self, key: str, default: Any = None, secret_type: str = None) -> Any:
        """Get a configuration value, trying AWS Secrets Manager first, then environment variables"""
        # If USE_AWS_SECRETS is false, skip AWS and go straight to environment variables
        if self.use_aws_secrets and self.client:
            if secret_type:
                # Try specific secret type first
                secret_name = f"ai-paws-{secret_type}-{self.environment}"
                secret_data = self.get_secret(secret_name)
                if secret_data and key in secret_data:
                    return secret_data[key]
            else:
                # Try all secrets
                all_secrets = self.get_all_secrets()
                if key in all_secrets:
                    return all_secrets[key]
        
        # Fallback to environment variables
        env_value = os.getenv(key.upper(), default)
        if env_value is not None:
            logger.debug(f"Using environment variable for {key}")
            return env_value
        
        logger.warning(f"Configuration value {key} not found in AWS Secrets or environment variables")
        return default


# Global instance
aws_secrets = AWSSecretsManager()