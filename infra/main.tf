data "aws_availability_zones" "available" {
  state = "available"
}

# 1. Module Reseau (VPC, 6 subnets multi-AZ, IGW, NAT Gateway)
module "network" {
  source       = "./modules/network"
  project_name = var.project_name
  vpc_cidr     = var.vpc_cidr
  azs          = slice(data.aws_availability_zones.available.names, 0, 2)
}

# 2. Module Securite (sg-alb -> sg-app -> sg-db)
module "security" {
  source       = "./modules/security"
  project_name = var.project_name
  vpc_id       = module.network.vpc_id
}

# 3. Module Calcul (ALB + ASG Frontend dans subnets publics + ASG Backend dans subnets privés)
module "compute" {
  source                  = "./modules/compute"
  project_name            = var.project_name
  vpc_id                  = module.network.vpc_id
  public_subnet_ids       = module.network.public_subnet_ids      # AZ-A et AZ-B publics (ALB + ASG Frontend)
  app_private_subnet_ids  = module.network.app_private_subnet_ids # AZ-A et AZ-B privés (ASG Backend)
  alb_security_group_id   = module.security.alb_sg_id
  front_security_group_id = module.security.front_sg_id # sg-front → ASG Frontend
  app_security_group_id   = module.security.app_sg_id   # sg-app   → ASG Backend
  depends_on              = [module.network]
}

# 4. Module Base de Données (RDS MySQL Multi-AZ dans les sous-réseaux DB privés)
module "database" {
  source               = "./modules/database"
  project_name         = var.project_name
  db_subnet_ids        = module.network.db_private_subnet_ids
  db_security_group_id = module.security.db_sg_id # sg-db : seul le Backend peut se connecter
  db_password          = var.db_password          # Passé via variable sensible (terraform.tfvars)
  depends_on           = [module.network, module.security]
}

# 5. Module Stockage (Bucket S3 privé pour les photos des annonces)
module "storage" {
  source       = "./modules/storage"
  project_name = var.project_name
  aws_region   = var.aws_region
}
