"""
Finds the first CSV file in the configured Drive folder and downloads it.
"""

import io
from googleapiclient.http import MediaIoBaseDownload

from gdrive_csv_to_s3.config import GDRIVE_FOLDER_ID


def get_csv_file(service) -> dict:
    """Return {id, name} for the CSV file in the folder. Raises if none found."""
    query = (
        f"'{GDRIVE_FOLDER_ID}' in parents"
        " and mimeType='text/csv'"
        " and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if not files:
        raise FileNotFoundError(
            f"No CSV file found in Drive folder '{GDRIVE_FOLDER_ID}'. "
            "Check the folder ID and sharing permissions."
        )
    return files[0]


def download_file(service, file_id: str) -> bytes:
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()
