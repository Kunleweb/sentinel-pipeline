import _bootstrap  # noqa: F401
from decimal import Decimal

import pyarrow as pa

from type_utils import to_decimal, parse_date, parse_timestamp
from claims.config import CLAIMS_SCHEMA, PAYMENTS_SCHEMA


def build_claim_row(claim: dict) -> dict:
    loc = claim.get("incident_location") or {}
    return {
        "claim_id":        claim["claim_id"],
        "policy_id":       claim["policy_id"],
        "customer_id":     claim["customer_id"],
        "incident_date":   parse_date(claim.get("incident_date")),
        "report_date":     parse_date(claim.get("report_date")),
        "incident_city":   (loc.get("city") or "").title() or None,
        "incident_state":  (loc.get("state") or "").upper() or None,
        "incident_zip":    str(loc["zip"]) if loc.get("zip") else None,
        "incident_type":   claim.get("incident_type"),
        "description":     claim.get("description"),
        "status":          (claim.get("status") or "").upper() or None,
        "claim_amount":    to_decimal(claim.get("claim_amount")),
        "approved_amount": to_decimal(claim.get("approved_amount")),
        "created_at":      parse_timestamp(claim.get("created_at")),
    }


def build_payment_rows(claim: dict) -> list[dict]:
    rows = []
    for seq, event in enumerate(
        (e for e in claim.get("events", []) if e.get("event_type") == "Payment_Issued"),
        start=1,
    ):
        rows.append({
            "payment_id":        f"{claim['claim_id']}-PAY-{seq:03d}",
            "claim_id":          claim["claim_id"],
            "adjuster_id":       event.get("adjuster_id"),
            "payment_amount":    to_decimal(event.get("payment_amount")),
            "payment_type":      event.get("payment_type"),
            "payment_timestamp": parse_timestamp(event.get("timestamp")),
        })
    return rows


def rows_to_table(rows: list[dict], schema: pa.Schema) -> pa.Table:
    if not rows:
        return pa.table({f.name: pa.array([], type=f.type) for f in schema})
    cols = {k: [r[k] for r in rows] for k in rows[0]}
    return pa.table(cols).cast(schema)


def sanity_check(claim_rows: list[dict], payment_rows: list[dict]) -> bool:
    total_approved = sum(r["approved_amount"] or Decimal(0) for r in claim_rows)
    total_payments = sum(r["payment_amount"]  or Decimal(0) for r in payment_rows)
    passed = total_payments <= total_approved
    print(f"\n  Sanity check:")
    print(f"    total approved_amount : {total_approved:,.2f}")
    print(f"    total payment_amount  : {total_payments:,.2f}")
    print(f"    payments <= approved  : {'PASS' if passed else 'FAIL ⚠'}")
    return passed
