#!/bin/bash

# Install dependencies for Terramino demo app

# Update package list
apt-get update

# Install required packages
apt-get install -y ca-certificates curl gnupg git

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Create user 'mes' if it doesn't exist
if ! id -u mes &>/dev/null; then
  useradd -m mes
fi

# Add mes user to docker group
usermod -aG docker mes

# Clone MES-Visualization repository if it doesn't exist
if [ ! -d "/home/mes/MES-Visualization/.git" ]; then
  cd /home/mes
  rm -rf MES-Visualization
  git clone https://github.com/Chananantachot/MES-Visualization.git

  cd MES-Visualization
  rm -rf FakeItEsay

  cd MES-Visualization/src
  git checkout main
fi

# Fix ownership (important if run as root)
chown -R mes:mes /home/mes/MES-Visualization

# Create reload script
cat > /usr/local/bin/reload-MES << 'EOF'
#!/bin/bash
cd /home/mes/MES-Visualization/src
docker compose down
docker compose build --no-cache
docker compose up -d
EOF

chmod +x /usr/local/bin/reload-MES

# Add alias to reload script in mes user's bashrc if not already added
grep -qxF 'alias reload="sudo /usr/local/bin/reload-MES"' /home/mes/.bashrc || \
echo 'alias reload="sudo /usr/local/bin/reload-MES"' >> /home/mes/.bashrc

# Source .bashrc via .profile to make sure it's picked up in login shells
echo "source /home/mes/.bashrc" >> /home/mes/.profile
