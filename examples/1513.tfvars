aws_region  = "us-east-1"
name_prefix = "cloudtrail-loki"

environments = {
  "1513" = {
    cloudtrail_bucket_name      = "<cloudtrail-bucket-1513>"
    cloudtrail_prefix           = "AWSLogs/1513/CloudTrail/"
    loki_url                    = "https://<onprem-loki-fqdn>"
    loki_username_secret_arn    = "arn:aws:secretsmanager:us-east-1:222222222222:secret:loki/username-1513"
    loki_password_secret_arn    = "arn:aws:secretsmanager:us-east-1:222222222222:secret:loki/password-encrypted-1513"
    ansible_vault_password_arn  = "arn:aws:secretsmanager:us-east-1:222222222222:secret:vault/password-1513"
    loki_ca_cert_secret_arn     = "arn:aws:secretsmanager:us-east-1:222222222222:secret:loki/ca-cert-1513"
  }
}
