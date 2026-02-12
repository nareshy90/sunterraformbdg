from handler import _to_loki_streams


def test_to_loki_streams_builds_labels():
    records = [{"recipientAccountId": "123456789012", "eventSource": "ec2.amazonaws.com", "eventName": "RunInstances", "awsRegion": "us-east-1"}]
    payload = _to_loki_streams(records, "1517")

    assert len(payload["streams"]) == 1
    stream = payload["streams"][0]["stream"]
    assert stream["environment"] == "1517"
    assert stream["aws_account_id"] == "123456789012"
