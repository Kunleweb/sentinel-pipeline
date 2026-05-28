from datetime import date

from botocore.exceptions import ClientError

from local_to_s3.config import S3_BUCKET
from local_to_s3.extractor import get_local_files, read_file
from shared.converter import csv_to_parquet
from shared.config import S3_PREFIX
from shared.s3_client import get_s3_client


def _s3_key(source: str, file_name: str) -> str:
    return f"{S3_PREFIX}source={source}/day={date.today().isoformat()}/{file_name}.parquet"


def _exists(s3_client, key: str) -> bool:
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def run():
    s3 = get_s3_client()
    uploaded, skipped = [], []

    for f in get_local_files():
        s3_key = _s3_key(f["source"], f["file_name"])
        uri = f"s3://{S3_BUCKET}/{s3_key}"

        if _exists(s3, s3_key):
            skipped.append(uri)
            print(f"  [{f['file_name']}] skipped")
            continue

        parquet_bytes = csv_to_parquet(read_file(f["path"]))
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=parquet_bytes,
            ContentType="application/octet-stream",
            ServerSideEncryption="AES256",
        )
        uploaded.append(uri)
        print(f"  [{f['file_name']}] → {uri}")

    print(f"\n  {len(uploaded)} uploaded, {len(skipped)} skipped")
