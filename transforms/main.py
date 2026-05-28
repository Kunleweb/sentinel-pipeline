import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from runner import run_all

if __name__ == "__main__":
    print("=" * 54)
    print("  TRANSFORMS: Landing → Processed")
    print("=" * 54)

    results = run_all()

    print("\nSummary")
    for uri in results["uploaded"]:
        print(f"  uploaded  {uri}")
    for uri in results["skipped"]:
        print(f"  skipped   {uri}")
    for name in results["errors"]:
        print(f"  ERROR     {name} — no landing data found")
    print(f"\n  {len(results['uploaded'])} uploaded, "
          f"{len(results['skipped'])} skipped, "
          f"{len(results['errors'])} errors.")
    print(".")
