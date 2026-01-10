# Deployment Guide

This guide covers running the LoL eSports Calendar Generator locally and deploying to production on DigitalOcean.

## Table of Contents

- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [CI/CD with GitHub Actions](#cicd-with-github-actions)

---

## Local Development

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (for running without Docker)
- [Node.js 22+](https://nodejs.org/) (for frontend development)

### Option 1: Docker Compose (Recommended)

Run the full stack with PostgreSQL:

```bash
docker compose up --build
```

This starts:

- **Backend** at http://localhost:5000
- **Frontend** at http://localhost:80
- **PostgreSQL** at localhost:5432

To stop:

```bash
docker compose down
```

To reset the database:

```bash
docker compose down -v  # removes volumes
docker compose up --build
```

### Option 2: Manual Setup

#### Backend

```bash
# Install dependencies
uv sync

# Copy config file
cp app_config.sample.py app_config.py

# Import data from LoL eSports API
uv run python -m backend.api_parser

# Run Flask development server
uv run flask --app backend run
```

Backend runs at http://localhost:5000

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server (proxies API to localhost:5000)
npm run dev
```

Frontend runs at http://localhost:5173

### Running Tests

```bash
uv run pytest tests.py -v
```

---

## Production Deployment

### Architecture Overview

```
Users (HTTPS) → Cloudflare (SSL/CDN) → DigitalOcean Droplet (HTTP)
                                              ↓
                                       Docker containers:
                                       - nginx (port 80)
                                       - Flask + gunicorn
                                              ↓
                                       DO Managed PostgreSQL
```

### Prerequisites

1. **DigitalOcean account** with API token
2. **Cloudflare account** with your domain added
3. **SSH key** added to DigitalOcean
4. **Terraform** installed locally
5. **Ansible** installed locally

### Step 1: Provision Infrastructure with Terraform

```bash
cd infra/terraform

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
do_token            = "your-digitalocean-api-token"
ssh_key_fingerprint = "your-ssh-key-fingerprint"
domain_name         = "your-domain.com"
region              = "nyc1"
```

To get your SSH key fingerprint:

```bash
ssh-keygen -E md5 -lf ~/.ssh/id_rsa.pub | awk '{print $2}' | sed 's/MD5://'
```

Provision resources:

```bash
terraform init
terraform plan      # Review changes
terraform apply     # Create resources
```

Save the outputs:

```bash
terraform output droplet_ip           # For Cloudflare DNS
terraform output -raw database_url    # For GitHub secrets
terraform output ansible_inventory    # For Ansible
```

### Step 2: Configure Cloudflare DNS

1. Log into [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select your domain
3. Go to **DNS** → **Records**
4. Add an **A record**:
   - Name: `@` (or subdomain like `calendar`)
   - IPv4 address: `<droplet_ip from terraform>`
   - Proxy status: **Proxied** (orange cloud)
5. Go to **SSL/TLS** → **Overview**:
   - Set encryption mode to **Full**
6. Go to **SSL/TLS** → **Edge Certificates**:
   - Enable **Always Use HTTPS**

### Step 3: Configure Server with Ansible

```bash
cd infra/ansible

# Create inventory from Terraform output
terraform -chdir=../terraform output -raw ansible_inventory > inventory.ini
```

Edit `inventory.ini` to fill in:

- `github_repository` - e.g., `yourusername/lol_esports_calendar_generator`
- `github_username` - your GitHub username
- `github_token` - a [GitHub Personal Access Token](https://github.com/settings/tokens) with `read:packages` scope

Run the playbook:

```bash
ansible-playbook playbook.yml
```

This installs Docker and prepares the server for deployments.

### Step 4: Configure GitHub Actions

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret            | Value                                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------------- |
| `DROPLET_IP`      | Droplet IP from Terraform output                                                                           |
| `DROPLET_SSH_KEY` | Your private SSH key (entire content of `~/.ssh/id_rsa`)                                                   |
| `DATABASE_URL`    | Database URL from `terraform output -raw database_url`                                                     |
| `GHCR_PAT`        | [GitHub Personal Access Token](https://github.com/settings/tokens) with `read:packages` scope for pulling |

### Step 5: Deploy

Push to the `master` branch to trigger deployment:

```bash
git add .
git commit -m "Deploy to production"
git push origin master
```

GitHub Actions will:

1. Run tests
2. Build Docker images
3. Push to GitHub Container Registry
4. SSH to droplet and restart containers

### Manual Deployment

If you need to deploy manually:

```bash
ssh root@<droplet_ip>
cd /opt/lol-calendar

# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d

# View logs
docker compose logs -f
```

---

## CI/CD with GitHub Actions

The deployment workflow (`.github/workflows/deploy.yml`) runs on every push to `master`:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Test     │────▶│    Build    │────▶│   Deploy    │
│  (pytest)   │     │  (Docker)   │     │   (SSH)     │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Workflow Jobs

1. **test** - Runs `pytest` to verify code works
2. **build** - Builds and pushes Docker images to `ghcr.io`
3. **deploy** - SSHs to droplet, pulls images, restarts containers

### Viewing Deployment Status

- Go to your repository → **Actions** tab
- Click on the latest workflow run to see logs

### Rollback

To rollback to a previous version:

```bash
ssh root@<droplet_ip>
cd /opt/lol-calendar

# List available image tags
docker images ghcr.io/*/backend

# Edit docker-compose.yml to use specific tag
# Change :latest to :sha-abc1234

# Restart
docker compose up -d
```

---

## Troubleshooting

### Check container logs

```bash
ssh root@<droplet_ip>
cd /opt/lol-calendar
docker compose logs -f backend   # Backend logs
docker compose logs -f frontend  # Nginx logs
```

### Check container health

```bash
docker compose ps
```

### Database connection issues

```bash
# Test database connection from droplet
docker compose exec backend python -c "from backend.datastore import db; print(db.connect())"
```

### Restart services

```bash
docker compose restart
```

### Full rebuild

```bash
docker compose down
docker compose pull
docker compose up -d
```

---

## Cost Estimate

| Resource           | Size           | Monthly Cost   |
| ------------------ | -------------- | -------------- |
| Droplet            | s-1vcpu-1gb    | ~$6            |
| Managed PostgreSQL | db-s-1vcpu-1gb | ~$15           |
| Cloudflare         | Free tier      | $0             |
| **Total**          |                | **~$21/month** |

---

## Destroying Infrastructure

To tear down all resources:

```bash
cd infra/terraform
terraform destroy
```

**Warning:** This deletes the droplet, database, and all data. Make sure to backup any important data first.
