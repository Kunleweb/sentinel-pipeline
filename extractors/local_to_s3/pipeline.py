from datetime import date

from botocore.exceptions import ClientError

from local_to_s3.config import S3_BUCKET
from local_to_s3.extractor import get_local_files, read_file
from local_to_s3.converter import csv_to_parquet
from shared.config import S3_PREFIX
from shared.s3_client import get_s3_client


def _s3_key(source: str, file_name: str) -> str:
    day = date.today().isoformat()
    return f"{S3_PREFIX}source={source}/day={day}/{file_name}.parquet"


def _exists(s3_client, key: str) -> bool:
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def run():
    print("Step 1/3  Establishing S3 connection...")
    s3 = get_s3_client()

    print("Step 2/3  Reading local files...\n")
    files = get_local_files()

    print("Step 3/3  Converting and uploading...\n")
    uploaded, skipped = [], []

    for f in files:
        s3_key = _s3_key(f["source"], f["file_name"])
        uri = f"s3://{S3_BUCKET}/{s3_key}"

        if _exists(s3, s3_key):
            skipped.append(uri)
            print(f"  [{f['file_name']}] skipped — already exists")
            continue

        print(f"  [{f['file_name']}] reading from disk...")
        csv_bytes = read_file(f["path"])
        print(f"  [{f['file_name']}] {len(csv_bytes):,} bytes — converting to parquet...")
        parquet_bytes = csv_to_parquet(csv_bytes)

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=parquet_bytes,
            ContentType="application/octet-stream",
            ServerSideEncryption="AES256",
        )
        uploaded.append(uri)
        print(f"  [{f['file_name']}] uploaded → {uri}")

    print("\n── Verification ──────────────────────────────────────")
    for uri in uploaded:
        print(f"  uploaded  {uri}")
    for uri in skipped:
        print(f"  skipped   {uri}")
    print(f"\n  {len(uploaded)} uploaded, {len(skipped)} skipped.")
    print("──────────────────────────────────────────────────────")
