#!/bin/bash

# VR-ORCA 环境运行脚本
# 使用Docker Compose运行VR-ORCA实验环境

echo "🐳 启动 VR-ORCA Docker 环境"
echo "============================="

# 切换到docker目录
cd "$(dirname "$0")/docker"

# 检查Docker和Docker Compose是否可用
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装或不可用"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装或不可用"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 构建并启动VR-ORCA容器
echo "🔧 构建 VR-ORCA 镜像..."
docker-compose build vr-orca

if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败"
    exit 1
fi

echo "🚀 启动 VR-ORCA 容器..."
echo ""
echo "容器启动后，所有模块已预编译完成，可以直接运行："
echo "1. 验证安装：         python quick_test.py"
echo "2. 运行完整实验：     python comparison_experiments.py"
echo "3. 简单测试：         python run_experiment.py"
echo ""
echo "退出容器：输入 'exit'"
echo ""

# 运行交互式容器
docker-compose run --rm vr-orca

echo "👋 VR-ORCA 环境已关闭"