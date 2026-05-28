import _bootstrap  # noqa: F401
import json
from collections import defaultdict

from shared.config import S3_BUCKET, S3_PREFIX
from s3_io import get_s3_client, key_exists, write_parquet, list_files
from claims.config import CLAIMS_SOURCE, PROCESSED_PREFIX, CLAIMS_SCHEMA, PAYMENTS_SCHEMA
from claims.transformer import build_claim_row, build_payment_rows, rows_to_table, sanity_check


def _read_json(s3, key: str) -> dict:
    return json.loads(s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read())


def _day_from_key(key: str) -> str:
    for part in key.split("/"):
        if part.startswith("day="):
            return part.replace("day=", "")
    raise ValueError(f"No day= partition found in key: {key}")


def _processed_key(folder: str, day: str) -> str:
    return f"{PROCESSED_PREFIX}{folder}/day={day}/{folder}.parquet"


def run():
    s3 = get_s3_client()

    all_keys = list_files(s3, f"{S3_PREFIX}source={CLAIMS_SOURCE}/", suffix=".json")
    print(f"  {len(all_keys)} claim file(s) found\n")

    by_day: dict[str, list[str]] = defaultdict(list)
    for key in all_keys:
        by_day[_day_from_key(key)].append(key)

    uploaded, skipped = [], []
    all_claim_rows, all_payment_rows = [], []

    for day in sorted(by_day):
        print(f"  [day={day}] {len(by_day[day])} file(s)")

        cf_key  = _processed_key("claims_fact", day)
        pay_key = _processed_key("payments",    day)

        if key_exists(s3, cf_key) and key_exists(s3, pay_key):
            skipped += [f"s3://{S3_BUCKET}/{cf_key}", f"s3://{S3_BUCKET}/{pay_key}"]
            print(f"    skipped — already processed")
            continue

        day_claim_rows, day_payment_rows = [], []

        for key in by_day[day]:
            claim = _read_json(s3, key)
            claim_row    = build_claim_row(claim)
            payment_rows = build_payment_rows(claim)
            day_claim_rows.append(claim_row)
            day_payment_rows.extend(payment_rows)
            print(f"    [{key.split('/')[-1]}] read ({len(payment_rows)} payment(s))")

        all_claim_rows.extend(day_claim_rows)
        all_payment_rows.extend(day_payment_rows)

        write_parquet(s3, rows_to_table(day_claim_rows, CLAIMS_SCHEMA), cf_key)
        write_parquet(s3, rows_to_table(day_payment_rows, PAYMENTS_SCHEMA), pay_key)

        uploaded += [f"s3://{S3_BUCKET}/{cf_key}", f"s3://{S3_BUCKET}/{pay_key}"]
        print(f"    written → {len(day_claim_rows)} claim(s), {len(day_payment_rows)} payment(s)")

    if all_claim_rows:
        sanity_check(all_claim_rows, all_payment_rows)

    return {"uploaded": uploaded, "skipped": skipped, "errors": []}
