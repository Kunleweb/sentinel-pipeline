import io
from datetime import date

import pyarrow as pa
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

from shared.config import S3_BUCKET, S3_PREFIX


def _s3_key(source: str, table_name: str, extension: str, day: str = None) -> str:
    day = day or date.today().isoformat()
    return (
        f"{S3_PREFIX}"
        f"source={source}/"
        f"table={table_name}/"
        f"day={day}/"
        f"{table_name}.{extension}"
    )


def key_exists(s3_client, key: str) -> bool:
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def s3_key_for(source: str, table_name: str, extension: str, day: str = None) -> str:
    return _s3_key(source, table_name, extension, day)


def upload_table(s3_client, source: str, table_name: str, columns: list, rows: list) -> tuple[str, bool]:
    """Supabase tables → parquet. Returns (uri, skipped)."""
    s3_key = _s3_key(source, table_name, "parquet")

    if key_exists(s3_client, s3_key):
        return f"s3://{S3_BUCKET}/{s3_key}", True

    arrays = [pa.array([row[i] for row in rows]) for i in range(len(columns))]
    table = pa.table(dict(zip(columns, arrays)))
    buf = io.BytesIO()
    pq.write_table(table, buf)

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=buf.getvalue(),
        ContentType="application/octet-stream",
        ServerSideEncryption="AES256",
    )
    return f"s3://{S3_BUCKET}/{s3_key}", False


def upload_json_file(s3_client, source: str, table_name: str, content: bytes, day: str = None) -> tuple[str, bool]:
    """Google Drive JSON files → S3 as-is. Returns (uri, skipped)."""
    s3_key = _s3_key(source, table_name, "json", day=day)

    if key_exists(s3_client, s3_key):
        return f"s3://{S3_BUCKET}/{s3_key}", True

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=content,
        ContentType="application/json",
        ServerSideEncryption="AES256",
    )
    return f"s3://{S3_BUCKET}/{s3_key}", False
