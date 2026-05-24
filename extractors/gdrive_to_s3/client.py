from google.oauth2 import service_account
from googleapiclient.discovery import build

from shared.secrets import get_secret
from gdrive_to_s3.config import GDRIVE_SECRET_NAME


def get_gdrive_service():
    creds_dict = get_secret(GDRIVE_SECRET_NAME)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    return build("drive", "v3", credentials=credentials)
