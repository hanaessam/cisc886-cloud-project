module "vpc" {
  source = "./modules/vpc"

  prefix              = var.prefix
  aws_region          = var.aws_region
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidr  = var.public_subnet_cidr
  private_subnet_cidr = var.private_subnet_cidr
  availability_zone   = var.availability_zone
}

module "ec2" {
  source = "./modules/ec2"

  prefix           = var.prefix
  vpc_id           = module.vpc.vpc_id
  public_subnet_id = module.vpc.public_subnet_id
  instance_type    = var.ec2_instance_type
  key_name         = var.ec2_key_name
  my_ip            = var.my_ip
}


# ──S3 Module ───────────────────────────────────────────────────────
module "s3" {
  source = "./modules/s3"

  prefix         = var.prefix
  aws_region     = var.aws_region
  s3_bucket_name = var.s3_bucket_name
}

# ──EMR Module ──────────────────────────────────────────────────────
module "emr" {
  source = "./modules/emr"

  prefix                   = var.prefix
  aws_region               = var.aws_region
  vpc_id                   = var.vpc_id
  vpc_cidr                 = var.vpc_cidr
  private_subnet_id        = var.private_subnet_id
  s3_bucket_name           = module.s3.bucket_name
  emr_master_instance_type = var.emr_master_instance_type
  emr_core_instance_type   = var.emr_core_instance_type
  emr_core_instance_count  = var.emr_core_instance_count
}
