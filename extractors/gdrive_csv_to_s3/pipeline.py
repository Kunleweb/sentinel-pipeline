from datetime import date

from botocore.exceptions import ClientError

from gdrive_csv_to_s3.config import GDRIVE_SECRET_NAME, S3_BUCKET, SOURCE_PARTITION, FILE_NAME
from shared.config import S3_PREFIX
from gdrive_csv_to_s3.extractor import get_csv_file, download_file
from shared.converter import csv_to_parquet
from shared.secrets import get_secret
from shared.s3_client import get_s3_client
from google.oauth2 import service_account
from googleapiclient.discovery import build


def _get_gdrive_service():
    creds_dict = get_secret(GDRIVE_SECRET_NAME)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    return build("drive", "v3", credentials=credentials)


def _s3_key() -> str:
    day = date.today().isoformat()
    return f"{S3_PREFIX}source={SOURCE_PARTITION}/day={day}/{FILE_NAME}.parquet"


def _exists(s3_client, key: str) -> bool:
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def run():
    service = _get_gdrive_service()
    s3 = get_s3_client()
    s3_key = _s3_key()
    uri = f"s3://{S3_BUCKET}/{s3_key}"

    if _exists(s3, s3_key):
        print(f"  skipped — already exists: {uri}")
        return

    csv_file = get_csv_file(service)
    csv_bytes = download_file(service, csv_file["id"])
    parquet_bytes = csv_to_parquet(csv_bytes)

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=parquet_bytes,
        ContentType="application/octet-stream",
        ServerSideEncryption="AES256",
    )
    print(f"  {csv_file['name']} → {uri}")
