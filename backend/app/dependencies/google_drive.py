from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

from ..services.google_drive import upload_pdf
from ..settings import settings
from ..utils.logger import logger

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_drive_service():
    base_dir = Path(__file__).resolve().parent.parent
    creds_path = base_dir / settings.google_service_account_file
    logger.info(f"Resolved service account path: {creds_path}")
    credentials = service_account.Credentials.from_service_account_file(
        str(creds_path), scopes=SCOPES
    )

    drive_service = build("drive", "v3", credentials=credentials)
    return drive_service


def get_upload_pdf():
    return upload_pdf
