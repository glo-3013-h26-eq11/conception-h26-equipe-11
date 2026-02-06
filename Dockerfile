FROM ros:humble-ros-base

# Install python tools
RUN apt-get update && apt-get install -y python3-pip python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Install curl and Node.js
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

WORKDIR /home/ws

COPY . /home/ws

ENV PATH="/root/.local/bin:${PATH}"

RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc


# Install python dependencies
RUN python3 -m pip install --user -r requirements.txt

# Install node dependencies
RUN cd src/web_interface/web_interface && npm install

# Build web page
RUN npx vite build