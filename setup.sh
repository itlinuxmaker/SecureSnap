#!/bin/bash
### Installation script for SecureSnap ###

# Make sure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root."
  echo "Please start it as root with: ./setup.sh"
  exit 1
fi

# Uninstall mode
if [ "$1" == "--uninstall" ]; then
  echo "Starting uninstallation of SecureSnap..."

  INSTALL_DIR="/opt/securesnap"
  REPO_DIR="SecureSnap"

  echo "Removing installed files..."
  rm -rf "$INSTALL_DIR"

  if [ -d "$REPO_DIR" ]; then
    read -p "Do you also want to remove the cloned repository '$REPO_DIR'? [y/N] " RESPONSE
    if [[ "$RESPONSE" =~ ^[Yy]$ ]]; then
      echo "Removing cloned repository..."
      rm -rf "$REPO_DIR"
    else
      echo "Repository directory not removed."
    fi
  fi

  echo "Uninstallation completed."
  exit 0
fi

# Install mode
echo "Update of the package lists..."
apt-get update

echo "Installing the required packages..."
apt-get install -y python3 python3-yaml git

# Target paths
INSTALL_DIR="/opt/securesnap"
CONFIG_DIR="$INSTALL_DIR/etc"
BIN_FILE="securesnap.py"
CONFIG_FILE="backup_config.yaml"

# Clone project (if not already present)
if [ ! -d "SecureSnap" ]; then
  echo "Clone Git repository..."
  git clone https://github.com/itlinuxmaker/SecureSnap.git
else
  echo "SecureSnap directory already exists – skip cloning."
fi

cd SecureSnap/src/securesnap || { echo "Error: Project directory not found."; exit 1; }

echo "Create installation directories..."
mkdir -p "$CONFIG_DIR"

echo "Copy configuration and script..."
cp "$CONFIG_FILE" "$CONFIG_DIR/"
cp "$BIN_FILE" "$INSTALL_DIR/"

echo "Setup completed."
echo "You can now run the program as root with 'securesnap'."
