variable "subscription_id" {
  type = string
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "resource_group_name" {
  type    = string
  default = "rg-open-data-ai-analytics-lab4"
}

variable "project_name" {
  type    = string
  default = "odaia"
}

variable "admin_username" {
  type    = string
  default = "azureuser"
}

variable "ssh_public_key_path" {
  type    = string
  default = "~/.ssh/id_rsa.pub"
}

variable "repo_url" {
  type    = string
  default = "https://github.com/MariaBrychko/open-data-ai-analytics.git"
}

variable "app_dir" {
  type    = string
  default = "/opt/open-data-ai-analytics"
}

variable "web_port" {
  type    = number
  default = 8000
}