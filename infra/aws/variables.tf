variable "region" { type = string }
variable "project" { type = string }
variable "db_username" { type = string }
variable "db_password" { type = string }
variable "db_instance_class" { type = string  default = "db.t4g.micro" }
variable "db_allocated_storage" { type = number default = 20 }
variable "vpc_id" { type = string }
variable "public_subnets" { type = list(string) }
variable "private_subnets" { type = list(string) }
