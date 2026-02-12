# Enhanced Prompt: Enterprise Terraform Modules for CloudTrail → Lambda Promtail → On-Prem Loki

You are a senior platform engineer. Generate **enterprise-grade, reusable Terraform code** to deploy AWS infrastructure and Lambda code for shipping CloudTrail logs from S3 (`.json.gz`) to an on-prem Grafana Loki endpoint.

## Primary Goal
Build a generic Terraform solution with modules for:
1. `lambda-promtail` (Lambda function + packaging + event source integration)
2. `lambda-iam` (least-privilege IAM role/policies for Lambda)

The solution must support **multiple AWS environments/accounts** with environment-specific configuration and secrets.

---

## Business & Technical Context
- CloudTrail logs are stored in S3 as `.json.gz` files (daily/monthly partitions).
- Lambda must consume new CloudTrail objects and push logs to on-prem Loki.
- Loki requires:
  - username
  - password
  - internal root CA certificate for TLS trust
- Sensitive values handling:
  - Loki password is encrypted with Ansible Vault.
  - Ansible Vault password is stored in AWS Secrets Manager.
  - Lambda must retrieve vault password + encrypted Loki password and decrypt at runtime.
  - Do not leak secrets into logs, Terraform state, plan output, or environment variables unnecessarily.

---

## Multi-Environment Requirements
Support 3 environments/accounts (placeholder names are fine):
- `1517`
- `1513`
- `1512`

Create reusable maps/objects for environment-specific settings, including placeholders for:
- CloudTrail S3 bucket name
- Secret names/ARNs:
  - Ansible Vault password secret
  - Encrypted Loki password secret (or encrypted value source)
  - Loki root CA cert secret
- Optional Loki URL overrides per environment

Use a **single codebase** with `for_each` / maps / locals to avoid duplication.

---

## Required Deliverables
Generate all code needed with clear file structure:

1. **Root Terraform configuration**
   - Provider configuration
   - Backend placeholder
   - Variable definitions
   - Environment map and tfvars examples
   - Module instantiation for each environment

2. **Module: `modules/lambda-iam`**
   - IAM role for Lambda
   - Least privilege policy statements for:
     - CloudWatch Logs write
     - S3 read for CloudTrail bucket prefix (scoped)
     - Secrets Manager read for only required secrets
     - KMS decrypt if required by secrets
   - Trust policy for Lambda service

3. **Module: `modules/lambda-promtail`**
   - Lambda function resource
   - Runtime, memory, timeout, ephemeral storage settings
   - Environment variables (non-sensitive only)
   - Dead letter / failure handling option (SQS or on-failure destination)
   - CloudWatch log retention configuration
   - S3 event notification wiring (or optional EventBridge alternative)
   - Concurrency controls and retry behavior

4. **Lambda application code skeleton** (Python preferred)
   - Triggered by S3 object create events
   - Downloads `.json.gz`, decompresses, parses CloudTrail JSON records
   - Converts to Loki stream format with labels
   - Retrieves secrets at runtime from Secrets Manager
   - Uses vault password to decrypt encrypted Loki password in-memory
   - Uses CA cert for TLS verification when posting to Loki
   - Implements robust retry/backoff and timeout handling
   - Implements structured logging with secret redaction
   - Idempotency-safe behavior where possible

5. **Security hardening**
   - No plain-text secret outputs
   - `sensitive = true` where relevant
   - Validate input variables
   - Optional VPC config for private routing to on-prem endpoint
   - Explicit note of risks and mitigations

6. **Operational excellence**
   - README with architecture diagram (ASCII acceptable)
   - Deployment steps
   - Rollback guidance
   - Monitoring/alert recommendations
   - Cost considerations

7. **Validation**
   - `terraform fmt`, `validate`, and example `plan` commands
   - Optional unit test placeholders for Lambda parser/transform logic

---

## Non-Functional Requirements
- Follow Terraform module best practices and naming conventions.
- Keep modules generic and composable.
- Avoid hardcoding account IDs, bucket names, secret ARNs, endpoints.
- Minimize blast radius with least privilege.
- Keep code production-ready, readable, and documented.

---

## Output Format
Provide output in this order:
1. Proposed repository tree
2. Terraform code per file
3. Lambda code per file
4. Example `terraform.tfvars` for each environment (`1517`, `1513`, `1512`) with placeholders
5. README and runbook
6. Security checklist
7. Future enhancements

If any assumption is made, list it explicitly before the code.
