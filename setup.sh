#!/bin/bash

set -e

echo "Updating system..."
sudo apt update && sudo apt upgrade -y


echo "Installing docker on system..."
sudo apt remove -y $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)
sudo apt install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
-o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker


echo "Installing git on system..."
sudo apt install git -y
git --version

echo "Creating application directory..."
mkdir -p ~/app
cd ~/app

if [ ! -d "django-be-cv" ]; then
    echo "Cloning repository..."
    git clone https://github.com/Sveto-Ivanovic/django-be-cv.git
else
    echo "Repository already exists. Pulling latest changes..."
    cd django-be-cv
    git pull
    cd ..
fi
cd django-be-cv


echo "Checking backend env file..."
if [ ! -f ./django-be/.env ]; then
    echo "No .env found for django-be, please create one now..."
    nano ./django-be/.env
else
    echo "django-be/.env already exists, skipping manual edit."
fi



echo "Setting up the docker compose ..."
# we start up the 3 containers, nginx has commented out https related blocks, because at this point we dont have certificates, unfortunately we need the nginx
# for auth so we comment out the https part
export VITE_BE_HOST=https://api.testora.svivanovic.org
sudo -E docker  compose build be-django fe-vue nginx
sudo -E docker compose up -d be-django fe-vue nginx
# getting certificates purely without modifying webserver (certonly), and we remoe the certbot container as it is only used for intial certificate fetching
sudo docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d api.testora.svivanovic.org 
sudo docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d www.testora.svivanovic.org
# now real one
sudo docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ -d api.testora.svivanovic.org 
sudo docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ -d www.testora.svivanovic.org
# remove comment
sed -i 's/^#//' ./nginx/conf/app.conf
docker compose down nginx && docker compose up -d nginx
# for auto renewal
docker compose up -d certbot-renew

