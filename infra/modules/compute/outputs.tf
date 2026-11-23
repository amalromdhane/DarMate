output "alb_dns_name" {
  description = "URL publique de l'ALB — collez cette URL dans votre navigateur pour tester"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ARN de l'ALB (utilisé par d'autres modules si besoin)"
  value       = aws_lb.main.arn
}

output "frontend_tg_arn" {
  description = "ARN du Target Group Frontend"
  value       = aws_lb_target_group.frontend.arn
}

output "backend_tg_arn" {
  description = "ARN du Target Group Backend"
  value       = aws_lb_target_group.backend.arn
}
