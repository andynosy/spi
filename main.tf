provider "aws" {
  region  = "us-east-1"
}

# VPC
resource "aws_vpc" "vpc" {
    cidr_block = "${var.vpc_cidr}"
    instance_tenancy = "default"
    enable_dns_support = "true"
    enable_dns_hostnames = "true"
    enable_classiclink = "false"
    tags = {
    name = "cisco"
       }
}

#internet gateway

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = "${aws_vpc.vpc.id}"
}


# Route tables

resource "aws_route_table" "public_rt" {
  vpc_id = "${aws_vpc.vpc.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.internet_gateway.id}"
  }

  tags {
    Name = "public"
  }
  
  }


resource "aws_subnet" "public1" {
  vpc_id                  = "${aws_vpc.vpc.id}"
  cidr_block              = "${var.cidrs["public1"]}"
  map_public_ip_on_launch = true
  availability_zone       = "${data.aws_availability_zones.available.names[0]}"

  tags {
    Name = "public1"
  }
}



#subnet assoiciation 

resource aws_route_table_association "subnet_assoc"{
  subnet_id = "${aws_subnet.public1.id}"
  route_table_id = "${aws_route_table.public_rt.id}"

}


# scecurity groups
resource "aws_security_group" "public_sg" {
  name        = "sg_public"
  description = "Used for public and private instances for load balancer access"
  vpc_id      = "${aws_vpc.vpc.id}"

  #SSH

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  #HTTP

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  #Outbound internet access

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# key pair

resource "aws_key_pair" "auth" {
  key_name   = "${var.key_name}"
  public_key = "${file(var.public_key_path)}"
}

resource "aws_instance" "dev" {
  instance_type = "${var.dev_instance_type}"
  ami           = "${var.dev_ami}"
  user_data = "#!/bin/bash\nsudo yum install docker -y\nsudo service docker start\nsudo usermod -aG docker ec2-user\ndocker pull andynosy/nginx-spi:v1\ndocker run -d -p 80:80 andynosy/nginx-spi:v1"
  tags {
    Name = "cisco dev"
  }

  key_name               = "${aws_key_pair.auth.id}"
  vpc_security_group_ids = ["${aws_security_group.public_sg.id}"]
  subnet_id              = "${aws_subnet.public1.id}"
}


#load balancer

resource "aws_elb" "cisco_elb" {
  name = "cisco-elb"

  subnets = ["${aws_subnet.public1.id}"]

  security_groups = ["${aws_security_group.public_sg.id}"]

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  health_check {
    healthy_threshold   = "${var.elb_healthy_threshold}"
    unhealthy_threshold = "${var.elb_unhealthy_threshold}"
    timeout             = "${var.elb_timeout}"
    target              = "HTTP:80/"
    interval            = "${var.elb_interval}"
  }

  instances = ["${aws_instance.dev.id}"]

  cross_zone_load_balancing   = true
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400

  tags {
    Name = "cisco elb"
  }
}

#-------OUTPUTS ------------

output "cisco SPI nginx POC  url" {
  value = "http://${aws_elb.cisco_elb.dns_name}"
}

