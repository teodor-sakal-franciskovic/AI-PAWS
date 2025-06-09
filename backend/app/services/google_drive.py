import io

from googleapiclient.http import MediaIoBaseUpload

from ..models.user import User
from ..settings import settings
from ..utils.logger import logger


def _get_or_create_folder(
    drive_service, parent_folder_id: str, folder_name: str
) -> str:
    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and name='{folder_name}' "
        f"and '{parent_folder_id}' in parents "
        f"and trashed = false"
    )

    results = (
        drive_service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    folders = results.get("files", [])

    if folders:
        return folders[0]["id"]

    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }

    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]


def upload_pdf(
    drive_service, file_bytes: bytes, current_user: User, chapter_name: str, mode: str
):
    file_stream = io.BytesIO(file_bytes)

    subfolder_name = f"PGL_{chapter_name}_MOD_{mode}"
    parent_folder_id = settings.google_drive_folder_id
    logger.info(f"Creating/Retrieving folder {subfolder_name}")
    subfolder_id = _get_or_create_folder(
        drive_service, parent_folder_id, subfolder_name
    )
    logger.info(f"Successfully create/retrieved folder {subfolder_name}")

    file_metadata = {
        "name": f"{current_user.index}_{current_user.name}_{current_user.surname}.pdf",
        "parents": [subfolder_id],
    }

    media = MediaIoBaseUpload(file_stream, mimetype="application/pdf")

    logger.info(f"Uploading the submitted file {file_metadata['name']}...")
    uploaded_file = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    logger.info(f"Successfully uploaded the submitted file: {file_metadata['name']}")

    file_id = uploaded_file.get("id")

    drive_service.permissions().create(
        fileId=file_id,
        body={
            "type": "anyone",
            "role": "reader",
        },
    ).execute()

    file_link = f"https://drive.google.com/file/d/{file_id}/view"

    logger.info(f"File link {file_link}")

    # Submission schema will be initiated here and filled with other data in the other functions
    return file_id, file_link
