# VR-ORCA Docker 运行指南

## 🚀 快速启动

你现在有两种方式来运行 VR-ORCA 环境：

### 方式一：使用便捷脚本（推荐）

```bash
# 在项目根目录运行
./run_vr_orca.sh
```

### 方式二：直接使用 Docker Compose

```bash
# 切换到 docker 目录
cd docker

# 构建并运行 VR-ORCA 容器
docker-compose run --rm vr-orca
```

## 📋 容器内操作步骤

启动容器后，你将进入 `/catkin_ws/src/code_llm/orca` 目录，请按以下步骤操作：

### 1. 安装 VR-ORCA 模块
```bash
bash scripts/install_in_docker.sh
```

这个脚本会：
- 检查并安装必要的系统依赖
- 编译安装 RVO2 (ORCA) 模块
- 编译安装 VR-ORCA 模块
- 测试模块安装是否成功

### 2. 运行实验

**完整对比实验**（推荐，包含VR-ORCA与ORCA的完整对比）：
```bash
python comparison_experiments.py
```

**简单性能测试**：
```bash
python run_experiment.py
```

**快速验证安装**：
```bash
python -c "import rvo2; import vrorca; print('✅ 所有模块加载成功')"
```

## 📊 实验结果

- 实验结果会自动保存到带时间戳的目录中
- 包含性能指标统计和可视化图表
- 完整实验大约需要 10-30 分钟

## 🛠 故障排除

### 如果遇到构建错误：
```bash
# 重新构建镜像
docker-compose build --no-cache vr-orca
```

### 如果模块安装失败：
```bash
# 检查依赖
apt-get update && apt-get install -y cmake libboost-all-dev libeigen3-dev

# 手动安装模块
cd Python-RVO2 && python setup.py install
cd ../python-vr-orca && python setup.py install
```

### 如果需要清理环境：
```bash
# 删除所有相关镜像
docker-compose down --rmi all
docker system prune -f
```

## 📁 重要目录

- `/catkin_ws/src/code_llm/orca/` - VR-ORCA 主目录
- `/catkin_ws/src/code_llm/orca/results/` - 实验结果目录
- `/catkin_ws/src/code_llm/orca/scripts/` - 脚本目录

## 💡 提示

- 容器使用 `py310` conda 环境
- 所有 Python 依赖都已预装
- 支持图形输出（使用 Agg 后端）
- 退出容器使用 `exit` 命令