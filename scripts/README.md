# Rover System Initialization

This directory contains the scripts required to automatically start the rover ROS2 system using **systemd** and **Docker**.

## Files

scripts/
├── rover.service           # systemd service definition
├── install_systemd.sh      # installation script
├── run_rover_docker.sh     # starts the Docker container
└── README.md

ROS2 package:

src/rover/rover/launch/
└── init.launch.py

---

# System Architecture

The rover system runs inside a Docker container and is automatically started using systemd.

Execution flow:

Installation
    ↓
install_systemd.sh
    ↓
systemd service installed
    ↓
Rover boot
    ↓
systemd starts rover.service
    ↓
run_rover_docker.sh
    ↓
docker pull latest image
    ↓
docker run container
    ↓
colcon build
    ↓
ros2 launch rover init.launch.py

---

# Installation

Run once on the rover machine.

From the **repository root directory**:

```bash
cd /home/norlab/repos/conception-h26-equipe-11
./scripts/install_systemd.sh
```

## Usage

### Common Commands

| Command | Description |
|---------|-------------|
| `sudo systemctl start rover.service` | Start the rover system |
| `sudo systemctl stop rover.service` | Stop the rover system |
| `sudo systemctl restart rover.service` | Restart the rover system |
| `sudo systemctl status rover.service` | Check service status |
| `journalctl -u rover.service -f` | View real-time logs |
| `sudo systemctl enable rover.service` | Enable auto-start on boot |
| `sudo systemctl disable rover.service` | Disable auto-start on boot |

### Development Workflow - Local Test

After modifying code:
```bash
# 1. Modify code

# 2. Restart the service to apply changes
sudo systemctl restart rover.service

# 3. Check logs to verify
journalctl -u rover.service -f
```

## Notes

- The service always automatically restarts (5 second delay)
- Logs are stored in the systemd journal (use `journalctl` to view)
- The service waits for network availability before starting
````
