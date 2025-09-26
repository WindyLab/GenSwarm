#!/usr/bin/env python3
"""
VR-ORCA 环境验证脚本
此脚本应该在 Docker 镜像构建后立即可用
"""

def quick_test():
    print("⚡ VR-ORCA 环境验证")
    print("-" * 30)
    
    # 1. 测试基础模块
    try:
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        print("✅ 基础模块 OK")
    except ImportError as e:
        print(f"❌ 基础模块失败: {e}")
        return False
    
    # 2. 测试 RVO2 (ORCA)
    try:
        import rvo2
        sim = rvo2.PyRVOSimulator(0.25, 6.0, 10, 10.0, 10.0, 0.6, 0.8)
        agent = sim.addAgent((0.0, 0.0))
        sim.setAgentPrefVelocity(agent, (1.0, 0.0))
        sim.doStep()
        pos = sim.getAgentPosition(agent)
        print(f"✅ RVO2 (ORCA) OK - 位置: [{pos[0]:.2f}, {pos[1]:.2f}]")
    except Exception as e:
        print(f"❌ RVO2 失败: {e}")
        return False
    
    # 3. 测试 VR-ORCA
    try:
        import vrorca
        # VR-ORCA 使用 PyVRORCASimulator 接口
        sim = vrorca.PyVRORCASimulator(
            timeStep=0.25,
            neighborDist=6.0,
            maxNeighbors=10,
            timeHorizon=10.0,
            timeHorizonObst=10.0,
            radius=0.6,
            maxSpeed=0.8,
            prefSpeed=0.4,
            velocity=(0.0, 0.0)
        )
        agent = sim.addAgent((0.0, 0.0))
        sim.setAgentPrefVelocity(agent, (1.0, 0.0))
        sim.doStep()
        pos = sim.getAgentPosition(agent)
        print(f"✅ VR-ORCA OK - 位置: [{pos[0]:.2f}, {pos[1]:.2f}]")
    except Exception as e:
        print(f"❌ VR-ORCA 失败: {e}")
        return False
    
    # 4. 测试配置
    try:
        from config import ExperimentConfig
        config = ExperimentConfig()
        print(f"✅ 配置 OK - {config.NUM_AGENTS} 智能体")
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        return False
    
    print("-" * 30)
    print("🎉 所有功能正常！镜像构建成功")
    print("🚀 可以直接运行实验:")
    print("   python comparison_experiments.py")
    print("   python run_experiment.py")
    return True

if __name__ == "__main__":
    quick_test()