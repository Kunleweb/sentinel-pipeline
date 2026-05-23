"""
Establishes and returns a boto3 S3 client.
Authentication is handled by the AWS credential chain:
  1. IAM role attached to the compute (EC2 / Lambda / ECS) — preferred in production
  2. AWS SSO / named profile for local runs  (aws configure sso)
  3. Explicit access keys — least preferred, avoid if possible
No credentials are passed explicitly; boto3 resolves them automatically.
"""

import boto3
from botocore.exceptions import NoCredentialsError, NoRegionError

from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def get_s3_client():
    """Return a boto3 S3 client for AWS_REGION."""
    try:
        client = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        # Lightweight check — confirms credentials are valid before any real work
        client.list_buckets()
        return client
    except NoCredentialsError as exc:
        raise RuntimeError(
            "No AWS credentials found. "
            "Attach an IAM role to your compute, or run `aws configure sso` locally."
        ) from exc
    except NoRegionError as exc:
        raise RuntimeError(
            f"AWS region not set. Check AWS_REGION in config.py (currently: {AWS_REGION!r})"
        ) from exc
