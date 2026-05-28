import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "extractors"))

import snowflake.connector
from shared.secrets import get_secret

STAGE   = "@SENTINEL.STAGING.S3_PROCESSED_STAGE"
STAGING = "SENTINEL.STAGING"
WH      = "SENTINEL.WAREHOUSE"

TABLES = [
    ("claims_fact",   "claims_fact/",   "claims_fact",   "claim_id"),
    ("payments",      "payments/",      "payments",      "payment_id"),
    ("dim_customer",  "customers/",     "dim_customer",  "customer_id"),
    ("dim_agent",     "agents/",        "dim_agent",     "agent_id"),
    ("dim_policy",    "policies/",      "dim_policy",    "policy_id"),
    ("dim_coverage",  "coverages/",     "dim_coverage",  "coverage_id"),
    ("weather_daily", "weather_daily/", "weather_daily", "weather_date,zip_code"),
]


def _get_connection():
    secret = get_secret("snowflake_secret")
    return snowflake.connector.connect(
        account   = secret["account"],
        user      = secret["user"],
        password  = secret["password"],
        warehouse = secret["warehouse"],
        database  = "SENTINEL",
        schema    = "STAGING",
        role      = secret.get("role", "SYSADMIN"),
    )


def _columns(cur, staging_table: str) -> list[str]:
    cur.execute(
        f"SELECT column_name FROM information_schema.columns "
        f"WHERE table_schema = 'STAGING' AND table_name = '{staging_table.upper()}' "
        f"ORDER BY ordinal_position"
    )
    return [row[0] for row in cur.fetchall()]


def _copy_into_staging(cur, staging_table: str, s3_subfolder: str) -> int:
    cur.execute(f"""
        COPY INTO {STAGING}.{staging_table}
        FROM {STAGE}/{s3_subfolder}
        FILE_FORMAT  = (FORMAT_NAME = SENTINEL.STAGING.PARQUET_FMT)
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        FORCE        = TRUE
        PURGE        = FALSE
        ON_ERROR     = ABORT_STATEMENT
    """)
    results = cur.fetchall()
    return sum(r[3] for r in results) if results else 0


def _merge_into_warehouse(cur, staging_table: str, wh_table: str, merge_key: str, cols: list[str]) -> None:
    keys         = [k.strip() for k in merge_key.split(",")]
    join_clause  = " AND ".join(f"t.{k} = s.{k}" for k in keys)
    update_pairs = ", ".join(f"t.{c} = s.{c}" for c in cols if c not in keys)
    insert_cols  = ", ".join(cols)
    insert_vals  = ", ".join(f"s.{c}" for c in cols)

    cur.execute(f"""
        MERGE INTO {WH}.{wh_table} t
        USING {STAGING}.{staging_table} s
        ON {join_clause}
        WHEN MATCHED THEN UPDATE SET {update_pairs}
        WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
    """)


def run():
    conn = _get_connection()
    cur  = conn.cursor()
    results = []

    for staging_table, s3_subfolder, wh_table, merge_key in TABLES:
        print(f"\n  [{wh_table}]")
        cur.execute(f"TRUNCATE TABLE {STAGING}.{staging_table}")

        rows_loaded = _copy_into_staging(cur, staging_table, s3_subfolder)
        print(f"    {rows_loaded:,} rows loaded")

        _merge_into_warehouse(cur, staging_table, wh_table, merge_key, _columns(cur, staging_table))

        cur.execute(f"SELECT COUNT(*) FROM {WH}.{wh_table}")
        wh_count = cur.fetchone()[0]
        print(f"    {wh_count:,} rows in warehouse")
        results.append((wh_table, rows_loaded, wh_count))

    cur.close()
    conn.close()

    print("\n  table                staged    warehouse")
    print("  " + "-" * 42)
    for table, loaded, total in results:
        print(f"  {table:<20} {loaded:<10,} {total:,}")


if __name__ == "__main__":
    run()
