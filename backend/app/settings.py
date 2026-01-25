import os
from pydantic_settings import BaseSettings
from typing import Optional
from .utils.aws_secrets import aws_secrets


class Settings(BaseSettings):
    # Environment detection
    environment: str = os.getenv("ENVIRONMENT", "dev")
    use_aws_secrets: bool = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"

    # Database configuration
    database_user: str = None
    database_password: str = None
    database_host: str = None
    database_port: str = None
    database_name: str = None

    # JWT configuration
    secret_key: str = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    # API keys
    groq_cloud_api_key: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_configuration()

    def _load_configuration(self):
        """Load configuration from AWS Secrets Manager or environment variables"""
        # Database configuration
        self.database_user = aws_secrets.get_config_value(
            "database_user", secret_type="database"
        ) or os.getenv("DATABASE_USER", "ai-paws")
        self.database_password = aws_secrets.get_config_value(
            "database_password", secret_type="database"
        ) or os.getenv("DATABASE_PASSWORD", "pawsword123")
        self.database_host = aws_secrets.get_config_value(
            "database_host", secret_type="database"
        ) or os.getenv("DATABASE_HOST", "ai-paws-db")
        self.database_port = aws_secrets.get_config_value(
            "database_port", secret_type="database"
        ) or os.getenv("DATABASE_PORT", "5432")
        self.database_name = aws_secrets.get_config_value(
            "database_name", secret_type="database"
        ) or os.getenv("DATABASE_NAME", "ai-paws")

        # JWT configuration
        self.secret_key = aws_secrets.get_config_value(
            "secret_key", secret_type="application"
        ) or os.getenv("SECRET_KEY", "1234567890")
        self.algorithm = aws_secrets.get_config_value(
            "algorithm", secret_type="application"
        ) or os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            aws_secrets.get_config_value(
                "access_token_expire_minutes", secret_type="application"
            )
            or os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
        )

        # API keys (optional)
        self.groq_cloud_api_key = os.getenv("GROQ_CLOUD_API_KEY", "")

    class Config:
        env_file = ".env"


settings = Settings()
