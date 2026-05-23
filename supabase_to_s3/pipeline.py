"""
Orchestration layer — ties secrets, database, and storage together.
Contains no business logic of its own; just coordinates the other modules.
"""

from config import TABLES
from secrets import get_db_credentials
from database import get_connection, extract_table
from s3_client import get_s3_client
from s3_storage import upload_table


def run():
    print("Step 1/4  Fetching credentials from Secrets Manager...")
    credentials = get_db_credentials()

    print("Step 2/4  Establishing S3 connection...")
    s3 = get_s3_client()

    print("Step 3/4  Connecting to Supabase PostgreSQL...")
    with get_connection(credentials) as conn:
        print(f"Step 4/4  Exporting {len(TABLES)} table(s) to S3...\n")
        for table in TABLES:
            print(f"  [{table}] extracting...")
            columns, rows = extract_table(conn, table)
            print(f"  [{table}] {len(rows):,} rows — uploading...")
            uri = upload_table(s3, table, columns, rows)
            print(f"  [{table}] done → {uri}")

    print("\nAll tables exported successfully.")
