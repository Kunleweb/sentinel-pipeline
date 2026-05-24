import io

from googleapiclient.http import MediaIoBaseDownload

from gdrive_to_s3.config import GDRIVE_FOLDER_ID


def _list_day_folders(service) -> list[dict]:
    query = (
        f"'{GDRIVE_FOLDER_ID}' in parents"
        " and mimeType='application/vnd.google-apps.folder'"
        " and trashed=false"
    )
    return service.files().list(q=query, fields="files(id, name)").execute().get("files", [])


def _list_json_files_in_folder(service, folder_id: str) -> list[dict]:
    query = (
        f"'{folder_id}' in parents"
        " and mimeType='application/json'"
        " and trashed=false"
    )
    return service.files().list(q=query, fields="files(id, name)").execute().get("files", [])


def list_all_json_files(service) -> list[dict]:
    """Walk every day=<date> subfolder; return flat list of {id, name, table_name, day}."""
    all_files = []
    for folder in _list_day_folders(service):
        day = folder["name"].removeprefix("day=")
        for f in _list_json_files_in_folder(service, folder["id"]):
            all_files.append({
                "id":         f["id"],
                "name":       f["name"],
                "table_name": f["name"].removesuffix(".json"),
                "day":        day,
            })
    return all_files


def download_file(service, file_id: str) -> bytes:
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()
