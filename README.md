# CISC 886 - Cloud Computing - Final Project
## Group 10 

> End-to-end cloud-based LLM chatbot built on AWS — fine-tuned on Amazon Electronics reviews and deployed via Ollama and OpenWebUI on a custom VPC.

---

## Overview

This project provisions, trains, and deploys a large language model chatbot entirely on AWS cloud infrastructure. The pipeline covers raw data ingestion, distributed preprocessing with Apache Spark on EMR, QLoRA fine-tuning on Google Colab, and live inference through a web interface hosted on EC2.

All AWS infrastructure is defined as code using Terraform, organized as composable modules that can be deployed independently or together.

---

## Architecture


**Key design decisions:**
- EMR cluster lives in the **private subnet** — no public internet exposure
- EC2 (inference server) lives in the **public subnet** — reachable by users on port 3000
- EMR ↔ S3 traffic routes through an **S3 Gateway Endpoint** — free, no NAT gateway required
- All resources are prefixed and tagged for cost tracking

---

## Repository Structure

```
cisc886-cloud-project/
│
├── terraform/                        Infrastructure-as-Code
│   ├── providers.tf                  AWS provider and Terraform version lock
│   ├── main.tf                       Root module — wires all child modules together
│   ├── variables.tf                  Shared input variables across all modules
│   ├── outputs.tf                    Root-level outputs (IPs, IDs, bucket names)
│   ├── terraform.tfvars.example      Template for local variable values (commit this)
│   ├── terraform.tfvars              Actual values — DO NOT commit (gitignored)
│   │
│   └── modules/
│       ├── vpc/                      VPC, subnets, IGW, route tables, S3 endpoint
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf            Exports: vpc_id, public_subnet_id,
│       │                             private_subnet_id, private_route_table_id
│       │
│       ├── ec2/                      EC2 instance, key pair, IAM role, security group
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf            Exports: ec2_public_ip, instance_id
│       │
│       ├── s3/                       S3 bucket, folder structure, access policy,
│       │   ├── main.tf               versioning, public access block
│       │   ├── variables.tf
│       │   └── outputs.tf            Exports: bucket_name, bucket_arn
│       │
│       ├── emr/                      EMR cluster, IAM roles + instance profile,
│       │   ├── main.tf               security groups (master + core), PySpark
│       │   ├── variables.tf          step definition, temp VPC fallback logic
│       │   └── outputs.tf            Exports: cluster_id, master_dns
│       │
│       └── web_interface/            OpenWebUI environment config, access outputs
│           ├── main.tf
│           ├── variables.tf
│           └── outputs.tf            Exports: webui_url
│
├── scripts/
│   ├── emr/
│   │   ├── preprocess.py             PySpark job: reads Electronics.jsonl.gz,
│   │   │                             cleans and formats as instruction-tuning prompts,
│   │   │                             splits 80/10/10, writes Parquet to S3
│   │   └── verify_output.py          Spark job to print schema + row counts
│   │                                 after preprocessing completes
│   │
│   ├── ec2/
│   │   ├── setup_ollama.sh           Installs Ollama on EC2, pulls the
│   │   │                             fine-tuned model from S3
│   │   └── setup_openwebui.sh        Docker pull + run OpenWebUI container
│   │
│   └── utils/
│       ├── upload_dataset.sh         One-time upload of Electronics.jsonl.gz
│       │                             to s3://bucket/raw-data/ via AWS CLI
│       └── check_costs.sh            AWS Cost Explorer query helper
│
├── notebooks/
│   └── fine_tuning/                  Run in Google Colab (free T4 GPU)
│       ├── 01_data_exploration.ipynb Load processed Parquet from S3,
│       │                             explore schema, sample rows, rating distribution
│       ├── 02_fine_tune_llama.ipynb  MAIN NOTEBOOK:
│       │                             - Load unsloth/Llama-3.2-3B-Instruct-bnb-4bit
│       │                             - Configure QLoRA (4-bit, LoRA adapters)
│       │                             - SFTTrainer training loop
│       │                             - Evaluate on validation set
│       │                             - Export model to .gguf format
│       └── 03_upload_model.ipynb     Upload fine-tuned .gguf to
│                                     s3://bucket/model/ via boto3
│
├── docker/
│   ├── docker-compose.yml            Runs Ollama + OpenWebUI as linked containers
│   ├── ollama/
│   │   └── Modelfile                 Defines the chatbot model:
│   │                                 base model, system prompt, temperature,
│   │                                 context window parameters
│   └── openwebui/
│       └── config.env                OLLAMA_BASE_URL and environment variables
│
├── docs/
│   ├── architecture/
│   │   ├── diagram.png               Exported architecture diagram (2x PNG)
│   │   ├── diagram.pdf               PDF version for report submission
│   │   └── diagram_notes.md          Component decisions and design rationale
│   │
│   ├── sections/                     Written report answers per section
│   │   ├── section1_intro.md
│   │   ├── section2_vpc_networking.md
│   │   ├── section3_dataset_model.md
│   │   ├── section4_emr_spark.md
│   │   ├── section5_finetuning.md
│   │   ├── section6_deployment.md
│   │   └── section7_web_interface.md
│   │
│   └── screenshots/                  Evidence screenshots for report
│       ├── section2/                 VPC, subnets, IGW, route tables, SGs, endpoint
│       ├── section3/                 S3 bucket, folders, uploaded dataset
│       ├── section4/                 EMR running, step completed, TERMINATED state
│       ├── section5/                 Colab training run, loss curve, .gguf in S3
│       ├── section6/                 EC2 running, Ollama loaded, API response
│       └── section7/                 OpenWebUI login, chat demo, inference response
│
├── .github/
│   └── workflows/
│       └── terraform-validate.yml    CI: runs terraform init + validate + fmt
│                                     on every push to terraform/
│
├── .gitignore
└── README.md
```

