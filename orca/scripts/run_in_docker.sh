#!/bin/bash

# VR-ORCA实验运行脚本 (适用于现有Docker Compose环境)

echo "🚀 VR-ORCA实验启动脚本"
echo "======================"

# 检查当前目录
if [ ! -f "comparison_experiments.py" ]; then
    echo "❌ 请在orca目录下运行此脚本"
    exit 1
fi

echo "📁 当前目录: $(pwd)"

# 创建结果目录
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="docker_results_${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo "📊 结果将保存到: $RESULTS_DIR"

# 设置环境变量
export MPLBACKEND=Agg
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "🔧 环境变量设置完成"

# 检查模块可用性
echo "🧪 检查模块..."
python -c "
import sys
sys.path.append('$(pwd)')

try:
    import rvo2
    print('✅ RVO2 (ORCA) 模块可用')
except ImportError:
    print('❌ RVO2 模块不可用，需要先安装')
    exit(1)

try:
    import vrorca
    print('✅ VR-ORCA 模块可用')
except ImportError:
    print('❌ VR-ORCA 模块不可用，需要先安装')
    exit(1)

print('🎉 所有模块检查通过！')
"

if [ $? -ne 0 ]; then
    echo ""
    echo "🛠️  需要先安装模块，运行安装脚本："
    echo "   bash install_in_docker.sh"
    echo ""
    echo "或者手动安装："
    echo "   cd Python-RVO2 && python setup.py install"
    echo "   cd python-vr-orca && python setup.py install"
    exit 1
fi

# 运行实验
echo ""
echo "🎯 开始运行VR-ORCA实验..."
echo "⏱️  这可能需要几分钟时间..."

# 修改配置文件，将输出目录设置为我们创建的目录
python -c "
import sys
sys.path.append('$(pwd)')
from config import ExperimentConfig
config = ExperimentConfig()
# 创建自定义输出目录函数
def create_custom_output_directory():
    return '$(pwd)/$RESULTS_DIR'
config.create_output_directory = create_custom_output_directory
"

# 运行实验
python comparison_experiments.py

if [ $? -eq 0 ]; then
    echo "🎉 实验完成！"
    echo "📊 结果已保存到: $RESULTS_DIR"
    echo ""
    echo "生成的文件："
    ls -la "$RESULTS_DIR/"
else
    echo "❌ 实验失败"
    exit 1
fi