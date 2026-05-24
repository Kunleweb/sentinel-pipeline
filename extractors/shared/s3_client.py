import boto3
from botocore.exceptions import NoCredentialsError, NoRegionError

from shared.config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def get_s3_client():
    try:
        client = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        client.list_buckets()
        return client
    except NoCredentialsError as exc:
        raise RuntimeError("No AWS credentials found.") from exc
    except NoRegionError as exc:
        raise RuntimeError(f"AWS region not set. Check shared/config.py") from exc
