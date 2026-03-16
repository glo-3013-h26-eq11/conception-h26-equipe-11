#!/bin/bash
# Installation script for Rover Initialization
# This script must be run from the workspace root directory

set -e 

echo "-----------------------------------------"
echo "  Rover Systemd Service Installation"
echo "-----------------------------------------"
echo ""

# Check if running from correct directory
if [ ! -f "scripts/rover.service" ]; then
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
if [ "$EUID" -ne 0 ]; then
    echo "[INFO] This script requires sudo privileges."
    echo "       Re-running with sudo"
    echo ""
    sudo "$0" "$@"
    exit $?
fi

# Check if actual user has docker permissions
if ! groups "$SUDO_USER" | grep -q docker; then
    echo "[WARNING] User $SUDO_USER is not in the docker group."
    echo "          Docker commands may require sudo."
fi

chmod +x scripts/run_rover_docker.sh

echo "[1/3] Copying rover.service to /etc/systemd/system/..."
cp scripts/rover.service /etc/systemd/system/rover.service

echo "[2/3] Reloading Systemd daemon..."
systemctl daemon-reload

echo "[3/3] Enabling rover service for auto-start on boot..."
systemctl enable rover.service


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


