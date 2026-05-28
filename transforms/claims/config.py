import _bootstrap  # noqa: F401
import pyarrow as pa

CLAIMS_SOURCE    = "claims_mgmt"
PROCESSED_PREFIX = "processed/"

CLAIMS_SCHEMA = pa.schema([
    pa.field("claim_id",        pa.string()),
    pa.field("policy_id",       pa.string()),
    pa.field("customer_id",     pa.string()),
    pa.field("incident_date",   pa.date32()),
    pa.field("report_date",     pa.date32()),
    pa.field("incident_city",   pa.string()),
    pa.field("incident_state",  pa.string()),
    pa.field("incident_zip",    pa.string()),
    pa.field("incident_type",   pa.string()),
    pa.field("description",     pa.string()),
    pa.field("status",          pa.string()),
    pa.field("claim_amount",    pa.decimal128(18, 2)),
    pa.field("approved_amount", pa.decimal128(18, 2)),
    pa.field("created_at",      pa.timestamp("us", tz="UTC")),
])

PAYMENTS_SCHEMA = pa.schema([
    pa.field("payment_id",        pa.string()),
    pa.field("claim_id",          pa.string()),
    pa.field("adjuster_id",       pa.string()),
    pa.field("payment_amount",    pa.decimal128(18, 2)),
    pa.field("payment_type",      pa.string()),
    pa.field("payment_timestamp", pa.timestamp("us", tz="UTC")),
])
