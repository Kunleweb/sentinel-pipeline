import json
import boto3
from botocore.exceptions import ClientError

from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, SECRETS_MANAGER_SECRET_NAME


def get_db_credentials() -> dict:
    client = boto3.client(
        "secretsmanager",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    try:
        response = client.get_secret_value(SecretId=SECRETS_MANAGER_SECRET_NAME)
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        raise RuntimeError(
            f"Could not retrieve secret '{SECRETS_MANAGER_SECRET_NAME}': {error_code}"
        ) from exc

    return json.loads(response["SecretString"])
