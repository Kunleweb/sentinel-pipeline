import csv
import io

from config import S3_BUCKET, S3_PREFIX


def _to_csv_bytes(columns: list, rows: list) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def upload_table(s3_client, table_name: str, columns: list, rows: list) -> str:
    data = _to_csv_bytes(columns, rows)
    s3_key = f"{S3_PREFIX}{table_name}.csv"

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=data,
        ServerSideEncryption="AES256",
    )

    return f"s3://{S3_BUCKET}/{s3_key}"
