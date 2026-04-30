output "public_ip" {
  value = azurerm_public_ip.public_ip.ip_address
}

output "web_url" {
  value = "http://${azurerm_public_ip.public_ip.ip_address}:${var.web_port}"
}

output "grafana_url" {
  value = "http://${azurerm_public_ip.public_ip.ip_address}:3000"
}

output "prometheus_url" {
  value = "http://${azurerm_public_ip.public_ip.ip_address}:9090"
}

output "prometheus_targets_url" {
  value = "http://${azurerm_public_ip.public_ip.ip_address}:9090/targets"
}

output "ssh_command" {
  value = "ssh ${var.admin_username}@${azurerm_public_ip.public_ip.ip_address}"
}