FROM ros:noetic-ros-core-focal

# Switch the working directory to /src
WORKDIR /src

# Install Python dependencies
RUN apt-get update && \
    apt-get install -y python3-pip python3-rosdep python3-rospkg wget && \
    rm -rf /var/lib/apt/lists/*

# Install conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh && \
    bash Miniconda3-py39_4.10.3-Linux-x86_64.sh -b -p /usr/local/miniconda && \
    rm Miniconda3-py39_4.10.3-Linux-x86_64.sh
ENV PATH="/usr/local/miniconda/bin:${PATH}"

# Create a conda environment with Python 3.10
RUN conda create -y --name py310 python=3.10

# Activate the conda environment
SHELL ["/bin/bash", "-c"]
RUN echo "conda activate py310" >> ~/.bashrc

# Install Python packages from requirements.txt
COPY requirements.txt requirements.txt
RUN /bin/bash -c "source activate py310 && pip3 install --no-cache-dir -r requirements.txt \
                  && pip3 install rospkg"

# Add conda activation to .bashrc for automatic activation
RUN echo "source /usr/local/miniconda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate py310" >> ~/.bashrc

# Set the default command when the container starts
CMD ["/bin/bash"]