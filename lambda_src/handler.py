import base64
import gzip
import json
import logging
import os
import tempfile
import time
from typing import Dict, List, Optional
from urllib.parse import unquote_plus

import boto3
import requests
from requests.auth import HTTPBasicAuth

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))

SECRETS_CLIENT = boto3.client("secretsmanager")
S3_CLIENT = boto3.client("s3")


def _get_secret(secret_arn: str) -> str:
    response = SECRETS_CLIENT.get_secret_value(SecretId=secret_arn)
    if "SecretString" in response:
        return response["SecretString"]
    return base64.b64decode(response["SecretBinary"]).decode("utf-8")


def _decrypt_ansible_vault(cipher_text: str, vault_password: str) -> str:
    """
    Decrypt ansible-vault encrypted text in-memory.
    Requires ansible-core dependency packaged with the Lambda artifact.
    """
    from ansible.parsing.vault import VaultLib, VaultSecret

    vault = VaultLib([("default", VaultSecret(vault_password.encode("utf-8")))])
    return vault.decrypt(cipher_text.encode("utf-8")).decode("utf-8")


def _load_cloudtrail_records(bucket: str, key: str) -> List[Dict]:
    response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
    raw_bytes = response["Body"].read()
    payload = gzip.decompress(raw_bytes).decode("utf-8")
    document = json.loads(payload)
    return document.get("Records", [])


def _to_loki_streams(records: List[Dict], environment_id: str) -> Dict:
    streams = []
    now_ns = str(int(time.time() * 1_000_000_000))
    for record in records:
        labels = {
            "job": "cloudtrail",
            "environment": environment_id,
            "aws_account_id": str(record.get("recipientAccountId", "unknown")),
            "event_source": str(record.get("eventSource", "unknown")),
            "event_name": str(record.get("eventName", "unknown")),
            "aws_region": str(record.get("awsRegion", "unknown")),
        }
        streams.append({"stream": labels, "values": [[now_ns, json.dumps(record, separators=(",", ":"))]]})
    return {"streams": streams}


def _post_to_loki(
    loki_url: str,
    username: str,
    password: str,
    ca_cert_pem: str,
    payload: Dict,
    max_attempts: int = 3,
) -> None:
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as cert_file:
        cert_file.write(ca_cert_pem)
        cert_path = cert_file.name

    try:
        backoff_seconds = 1
        last_exc: Optional[Exception] = None

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(
                    f"{loki_url.rstrip('/')}/loki/api/v1/push",
                    auth=HTTPBasicAuth(username, password),
                    json=payload,
                    verify=cert_path,
                    timeout=(3.05, 15),
                )
                response.raise_for_status()
                return
            except requests.RequestException as exc:
                last_exc = exc
                if attempt == max_attempts:
                    break
                LOGGER.warning(
                    "Loki push failed, retrying",
                    extra={"attempt": attempt, "next_backoff_seconds": backoff_seconds},
                )
                time.sleep(backoff_seconds)
                backoff_seconds *= 2

        raise RuntimeError("Failed to push log payload to Loki") from last_exc
    finally:
        os.remove(cert_path)


def lambda_handler(event, context):
    environment_id = os.environ["ENVIRONMENT_ID"]
    loki_url = os.environ["LOKI_URL"]

    loki_username = _get_secret(os.environ["LOKI_USERNAME_SECRET_ARN"])
    encrypted_loki_password = _get_secret(os.environ["LOKI_PASSWORD_SECRET_ARN"])
    vault_password = _get_secret(os.environ["ANSIBLE_VAULT_PASSWORD_ARN"])
    ca_cert_pem = _get_secret(os.environ["LOKI_CA_CERT_SECRET_ARN"])

    loki_password = _decrypt_ansible_vault(encrypted_loki_password, vault_password)

    successful = 0
    failed = 0

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        if not key.endswith(".json.gz"):
            LOGGER.info("Skipping non-CloudTrail object", extra={"bucket": bucket, "key": key})
            continue

        try:
            cloudtrail_records = _load_cloudtrail_records(bucket, key)
            payload = _to_loki_streams(cloudtrail_records, environment_id)
            if payload["streams"]:
                _post_to_loki(loki_url, loki_username, loki_password, ca_cert_pem, payload)
            successful += 1
            LOGGER.info(
                "Processed CloudTrail object",
                extra={"bucket": bucket, "key": key, "record_count": len(cloudtrail_records)},
            )
        except Exception as exc:  # noqa: BLE001
            failed += 1
            LOGGER.exception(
                "Failed to process CloudTrail object",
                extra={"bucket": bucket, "key": key, "error_type": type(exc).__name__},
            )

    return {
        "processed": successful,
        "failed": failed,
    }
