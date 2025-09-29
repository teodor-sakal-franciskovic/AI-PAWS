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
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 120

    # SMTP configuration
    smtp_server: Optional[str] = None
    smtp_port: Optional[str] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # Google Drive configuration
    google_service_account_file: Optional[str] = None
    google_drive_folder_id: Optional[str] = None

    # OpenAI configuration
    openai_api_key: str = None
    llm_name: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_configuration()

    def _load_configuration(self):
        """Load configuration from AWS Secrets Manager or environment variables"""
        # Database configuration
        self.database_user = aws_secrets.get_config_value("database_user", secret_type="database") or os.getenv("DATABASE_USER", "ai-paws")
        self.database_password = aws_secrets.get_config_value("database_password", secret_type="database") or os.getenv("DATABASE_PASSWORD", "pawsword123")
        self.database_host = aws_secrets.get_config_value("database_host", secret_type="database") or os.getenv("DATABASE_HOST", "ai-paws-db")
        self.database_port = aws_secrets.get_config_value("database_port", secret_type="database") or os.getenv("DATABASE_PORT", "5432")
        self.database_name = aws_secrets.get_config_value("database_name", secret_type="database") or os.getenv("DATABASE_NAME", "ai-paws")

        # JWT configuration
        self.secret_key = aws_secrets.get_config_value("secret_key", secret_type="application") or os.getenv("SECRET_KEY", "1234567890")
        self.algorithm = aws_secrets.get_config_value("algorithm", secret_type="application") or os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(aws_secrets.get_config_value("access_token_expire_minutes", secret_type="application") or os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        # SMTP configuration
        self.smtp_server = aws_secrets.get_config_value("smtp_server", secret_type="smtp") or os.getenv("SMTP_SERVER", "")
        self.smtp_port = aws_secrets.get_config_value("smtp_port", secret_type="smtp") or os.getenv("SMTP_PORT", "")
        self.smtp_username = aws_secrets.get_config_value("smtp_username", secret_type="smtp") or os.getenv("SMTP_USERNAME", "")
        self.smtp_password = aws_secrets.get_config_value("smtp_password", secret_type="smtp") or os.getenv("SMTP_PASSWORD", "")

        # Google Drive configuration
        self.google_service_account_file = aws_secrets.get_config_value("google_service_account_file", secret_type="google") or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
        self.google_drive_folder_id = aws_secrets.get_config_value("google_drive_folder_id", secret_type="google") or os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

        # OpenAI configuration
        self.openai_api_key = aws_secrets.get_config_value("openai_api_key", secret_type="openai") or os.getenv("OPENAI_API_KEY")
        self.llm_name = aws_secrets.get_config_value("llm_name", secret_type="openai") or os.getenv("LLM_NAME", "gpt-4o")

    class Config:
        env_file = ".env"


settings = Settings()
