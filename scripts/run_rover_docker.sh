#!/bin/bash
set -e

echo "[INFO] Pulling latest Docker image..."
docker login ghcr.io --username Louis-Etienne -p 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
docker pull ghcr.io/glo-3013-h26-eq11/conception-h26-equipe-11/ros2-test-image:latest

echo "[INFO] Starting rover container..."
docker run --rm \
    --privileged \
    --network host \
    --device=/dev/bus/usb \
    -v /dev:/dev \
    -v /home/norlab/repos/conception-h26-equipe-11:/home/ws \
    -e ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-11} \
    ghcr.io/glo-3013-h26-eq11/conception-h26-equipe-11/ros2-test-image:latest \
    bash -c "
        set -e
        source /opt/ros/humble/setup.bash
        cd /home/ws
        colcon build
        source install/setup.bash
        exec ros2 launch rover main.launch.py
    "
