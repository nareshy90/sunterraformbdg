variable "name_prefix" { type = string }
variable "lambda_role_arn" { type = string }
variable "source_dir" { type = string }
variable "cloudtrail_bucket_name" { type = string }
variable "create_s3_notification" { type = bool }
variable "s3_event_prefix_filter" { type = string }
variable "s3_event_suffix_filter" { type = string }
variable "memory_size" { type = number }
variable "timeout_seconds" { type = number }
variable "reserved_concurrency" { type = number }
variable "log_retention_days" { type = number }
variable "environment_variables" {
  type      = map(string)
  sensitive = true
}
variable "dead_letter_target_arn" {
  type    = string
  default = null
}
variable "vpc_subnet_ids" {
  type    = list(string)
  default = []
}
variable "vpc_security_group_ids" {
  type    = list(string)
  default = []
}
variable "tags" {
  type    = map(string)
  default = {}
}
