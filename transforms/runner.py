"""
Reads parquet from S3 landing, applies transforms, writes to S3 processed zone.
"""

import io
from datetime import date

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

from config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    S3_BUCKET, S3_PREFIX, PROCESSED_PREFIX, TABLE_TRANSFORMS,
)
from cleaner import clean


def _s3_client():
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def _find_latest_day(s3, source: str, name: str) -> str | None:
    """Return the most recent day= partition available in landing for this table."""
    prefix = f"{S3_PREFIX}source={source}/table={name}/"
    # weather has no table= segment
    if source == "meteo_weather":
        prefix = f"{S3_PREFIX}source={source}/"

    paginator = s3.get_paginator("list_objects_v2")
    days = []
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix, Delimiter="/"):
        for item in page.get("CommonPrefixes", []):
            part = item["Prefix"].rstrip("/").split("/")[-1]
            if part.startswith("day="):
                days.append(part.replace("day=", ""))
    return max(days) if days else None


def _read_parquet(s3, key: str) -> pa.Table:
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return pq.read_table(io.BytesIO(obj["Body"].read()))


def _processed_key(output_name: str) -> str:
    day = date.today().isoformat()
    return f"{PROCESSED_PREFIX}{output_name}/day={day}/{output_name}.parquet"


def _key_exists(s3, key: str) -> bool:
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def _write_parquet(s3, table: pa.Table, key: str) -> None:
    buf = io.BytesIO()
    pq.write_table(table, buf)
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=buf.getvalue(),
        ContentType="application/octet-stream",
        ServerSideEncryption="AES256",
    )


def run_all():
    s3 = _s3_client()
    results = {"uploaded": [], "skipped": [], "errors": []}

    for name, cfg in TABLE_TRANSFORMS.items():
        print(f"\n  [{cfg['output_name']}]")
        out_key = _processed_key(cfg["output_name"])

        if _key_exists(s3, out_key):
            uri = f"s3://{S3_BUCKET}/{out_key}"
            results["skipped"].append(uri)
            print(f"    skipped — already exists in processed")
            continue

        # find latest landing day
        day = _find_latest_day(s3, cfg["landing_source"], cfg["landing_name"])
        if not day:
            results["errors"].append(cfg["output_name"])
            print(f"    ERROR — no landing data found for source={cfg['landing_source']}")
            continue

        # build landing key
        if cfg["landing_source"] == "meteo_weather":
            land_key = f"{S3_PREFIX}source={cfg['landing_source']}/day={day}/{cfg['landing_name']}.parquet"
        else:
            land_key = f"{S3_PREFIX}source={cfg['landing_source']}/table={cfg['landing_name']}/day={day}/{cfg['landing_name']}.parquet"

        print(f"    reading  s3://{S3_BUCKET}/{land_key}")
        table = _read_parquet(s3, land_key)
        print(f"    {len(table):,} rows before cleaning")

        table = clean(table, cfg)
        print(f"    {len(table):,} rows after cleaning")

        print(f"    writing  s3://{S3_BUCKET}/{out_key}")
        _write_parquet(s3, table, out_key)
        uri = f"s3://{S3_BUCKET}/{out_key}"
        results["uploaded"].append(uri)
        print(f"    done ✓")

    return results
