from gdrive_to_s3.config import SOURCE_PARTITION
from gdrive_to_s3.client import get_gdrive_service
from gdrive_to_s3.extractor import list_all_json_files, download_file
from shared.s3_client import get_s3_client
from shared.s3_storage import upload_json_file


def run():
    print("Step 1/4  Connecting to Google Drive...")
    service = get_gdrive_service()

    print("Step 2/4  Establishing S3 connection...")
    s3 = get_s3_client()

    print("Step 3/4  Listing JSON files across day partitions...")
    files = list_all_json_files(service)
    print(f"          Found {len(files)} file(s) across all day folders\n")

    print("Step 4/4  Uploading to S3...\n")
    uploaded, skipped = [], []
    for f in files:
        label = f"{f['day']}/{f['table_name']}"
        print(f"  [{label}] checking S3...")
        uri, exists = upload_json_file(s3, SOURCE_PARTITION, f["table_name"], None, day=f["day"])
        if exists:
            skipped.append(uri)
            print(f"  [{label}] skipped — already exists")
        else:
            print(f"  [{label}] downloading...")
            content = download_file(service, f["id"])
            uri, _ = upload_json_file(s3, SOURCE_PARTITION, f["table_name"], content, day=f["day"])
            uploaded.append(uri)
            print(f"  [{label}] uploaded → {uri}")

    print("\n── Verification ──────────────────────────────────────")
    for uri in uploaded:
        print(f"  uploaded  {uri}")
    for uri in skipped:
        print(f"  skipped   {uri}")
    print(f"\n  {len(uploaded)} uploaded, {len(skipped)} skipped.")
    print("──────────────────────────────────────────────────────")
