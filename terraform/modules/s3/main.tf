# ── 1. S3 Bucket ──────────────────────────────────────────────────────────────
resource "aws_s3_bucket" "main" {
  bucket        = var.s3_bucket_name
  force_destroy = true

  tags = {
    Name  = var.s3_bucket_name
    Owner = var.prefix
  }
}

# ── 2. Block all public access ────────────────────────────────────────────────
resource "aws_s3_bucket_public_access_block" "main" {
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ── 3. Versioning ─────────────────────────────────────────────────────────────
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ── 4. Server-side encryption ─────────────────────────────────────────────────
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ── 5. Folder placeholders ────────────────────────────────────────────────────
resource "aws_s3_object" "raw_data" {
  bucket  = aws_s3_bucket.main.id
  key     = "raw-data/"
  content = ""
}

resource "aws_s3_object" "processed" {
  bucket  = aws_s3_bucket.main.id
  key     = "processed/"
  content = ""
}

resource "aws_s3_object" "model" {
  bucket  = aws_s3_bucket.main.id
  key     = "model/"
  content = ""
}

resource "aws_s3_object" "scripts" {
  bucket  = aws_s3_bucket.main.id
  key     = "scripts/"
  content = ""
}

resource "aws_s3_object" "emr_logs" {
  bucket  = aws_s3_bucket.main.id
  key     = "emr-logs/"
  content = ""
}

# ── 6. Upload PySpark script ──────────────────────────────────────────────────
resource "aws_s3_object" "preprocess_script" {
  bucket = aws_s3_bucket.main.id
  key    = "scripts/preprocess.py"
  source = "${path.root}/../scripts/emr/preprocess.py"
  etag   = filemd5("${path.root}/../scripts/emr/preprocess.py")
}
