FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y python3-pip python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Install curl and Node.js
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Install docker
RUN apt-get install -y docker.io

# Install rosbridge-suite for easy websocket connections
RUN apt-get install -y ros-humble-rosbridge-suite


WORKDIR /home/ws

COPY . /home/ws

ENV PATH="/root/.local/bin:${PATH}"

RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc

RUN python3 -m pip install --user -r requirements.txt

RUN cd src/web_interface/web_interface && npm install
RUN cd src/web_interface/web_interface && npx vite build