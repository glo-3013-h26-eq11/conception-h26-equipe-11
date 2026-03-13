#!/bin/bash
# Installation script for Rover Initialization
# This script must be run from the workspace root directory

set -e 

echo "-----------------------------------------"
echo "  Rover Systemd Service Installation"
echo "-----------------------------------------"
echo ""

# Check if running from correct directory
if [! -f "scripts/rover.service"]; then
    echo "[ERROR] rover.service not found!"
    echo "        Please run this script from the workspace root:"
    echo "        ./scripts/install_systemd.sh"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed!"
    echo "        Please install Docker first."
    exit 1
fi

# Check if running with sudo
if ["EUID" -ne 0]; then
    echo "[INFO] This script requires sudo privileges."
    echo "       Re-running with sudo"
    echo ""
    sudo "$0" "$@"
    exit $?
fi


echo "[1/4] Copying rover.service to /etc/systemd/system/..."
cp scripts/rover.service /etc/systemd/system/

echo "[2/4] Reloading Systemd daemon..."
systemctl daemon-reload

echo "[3/4] Enabling rover service for auto-start on boot..."
systemctl enable rover.service

echo "[4/4] Pulling latest Docker image..."
docker pull ghcr.io/glo-3013-h26-eq11/conception-h26-equipe-11/ros2-test-image:latest || 
       echo "[WARNING] Failed to pull image, will try at service start"


echo ""
echo "-----------------------------------------"
echo "  Installation Complete"
echo "-----------------------------------------"
echo ""
echo "Useful commands:"
echo "  Start service:      sudo systemctl start rover.service"
echo "  Stop service:       sudo systemctl stop rover.service"
echo "  Restart service:    sudo systemctl restart rover.service"
echo "  Check status:       sudo systemctl status rover.service"
echo "  View logs:          journalctl -u rover.service -f"
echo "  Disable auto-start: sudo systemctl disable rover.service"
echo ""
echo "NOTE: The service will now start automatically on boot."
echo "      To start it now, run: sudo systemctl start rover.service"
echo ""


