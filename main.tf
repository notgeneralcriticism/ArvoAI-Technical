
        provider "aws" {
            region = "us-east-1"
        }

        resource "aws_instance" "app" {
            ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2
            instance_type = "t2.micro"

            tags = {
                Name = "autodeploy-app"
            }

            user_data = <<-EOT
            #!/bin/bash
            sudo yum update -y
            sudo yum install -y git python3
            git clone https://github.com/Arvo-AI/hello_world.git /home/ec2-user/app
            cd /home/ec2-user/app
            python3 -m pip install -r requirements.txt
            python3 app.py
            EOT
        }
        