from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_user: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    smtp_server: str
    smtp_port: str
    smtp_username: str
    smtp_password: str

    google_service_account_file: str
    google_drive_folder_id: str

    openai_api_key: str
    llm_name: str

    class Config:
        env_file = ".env"


settings = Settings()
