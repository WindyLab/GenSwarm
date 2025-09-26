#!/usr/bin/env python3
"""
容器内简单验证脚本
"""

def simple_container_test():
    print("🧪 容器内 VR-ORCA 验证")
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
    
    # 2. 测试 RVO2
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
    
    # 3. 测试 VR-ORCA（简化版）
    try:
        import vrorca
        print("✅ VR-ORCA 模块导入成功")
        
        # 检查可用的属性
        attrs = [attr for attr in dir(vrorca) if not attr.startswith('_')]
        print(f"   可用接口: {', '.join(attrs[:5])}...")
        
        # 尝试创建仿真器
        if hasattr(vrorca, 'PyVRORCASimulator'):
            sim = vrorca.PyVRORCASimulator(
                timeStep=0.25, neighborDist=6.0, maxNeighbors=10,
                timeHorizon=10.0, timeHorizonObst=10.0, 
                radius=0.6, maxSpeed=0.8, prefSpeed=0.4
            )
            agent = sim.addAgent((0.0, 0.0))
            sim.setAgentPrefVelocity(agent, (1.0, 0.0))
            sim.doStep()
            pos = sim.getAgentPosition(agent)
            print(f"✅ VR-ORCA 仿真 OK - 位置: [{pos[0]:.2f}, {pos[1]:.2f}]")
        else:
            print("⚠️  VR-ORCA 接口与预期不同，但模块加载成功")
            
    except Exception as e:
        print(f"❌ VR-ORCA 失败: {e}")
        return False
    
    # 4. 测试配置文件
    try:
        from config import ExperimentConfig
        config = ExperimentConfig()
        print(f"✅ 配置 OK - {config.num_agents} 智能体")
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        return False
    
    print("-" * 30)
    print("🎉 容器验证完成！")
    print("🚀 可以运行实验:")
    print("   python comparison_experiments.py")
    print("   python run_experiment.py")
    return True

if __name__ == "__main__":
    simple_container_test()