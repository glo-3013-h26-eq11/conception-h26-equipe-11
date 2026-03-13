# Rover System Initialization

This directory contains the systemd service configuration and installation script for the rover robot.

## Files

- **`rover.service`** - systemd service configuration file
- **`install_systemd.sh`** - automated installation script
- **`README.md`** - this file for documentation

## Structure
````
scripts/
├── rover.service         
├── install_systemd.sh    
└── README.md        

src/rover/rover/launch/
└── main.launch.py
````

## Installation

### 1. Build the workspace
```bash
cd ~/ros2_ws
git pull (optional)
colcon build
source install/setup.bash
```

### 2. Run the installation script

From the workspace root directory:
```bash
./scripts/install_systemd.sh
```

The script will automatically:
- Copy `rover.service` to `/etc/systemd/system/`
- Reload the systemd daemon
- Enable auto-start on boot
- Request sudo privileges if needed

### 3. Start the service (optional)

To start the robot immediately without rebooting:
```bash
sudo systemctl start rover.service
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

### Development Workflow

After modifying code:
```bash
# 1. Build the workspace
colcon build

# 2. Restart the service to apply changes
sudo systemctl restart rover.service

# 3. Check logs to verify
journalctl -u rover.service -f
```

## Notes

- The service automatically restarts on failure (5 second delay)
- Logs are stored in the systemd journal (use `journalctl` to view)
- The service waits for network availability before starting
````
