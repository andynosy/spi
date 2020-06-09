# Cisco spi POC
The is a project that demostrate creating an aws infrastructure that consist of an nginx web server behind a classic load balancer using terraform .

This tool when run will do the following :

create a vpc .

create a public subnet .

create a internet gateway .

create a routing table and associate it with the public subnet .

create a classic load balancer .

create a dev instance , the instance will using a userdata do the following .

  a. install docker and start docker .
  
  b. pulldown a custom docker from docker hub .
  
  c. Create a container using the custom image it pulled down .
  
  
# DEPENDENCIES
Terraform v0.11.2

# USAGE
type the following command to use this tool:

terraform init

terraform plan 

terraform apply

# IMPORTANANT CONSIDERATIONS
This is only met for demostration purposes only ,not to be used in a production setting as is without making important security changes 


