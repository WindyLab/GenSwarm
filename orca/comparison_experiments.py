#!/usr/bin/env python
"""
VR-ORCA论文完整复刻实验

按照用户详细分析重新构建的模块化实验框架
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime
from config import ExperimentConfig
from simulation_core import run_single_experiment

# 设置matplotlib不显示图片
plt.ioff()  # 关闭交互模式
plt.switch_backend('Agg')  # 使用非交互后端

def run_neighborhood_range_experiment(scenario: str = "circle", output_dir: str = None):
    """运行邻域范围影响实验（图5）"""
    print(f"\n━━ 邻域范围影响实验 ({scenario.title()}场景) ━━")
    print(f"正在测试不同邻域范围对算法性能的影响...")
    
    config = ExperimentConfig()
    neighbor_ranges = config.NEIGHBORHOOD_RANGE_VALUES
    
    orca_results = []
    vrorca_results = []
    
    print(f"测试范围: {neighbor_ranges[0]}m 到 {neighbor_ranges[-1]}m")
    print(f"智能体数量: {config.NUM_AGENTS}个")
    print()
    
    for i, neighbor_range in enumerate(neighbor_ranges):
        print(f"[{i+1}/{len(neighbor_ranges)}] 测试邻域范围: {neighbor_range}m")
        
        # ORCA实验
        print("  • 运行ORCA算法...", end=" ")
        try:
            orca_metrics = run_single_experiment(
                "ORCA", scenario, neighbor_range=neighbor_range, max_time=50.0
            )
            orca_results.append(orca_metrics)
            print(f"✓ 成功 (Time: {orca_metrics.time_ratio:.3f}, Success: {orca_metrics.success_rate:.1%})")
        except Exception as e:
            print(f"✗ 失败: {e}")
            orca_results.append(None)
        
        # VR-ORCA实验
        print("  • 运行VR-ORCA算法...", end=" ")
        try:
            vrorca_metrics = run_single_experiment(
                "VR-ORCA", scenario, neighbor_range=neighbor_range, max_time=50.0
            )
            vrorca_results.append(vrorca_metrics)
            print(f"✓ 成功 (Time: {vrorca_metrics.time_ratio:.3f}, Success: {vrorca_metrics.success_rate:.1%})")
        except Exception as e:
            print(f"✗ 失败: {e}")
            vrorca_results.append(None)
        print()
    
    # 保存数据
    results = {
        'neighbor_ranges': neighbor_ranges.tolist(),
        'orca_results': [r.__dict__ if r else None for r in orca_results],
        'vrorca_results': [r.__dict__ if r else None for r in vrorca_results],
        'scenario': scenario,
        'experiment_type': 'neighborhood_range',
        'timestamp': datetime.now().isoformat()
    }
    
    if output_dir:
        data_file = os.path.join(output_dir, f"neighborhood_{scenario}_data.json")
        with open(data_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"数据已保存: {data_file}")
    
    return {
        'neighbor_ranges': neighbor_ranges,
        'orca_results': orca_results,
        'vrorca_results': vrorca_results
    }

def run_safety_weight_experiment(scenario: str = "circle", output_dir: str = None):
    """运行安全权重影响实验（图4）"""
    print(f"\n━━ 安全权重影响实验 ({scenario.title()}场景) ━━")
    print(f"正在测试不同安全权重γ对VR-ORCA性能的影响...")
    
    config = ExperimentConfig()
    safety_weights = config.SAFETY_WEIGHT_RANGE
    
    print(f"测试范围: γ = {safety_weights[0]} 到 {safety_weights[-1]}")
    print(f"智能体数量: {config.NUM_AGENTS}个")
    print()
    
    # ORCA只运行一次（没有安全权重参数）
    print("[1/1] 运行ORCA算法（无安全权重参数）...")
    orca_result = None
    try:
        orca_result = run_single_experiment("ORCA", scenario, max_time=50.0)
        print(f"  ✓ ORCA成功 (Time: {orca_result.time_ratio:.3f}, Success: {orca_result.success_rate:.1%})")
    except Exception as e:
        print(f"  ✗ ORCA失败: {e}")
    print()
    
    # VR-ORCA不同安全权重
    vrorca_results = []
    for i, safety_weight in enumerate(safety_weights):
        print(f"[{i+1}/{len(safety_weights)}] 测试VR-ORCA安全权重: γ={safety_weight}")
        
        try:
            vrorca_metrics = run_single_experiment(
                "VR-ORCA", scenario, safety_weight=safety_weight, max_time=50.0
            )
            vrorca_results.append(vrorca_metrics)
            print(f"  ✓ 成功 (Time: {vrorca_metrics.time_ratio:.3f}, Success: {vrorca_metrics.success_rate:.1%})")
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            vrorca_results.append(None)
    
    # 保存数据
    results = {
        'safety_weights': safety_weights.tolist(),
        'orca_result': orca_result.__dict__ if orca_result else None,
        'vrorca_results': [r.__dict__ if r else None for r in vrorca_results],
        'scenario': scenario,
        'experiment_type': 'safety_weight',
        'timestamp': datetime.now().isoformat()
    }
    
    if output_dir:
        data_file = os.path.join(output_dir, f"safety_{scenario}_data.json")
        with open(data_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n数据已保存: {data_file}")
    
    return {
        'safety_weights': safety_weights,
        'orca_result': orca_result,
        'vrorca_results': vrorca_results
    }

def plot_results(results, result_type, scenario, output_dir):
    """绘制结果并保存到文件"""
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    
    if result_type == "neighborhood":
        x_values = results['neighbor_ranges']
        orca_results = results['orca_results']
        vrorca_results = results['vrorca_results']
        
        # 提取数据
        orca_time = [r.time_ratio if r else np.nan for r in orca_results]
        orca_distance = [r.distance_ratio if r else np.nan for r in orca_results]
        orca_penetration = [r.penetration_ratio if r else np.nan for r in orca_results]
        
        vrorca_time = [r.time_ratio if r else np.nan for r in vrorca_results]
        vrorca_distance = [r.distance_ratio if r else np.nan for r in vrorca_results]
        vrorca_penetration = [r.penetration_ratio if r else np.nan for r in vrorca_results]
        
        # 绘图
        axes[0].plot(x_values, orca_time, 'o-', color='blue', label='ORCA', linewidth=2)
        axes[0].plot(x_values, vrorca_time, 'o-', color='red', label='VR-ORCA', linewidth=2)
        axes[0].set_xlabel('Neighborhood range (m)')
        
        axes[1].plot(x_values, orca_distance, 'o-', color='blue', linewidth=2)
        axes[1].plot(x_values, vrorca_distance, 'o-', color='red', linewidth=2)
        
        axes[2].plot(x_values, orca_penetration, 'o-', color='blue', linewidth=2)
        axes[2].plot(x_values, vrorca_penetration, 'o-', color='red', linewidth=2)
        
        filename = f'figure5_{scenario}_neighborhood.png'
        
        # 打印统计信息
        print(f"\n━━ {scenario.title()}场景邻域范围实验结果统计 ━━")
        valid_orca = [r for r in orca_results if r is not None]
        valid_vrorca = [r for r in vrorca_results if r is not None]
        
        if valid_orca:
            avg_orca_time = np.mean([r.time_ratio for r in valid_orca])
            avg_orca_success = np.mean([r.success_rate for r in valid_orca])
            print(f"ORCA平均性能: Time={avg_orca_time:.3f}, Success={avg_orca_success:.1%}")
        
        if valid_vrorca:
            avg_vrorca_time = np.mean([r.time_ratio for r in valid_vrorca])
            avg_vrorca_success = np.mean([r.success_rate for r in valid_vrorca])
            print(f"VR-ORCA平均性能: Time={avg_vrorca_time:.3f}, Success={avg_vrorca_success:.1%}")
            
            if valid_orca and valid_vrorca:
                improvement = ((avg_orca_time - avg_vrorca_time) / avg_orca_time) * 100
                print(f"VR-ORCA改进: {improvement:+.1f}% 时间效率")
        
    else:  # safety weight
        x_values = results['safety_weights']
        orca_result = results['orca_result']
        vrorca_results = results['vrorca_results']
        
        # ORCA结果（水平线）
        orca_time = orca_result.time_ratio if orca_result else 0
        orca_distance = orca_result.distance_ratio if orca_result else 0
        orca_penetration = orca_result.penetration_ratio if orca_result else 0
        
        # VR-ORCA结果
        vrorca_time = [r.time_ratio if r else np.nan for r in vrorca_results]
        vrorca_distance = [r.distance_ratio if r else np.nan for r in vrorca_results]
        vrorca_penetration = [r.penetration_ratio if r else np.nan for r in vrorca_results]
        
        # 绘图
        axes[0].plot(x_values, vrorca_time, 'o-', color='red', label='VR-ORCA', linewidth=2)
        axes[0].axhline(y=orca_time, color='blue', linestyle='-', linewidth=2, label='ORCA')
        axes[0].set_xlabel('Safety weight')
        
        axes[1].plot(x_values, vrorca_distance, 'o-', color='red', linewidth=2)
        axes[1].axhline(y=orca_distance, color='blue', linestyle='-', linewidth=2)
        
        axes[2].plot(x_values, vrorca_penetration, 'o-', color='red', linewidth=2)
        axes[2].axhline(y=orca_penetration, color='blue', linestyle='-', linewidth=2)
        
        filename = f'figure4_{scenario}_safety.png'
        
        # 打印统计信息
        print(f"\n━━ {scenario.title()}场景安全权重实验结果统计 ━━")
        if orca_result:
            print(f"ORCA性能: Time={orca_result.time_ratio:.3f}, Success={orca_result.success_rate:.1%}")
        
        valid_vrorca = [r for r in vrorca_results if r is not None]
        if valid_vrorca:
            best_vrorca = min(valid_vrorca, key=lambda x: x.time_ratio)
            best_gamma = x_values[vrorca_results.index(best_vrorca)]
            print(f"VR-ORCA最佳性能: Time={best_vrorca.time_ratio:.3f}, Success={best_vrorca.success_rate:.1%} (γ={best_gamma})")
            
            if orca_result:
                improvement = ((orca_result.time_ratio - best_vrorca.time_ratio) / orca_result.time_ratio) * 100
                print(f"最佳改进: {improvement:+.1f}% 时间效率")
    
    # 通用设置
    axes[0].set_ylabel('Time ratio')
    axes[0].set_title(f'{scenario.title()} Scenario')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_ylabel('Distance ratio')
    axes[1].grid(True, alpha=0.3)
    
    axes[2].set_ylabel('Maximum penetration ratio')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图片，不显示
    
    print(f"图表已保存: {filename}")

def run_complete_paper_experiments():
    """运行完整论文实验"""
    print("┌" + "─" * 58 + "┐")
    print("│" + " " * 10 + "VR-ORCA Paper Complete Replication" + " " * 10 + "│")
    print("│" + " " * 15 + "论文完整复刻实验" + " " * 15 + "│")
    print("└" + "─" * 58 + "┘")
    
    # 创建输出目录
    config = ExperimentConfig()
    output_dir = config.create_output_directory()
    print(f"\n输出目录: {output_dir}")
    
    start_time = datetime.now()
    print(f"实验开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 保存实验配置
    experiment_config = {
        'agent_radius': config.AGENT_RADIUS,
        'max_speed': config.MAX_SPEED,
        'preferred_speed': config.PREFERRED_SPEED,
        'time_step': config.TIME_STEP,
        'num_agents': config.NUM_AGENTS,
        'circle_radius': config.CIRCLE_RADIUS,
        'random_map_size': config.RANDOM_MAP_SIZE,
        'neighborhood_range_values': config.NEIGHBORHOOD_RANGE_VALUES.tolist(),
        'safety_weight_range': config.SAFETY_WEIGHT_RANGE.tolist(),
        'start_time': start_time.isoformat()
    }
    
    config_file = os.path.join(output_dir, 'experiment_config.json')
    with open(config_file, 'w') as f:
        json.dump(experiment_config, f, indent=2)
    
    # 1. 邻域范围实验（图5）
    print(f"\n{'='*60}")
    print("第一部分: 邻域范围影响实验 (Figure 5)")
    print(f"{'='*60}")
    
    for scenario in ['circle', 'random']:
        results = run_neighborhood_range_experiment(scenario, output_dir)
        plot_results(results, "neighborhood", scenario, output_dir)
    
    # 2. 安全权重实验（图4）
    print(f"\n\n{'='*60}")
    print("第二部分: 安全权重影响实验 (Figure 4)")
    print(f"{'='*60}")
    
    for scenario in ['circle', 'random']:
        results = run_safety_weight_experiment(scenario, output_dir)
        plot_results(results, "safety", scenario, output_dir)
    
    # 统计总结
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n\n┌" + "─" * 58 + "┐")
    print("│" + " " * 20 + "实验完成总结" + " " * 20 + "│")
    print("└" + "─" * 58 + "┘")
    
    print(f"实验结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总耗时: {duration.total_seconds():.1f}秒")
    print(f"输出目录: {output_dir}")
    
    print("\n生成的文件:")
    generated_files = [
        "experiment_config.json - 实验配置",
        "figure5_circle_neighborhood.png - Circle场景邻域分析",
        "figure5_random_neighborhood.png - Random场景邻域分析",
        "figure4_circle_safety.png - Circle场景安全权重分析",
        "figure4_random_safety.png - Random场景安全权重分析",
        "neighborhood_circle_data.json - Circle邻域数据",
        "neighborhood_random_data.json - Random邻域数据",
        "safety_circle_data.json - Circle安全权重数据",
        "safety_random_data.json - Random安全权重数据"
    ]
    
    for file_desc in generated_files:
        print(f"  • {file_desc}")
    
    print(f"\n✓ VR-ORCA论文复刻实验完成！")
    print(f"✓ 所有结果已保存到: {output_dir}")

if __name__ == "__main__":
    run_complete_paper_experiments()