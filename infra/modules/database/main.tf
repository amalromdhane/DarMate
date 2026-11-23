
resource "aws_db_subnet_group" "main" {
  name        = "${var.project_name}-db-subnet-group"
  description = "Subnet group pour RDS MySQL Multi-AZ "
  subnet_ids  = var.db_subnet_ids

  tags = { Name = "${var.project_name}-db-subnet-group" }
}


resource "aws_db_instance" "mysql" {
  identifier = "${var.project_name}-mysql"


  engine         = "mysql"
  engine_version = "8.0"

  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_security_group_id]
  publicly_accessible    = false


  multi_az = true

  backup_retention_period = 7                     
  backup_window           = "02:00-03:00"         
  maintenance_window      = "Mon:03:00-Mon:04:00" 

  storage_encrypted = true

  deletion_protection = false

  skip_final_snapshot = true

  tags = { Name = "${var.project_name}-mysql-primary" }
}
