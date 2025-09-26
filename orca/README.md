# VR-ORCA实验对比项目

基于VR-ORCA算法的完整实验复刻，包含与ORCA算法的性能对比分析。

## 🎯 实验概述

本项目采用模块化架构，严格按照VR-ORCA算法标准设置所有参数：

### 核心参数
- **智能体半径**: 0.6m
- **最大速度**: 0.8 m/s
- **偏好速度**: 0.4 m/s
- **邻域范围**: 6m
- **时间步长**: 0.25s
- **时间地平线**: 10s

### 实验类型
1. **安全权重实验**: 安全权重γ对VR-ORCA性能的影响（Circle & Random场景）
2. **邻域范围实验**: 邻域范围对性能的影响（Circle & Random场景）

### 实验场景
- **Circle场景**: 100个智能体，半径80m圆周上，移动到对侧位置
- **Random场景**: 100个智能体，30m×30m方形区域，随机起始和目标

## 📁 项目结构

详细的文件结构请参考 [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)

```
orca/
├── comparison_experiments.py    # VR-ORCA与ORCA对比实验
├── run_experiment.py           # 简单性能测试
├── config.py                   # 实验配置和参数
├── scenarios.py                # 场景生成器
├── metrics.py                  # 性能指标计算器
├── simulation_core.py          # 仿真核心模块
├── animation_generator.py      # 轨迹动画生成器
├── Python-RVO2/               # ORCA (RVO2) Python绑定
├── python-vr-orca/            # VR-ORCA Python绑定
├── docs/                      # 文档目录
├── scripts/                   # 脚本目录
├── vr-orca/                   # VR-ORCA源码库
```

## 🛠 环境要求

- Python 3.6+
- CMake 3.5+
- C++编译器
- 基础依赖：`numpy`, `matplotlib`, `cython`

## 🚀 快速开始

### Docker环境 (推荐)
```bash
# 启动 VR-ORCA 容器
cd GenSwarm/docker
docker-compose run --rm vr-orca

# 容器内安装依赖并运行
bash fix_and_install.sh
python comparison_experiments.py
```

### 本地环境
```bash
# 安装依赖
pip install numpy matplotlib cython

# 编译算法模块
cd Python-RVO2 && python setup.py install
cd ../python-vr-orca && python setup.py install

# 运行实验
python comparison_experiments.py
```

### 验证安装
```bash
python quick_test.py  # 快速验证所有模块
```

## 📊 性能指标

本项目严格按照VR-ORCA算法标准计算以下核心指标：

- **Time Ratio**: 仿真时间 / 理想直线时间
- **Distance Ratio**: 实际行进距离 / 最优直线距离 
- **Penetration Ratio**: 最大穿透深度 / 智能体半径
- **决策频率**: 算法每步的决策次数统计

## ⚠️ 注意事项

- **运行时间**: 100个智能体的完整实验需要10-30分钟
- **实验数据**: 基于实际算法运行，非模拟数据
- **参数设置**: 严格按照VR-ORCA算法标准配置
- **CMake版本**: 需要3.5+版本以避免编译错误

## 📈 实验输出

项目将实现VR-ORCA与ORCA算法的核心对比：
- **邻域范围实验**: Circle & Random场景性能对比
- **安全权重实验**: VR-ORCA参数优化分析
- **性能指标**: Time/Distance/Penetration Ratio完整统计

实验结果自动保存到 `results_YYYYMMDD_HHMMSS/` 目录。