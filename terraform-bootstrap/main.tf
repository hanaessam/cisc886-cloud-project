terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# ── S3 Bucket for Terraform State ─────────────────────────────────────────────
resource "aws_s3_bucket" "tf_state" {
  bucket        = "cisc886-terraform-state"
  force_destroy = false   # safety: prevents accidental deletion of state

  tags = {
    Name    = "cisc886-terraform-state"
    Project = "cisc886-cloud-project"
    Purpose = "Terraform remote state storage"
  }
}

# Block all public access — state files contain sensitive infrastructure details
resource "aws_s3_bucket_public_access_block" "tf_state" {
  bucket                  = aws_s3_bucket.tf_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning — lets you recover a previous state if something goes wrong
resource "aws_s3_bucket_versioning" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Encryption — state files can contain secrets
resource "aws_s3_bucket_server_side_encryption_configuration" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ── DynamoDB Table for State Locking ──────────────────────────────────────────
# Prevents two people from running terraform apply at the same time
resource "aws_dynamodb_table" "tf_lock" {
  name         = "cisc886-terraform-lock"
  billing_mode = "PAY_PER_REQUEST"   # no upfront cost, charged per request
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name    = "cisc886-terraform-lock"
    Project = "cisc886-cloud-project"
    Purpose = "Terraform state locking"
  }
}