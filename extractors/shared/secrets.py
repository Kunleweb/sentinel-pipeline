import json
import boto3
from botocore.exceptions import ClientError

from shared.config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def get_secret(secret_name: str) -> dict:
    client = boto3.client(
        "secretsmanager",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        raise RuntimeError(
            f"Could not retrieve secret '{secret_name}': {error_code}"
        ) from exc
    return json.loads(response["SecretString"])
