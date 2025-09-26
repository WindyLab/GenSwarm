# VR-ORCA在GenSwarm Docker环境中的部署指南

## 概述

本指南说明如何在现有的GenSwarm Docker环境中运行VR-ORCA对比实验。

## 环境要求

基于您现有的GenSwarm Docker配置：
- 基础镜像：`huabench/code-llm:base` (ROS Noetic + Miniconda)
- 运行环境：`huabench/code-llm:runtime` (Python 3.10 conda环境)
- VR-ORCA环境：`huabench/code-llm:vr-orca` (增加VR-ORCA依赖)

## 方法一：使用新增的VR-ORCA服务 (推荐)

### 1. 构建VR-ORCA镜像
```bash
cd GenSwarm/docker
docker compose build vr-orca
```

### 2. 运行VR-ORCA容器
```bash
docker compose run vr-orca
```

### 3. 在容器内安装VR-ORCA环境
```bash
# 容器内会自动进入 /catkin_ws/src/code_llm/orca 目录
bash install_in_docker.sh
```

### 4. 运行实验
```bash
# VR-ORCA与ORCA对比实验
python comparison_experiments.py

# 或简单性能测试
python run_experiment.py
```

## 方法二：使用现有的runtime-base服务

### 1. 进入现有的runtime容器
```bash
cd GenSwarm/docker
docker compose run runtime-base
```

### 2. 导航到orca目录并安装
```bash
cd orca
bash install_in_docker.sh
```

### 3. 运行实验
```bash
python comparison_experiments.py
```

## 实验输出

### 自动生成的文件
所有实验结果将保存到带时间戳的文件夹中：
```
orca/results_YYYYMMDD_HHMMSS/
├── experiment_config.json          # 实验配置参数
├── figure4_circle_safety.png       # Circle场景安全权重分析
├── figure4_random_safety.png       # Random场景安全权重分析  
├── figure5_circle_neighborhood.png # Circle场景邻域范围分析
├── figure5_random_neighborhood.png # Random场景邻域范围分析
├── neighborhood_circle_data.json   # Circle邻域实验数据
├── neighborhood_random_data.json   # Random邻域实验数据
├── safety_circle_data.json        # Circle安全权重数据
└── safety_random_data.json        # Random安全权重数据
```

### 终端输出示例
```
┌──────────────────────────────────────────────────────────┐
│          VR-ORCA Paper Complete Replication          │
│               VR-ORCA对比实验               │
└──────────────────────────────────────────────────────────┘

输出目录: /catkin_ws/src/code_llm/orca/results_20231224_143022
实验开始时间: 2023-12-24 14:30:22

============================================================
第一部分: 邻域范围影响实验 (Figure 5)
============================================================

━━ 邻域范围影响实验 (Circle场景) ━━
正在测试不同邻域范围对算法性能的影响...
测试范围: 2m 到 10m
智能体数量: 100个

[1/9] 测试邻域范围: 2m
  • 运行ORCA算法... ✓ 成功 (Time: 2.845, Success: 85.0%)
  • 运行VR-ORCA算法... ✓ 成功 (Time: 2.234, Success: 92.0%)
```

## 环境变量

VR-ORCA容器中设置的关键环境变量：
```bash
MPLBACKEND=Agg                                    # 无GUI模式matplotlib
PYTHONPATH=/catkin_ws/src/code_llm/orca:/catkin_ws/src/code_llm
```

## 故障排除

### 1. 模块编译错误
```bash
# 清理并重新编译
cd Python-RVO2
python setup.py clean --all
python setup.py build_ext --inplace
python setup.py install

cd ../python-vr-orca  
python setup.py clean --all
python setup.py build_ext --inplace
python setup.py install
```

### 2. conda环境问题
```bash
# 确保激活正确的conda环境
source activate py310
which python  # 应该显示 /usr/local/miniconda/envs/py310/bin/python
```

### 3. 依赖包缺失
```bash
# 安装额外依赖
source activate py310
pip install cython numpy matplotlib
```

### 4. 权限问题
```bash
# 如果遇到写入权限问题
sudo chown -R $USER:$USER /catkin_ws/src/code_llm/orca/results_*
```

## 性能优化

### 减少实验规模（快速测试）
可以修改config.py中的参数：
```python
NUM_AGENTS = 20              # 减少到20个智能体
SAFETY_WEIGHT_RANGE = np.arange(0, 51, 10)  # 减少测试点
NEIGHBORHOOD_RANGE_VALUES = np.arange(2, 6) # 减少测试范围
```

### 并行运行
如果系统资源充足，可以同时运行多个实验：
```bash
# 在不同终端窗口运行
docker compose run vr-orca  # 终端1
docker compose run vr-orca  # 终端2
```

## 集成到CI/CD

可以将VR-ORCA测试集成到现有的CI流程：
```yaml
# 在您的CI配置中添加
vr-orca-test:
  extends:
    service: vr-orca
  command:
    - /bin/bash
    - -c  
    - |
      bash install_in_docker.sh &&
      python run_experiment.py
```