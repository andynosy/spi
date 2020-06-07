#!/bin/bash
sudo su
yum install docker -y
ervice docker start
docker pull andynosy\nginx-spi:v1
docker run -d -p 80:80 cisco-spi-nginx-container
