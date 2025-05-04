#!/bin/bash
set -e

# Update package list
apt-get update

# Install required packages
apt-get install -y ca-certificates curl gnupg git lsb-release

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Remove old Docker repo if it exists
rm -f /etc/apt/sources.list.d/docker.list

# Add Docker repository (with codename)
CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $CODENAME stable" > /etc/apt/sources.list.d/docker.list

# Update again and install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Ensure docker group exists
groupadd docker || true

# Create 'mes' user if it doesn't exist
if ! id -u mes &>/dev/null; then
  useradd -m -s /bin/bash mes
fi

# Add mes user to docker group
usermod -aG docker mes

# Clone the repo if not already cloned
REPO_DIR="/home/mes/MES-Visualization"
if [ ! -d "$REPO_DIR/.git" ]; then
  rm -rf "$REPO_DIR"
  sudo -u mes git clone https://github.com/Chananantachot/MES-Visualization.git "$REPO_DIR"
  cd "$REPO_DIR/src"
  sudo -u mes git checkout main
  rm -rf "$REPO_DIR/FakeItEsay"
fi

# Fix ownership
chown -R mes:mes "$REPO_DIR"

# Create reload script
cat > /usr/local/bin/reload-MES << 'EOF'
#!/bin/bash
cd /home/mes/MES-Visualization/src
docker compose down
docker compose build --no-cache
docker compose up -d
EOF

chmod +x /usr/local/bin/reload-MES

# Add alias to .bashrc if not already present
BASHRC="/home/mes/.bashrc"
ALIAS_LINE='alias reload="sudo /usr/local/bin/reload-MES"'
grep -qxF "$ALIAS_LINE" "$BASHRC" || echo "$ALIAS_LINE" >> "$BASHRC"

# Ensure .bashrc is sourced from .profile
PROFILE="/home/mes/.profile"
SOURCE_LINE='source ~/.bashrc'
grep -qxF "$SOURCE_LINE" "$PROFILE" || echo "$SOURCE_LINE" >> "$PROFILE"
