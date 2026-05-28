from supabase_to_s3.config import TABLES, SOURCE_PARTITION, SECRETS_MANAGER_SECRET_NAME
from shared.secrets import get_secret
from shared.s3_client import get_s3_client
from shared.s3_storage import upload_table, key_exists, s3_key_for
from supabase_to_s3.database import get_connection, extract_table


def run():
    print("Step 1/4  Fetching DB credentials from Secrets Manager...")
    credentials = get_secret(SECRETS_MANAGER_SECRET_NAME)

    print("Step 2/4  Establishing S3 connection...")
    s3 = get_s3_client()

    print("Step 3/4  Checking which tables already exist in S3...")
    to_extract = []
    skipped = []
    for table in TABLES:
        s3_key = s3_key_for(SOURCE_PARTITION, table, "parquet")
        uri = f"s3://sentinel-kunle/{s3_key}"
        if key_exists(s3, s3_key):
            skipped.append(uri)
            print(f"  [{table}] skipped — already exists")
        else:
            to_extract.append(table)
            print(f"  [{table}] queued for extraction")

    if not to_extract:
        print("\n  All tables already exist in S3. Nothing to do.")
        return

    print(f"\nStep 4/4  Extracting and uploading {len(to_extract)} table(s)...\n")
    uploaded = []
    with get_connection(credentials) as conn:
        for table in to_extract:
            print(f"  [{table}] extracting from Supabase...")
            columns, rows = extract_table(conn, table)
            print(f"  [{table}] {len(rows):,} rows — uploading...")
            uri, _ = upload_table(s3, SOURCE_PARTITION, table, columns, rows)
            uploaded.append(uri)
            print(f"  [{table}] uploaded → {uri}")

    print("\n── Verification ──────────────────────────────────────")
    for uri in uploaded:
        print(f"  uploaded  {uri}")
    for uri in skipped:
        print(f"  skipped   {uri}")
    print(f"\n  {len(uploaded)} uploaded, {len(skipped)} skipped.")
    print("──────────────────────────────────────────────────────")
