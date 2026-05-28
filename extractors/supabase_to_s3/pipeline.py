from supabase_to_s3.config import TABLES, SOURCE_PARTITION, SECRETS_MANAGER_SECRET_NAME
from shared.secrets import get_secret
from shared.s3_client import get_s3_client
from shared.s3_storage import upload_table, key_exists, s3_key_for
from supabase_to_s3.database import get_connection, extract_table


def run():
    credentials = get_secret(SECRETS_MANAGER_SECRET_NAME)
    s3 = get_s3_client()

    to_extract, skipped = [], []
    for table in TABLES:
        s3_key = s3_key_for(SOURCE_PARTITION, table, "parquet")
        if key_exists(s3, s3_key):
            skipped.append(f"s3://sentinel-kunle/{s3_key}")
            print(f"  [{table}] skipped")
        else:
            to_extract.append(table)

    if not to_extract:
        print("  all tables already in S3")
        return

    uploaded = []
    with get_connection(credentials) as conn:
        for table in to_extract:
            columns, rows = extract_table(conn, table)
            uri, _ = upload_table(s3, SOURCE_PARTITION, table, columns, rows)
            uploaded.append(uri)
            print(f"  [{table}] {len(rows):,} rows → {uri}")

    for uri in skipped:
        print(f"  skipped  {uri}")
