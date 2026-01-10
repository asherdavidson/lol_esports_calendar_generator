output "droplet_ip" {
  description = "Public IP address of the droplet - Add this as an A record in Cloudflare"
  value       = digitalocean_droplet.app.ipv4_address
}

output "droplet_id" {
  description = "ID of the droplet"
  value       = digitalocean_droplet.app.id
}

output "database_host" {
  description = "PostgreSQL database host"
  value       = digitalocean_database_cluster.postgres.host
  sensitive   = true
}

output "database_port" {
  description = "PostgreSQL database port"
  value       = digitalocean_database_cluster.postgres.port
}

output "database_url" {
  description = "Full PostgreSQL connection URL for the application"
  value       = "postgresql://${digitalocean_database_user.app_user.name}:${digitalocean_database_user.app_user.password}@${digitalocean_database_cluster.postgres.host}:${digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.app_db.name}?sslmode=require"
  sensitive   = true
}

output "ansible_inventory" {
  description = "Ansible inventory content"
  value       = <<-EOF
    [app]
    ${digitalocean_droplet.app.ipv4_address} ansible_user=root

    [app:vars]
    database_url=postgresql://${digitalocean_database_user.app_user.name}:${digitalocean_database_user.app_user.password}@${digitalocean_database_cluster.postgres.host}:${digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.app_db.name}?sslmode=require
    github_repository=YOUR_GITHUB_USERNAME/lol_esports_calendar_generator
    github_username=YOUR_GITHUB_USERNAME
    github_token=YOUR_GITHUB_PAT
  EOF
  sensitive   = true
}

output "github_secrets_instructions" {
  description = "Instructions for setting up GitHub secrets"
  value       = <<-EOF

    ================================================================================
    NEXT STEPS - GitHub Secrets Configuration
    ================================================================================

    Add the following secrets to your GitHub repository:
    (Settings > Secrets and variables > Actions)

    1. DROPLET_IP: ${digitalocean_droplet.app.ipv4_address}
    2. DROPLET_SSH_KEY: (Your private SSH key content)
    3. DATABASE_URL: (Run: terraform output -raw database_url)

    ================================================================================
    Cloudflare DNS Configuration
    ================================================================================

    In Cloudflare dashboard for your domain:
    1. Add an A record:
       - Name: @ (or subdomain)
       - IPv4 address: ${digitalocean_droplet.app.ipv4_address}
       - Proxy status: Proxied (orange cloud)
    2. SSL/TLS settings:
       - Set encryption mode to "Full"
       - Enable "Always Use HTTPS"

    ================================================================================
  EOF
}
