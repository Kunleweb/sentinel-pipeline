import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "extractors"))
sys.path.insert(0, os.path.join(ROOT, "transforms"))

from supabase_to_s3 import pipeline as supabase_pipeline
from gdrive_to_s3 import pipeline as gdrive_pipeline
from gdrive_csv_to_s3 import pipeline as billing_pipeline
from local_to_s3 import pipeline as local_pipeline
from policy_admin.pipeline import run as run_policy_admin
from claims.pipeline import run as run_claims
from loaders.load_warehouse import run as run_warehouse


def _summary(results: dict) -> None:
    u, s, e = len(results["uploaded"]), len(results["skipped"]), len(results["errors"])
    print(f"  {u} uploaded, {s} skipped, {e} errors")
    for name in results["errors"]:
        print(f"  error: {name}")


if __name__ == "__main__":
    print("extract: supabase → s3")
    supabase_pipeline.run()

    print("\nextract: gdrive → s3")
    gdrive_pipeline.run()

    print("\nextract: gdrive csv → s3")
    billing_pipeline.run()

    print("\nextract: local → s3")
    local_pipeline.run()

    print("\ntransform: policy admin → processed")
    _summary(run_policy_admin())

    print("\ntransform: claims → processed")
    _summary(run_claims())

    print("\nload: processed → snowflake")
    run_warehouse()
