aws_region  = "us-east-1"
name_prefix = "cloudtrail-loki"

default_tags = {
  owner   = "platform"
  service = "cloudtrail-loki"
}

environments = {
  "1517" = {
    cloudtrail_bucket_name      = "<cloudtrail-bucket-1517>"
    cloudtrail_prefix           = "AWSLogs/1517/CloudTrail/"
    loki_url                    = "https://<onprem-loki-fqdn>"
    loki_username_secret_arn    = "arn:aws:secretsmanager:us-east-1:111111111111:secret:loki/username-1517"
    loki_password_secret_arn    = "arn:aws:secretsmanager:us-east-1:111111111111:secret:loki/password-encrypted-1517"
    ansible_vault_password_arn  = "arn:aws:secretsmanager:us-east-1:111111111111:secret:vault/password-1517"
    loki_ca_cert_secret_arn     = "arn:aws:secretsmanager:us-east-1:111111111111:secret:loki/ca-cert-1517"
    secret_kms_key_arns         = ["arn:aws:kms:us-east-1:111111111111:key/<kms-key-id>"]
  }
}
