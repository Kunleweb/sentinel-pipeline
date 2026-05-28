import _bootstrap  # noqa: F401

from policy_admin.pipeline import run as run_policy_admin
from claims.pipeline import run as run_claims


def _print_results(results: dict) -> None:
    for uri in results["uploaded"]:
        print(f"  uploaded  {uri}")
    for uri in results["skipped"]:
        print(f"  skipped   {uri}")
    for name in results["errors"]:
        print(f"  error     {name} — no landing data found")
    u, s, e = len(results["uploaded"]), len(results["skipped"]), len(results["errors"])
    print(f"\n  {u} uploaded, {s} skipped, {e} errors")


if __name__ == "__main__":
    print("policy admin → processed")
    _print_results(run_policy_admin())

    print("\nclaims → processed")
    _print_results(run_claims())
