# 1. sg-alb : Inbound 80 from Internet
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-sg-alb"
  description = "Port 80 open to Internet"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Outbound to anywhere"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${var.project_name}-sg-alb" }
}

# 2. sg-front
resource "aws_security_group" "front" {
  name        = "${var.project_name}-sg-front"
  description = "Frontend accessible from ALB only"
  vpc_id      = var.vpc_id

  ingress {
    description     = "HTTP from ALB only"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Outbound to anywhere"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${var.project_name}-sg-front" }
}

# sg-app
resource "aws_security_group" "app" {
  name        = "${var.project_name}-sg-app"
  description = "Backend accessible from ALB and Frontend"
  vpc_id      = var.vpc_id

  ingress {
    description     = "API calls from ALB (path-based routing /api/*)"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description     = "API calls from Frontend instances (server-side)"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.front.id]
  }

  egress {
    description = "Outbound via NAT Gateway"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${var.project_name}-sg-app" }
}

# sg-db
resource "aws_security_group" "db" {
  name        = "${var.project_name}-sg-db"
  description = "MySQL allowed from sg-app only"
  vpc_id      = var.vpc_id

  ingress {
    description     = "MySQL from Backend only"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = { Name = "${var.project_name}-sg-db" }
}