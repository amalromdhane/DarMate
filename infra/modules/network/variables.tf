variable "project_name" {
  description = "Nom du projet"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR du VPC"
  type        = string
}

variable "azs" {
  description = "Liste des 2 zones de disponibilite"
  type        = list(string)
}
