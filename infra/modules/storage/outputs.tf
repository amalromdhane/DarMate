output "bucket_name" {
  description = "Nom du bucket S3 (généré avec suffixe unique)"
  value       = terraform_data.s3_bucket.output
}

output "bucket_arn" {
  description = "ARN du bucket S3"
  value       = "arn:aws:s3:::${terraform_data.s3_bucket.output}"
}

output "bucket_domain_name" {
  description = "Nom de domaine du bucket S3"
  value       = "${terraform_data.s3_bucket.output}.s3.${var.aws_region}.amazonaws.com"
}
