import sys
import os

# Make extractors/ the root so shared, supabase_to_s3, gdrive_to_s3 are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase_to_s3 import pipeline as supabase_pipeline
from gdrive_to_s3 import pipeline as gdrive_pipeline

if __name__ == "__main__":
    print("=" * 54)
    print("  PIPELINE 1: Supabase → S3 (parquet)")
    print("=" * 54)
    supabase_pipeline.run()

    print()
    print("=" * 54)
    print("  PIPELINE 2: Google Drive → S3 (json)")
    print("=" * 54)
    gdrive_pipeline.run()
