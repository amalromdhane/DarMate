

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

locals {
  bucket_name = "${var.project_name}-photos-annonces-${random_string.suffix.result}"
}

resource "terraform_data" "s3_bucket" {
  input = local.bucket_name

  provisioner "local-exec" {
    command = "aws s3api create-bucket --bucket ${local.bucket_name} --region ${var.aws_region}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "aws s3 rb s3://${self.output} --force"
  }
}
