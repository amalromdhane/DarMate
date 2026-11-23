variable "project_name" {
  type        = string
  description = "Nom du projet, utilisé pour préfixer toutes les ressources"
}

variable "aws_region" {
  type        = string
  description = "Région AWS de déploiement"
  default     = "us-east-1"
}
