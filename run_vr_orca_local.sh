#!/bin/bash

# VR-ORCA 快速本地运行脚本
# 不依赖 Docker，直接在本地运行

echo "🚀 VR-ORCA 本地环境快速设置"
echo "================================"

# 检查当前目录
if [ ! -d "orca" ]; then
    echo "❌ 请在 GenSwarm 项目根目录运行此脚本"
    exit 1
fi

cd orca

echo "📁 当前目录: $(pwd)"

# 检查 Python 环境
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到 Python 环境"
    exit 1
fi

echo "🐍 使用 Python: $PYTHON_CMD"

# 检查必要的 Python 包
echo "📦 检查 Python 依赖..."
$PYTHON_CMD -c "import numpy, matplotlib, sys; print('✅ 基础依赖可用')" 2>/dev/null || {
    echo "⚠️  缺少基础依赖，尝试安装..."
    pip install numpy matplotlib cython scipy
}

# 检查系统编译工具
echo "🔧 检查编译工具..."
if ! command -v cmake &> /dev/null; then
    echo "⚠️  需要安装 CMake"
    echo "macOS: brew install cmake"
    echo "Ubuntu: sudo apt install cmake"
    exit 1
fi

echo "✅ CMake 可用"

# 尝试编译安装 RVO2
echo "🔧 编译 RVO2 (ORCA)..."
cd Python-RVO2
if [ -f "setup.py" ]; then
    $PYTHON_CMD setup.py build_ext --inplace
    if [ $? -eq 0 ]; then
        echo "✅ RVO2 编译成功"
        $PYTHON_CMD setup.py install --user
    else
        echo "⚠️  RVO2 编译失败，但可能仍可使用"
    fi
else
    echo "❌ 未找到 RVO2 setup.py"
fi

# 尝试编译安装 VR-ORCA
echo "🔧 编译 VR-ORCA..."
cd ../python-vr-orca
if [ -f "setup.py" ]; then
    $PYTHON_CMD setup.py build_ext --inplace
    if [ $? -eq 0 ]; then
        echo "✅ VR-ORCA 编译成功"
        $PYTHON_CMD setup.py install --user
    else
        echo "⚠️  VR-ORCA 编译失败，但可能仍可使用"
    fi
else
    echo "❌ 未找到 VR-ORCA setup.py"
fi

# 回到主目录
cd ..

# 设置环境变量
export MPLBACKEND=Agg
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 测试模块
echo "🧪 测试模块安装..."
$PYTHON_CMD -c "
import sys
sys.path.insert(0, '$(pwd)')

try:
    import rvo2
    print('✅ RVO2 (ORCA) 模块可用')
except ImportError as e:
    print(f'⚠️  RVO2 模块问题: {e}')

try:
    import vrorca
    print('✅ VR-ORCA 模块可用')
except ImportError as e:
    print(f'⚠️  VR-ORCA 模块问题: {e}')

try:
    from config import ExperimentConfig
    print('✅ 配置模块可用')
except ImportError as e:
    print(f'⚠️  配置模块问题: {e}')

print('🎯 可以尝试运行实验')
"

echo ""
echo "🎉 本地环境设置完成！"
echo ""
echo "🚀 现在可以运行："
echo "   $PYTHON_CMD run_experiment.py           # 简单测试"
echo "   $PYTHON_CMD comparison_experiments.py   # 完整实验"
echo ""
echo "💡 如果遇到模块导入错误，可能需要安装额外依赖："
echo "   macOS: brew install boost eigen"
echo "   Ubuntu: sudo apt install libboost-all-dev libeigen3-dev"