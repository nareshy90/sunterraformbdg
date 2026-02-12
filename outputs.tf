output "lambda_function_arns" {
  description = "Lambda ARNs by environment."
  value = {
    for env, mod in module.lambda_promtail : env => mod.lambda_function_arn
  }
}

output "lambda_role_arns" {
  description = "IAM role ARNs by environment."
  value = {
    for env, mod in module.lambda_iam : env => mod.role_arn
  }
}
