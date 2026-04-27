# ── Region ────────────────────────────────────────────────────────────────────
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

# ── Naming ────────────────────────────────────────────────────────────────────
variable "prefix" {
  description = "Prefix applied to every resource name"
  type        = string
}

# ── Networking ────────────────────────────────────────────────────────────────
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "availability_zone" {
  description = "Availability zone for subnets"
  type        = string
  default     = "us-east-1a"
}

# ── EC2 ───────────────────────────────────────────────────────────────────────
variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.large"
}

variable "ec2_key_name" {
  description = "Name of existing EC2 key pair for SSH"
  type        = string
}

variable "my_ip" {
  description = "Your public IP for SSH access — format: x.x.x.x/32"
  type        = string
}

# ── Networking inputs  ─────────────────────────────────
variable "vpc_id" {
  description = "VPC ID — output from Person 1 terraform apply"
  type        = string
}

variable "private_subnet_id" {
  description = "Private subnet ID — output from Person 1 terraform apply"
  type        = string
}

variable "private_route_table_id" {
  description = "Private route table ID — output from Person 1 terraform apply"
  type        = string
}

# ──  S3 ──────────────────────────────────────────────────────────────
variable "s3_bucket_name" {
  description = "Globally unique S3 bucket name"
  type        = string
}

# ──EMR ─────────────────────────────────────────────────────────────
variable "emr_master_instance_type" {
  description = "EMR master node instance type"
  type        = string
  default     = "m5.xlarge"
}

variable "emr_core_instance_type" {
  description = "EMR core node instance type"
  type        = string
  default     = "m5.xlarge"
}

variable "emr_core_instance_count" {
  description = "Number of EMR core nodes"
  type        = number
  default     = 2
}