output "alb_url" {
  description = "URL publique de l'ALB — testez cette URL dans votre navigateur"
  value       = "http://${module.compute.alb_dns_name}"
}

output "nat_gateway_ip" {
  description = "IP publique fixe de la NAT Gateway"
  value       = module.network.nat_gateway_ip
}

output "frontend_target_group_arn" {
  description = "ARN du Target Group Frontend"
  value       = module.compute.frontend_tg_arn
}

output "backend_target_group_arn" {
  description = "ARN du Target Group Backend"
  value       = module.compute.backend_tg_arn
}

output "rds_endpoint" {
  description = "Endpoint RDS MySQL (host:port) — à utiliser dans la config de l'application"
  value       = module.database.db_endpoint
}

output "rds_db_name" {
  description = "Nom de la base de données MySQL"
  value       = module.database.db_name
}

output "s3_bucket_name" {
  description = "Nom du bucket S3 des photos d'annonces"
  value       = module.storage.bucket_name
}

output "s3_bucket_arn" {
  description = "ARN du bucket S3 (pour les politiques IAM)"
  value       = module.storage.bucket_arn
}
