import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "extractors"))

from shared.config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET, S3_PREFIX

PROCESSED_PREFIX = "processed/"

# Each entry defines how a landed table should be cleaned.
TABLE_TRANSFORMS = {
    "agents": {
        "landing_source": "policy_admin",
        "landing_name":   "agents",
        "output_name":    "agents",
        "pk":             ["agent_id"],
        "date_fields":    ["hire_date"],
        "money_fields":   [],
        "upper_fields":   ["territory"],
        "title_fields":   ["agent_name"],
        "lower_fields":   [],
    },
    "coverages": {
        "landing_source": "policy_admin",
        "landing_name":   "coverages",
        "output_name":    "coverages",
        "pk":             ["coverage_id"],
        "date_fields":    [],
        "money_fields":   ["coverage_limit", "deductible"],
        "upper_fields":   ["coverage_code"],
        "title_fields":   [],
        "lower_fields":   [],
    },
    "customers": {
        "landing_source": "policy_admin",
        "landing_name":   "customers",
        "output_name":    "customers",
        "pk":             ["customer_id"],
        "date_fields":    ["dob"],
        "money_fields":   [],
        "upper_fields":   ["state"],
        "title_fields":   ["first_name", "last_name", "city"],
        "lower_fields":   ["email"],
    },
    "policies": {
        "landing_source": "policy_admin",
        "landing_name":   "policies",
        "output_name":    "policies",
        "pk":             ["policy_id"],
        "date_fields":    ["start_date", "end_date"],
        "money_fields":   ["premium_amount"],
        "upper_fields":   ["status", "coverage_type"],
        "title_fields":   [],
        "lower_fields":   [],
    },
    "weather": {
        "landing_source": "meteo_weather",
        "landing_name":   "meteo-weather",
        "output_name":    "weather_daily",
        "pk":             ["weather_date", "zip_code"],
        "date_fields":    [],           # already date32 in source
        "money_fields":   [],
        "upper_fields":   ["state"],
        "title_fields":   ["city", "severity"],
        "lower_fields":   [],
    },
}
