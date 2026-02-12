# CloudTrail S3 to On-Prem Loki (Lambda Promtail) Terraform

## Architecture

```text
CloudTrail -> S3 (.json.gz) -> S3 Event -> Lambda (promtail adapter)
                                            |-> Secrets Manager (username, encrypted password, vault pass, CA cert)
                                            |-> decrypt ansible-vault secret in-memory
                                            |-> HTTPS push to on-prem Loki
```

## Repository Tree

- `main.tf`, `variables.tf`, `versions.tf`, `outputs.tf`: root orchestration.
- `modules/lambda-iam`: least-privilege IAM role/policy.
- `modules/lambda-promtail`: Lambda function, logging, and S3 trigger integration.
- `lambda_src`: Python Lambda handler and test scaffold.
- `examples`: per-environment tfvars placeholders (`1517`, `1513`, `1512`).

## Deployment

1. Configure backend in `backend.hcl`.
2. Select or prepare the environment tfvars in `examples/`.
3. Package dependencies for Lambda (for production, build a zip/layer with dependencies).
4. Deploy:

```bash
terraform init -backend-config=backend.hcl
terraform fmt -recursive
terraform validate
terraform plan -var-file=examples/1517.tfvars
terraform apply -var-file=examples/1517.tfvars
```

## Rollback

- Revert to prior git tag/commit and run `terraform apply`.
- For emergency stop, set `enabled = false` for environment and apply.

## Monitoring and Alerts

- CloudWatch metric filters on Lambda errors/timeouts.
- Alarms on `Errors`, `Throttles`, and high `Duration`.
- Alarm on DLQ depth if using DLQ target.

## Security Notes

- Secret values are fetched at runtime from Secrets Manager.
- Terraform only stores ARNs, not secret plaintext.
- Encrypted Loki password is decrypted in memory only.
- CA cert is loaded from Secrets Manager and written to temp file for TLS verify.

## Cost Considerations

- Main cost drivers: Lambda invocations + duration, CloudWatch logs, Secrets Manager API calls.
- Tune memory/timeout/concurrency per environment.

## Assumptions

- Encrypted Loki password follows ansible-vault format and can be decrypted by ansible-core runtime.
- On-prem Loki is reachable from Lambda network path (public TLS endpoint or private via VPC).
- Bucket notifications are not managed elsewhere (or set `create_s3_notification = false`).
