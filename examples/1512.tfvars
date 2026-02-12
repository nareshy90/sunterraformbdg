aws_region  = "us-east-1"
name_prefix = "cloudtrail-loki"

environments = {
  "1512" = {
    cloudtrail_bucket_name      = "<cloudtrail-bucket-1512>"
    cloudtrail_prefix           = "AWSLogs/1512/CloudTrail/"
    loki_url                    = "https://<onprem-loki-fqdn>"
    loki_username_secret_arn    = "arn:aws:secretsmanager:us-east-1:333333333333:secret:loki/username-1512"
    loki_password_secret_arn    = "arn:aws:secretsmanager:us-east-1:333333333333:secret:loki/password-encrypted-1512"
    ansible_vault_password_arn  = "arn:aws:secretsmanager:us-east-1:333333333333:secret:vault/password-1512"
    loki_ca_cert_secret_arn     = "arn:aws:secretsmanager:us-east-1:333333333333:secret:loki/ca-cert-1512"
  }
}
