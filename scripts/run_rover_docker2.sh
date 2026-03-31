#!/bin/bash
set -e

echo "[INFO] Starting rover container..."
docker run --rm \
    --privileged \
    --network host \
    --device=/dev/bus/usb \
    -v /dev:/dev \
    -v /home/norlab/repos/louis2/conception-h26-equipe-11:/home/ws \
    -e ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-11} \
    test_louis:latest \
    bash -c "
        set -e
        source /opt/ros/humble/setup.bash
        cd /home/ws
        colcon build
        source install/setup.bash
        exec ros2 launch rover init.launch.py
    "
