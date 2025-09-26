#!/usr/bin/env python
"""
简单的实验运行脚本

测试新的模块化架构，输出详细的性能指标
"""

from simulation_core import run_single_experiment
from datetime import datetime
import os
import json
import traceback

def run_simple_test():
    """运行简单测试"""
    print("┌" + "─" * 48 + "┐")
    print("│" + " " * 12 + "VR-ORCA vs ORCA Simple Test" + " " * 12 + "│")
    print("│" + " " * 16 + "简单性能对比测试" + " " * 16 + "│")
    print("└" + "─" * 48 + "┘")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"/Users/wenkang/GenSwarm/orca/simple_test_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输出目录: {output_dir}")
    print(f"测试场景: Circle场景 (小规模测试)")
    print(f"仿真时长: 20秒")
    
    results = {}
    
    try:
        # 测试ORCA
        print("\n" + "─" * 30)
        print("🔵 测试ORCA算法...")
        print("─" * 30)
        
        orca_metrics = run_single_experiment("ORCA", "circle", max_time=20.0)
        results['orca'] = orca_metrics.__dict__
        
        print(f"✓ ORCA测试完成")
        print(f"  • 时间比率: {orca_metrics.time_ratio:.3f}")
        print(f"  • 距离比率: {orca_metrics.distance_ratio:.3f}")
        print(f"  • 穿透比率: {orca_metrics.penetration_ratio:.3f}")
        print(f"  • 成功率: {orca_metrics.success_rate:.1%}")
        print(f"  • 平均决策时间: {orca_metrics.average_decision_time:.2f}ms")
        print(f"  • 总仿真时间: {orca_metrics.total_simulation_time:.1f}s")
        
        # 测试VR-ORCA
        print("\n" + "─" * 30)
        print("🔴 测试VR-ORCA算法...")
        print("─" * 30)
        
        vrorca_metrics = run_single_experiment("VR-ORCA", "circle", max_time=20.0)
        results['vr_orca'] = vrorca_metrics.__dict__
        
        print(f"✓ VR-ORCA测试完成")
        print(f"  • 时间比率: {vrorca_metrics.time_ratio:.3f}")
        print(f"  • 距离比率: {vrorca_metrics.distance_ratio:.3f}")
        print(f"  • 穿透比率: {vrorca_metrics.penetration_ratio:.3f}")
        print(f"  • 成功率: {vrorca_metrics.success_rate:.1%}")
        print(f"  • 平均决策时间: {vrorca_metrics.average_decision_time:.2f}ms")
        print(f"  • 总仿真时间: {vrorca_metrics.total_simulation_time:.1f}s")
        
        # 对比分析
        print("\n" + "═" * 50)
        print("📊 性能对比分析")
        print("═" * 50)
        
        time_improvement = ((orca_metrics.time_ratio - vrorca_metrics.time_ratio) / orca_metrics.time_ratio) * 100
        distance_improvement = ((orca_metrics.distance_ratio - vrorca_metrics.distance_ratio) / orca_metrics.distance_ratio) * 100
        success_diff = (vrorca_metrics.success_rate - orca_metrics.success_rate) * 100
        decision_overhead = ((vrorca_metrics.average_decision_time - orca_metrics.average_decision_time) / orca_metrics.average_decision_time) * 100
        
        print(f"时间效率改进: {time_improvement:+.1f}%")
        print(f"距离效率改进: {distance_improvement:+.1f}%")
        print(f"成功率差异: {success_diff:+.1f}%")
        print(f"决策时间开销: {decision_overhead:+.1f}%")
        
        if time_improvement > 0:
            print(f"\n✅ VR-ORCA在时间效率上优于ORCA {time_improvement:.1f}%")
        else:
            print(f"\n❌ VR-ORCA在时间效率上不如ORCA {abs(time_improvement):.1f}%")
        
        # 保存结果
        results['comparison'] = {
            'time_improvement_percent': time_improvement,
            'distance_improvement_percent': distance_improvement,
            'success_rate_difference_percent': success_diff,
            'decision_time_overhead_percent': decision_overhead,
            'test_timestamp': datetime.now().isoformat()
        }
        
        result_file = os.path.join(output_dir, 'simple_test_results.json')
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📁 测试结果已保存到: {result_file}")
        print("\n✓ 简单测试完成成功！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        
        # 保存错误信息
        error_info = {
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        error_file = os.path.join(output_dir, 'error_log.json')
        with open(error_file, 'w') as f:
            json.dump(error_info, f, indent=2)
        
        print(f"错误信息已保存到: {error_file}")

if __name__ == "__main__":
    run_simple_test()