import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase_to_s3 import pipeline as supabase_pipeline
from gdrive_to_s3 import pipeline as gdrive_pipeline
from gdrive_csv_to_s3 import pipeline as billing_pipeline
from local_to_s3 import pipeline as local_pipeline

if __name__ == "__main__":
    print("supabase → s3")
    supabase_pipeline.run()

    print("\ngdrive → s3")
    gdrive_pipeline.run()

    print("\ngdrive csv → s3")
    billing_pipeline.run()

    print("\nlocal → s3")
    local_pipeline.run()
