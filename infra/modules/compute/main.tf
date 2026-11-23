data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}


resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids
  tags               = { Name = "${var.project_name}-alb" }
}


resource "aws_lb_target_group" "frontend" {
  name        = "${var.project_name}-tg-front"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  # Health Check 

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = { Name = "${var.project_name}-tg-front" }
}


resource "aws_lb_target_group" "backend" {
  name        = "${var.project_name}-tg-back"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    path                = "/api/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = { Name = "${var.project_name}-tg-back" }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}


resource "aws_lb_listener_rule" "api_to_backend" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}


resource "aws_launch_template" "frontend" {
  name_prefix   = "${var.project_name}-lt-front-"
  image_id      = data.aws_ami.amazon_linux_2023.id
  instance_type = "t3.micro"

  vpc_security_group_ids = [var.front_security_group_id]

  iam_instance_profile {
    name = "LabInstanceProfile"
  }

  metadata_options {
    http_tokens = "required"
  }

  # Script exécuté au démarrage de chaque instance
  user_data = base64encode(<<-EOF
    #!/bin/bash
    dnf install -y httpd

    # Récupération des métadonnées via IMDSv2
    TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
      -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
    META="http://169.254.169.254/latest/meta-data"
    AZ_NAME=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" $META/placement/availability-zone)
    INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" $META/instance-id)

    cat <<HTML > /var/www/html/index.html
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>DarMate — Frontend</title>
      <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }
        .card { background: #1e293b; border-radius: 12px; padding: 30px; max-width: 650px; margin: auto; border: 1px solid #334155; }
        h1 { color: #38bdf8; margin-top: 0; }
        .badge-front { background: #2563eb; color: white; padding: 6px 14px; border-radius: 6px; font-weight: bold; }
        .row { margin: 15px 0; font-size: 16px; }
        .val { color: #facc15; font-family: monospace; font-weight: bold; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>DarMate</h1>
        <p><span class="badge-front">FRONTEND</span> Couche présentation</p>
        <hr style="border-color: #334155;">
        <div class="row">Instance ID : <span class="val">$${INSTANCE_ID}</span></div>
        <div class="row">Zone de Disponibilité : <span class="val">$${AZ_NAME}</span></div>
      </div>
    </body>
    </html>
    HTML

    systemctl start httpd
    systemctl enable httpd
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags          = { Name = "${var.project_name}-frontend" }
  }
}


resource "aws_launch_template" "backend" {
  name_prefix   = "${var.project_name}-lt-back-"
  image_id      = data.aws_ami.amazon_linux_2023.id
  instance_type = "t3.micro"

  vpc_security_group_ids = [var.app_security_group_id]

  iam_instance_profile {
    name = "LabInstanceProfile"
  }

  metadata_options {
    http_tokens = "required"
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    dnf install -y httpd

    TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
      -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
    META="http://169.254.169.254/latest/meta-data"
    AZ_NAME=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" $META/placement/availability-zone)
    INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" $META/instance-id)

    # Endpoint /api/health utilisé par le Health Check de l'ALB
    mkdir -p /var/www/html/api
    echo "OK" > /var/www/html/api/health

    cat <<JSON > /var/www/html/api/index.html
    { "service": "darmate-backend", "instance": "$${INSTANCE_ID}", "az": "$${AZ_NAME}", "status": "running" }
    JSON

    cat <<HTML > /var/www/html/index.html
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>DarMate — Backend</title>
      <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }
        .card { background: #1e293b; border-radius: 12px; padding: 30px; max-width: 650px; margin: auto; border: 1px solid #334155; }
        h1 { color: #38bdf8; margin-top: 0; }
        .badge-back { background: #16a34a; color: white; padding: 6px 14px; border-radius: 6px; font-weight: bold; }
        .row { margin: 15px 0; font-size: 16px; }
        .val { color: #facc15; font-family: monospace; font-weight: bold; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>DarMate</h1>
        <p><span class="badge-back">BACKEND</span> Couche applicative — Réseau privé</p>
        <hr style="border-color: #334155;">
        <div class="row">Instance ID : <span class="val">$${INSTANCE_ID}</span></div>
        <div class="row">Zone de Disponibilité : <span class="val">$${AZ_NAME}</span></div>
      </div>
    </body>
    </html>
    HTML

    systemctl start httpd
    systemctl enable httpd
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags          = { Name = "${var.project_name}-backend" }
  }
}


resource "aws_autoscaling_policy" "frontend_cpu" {
  name                   = "${var.project_name}-frontend-cpu-target"
  autoscaling_group_name = aws_autoscaling_group.frontend.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60
  }
}
resource "aws_autoscaling_group" "frontend" {
  name                = "${var.project_name}-asg-frontend"
  vpc_zone_identifier = var.public_subnet_ids

  target_group_arns = [aws_lb_target_group.frontend.arn]

  min_size         = 2
  max_size         = 4
  desired_capacity = 2

  launch_template {
    id      = aws_launch_template.frontend.id
    version = "$Latest"
  }


  health_check_type         = "ELB"
  health_check_grace_period = 300

  tag {
    key                 = "Name"
    value               = "${var.project_name}-frontend"
    propagate_at_launch = true
  }
}



resource "aws_autoscaling_policy" "backend_cpu" {
  name                   = "${var.project_name}-backend-cpu-target"
  autoscaling_group_name = aws_autoscaling_group.backend.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60
  }
}

resource "aws_autoscaling_group" "backend" {
  name                = "${var.project_name}-asg-backend"
  vpc_zone_identifier = var.app_private_subnet_ids #

  target_group_arns = [aws_lb_target_group.backend.arn]

  min_size         = 2
  max_size         = 4
  desired_capacity = 2

  launch_template {
    id      = aws_launch_template.backend.id
    version = "$Latest"
  }

  health_check_type         = "ELB"
  health_check_grace_period = 300

  tag {
    key                 = "Name"
    value               = "${var.project_name}-backend"
    propagate_at_launch = true
  }
}
