variable "name_prefix" { type = string }
variable "cloudtrail_bucket_name" { type = string }
variable "cloudtrail_prefix" { type = string }
variable "loki_username_secret_arn" { type = string }
variable "loki_password_secret_arn" { type = string }
variable "ansible_vault_password_arn" { type = string }
variable "loki_ca_cert_secret_arn" { type = string }
variable "secret_kms_key_arns" {
  type    = list(string)
  default = []
}
variable "tags" {
  type    = map(string)
  default = {}
}
