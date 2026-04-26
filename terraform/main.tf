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
