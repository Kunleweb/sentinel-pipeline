import _bootstrap  # noqa: F401 — must be first
import io

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

from shared.config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET,
)


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def key_exists(s3, key: str) -> bool:
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def read_parquet(s3, key: str) -> pa.Table:
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return pq.read_table(io.BytesIO(obj["Body"].read()))


def write_parquet(s3, table: pa.Table, key: str) -> None:
    buf = io.BytesIO()
    pq.write_table(table, buf)
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=buf.getvalue(),
        ContentType="application/octet-stream",
        ServerSideEncryption="AES256",
    )


def find_latest_day(s3, prefix: str) -> str | None:
    """Return the most recent day=<date> partition value under prefix."""
    paginator = s3.get_paginator("list_objects_v2")
    days = []
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix, Delimiter="/"):
        for item in page.get("CommonPrefixes", []):
            part = item["Prefix"].rstrip("/").split("/")[-1]
            if part.startswith("day="):
                days.append(part.replace("day=", ""))
    return max(days) if days else None


def list_files(s3, prefix: str, suffix: str = ".json") -> list[str]:
    """Return all keys under prefix that end with suffix."""
    paginator = s3.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(suffix):
                keys.append(obj["Key"])
    return keys
