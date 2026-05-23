import boto3
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

# List all buckets visible to this user
print("Buckets visible to this user:")
try:
    for b in s3.list_buckets()["Buckets"]:
        print(" -", b["Name"])
except Exception as e:
    print(" ERROR:", e)

# Check the bucket region
print(f"\nChecking region of bucket '{S3_BUCKET}':")
try:
    loc = s3.get_bucket_location(Bucket=S3_BUCKET)
    print(" Region:", loc["LocationConstraint"] or "us-east-1")
except Exception as e:
    print(" ERROR:", e)

# Test write access
print(f"\nTesting PutObject on '{S3_BUCKET}':")
try:
    s3.put_object(Bucket=S3_BUCKET, Key="debug-test.txt", Body=b"test")
    print(" SUCCESS — write access confirmed")
    s3.delete_object(Bucket=S3_BUCKET, Key="debug-test.txt")
except Exception as e:
    print(" ERROR:", e)
