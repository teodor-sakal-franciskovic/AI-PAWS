import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AWSSecretsManager:
    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "eu-central-1")
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.use_aws_secrets = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
        self.client = None

        if self.use_aws_secrets:
            try:
                import boto3
                from botocore.exceptions import NoCredentialsError
                self.client = boto3.client("secretsmanager", region_name=self.region_name)
                logger.info(f"AWS Secrets Manager initialized for environment: {self.environment}")
            except ImportError:
                logger.warning("boto3 not installed, falling back to environment variables")
                self.use_aws_secrets = False
            except NoCredentialsError:
                logger.warning("AWS credentials not found, falling back to environment variables")
                self.use_aws_secrets = False
                self.client = None
        else:
            logger.info("Using local environment variables (USE_AWS_SECRETS=false)")

    def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a secret from AWS Secrets Manager"""
        if not self.use_aws_secrets or not self.client:
            return None

        try:
            from botocore.exceptions import ClientError
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

    def get_config_value(self, key: str, default: Any = None, secret_type: str = None) -> Any:
        """Get a configuration value from AWS Secrets Manager or environment variables"""
        if self.use_aws_secrets and self.client and secret_type:
            secret_name = f"ai-paws-{secret_type}-{self.environment}"
            secret_data = self.get_secret(secret_name)
            if secret_data and key in secret_data:
                return secret_data[key]

        # Fallback to environment variables
        env_value = os.getenv(key.upper(), default)
        if env_value is not None:
            return env_value

        return default


# Global instance
aws_secrets = AWSSecretsManager()
