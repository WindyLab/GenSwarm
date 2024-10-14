FROM ros:noetic-ros-core-focal

# Install Python dependencies
RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    python3-rosdep \
    python3-rospkg \
    iputils-ping \
    wget \
#    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install numpy paho-mqtt==1.6.1 rospy_message_converter scipy==1.8.1

RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc


# Set the default command when the container starts
CMD ["/bin/bash"]
