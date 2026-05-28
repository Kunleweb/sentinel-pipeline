# Sentinel

Multiple data sources into a single Snowflake warehouse.

## Source systems

- **Policy admin**  customers, agents, policies, coverages from Supabase PostgreSQL
- **Claims**  nested JSON files dropped daily to Google Drive
- **Billing** CSV exports from Google Drive
- **Weather** local CSV file

## Architecture

```
Sources : S3 landing/  S3 processed/ : Snowflake
```

**Landing** : raw data as-is, partitioned by `source=` and `day=`.  
**Processed** : flattened, typed, deduplicated Parquet.  
**Snowflake** : staging tables fed by S3, merged into warehouse tables.

All three layers are idempotent. Re-running skips anything already written.

## Running

```bash
python main.py
```

Or run individual layers:

```bash
python extractors/main.py
python transforms/main.py
python loaders/load_warehouse.py
```

## Setup

All secrets are in AWS Secrets Manager (region `eu-west-2`): `kunleweb_secret` for Supabase, `kunleweb_gdrive_secret` for Google Drive, and `snowflake_secret` for Snowflake. AWS credentials go in `extractors/shared/config.py` (gitignored).

Run `sql/snowflake_ddl.sql` once in Snowflake to create the database, schemas, tables, and S3 stage. After running it you'll need to grab the IAM user ARN and external ID from `DESC INTEGRATION S3_SENTINEL_INTEGRATION` and update the IAM role trust policy in AWS before the stage will work.

```bash
pip install -r requirements.txt
```

## Warehouse tables

`SENTINEL.WAREHOUSE` contains seven tables: `claims_fact`, `payments`, `dim_customer`, `dim_agent`, `dim_policy`, `dim_coverage`, `weather_daily`.
