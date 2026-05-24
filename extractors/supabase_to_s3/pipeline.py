from supabase_to_s3.config import TABLES, SOURCE_PARTITION, SECRETS_MANAGER_SECRET_NAME
from shared.secrets import get_secret
from shared.s3_client import get_s3_client
from shared.s3_storage import upload_table
from supabase_to_s3.database import get_connection, extract_table


def run():
    print("Step 1/4  Fetching DB credentials from Secrets Manager...")
    credentials = get_secret(SECRETS_MANAGER_SECRET_NAME)

    print("Step 2/4  Establishing S3 connection...")
    s3 = get_s3_client()

    print("Step 3/4  Connecting to Supabase PostgreSQL...")
    with get_connection(credentials) as conn:
        print(f"Step 4/4  Exporting {len(TABLES)} table(s) to S3...\n")
        uploaded, skipped = [], []
        for table in TABLES:
            print(f"  [{table}] extracting...")
            columns, rows = extract_table(conn, table)
            print(f"  [{table}] {len(rows):,} rows — checking S3...")
            uri, exists = upload_table(s3, SOURCE_PARTITION, table, columns, rows)
            if exists:
                skipped.append(uri)
                print(f"  [{table}] skipped — already exists")
            else:
                uploaded.append(uri)
                print(f"  [{table}] uploaded → {uri}")

    print("\n── Verification ──────────────────────────────────────")
    for uri in uploaded:
        print(f"  uploaded  {uri}")
    for uri in skipped:
        print(f"  skipped   {uri}")
    print(f"\n  {len(uploaded)} uploaded, {len(skipped)} skipped.")
    print("──────────────────────────────────────────────────────")
