terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4"
    }
  }

  backend "s3" {
    # Configure in backend.hcl per environment.
    # bucket = "<tf-state-bucket>"
    # key    = "cloudtrail-loki/terraform.tfstate"
    # region = "<region>"
  }
}
