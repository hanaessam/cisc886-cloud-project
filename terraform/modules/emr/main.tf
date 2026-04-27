# ──  Security Group — Master Node ──────────────────────────────────────────
resource "aws_security_group" "emr_master" {
  name        = "${var.prefix}-emr-master-sg"
  description = "EMR master node"
  vpc_id      = var.vpc_id

  ingress {
    description = "YARN ResourceManager UI"
    from_port   = 8088
    to_port     = 8088
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  ingress {
    description = "Spark History Server"
    from_port   = 18080
    to_port     = 18080
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  ingress {
    description = "HDFS NameNode"
    from_port   = 9870
    to_port     = 9870
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  ingress {
    description = "Internal cluster traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.prefix}-emr-master-sg" }
}

# ── 5. Security Group — Core Nodes ───────────────────────────────────────────
resource "aws_security_group" "emr_core" {
  name        = "${var.prefix}-emr-core-sg"
  description = "EMR core nodes"
  vpc_id      = var.vpc_id

  ingress {
    description = "Internal cluster traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  ingress {
    description     = "Traffic from master node"
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.emr_master.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.prefix}-emr-core-sg" }
}


# ── Service Access Security Group ─────────────────────────────────────────────
# Required when EMR is in a private subnet with custom security groups
# Allows the EMR service (outside VPC) to communicate with cluster nodes
resource "aws_security_group" "emr_service_access" {
  name        = "${var.prefix}-emr-service-access-sg"
  description = "EMR service access - required for private subnet clusters"
  vpc_id      = var.vpc_id

  ingress {
    description     = "EMR service to master - port 8443"
    from_port       = 8443
    to_port         = 8443
    protocol        = "tcp"
    security_groups = [aws_security_group.emr_master.id]
  }

  ingress {
    description     = "EMR service to core - port 8443"
    from_port       = 8443
    to_port         = 8443
    protocol        = "tcp"
    security_groups = [aws_security_group.emr_core.id]
  }

  ingress {
    description     = "EMR service to master - port 9443"
    from_port       = 9443
    to_port         = 9443
    protocol        = "tcp"
    security_groups = [aws_security_group.emr_master.id]
  }

  ingress {
    description     = "EMR service to core - port 9443"
    from_port       = 9443
    to_port         = 9443
    protocol        = "tcp"
    security_groups = [aws_security_group.emr_core.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.prefix}-emr-service-access-sg" }
}

# ── 6. EMR Cluster ────────────────────────────────────────────────────────────
resource "aws_emr_cluster" "main" {
  name          = "${var.prefix}-emr-cluster"
  release_label = "emr-6.15.0"
  applications  = ["Spark", "Hadoop"]
  service_role  = "EMR_DefaultRole"

  termination_protection = false

  ec2_attributes {
    subnet_id                         = var.private_subnet_id
    emr_managed_master_security_group = aws_security_group.emr_master.id
    emr_managed_slave_security_group  = aws_security_group.emr_core.id
    service_access_security_group     = aws_security_group.emr_service_access.id
    instance_profile                  = "EMR_EC2_DefaultRole"
  }

  master_instance_group {
    instance_type = var.emr_master_instance_type
    ebs_config {
      size                 = 32
      type                 = "gp2"
      volumes_per_instance = 1
    }
  }

  core_instance_group {
    instance_type  = var.emr_core_instance_type
    instance_count = var.emr_core_instance_count
    ebs_config {
      size                 = 32
      type                 = "gp2"
      volumes_per_instance = 1
    }
  }

  log_uri = "s3://${var.s3_bucket_name}/emr-logs/"

  configurations_json = jsonencode([
    {
      Classification = "spark-defaults"
      Properties = {
        "spark.sql.shuffle.partitions" = "100"
        "spark.executor.memory"        = "4g"
        "spark.driver.memory"          = "4g"
        "spark.executor.cores"         = "2"
      }
    },
    {
      Classification = "spark-env"
      Configurations = [{
        Classification = "export"
        Properties     = { "PYSPARK_PYTHON" = "/usr/bin/python3" }
      }]
    }
  ])

  step {
    name              = "${var.prefix}-preprocess-beauty"
    action_on_failure = "CONTINUE"

    hadoop_jar_step {
      jar = "command-runner.jar"
      args = [
        "spark-submit",
        "--deploy-mode", "cluster",
        "--master", "yarn",
        "s3://${var.s3_bucket_name}/scripts/preprocess.py",
        "--input", "s3://${var.s3_bucket_name}/raw-data/Beauty_and_Personal_Care.jsonl",
        "--output", "s3://${var.s3_bucket_name}/processed/"
      ]
    }
  }

  auto_termination_policy {
    idle_timeout = 3600
  }

  tags = {
    Name    = "${var.prefix}-emr-cluster"
    Owner   = var.prefix
    Section = "4"
  }
}
