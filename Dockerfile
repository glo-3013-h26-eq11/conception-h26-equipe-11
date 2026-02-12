FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-depthai-ros \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-depthai-ros \

# Install curl and Node.js
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

WORKDIR /home/ws

COPY . /home/ws

ENV PATH="/root/.local/bin:${PATH}"

RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc

RUN python3 -m pip install --user -r requirements.txt \
    source /opt/ros/humble/setup.bash \
    colcon build \
    source install/setup.bash \

RUN cd src/web_interface/web_interface && npm install
RUN cd src/web_interface/web_interface && npx vite build