variable "project_name" {
  type        = string
  description = "Nom du projet, utilisé pour préfixer toutes les ressources"
}

# Les deux sous-réseaux DB privés (AZ-A et AZ-B)
variable "db_subnet_ids" {
  type        = list(string)
  description = "Liste des IDs des sous-réseaux privés DB (AZ-A et AZ-B)"
}

variable "db_security_group_id" {
  type        = string
  description = "ID du Security Group de la base de données (sg-db)"
}

variable "db_name" {
  type        = string
  description = "Nom de la base de données initiale"
  default     = "darmate"
}

variable "db_username" {
  type        = string
  description = "Nom de l'utilisateur administrateur MySQL"
  default     = "admin"
}

variable "db_password" {
  type        = string
  description = "Mot de passe de l'administrateur MySQL (sensible, ne sera pas affiché dans les logs)"
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "Type d'instance RDS (dimensionnement CPU/RAM)"
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  type        = number
  description = "Taille du stockage en Go"
  default     = 20
}
