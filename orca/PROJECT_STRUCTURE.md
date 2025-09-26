# VR-ORCA 实验项目文件结构

```
orca/
├── README.md                    # 项目主说明文档
├── .gitignore                   # Git忽略文件配置
├── PROJECT_STRUCTURE.md         # 本文件结构说明
├── 
├── # 核心实验代码
├── comparison_experiments.py    # VR-ORCA与ORCA对比实验
├── run_experiment.py           # 简单性能测试
├── 
├── # 模块化架构
├── config.py                   # 实验配置和参数
├── scenarios.py                # 场景生成器 (Circle & Random)
├── metrics.py                  # 性能指标计算器
├── simulation_core.py          # 仿真核心模块
├── animation_generator.py      # 轨迹动画生成器
├── 
├── # 算法模块
├── Python-RVO2/               # ORCA (RVO2) Python绑定
├── python-vr-orca/            # VR-ORCA Python绑定
├── vr-orca/                   # VR-ORCA算法源码库
├── 
├── # 文档和脚本
├── docs/                      # 文档目录
│   └── DOCKER_README.md       # Docker使用指南
├── scripts/                   # 脚本目录
│   ├── install_in_docker.sh   # Docker环境安装脚本
│   └── run_in_docker.sh       # Docker运行脚本
└── 
```

## 主要功能模块

### 🎯 实验入口
- `comparison_experiments.py` - 运行VR-ORCA与ORCA的完整对比实验
- `run_experiment.py` - 快速性能对比测试

### ⚙️ 核心组件
- `config.py` - VR-ORCA算法的标准参数配置
- `scenarios.py` - Circle和Random场景生成
- `metrics.py` - Time/Distance/Penetration Ratio计算
- `simulation_core.py` - 集成ORCA和VR-ORCA算法调用

### 🐳 Docker支持
- `docs/DOCKER_README.md` - 详细的Docker部署指南
- `scripts/install_in_docker.sh` - 自动化环境安装
- `scripts/run_in_docker.sh` - 容器内运行脚本

### 📊 输出结果
实验结果自动保存到 `results_YYYYMMDD_HHMMSS/` 目录：
- 实验图表 (PNG格式)
- 实验数据 (JSON格式)
- 配置参数 (JSON格式)

## 快速开始

### 本地环境
```bash
python comparison_experiments.py  # 完整实验
python run_experiment.py         # 简单测试
```

### Docker环境
```bash
cd GenSwarm/docker
docker compose run vr-orca
# 容器内执行：
bash scripts/install_in_docker.sh
python comparison_experiments.py
```