provider "aws" {
  region = var.aws_region
}

locals {
  active_environments = {
    for env_id, cfg in var.environments : env_id => cfg
    if try(cfg.enabled, true)
  }
}

module "lambda_iam" {
  for_each = local.active_environments
  source   = "./modules/lambda-iam"

  name_prefix                 = "${var.name_prefix}-${each.key}"
  cloudtrail_bucket_name      = each.value.cloudtrail_bucket_name
  cloudtrail_prefix           = each.value.cloudtrail_prefix
  loki_username_secret_arn    = each.value.loki_username_secret_arn
  loki_password_secret_arn    = each.value.loki_password_secret_arn
  ansible_vault_password_arn  = each.value.ansible_vault_password_arn
  loki_ca_cert_secret_arn     = each.value.loki_ca_cert_secret_arn
  secret_kms_key_arns         = each.value.secret_kms_key_arns
  tags                        = merge(var.default_tags, { "environment" = each.key })
}

module "lambda_promtail" {
  for_each = local.active_environments
  source   = "./modules/lambda-promtail"

  name_prefix               = "${var.name_prefix}-${each.key}"
  lambda_role_arn           = module.lambda_iam[each.key].role_arn
  source_dir                = "${path.root}/lambda_src"
  cloudtrail_bucket_name    = each.value.cloudtrail_bucket_name
  create_s3_notification    = each.value.create_s3_notification
  s3_event_prefix_filter    = each.value.s3_event_prefix_filter
  s3_event_suffix_filter    = each.value.s3_event_suffix_filter
  memory_size               = each.value.memory_size
  timeout_seconds           = each.value.timeout_seconds
  reserved_concurrency      = each.value.reserved_concurrency
  log_retention_days        = each.value.log_retention_days
  dead_letter_target_arn    = try(each.value.dead_letter_target_arn, null)
  vpc_subnet_ids            = each.value.vpc_subnet_ids
  vpc_security_group_ids    = each.value.vpc_security_group_ids

  environment_variables = {
    ENVIRONMENT_ID               = each.key
    LOKI_URL                     = each.value.loki_url
    LOKI_USERNAME_SECRET_ARN     = each.value.loki_username_secret_arn
    LOKI_PASSWORD_SECRET_ARN     = each.value.loki_password_secret_arn
    ANSIBLE_VAULT_PASSWORD_ARN   = each.value.ansible_vault_password_arn
    LOKI_CA_CERT_SECRET_ARN      = each.value.loki_ca_cert_secret_arn
    LOG_LEVEL                    = "INFO"
  }

  tags = merge(var.default_tags, { "environment" = each.key })
}
