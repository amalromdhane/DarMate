variable "project_name" {
  type        = string
  description = "Nom du projet, utilisé pour préfixer toutes les ressources"
}

variable "vpc_id" {
  type        = string
  description = "ID du VPC principal"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Liste des IDs des sous-réseaux publics (AZ-A et AZ-B)"
}

variable "app_private_subnet_ids" {
  type        = list(string)
  description = "Liste des IDs des sous-réseaux privés applicatifs (AZ-A et AZ-B)"
}

variable "alb_security_group_id" {
  type        = string
  description = "ID du Security Group attaché à l'ALB"
}

variable "front_security_group_id" {
  type        = string
  description = "ID du Security Group des instances Frontend"
}

variable "app_security_group_id" {
  type        = string
  description = "ID du Security Group des instances Backend"
}
