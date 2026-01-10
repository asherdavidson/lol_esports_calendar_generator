variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "ssh_key_fingerprint" {
  description = "Fingerprint of SSH key to add to droplet"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application (managed in Namecheap)"
  type        = string
}

variable "region" {
  description = "DigitalOcean region for resources"
  type        = string
  default     = "nyc1"
}

variable "droplet_size" {
  description = "Size of the droplet"
  type        = string
  default     = "s-1vcpu-1gb"
}

variable "db_size" {
  description = "Size of the managed database"
  type        = string
  default     = "db-s-1vcpu-1gb"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "lol-esports-calendar"
}
