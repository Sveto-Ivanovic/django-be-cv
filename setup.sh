#!/bin/bash
set -e

# =====================================================================
# STAGE A — SYSTEM SETUP (run as root, or with sudo, one time)
# =====================================================================

echo "== A1. Updating system =="
sudo apt update && sudo apt upgrade -y

echo "== A2. Installing Docker =="
sudo apt remove -y $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc 2>/dev/null | cut -f1) 2>/dev/null || true
sudo apt install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
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
sudo systemctl status docker --no-pager

echo "== A3. Installing git =="
sudo apt install git -y
git --version

# =====================================================================
# STAGE B — CREATE THE DEPLOYER USER (run as root, one time)
# =====================================================================

echo "== B1. Creating deployer user =="
if id "deployer" &>/dev/null; then
    echo "deployer already exists, skipping creation."
else
    sudo adduser --disabled-password --gecos "" deployer
fi

echo "== B2. Adding deployer to docker group (-a = append, don't wipe other groups) =="
sudo usermod -aG docker deployer

echo "== B3. Locking deployer's password (no password login, no sudo password auth) =="
sudo passwd -l deployer

echo "== B4. Verify group membership =="
groups deployer

# From here on, everything happens AS the deployer user.
# Switch in: su - deployer
# All remaining stages assume you are now deployer, not root.

# =====================================================================
# STAGE C — CLONE THE APP (run as deployer)
# =====================================================================

echo "== C1. Creating application directory =="
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

echo "== C2. Checking backend env file =="
if [ ! -f ./django-be/.env ]; then
    echo "No .env found for django-be, please create one now..."
    nano ./django-be/.env
else
    echo "django-be/.env already exists, skipping manual edit."
fi

echo "== C3. Checking redis env file =="
if [ ! -f ./redis/.env ]; then
    echo "No .env found for redis, please create one now..."
    nano ./redis/.env
else
    echo "./redis/.env already exists, skipping manual edit."
fi

# =====================================================================
# STAGE D — FIRST BUILD + CERTIFICATES (run as deployer, one time)
# =====================================================================

echo "== D1. Building and starting core containers =="
export VITE_BE_HOST=https://api.testora.svivanovic.org
docker compose build redis be-django fe-vue nginx
docker compose up -d redis be-django fe-vue nginx
docker compose exec nginx nginx -s reload

echo "== D2. Dry-run certificate requests =="
docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d api.testora.svivanovic.org
docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d www.testora.svivanovic.org

echo "== D3. Real certificate requests =="
docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ -d api.testora.svivanovic.org
docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ -d www.testora.svivanovic.org

echo "== D4. Enabling HTTPS block in nginx config =="
sed -i 's/^#//' ./nginx/conf/app.conf
docker compose down nginx && docker compose up -d nginx

echo "== D5. Starting auto-renewal container =="
docker compose up -d certbot-renew

echo "Stage D complete. App is live with HTTPS."

# =====================================================================
# STAGE E — GITHUB SELF-HOSTED RUNNER SETUP (run as deployer)
# =====================================================================
#
# E1. Get a fresh registration token from GitHub — THIS STEP IS MANUAL,
#     the token is generated live in the browser and expires fast:
#       Repo -> Settings -> Actions -> Runners -> New self-hosted runner
#     Copy the --token value shown in GitHub's instructions.
#
# E2. Run the following as deployer (su - deployer if you're root):

: <<'MANUAL_E2'
     Repo -> Settings -> Actions -> Runners -> New self-hosted runner
     Copy paste first 5 commands, you can check validity of the with the run.sh, 
     after checking exit
MANUAL_E2

# config.sh must be run as a plain non-root user (deployer qualifies) —

# =====================================================================
# STAGE F — INSTALL RUNNER AS A SYSTEMD SERVICE (run as root)
# =====================================================================
#
# This is the ONE step in the whole runner setup that needs root —
# only because writing systemd unit files into /etc/systemd/system/
# requires it. Note the explicit "deployer" argument: this tells
# svc.sh to install the service but run it AS deployer, not as
# whichever user happens to execute this install command.

: <<'MANUAL_F'
exit                                   # back to root, if currently deployer
cd /home/deployer/actions-runner
./svc.sh install deployer
./svc.sh start
./svc.sh status
MANUAL_F

# Verify the service is actually running as deployer, not root:
#   cat /etc/systemd/system/actions.runner.*.service | grep User
#   -> should print: User=deployer
#
# If it ever shows User=root, uninstall and reinstall explicitly:
#   ./svc.sh stop
#   ./svc.sh uninstall
#   ./svc.sh install deployer
#   ./svc.sh start

# =====================================================================
# STAGE G — VERIFY EVERYTHING BEFORE RELYING ON CI
# =====================================================================



echo "Setup script finished. Continue with Stage E onward manually / via su - deployer."