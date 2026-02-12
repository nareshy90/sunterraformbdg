variable "aws_region" {
  description = "AWS region where resources are deployed."
  type        = string
}

variable "name_prefix" {
  description = "Prefix for all generated resources."
  type        = string
  default     = "cloudtrail-loki"
}

variable "default_tags" {
  description = "Default tags applied to all resources."
  type        = map(string)
  default     = {}
}

variable "environments" {
  description = "Map of environment configurations keyed by environment ID (e.g., 1517, 1513, 1512)."
  type = map(object({
    enabled                       = optional(bool, true)
    cloudtrail_bucket_name        = string
    cloudtrail_prefix             = optional(string, "AWSLogs/")
    loki_url                      = string
    loki_username_secret_arn      = string
    loki_password_secret_arn      = string
    ansible_vault_password_arn    = string
    loki_ca_cert_secret_arn       = string
    secret_kms_key_arns           = optional(list(string), [])
    memory_size                   = optional(number, 512)
    timeout_seconds               = optional(number, 300)
    reserved_concurrency          = optional(number, 2)
    log_retention_days            = optional(number, 30)
    create_s3_notification        = optional(bool, true)
    s3_event_prefix_filter        = optional(string, "")
    s3_event_suffix_filter        = optional(string, ".json.gz")
    dead_letter_target_arn        = optional(string)
    vpc_subnet_ids                = optional(list(string), [])
    vpc_security_group_ids        = optional(list(string), [])
  }))

  validation {
    condition = alltrue([
      for env in values(var.environments) : startswith(env.loki_url, "https://")
    ])
    error_message = "All loki_url values must start with https://."
  }
}
