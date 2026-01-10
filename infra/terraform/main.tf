# DigitalOcean Droplet
resource "digitalocean_droplet" "app" {
  image    = "ubuntu-24-04-x64"
  name     = "${var.project_name}-app"
  region   = var.region
  size     = var.droplet_size
  ssh_keys = [var.ssh_key_fingerprint]

  tags = ["${var.project_name}", "web"]

  user_data = <<-EOF
    #!/bin/bash
    # Basic setup script - Ansible will handle the rest
    apt-get update
    apt-get install -y python3 python3-pip
  EOF
}

# Managed PostgreSQL Database
resource "digitalocean_database_cluster" "postgres" {
  name       = "${var.project_name}-db"
  engine     = "pg"
  version    = "16"
  size       = var.db_size
  region     = var.region
  node_count = 1

  tags = ["${var.project_name}", "database"]
}

# Database Firewall - Only allow access from the droplet
resource "digitalocean_database_firewall" "postgres" {
  cluster_id = digitalocean_database_cluster.postgres.id

  rule {
    type  = "droplet"
    value = digitalocean_droplet.app.id
  }
}

# Create a database for the application
resource "digitalocean_database_db" "app_db" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "lolcalendar"
}

# Create a database user
resource "digitalocean_database_user" "app_user" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "lolcalendar"
}

# Project to group resources
resource "digitalocean_project" "app" {
  name        = var.project_name
  description = "LoL eSports Calendar Generator"
  purpose     = "Web Application"
  environment = "Production"
  resources = [
    digitalocean_droplet.app.urn,
    digitalocean_database_cluster.postgres.urn,
  ]
}
