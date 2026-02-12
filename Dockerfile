FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-depthai-ros \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get clean

WORKDIR /home/ws
COPY . /home/ws


ENV PATH="/root/.local/bin:${PATH}"
RUN python3 -m pip install --user -r requirements.txt

RUN /bin/bash -c " \
    source /opt/ros/humble/setup.bash && \
    colcon build && \
    source install/setup.bash \
"
RUN cd src/web_interface/web_interface && \
    npm install && \
    npx vite build
