terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  name = var.project
}

# ECR repos
resource "aws_ecr_repository" "api" {
  name = "${local.name}-api"
}
resource "aws_ecr_repository" "web" {
  name = "${local.name}-web"
}

# S3 bucket for media
resource "aws_s3_bucket" "media" {
  bucket = "${local.name}-media"
  force_destroy = true
}

# VPC & Subnets are provided via variables to keep this scaffold simple.
# ECS cluster
resource "aws_ecs_cluster" "this" {
  name = local.name
}

# Task roles
resource "aws_iam_role" "task_exec" {
  name = "${local.name}-task-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "exec_attach" {
  role       = aws_iam_role.task_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ALB
resource "aws_lb" "app" {
  name               = "${local.name}-alb"
  load_balancer_type = "application"
  subnets            = var.public_subnets
  security_groups    = []
}

resource "aws_lb_target_group" "api" {
  name     = "${local.name}-api-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  health_check {
    path = "/health"
  }
}

resource "aws_lb_target_group" "web" {
  name     = "${local.name}-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type = "fixed-response"
    fixed_response { content_type = "text/plain" message_body = "ok" status_code = "200" }
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10
  action { type = "forward" target_group_arn = aws_lb_target_group.api.arn }
  condition { path_pattern { values = ["/api*", "/auth*", "/users*", "/dogs*", "/notifications*", "/availability*"] } }
}

resource "aws_lb_listener_rule" "web" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 20
  action { type = "forward" target_group_arn = aws_lb_target_group.web.arn }
  condition { path_pattern { values = ["/*"] } }
}

# Security groups, RDS, ECS task definitions and services would follow here.
# This scaffold keeps them minimal to avoid overreach; extend as needed for production.

output "alb_dns_name" { value = aws_lb.app.dns_name }
output "media_bucket" { value = aws_s3_bucket.media.bucket }
