#!/bin/bash

# VR-ORCA Docker环境安装脚本 (适配GenSwarm Docker环境)

echo "🐳 VR-ORCA GenSwarm Docker环境安装"
echo "===================================="

# 检查conda环境
if command -v conda &> /dev/null; then
    echo "✅ 检测到conda环境"
    source activate py310
    echo "🐍 已激活py310环境"
else
    echo "⚠️  未检测到conda，使用系统Python"
fi

# 检查当前目录
if [ ! -f "comparison_experiments.py" ]; then
    echo "📁 切换到orca目录..."
    cd /catkin_ws/src/code_llm/orca
fi

echo "📍 当前目录: $(pwd)"

# 安装系统依赖 (如果需要)
echo "📦 检查系统依赖..."
if ! dpkg -l | grep -q cmake; then
    echo "🔧 安装cmake..."
    apt-get update && apt-get install -y cmake
fi

if ! dpkg -l | grep -q libboost-all-dev; then
    echo "🔧 安装boost库..."
    apt-get install -y libboost-all-dev libeigen3-dev
fi

# 编译安装RVO2
echo "🔧 编译安装RVO2 (ORCA)..."
cd Python-RVO2
if [ -f "setup.py" ]; then
    python setup.py clean --all 2>/dev/null || true
    python setup.py build_ext --inplace
    python setup.py install
    echo "✅ RVO2安装完成"
else
    echo "❌ 未找到RVO2 setup.py文件"
    exit 1
fi

# 编译安装VR-ORCA
echo "🔧 编译安装VR-ORCA..."
cd ../python-vr-orca
if [ -f "setup.py" ]; then
    python setup.py clean --all 2>/dev/null || true
    python setup.py build_ext --inplace
    python setup.py install
    echo "✅ VR-ORCA安装完成"
else
    echo "❌ 未找到VR-ORCA setup.py文件"
    exit 1
fi

# 回到orca主目录
cd ..

# 测试安装
echo "🧪 测试模块安装..."
python -c "
try:
    import rvo2
    print('✅ RVO2 (ORCA) 模块加载成功')
except ImportError as e:
    print(f'❌ RVO2 模块加载失败: {e}')
    exit(1)

try:
    import vrorca
    print('✅ VR-ORCA 模块加载成功')
except ImportError as e:
    print(f'❌ VR-ORCA 模块加载失败: {e}')
    exit(1)

from config import ExperimentConfig
print('✅ 配置模块加载成功')

print('🎉 所有模块测试通过！')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 VR-ORCA环境安装完成！"
    echo "🚀 现在可以运行实验："
    echo "   python comparison_experiments.py  # 完整论文复刻实验"
    echo "   python run_experiment.py         # 简单性能测试"
    echo ""
    echo "💡 提示：实验结果将自动保存到带时间戳的文件夹中"
else
    echo "❌ 模块测试失败，请检查安装过程"
    exit 1
fi