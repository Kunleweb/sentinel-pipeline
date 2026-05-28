import io
from googleapiclient.http import MediaIoBaseDownload

from gdrive_csv_to_s3.config import GDRIVE_FOLDER_ID


def get_csv_file(service) -> dict:
    query = (
        f"'{GDRIVE_FOLDER_ID}' in parents"
        " and mimeType='text/csv'"
        " and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if not files:
        raise FileNotFoundError(f"No CSV file found in Drive folder '{GDRIVE_FOLDER_ID}'.")
    return files[0]


def download_file(service, file_id: str) -> bytes:
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()
