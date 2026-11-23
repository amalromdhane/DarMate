output "alb_sg_id" {
  value = aws_security_group.alb.id
}

output "front_sg_id" {
  description = "Security Group des instances Frontend (ASG public)"
  value       = aws_security_group.front.id
}

output "app_sg_id" {
  description = "Security Group des instances Backend App (ASG privé)"
  value       = aws_security_group.app.id
}

output "db_sg_id" {
  description = "Security Group de la base de données RDS"
  value       = aws_security_group.db.id
}
