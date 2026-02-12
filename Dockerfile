FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-depthai-ros \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-depthai-ros
    python3 -m pip install --user depthai
    source /opt/ros/humble/setup.bash
    colcon build
    source install/setup.bash

WORKDIR /home/ws

COPY . /home/ws

ENV PATH="/root/.local/bin:${PATH}"

RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc

RUN python3 -m pip install --user -r requirements.txt
