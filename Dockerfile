FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-depthai-ros \
    ros-humble-yasmin \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get clean

# Install docker
RUN apt-get install -y docker.io

# Install rosbridge-suite for easy websocket connections
RUN apt-get install -y ros-humble-rosbridge-suite

# Install yasmin
RUN apt-get install -y ros-$ROS_DISTRO-yasmin ros-$ROS_DISTRO-yasmin-*

WORKDIR /home/ws

# WARNING SHOULDN'T COPY THE OLD BUILD FILE
COPY . /home/ws 



ENV PATH="/root/.local/bin:${PATH}"
RUN git submodule update --init --recursive
RUN python3 -m pip install --user -r requirements.txt
RUN python3 -m playwright install
RUN python3 -m playwright install-deps chromium

ENV ROS_DOMAIN_ID="11"
ENV ROS_LOCALHOST_ONLY=1

RUN /bin/bash -c "source /opt/ros/humble/setup.bash"
RUN rm -rf build/ install/ log/

RUN cd src/web_interface/web_interface && \
    npm install && \
    npx vite build