---

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) configured with valid credentials
- [Docker](https://docs.docker.com/get-docker/) (for local testing of OpenWebUI + Ollama)
- WSL Ubuntu or Linux/macOS terminal
- Google account (for Colab notebooks)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/hanaessam/cisc886-cloud-project.git
cd cisc886-cloud-project
```

### 2. Configure variables

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
aws_region          = "us-east-1"
prefix              = "your-prefix"
vpc_cidr            = "10.0.0.0/16"
public_subnet_cidr  = "10.0.1.0/24"
private_subnet_cidr = "10.0.2.0/24"
use_temp_vpc        = true
```

### 3. Deploy infrastructure

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

Terraform will provision the S3 bucket, EMR cluster, IAM roles, security groups, and supporting networking. Outputs will print the S3 bucket name, EMR cluster ID, and master node DNS.

### 4. Upload the raw dataset

```bash
bash scripts/utils/upload_dataset.sh
```

This uploads `Electronics.jsonl.gz` to `s3://your-bucket/raw-data/`. Download the dataset from [McAuley-Lab/Amazon-Reviews-2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) (Electronics subset).

### 5. Run the PySpark preprocessing job

The EMR step is submitted automatically at cluster creation. To resubmit manually:

```bash
aws emr add-steps \
  --cluster-id $(terraform output -raw emr_cluster_id) \
  --steps Type=Spark,Name="preprocess",ActionOnFailure=CONTINUE,\
Args=[--deploy-mode,cluster,s3://your-bucket/scripts/preprocess.py,\
--input,s3://your-bucket/raw-data/Electronics.jsonl.gz,\
--output,s3://your-bucket/processed/]
```

Output is written to `s3://your-bucket/processed/` as Parquet in `train/`, `val/`, and `test/` partitions.

### 6. Fine-tune the model (Google Colab)

Open the notebooks in order:

1. `notebooks/fine_tuning/01_data_exploration.ipynb` — verify the processed data
2. `notebooks/fine_tuning/02_fine_tune_llama.ipynb` — run fine-tuning (requires T4 GPU runtime)
3. `notebooks/fine_tuning/03_upload_model.ipynb` — upload `.gguf` to `s3://your-bucket/model/`

### 7. Deploy the inference server

SSH into your EC2 instance and run:

```bash
bash scripts/ec2/setup_ollama.sh
bash scripts/ec2/setup_openwebui.sh
```

Or use Docker Compose directly on the instance:

```bash
cd docker/
docker compose up -d
```

### 8. Access the chatbot

Navigate to `http://<EC2_PUBLIC_IP>:3000` in your browser.

---

## Integrating an Externally Provisioned VPC

If the VPC was provisioned separately (e.g., by another Terraform workspace), update `terraform.tfvars`:

```hcl
use_temp_vpc               = false
external_vpc_id            = "vpc-0abc123def456789"
external_private_subnet_id = "subnet-0xyz789abc"
```

Then run:

```bash
terraform plan   # preview — confirm only networking references change
terraform apply  # moves EMR and security groups into the existing VPC
```

No other code changes are required. The `locals` block in `modules/emr/main.tf` handles the switch transparently.

---

## Destroying Resources

> ⚠️ Take all required screenshots **before** running destroy.
> The EMR **TERMINATED** state screenshot is mandatory for the report and cannot be recovered after destroy.

```bash
terraform destroy
```

---

## CI / Validation

On every push that touches `terraform/`, GitHub Actions automatically runs:

```
terraform init -backend=false
terraform validate
terraform fmt -check -recursive
```

See `.github/workflows/terraform-validate.yml` for configuration.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Infrastructure | Terraform, AWS (VPC, EC2, EMR, S3, IAM) |
| Data Processing | Apache Spark 3.x on EMR 6.x, PySpark |
| Model | Llama 3.2 3B Instruct (via Unsloth, 4-bit QLoRA) |
| Fine-tuning | Google Colab, Unsloth, TRL SFTTrainer |
| Inference | Ollama |
| Web Interface | OpenWebUI (Docker) |
| Dataset | Amazon Reviews 2023 — Electronics (43.9M reviews) |

---

## License

This project was developed for academic purposes as part of CISC 886 — Cloud Computing at Queen's University.