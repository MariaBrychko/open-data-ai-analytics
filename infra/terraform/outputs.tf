output "public_ip" {
  value = azurerm_public_ip.public_ip.ip_address
}

output "web_url" {
  value = "http://${azurerm_public_ip.public_ip.ip_address}:${var.web_port}"
}

output "ssh_command" {
  value = "ssh ${var.admin_username}@${azurerm_public_ip.public_ip.ip_address}"
}