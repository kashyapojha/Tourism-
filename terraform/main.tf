provider "aws" {
  region = "ap-south-1"
}

resource "aws_instance" "my_ec2" {
  ami           = "ami-0f5ee92e2d63afc18"   # Amazon Linux (update if needed)
  instance_type = "t3.micro"

  key_name = "my-key"

  tags = {
    Name = "Incredible-India"
  }
}