import _bootstrap  # noqa: F401

from shared.config import S3_BUCKET, S3_PREFIX
from s3_io import get_s3_client, key_exists, read_parquet, write_parquet, find_latest_day
from policy_admin.config import TABLE_TRANSFORMS, PROCESSED_PREFIX
from policy_admin.cleaner import clean


def _landing_key(cfg: dict, day: str) -> str:
    if cfg["landing_source"] == "meteo_weather":
        return f"{S3_PREFIX}source={cfg['landing_source']}/day={day}/{cfg['landing_name']}.parquet"
    return (
        f"{S3_PREFIX}source={cfg['landing_source']}/"
        f"table={cfg['landing_name']}/"
        f"day={day}/{cfg['landing_name']}.parquet"
    )


def _landing_prefix(cfg: dict) -> str:
    if cfg["landing_source"] == "meteo_weather":
        return f"{S3_PREFIX}source={cfg['landing_source']}/"
    return f"{S3_PREFIX}source={cfg['landing_source']}/table={cfg['landing_name']}/"


def _processed_key(output_name: str, day: str) -> str:
    return f"{PROCESSED_PREFIX}{output_name}/day={day}/{output_name}.parquet"


def run():
    s3 = get_s3_client()
    uploaded, skipped, errors = [], [], []

    for name, cfg in TABLE_TRANSFORMS.items():
        print(f"\n  [{cfg['output_name']}]")

        day = find_latest_day(s3, _landing_prefix(cfg))
        if not day:
            errors.append(cfg["output_name"])
            print(f"    ERROR — no landing data found")
            continue

        out_key = _processed_key(cfg["output_name"], day)

        if key_exists(s3, out_key):
            skipped.append(f"s3://{S3_BUCKET}/{out_key}")
            print(f"    skipped — already exists: day={day}")
            continue

        land_key = _landing_key(cfg, day)
        print(f"    reading  s3://{S3_BUCKET}/{land_key}")
        table = read_parquet(s3, land_key)
        print(f"    {len(table):,} rows before cleaning")

        table = clean(table, cfg)
        print(f"    {len(table):,} rows after cleaning")

        write_parquet(s3, table, out_key)
        uploaded.append(f"s3://{S3_BUCKET}/{out_key}")
        print(f"    written → s3://{S3_BUCKET}/{out_key}")

    return {"uploaded": uploaded, "skipped": skipped, "errors": errors}
