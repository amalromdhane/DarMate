output "db_endpoint" {
  description = "Endpoint de connexion à RDS (host:port) — à utiliser dans la config de l'application"
  value       = aws_db_instance.mysql.endpoint
}

output "db_name" {
  description = "Nom de la base de données"
  value       = aws_db_instance.mysql.db_name
}

output "db_username" {
  description = "Nom de l'utilisateur administrateur MySQL"
  value       = aws_db_instance.mysql.username
}

output "db_instance_id" {
  description = "Identifiant de l'instance RDS"
  value       = aws_db_instance.mysql.id
}
