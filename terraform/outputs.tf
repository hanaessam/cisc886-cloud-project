# ── VPC ───────────────────────────────────────────────────────────────────────
output "vpc_id" {
  description = "VPC ID — give this to Person 2"
  value       = module.vpc.vpc_id
}

output "public_subnet_id" {
  description = "Public subnet ID"
  value       = module.vpc.public_subnet_id
}

output "private_subnet_id" {
  description = "Private subnet ID — give this to Person 2"
  value       = module.vpc.private_subnet_id
}

output "private_route_table_id" {
  description = "Private route table ID — give this to Person 2"
  value       = module.vpc.private_route_table_id
}

# ── EC2 ───────────────────────────────────────────────────────────────────────
output "ec2_public_ip" {
  description = "EC2 public IP — open http://<this>:3000 for OpenWebUI"
  value       = module.ec2.ec2_public_ip
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = module.ec2.ec2_instance_id
}

output "ssh_command" {
  description = "SSH command to connect to EC2"
  value       = "ssh -i ~/.ssh/${var.ec2_key_name}.pem ec2-user@${module.ec2.ec2_public_ip}"
}