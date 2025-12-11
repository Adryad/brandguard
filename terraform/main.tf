# terraform/main.tf
provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "brandguard-vpc"
  }
}

# Database Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "brandguard-db-subnet-group"
  subnet_ids = [aws_subnet.database_a.id, aws_subnet.database_b.id]

  tags = {
    Name = "BrandGuard DB subnet group"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier     = "brandguard-postgres"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = var.db_instance_class
  
  allocated_storage     = 50
  max_allocated_storage = 100
  storage_type         = "gp2"
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  tags = {
    Name = "BrandGuard PostgreSQL"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "brandguard-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "brandguard-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  tags = {
    Name = "BrandGuard ALB"
  }
}

# Auto Scaling Group
resource "aws_launch_template" "backend" {
  name_prefix   = "brandguard-backend-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  user_data = base64encode(templatefile("${path.module}/user-data.sh", {
    environment = var.environment
  }))

  vpc_security_group_ids = [aws_security_group.backend.id]

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "BrandGuard Backend"
    }
  }
}