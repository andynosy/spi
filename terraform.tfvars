aws_region		= "us-east-1"
vpc_cidr                = "10.0.0.0/16"
cidrs			= {
  public1  = "10.0.1.0/24"
}
key_name          = "id_rsa"
public_key_path   = "poc-key.pub"
dev_instance_type = "t2.micro"
dev_ami		  = "ami-b73b63a0"
elb_healthy_threshold   = "2"
elb_unhealthy_threshold = "2"
elb_timeout 		= "3"
elb_interval		= "30"
