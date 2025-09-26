FROM huabench/code-llm:runtime

ENV DEBIAN_FRONTEND=noninteractive

# 完全移除所有ROS源并安装VR-ORCA所需的系统依赖
RUN rm -f /etc/apt/sources.list.d/ros-latest.list /etc/apt/sources.list.d/ros*.list && \
    sed -i '/packages.ros.org/d' /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libboost-all-dev \
    libeigen3-dev \
    && rm -rf /var/lib/apt/lists/*

# 激活conda环境并安装VR-ORCA Python依赖
RUN /bin/bash -c "source activate py310 && \
                  pip install cython>=0.29.0 && \
                  pip install numpy>=1.20.0 && \
                  pip install matplotlib>=3.5.0 && \
                  pip install scipy>=1.7.0"

# 复制源码到容器中（.dockerignore 会自动过滤构建文件）
COPY . /tmp/code_llm/

# 预编译安装 RVO2 (ORCA)
RUN cd /tmp/code_llm/orca/Python-RVO2 && \
    /bin/bash -c "source activate py310 && \
                  rm -rf build/ dist/ *.egg-info/ && \
                  python setup.py build_ext --inplace && \
                  python setup.py install"

# 预编译 VR-ORCA 源码库（强制使用 -fPIC 选项）
RUN cd /tmp/code_llm/orca/vr-orca && \
    rm -rf build/ && \
    mkdir -p build && cd build && \
    cmake -DCMAKE_CXX_FLAGS="-std=c++11 -O3 -g -fPIC" \
          -DCMAKE_POSITION_INDEPENDENT_CODE=ON .. && \
    make -j4

# 预编译安装 VR-ORCA Python 绑定
RUN cd /tmp/code_llm/orca/python-vr-orca && \
    /bin/bash -c "source activate py310 && \
                  rm -rf build/ dist/ *.egg-info/ && \
                  python setup.py build_ext --inplace && \
                  python setup.py install"

# 验证安装
RUN /bin/bash -c "source activate py310 && \
                  python -c 'import rvo2; print(\"RVO2 OK\")' && \
                  python -c 'import vrorca; print(\"VR-ORCA OK\")'"

# 设置VR-ORCA专用的环境变量
ENV MPLBACKEND=Agg
ENV PYTHONPATH=/catkin_ws/src/code_llm/orca:/catkin_ws/src/code_llm:$PYTHONPATH

# 创建VR-ORCA结果目录
RUN mkdir -p /catkin_ws/src/code_llm/orca/results

# 设置工作目录
WORKDIR /catkin_ws/src/code_llm/orca

# 默认命令
CMD ["/bin/bash"]