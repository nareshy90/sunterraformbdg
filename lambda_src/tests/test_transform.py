import gzip
import io
import json
import os
import sys
import types
import unittest
from unittest.mock import Mock, patch

# Stub external modules unavailable in this environment before importing handler.
if "boto3" not in sys.modules:
    fake_boto3 = types.ModuleType("boto3")
    fake_boto3.client = Mock(return_value=Mock())
    sys.modules["boto3"] = fake_boto3

if "requests" not in sys.modules:
    fake_requests = types.ModuleType("requests")
    fake_requests.RequestException = Exception
    fake_requests.post = Mock()
    auth_mod = types.ModuleType("auth")

    class HTTPBasicAuth:  # pylint: disable=too-few-public-methods
        def __init__(self, username, password):
            self.username = username
            self.password = password

    auth_mod.HTTPBasicAuth = HTTPBasicAuth
    fake_requests.auth = auth_mod
    sys.modules["requests"] = fake_requests
    sys.modules["requests.auth"] = auth_mod

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import handler


class TestLambdaPromtail(unittest.TestCase):
    def test_to_loki_streams_builds_labels(self):
        records = [
            {
                "recipientAccountId": "123456789012",
                "eventSource": "ec2.amazonaws.com",
                "eventName": "RunInstances",
                "awsRegion": "us-east-1",
            }
        ]
        payload = handler._to_loki_streams(records, "1517")

        self.assertEqual(len(payload["streams"]), 1)
        stream = payload["streams"][0]["stream"]
        self.assertEqual(stream["environment"], "1517")
        self.assertEqual(stream["aws_account_id"], "123456789012")

    def test_load_cloudtrail_records_from_gzip(self):
        body = {"Records": [{"eventName": "ConsoleLogin"}]}
        compressed = gzip.compress(json.dumps(body).encode("utf-8"))

        with patch.object(handler.S3_CLIENT, "get_object", return_value={"Body": io.BytesIO(compressed)}):
            records = handler._load_cloudtrail_records("bucket", "key.json.gz")

        self.assertEqual(records[0]["eventName"], "ConsoleLogin")

    def test_lambda_handler_synthetic_event(self):
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-cloudtrail-bucket"},
                        "object": {"key": "AWSLogs/1517/CloudTrail/us-east-1/example.json.gz"},
                    }
                }
            ]
        }

        env = {
            "ENVIRONMENT_ID": "1517",
            "LOKI_URL": "https://loki.example.internal",
            "LOKI_USERNAME_SECRET_ARN": "arn:username",
            "LOKI_PASSWORD_SECRET_ARN": "arn:encpass",
            "ANSIBLE_VAULT_PASSWORD_ARN": "arn:vaultpass",
            "LOKI_CA_CERT_SECRET_ARN": "arn:cacert",
        }

        secret_map = {
            "arn:username": "loki-user",
            "arn:encpass": "$ANSIBLE_VAULT;1.1;AES256\n...",
            "arn:vaultpass": "vault-pass",
            "arn:cacert": "-----BEGIN CERTIFICATE-----\nMIIB\n-----END CERTIFICATE-----",
        }

        with patch.dict(os.environ, env, clear=True), patch.object(
            handler, "_get_secret", side_effect=lambda arn: secret_map[arn]
        ), patch.object(handler, "_decrypt_ansible_vault", return_value="loki-password"), patch.object(
            handler, "_load_cloudtrail_records", return_value=[{"eventName": "ConsoleLogin"}]
        ), patch.object(handler, "_post_to_loki") as mock_post:
            result = handler.lambda_handler(event, None)

        self.assertEqual(result, {"processed": 1, "failed": 0})
        self.assertEqual(mock_post.call_count, 1)


if __name__ == "__main__":
    unittest.main()
