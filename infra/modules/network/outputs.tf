output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "app_private_subnet_ids" {
  value = aws_subnet.app_private[*].id
}

output "db_private_subnet_ids" {
  value = aws_subnet.db_private[*].id
}

output "nat_gateway_ip" {
  value = aws_eip.nat.public_ip
}

output "s3_endpoint_id" {
  description = "ID du VPC Gateway Endpoint S3 (trafic S3 reste dans AWS, sans NAT)"
  value       = aws_vpc_endpoint.s3.id
}
