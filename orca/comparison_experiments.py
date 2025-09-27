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
from typing import Dict, List, Tuple, Optional, Any, Union
from config import ExperimentConfig
from simulation_core import run_single_experiment
from metrics import PerformanceMetrics

# 设置matplotlib不显示图片
plt.ioff()  # 关闭交互模式
plt.switch_backend('Agg')  # 使用非交互后端


class ComparisonFramework:
    """
    VR-ORCA 对比实验框架
    
    提供完整的 VR-ORCA vs ORCA 对比实验功能，包括：
    - 多场景实验管理
    - 参数扫描实验
    - 结果收集和分析
    - 统计评估
    """
    
    def __init__(self, config: Optional[ExperimentConfig] = None):
        """
        初始化对比实验框架
        
        Args:
            config: 实验配置对象，如果为None则使用默认配置
        """
        self.config = config if config is not None else ExperimentConfig()
        self.results = {}
        self.experiment_metadata = {
            'start_time': None,
            'end_time': None,
            'total_experiments': 0,
            'successful_experiments': 0,
            'failed_experiments': 0
        }
        
    def run_scenario_comparison(self, 
                              scenario: str,
                              algorithms: List[str] = None,
                              **kwargs) -> Dict[str, Optional[PerformanceMetrics]]:
        """
        运行单个场景的算法对比实验
        
        Args:
            scenario: 场景名称 ('circle', 'random', 'corridor', 等)
            algorithms: 要测试的算法列表，默认为 ['ORCA', 'VR-ORCA']
            **kwargs: 传递给实验的额外参数
            
        Returns:
            算法结果字典 {algorithm_name: PerformanceMetrics}
        """
        if algorithms is None:
            algorithms = ['ORCA', 'VR-ORCA']
            
        scenario_results = {}
        
        print(f"\n运行 {scenario.upper()} 场景对比实验...")
        print(f"测试算法: {', '.join(algorithms)}")
        
        for algorithm in algorithms:
            print(f"  • 测试 {algorithm}...", end=" ")
            
            try:
                # 运行单个实验
                metrics = run_single_experiment(
                    algorithm=algorithm,
                    scenario=scenario,
                    **kwargs
                )
                
                scenario_results[algorithm.lower()] = metrics
                self.experiment_metadata['successful_experiments'] += 1
                
                print(f"✓ 成功 (Time: {metrics.time_ratio:.3f}, Success: {metrics.success_rate:.1%})")
                
            except Exception as e:
                scenario_results[algorithm.lower()] = None
                self.experiment_metadata['failed_experiments'] += 1
                print(f"✗ 失败: {str(e)[:50]}...")
            
            self.experiment_metadata['total_experiments'] += 1
        
        return scenario_results
    
    def run_parameter_sweep(self, 
                          parameter_name: str,
                          parameter_values: List[float],
                          scenario: str = "circle",
                          algorithms: List[str] = None) -> Dict[str, Any]:
        """
        运行参数扫描实验
        
        Args:
            parameter_name: 参数名称 (如 'neighbor_range', 'safety_weight')
            parameter_values: 参数值列表
            scenario: 测试场景
            algorithms: 要测试的算法列表
            
        Returns:
            参数扫描结果字典
        """
        if algorithms is None:
            algorithms = ['ORCA', 'VR-ORCA']
            
        print(f"\n━━ {parameter_name.replace('_', ' ').title()} 参数扫描实验 ━━")
        print(f"场景: {scenario.upper()}")
        print(f"参数范围: {parameter_values[0]} 到 {parameter_values[-1]}")
        print(f"测试点数: {len(parameter_values)}")
        print()
        
        sweep_results = {
            'parameter_name': parameter_name,
            'parameter_values': parameter_values,
            'scenario': scenario,
            'algorithms': algorithms
        }
        
        # 为每个算法初始化结果列表
        for algorithm in algorithms:
            sweep_results[f'{algorithm.lower()}_results'] = []
        
        for i, param_value in enumerate(parameter_values):
            print(f"[{i+1}/{len(parameter_values)}] 测试 {parameter_name} = {param_value}")
            
            # 构建参数字典
            experiment_params = {parameter_name: param_value}
            
            # 运行对比实验
            scenario_results = self.run_scenario_comparison(
                scenario=scenario,
                algorithms=algorithms,
                **experiment_params
            )
            
            # 保存结果
            for algorithm in algorithms:
                algorithm_key = f'{algorithm.lower()}_results'
                result = scenario_results.get(algorithm.lower())
                sweep_results[algorithm_key].append(result)
        
        return sweep_results
    
    def run_multi_scenario_comparison(self, 
                                    scenarios: List[str],
                                    algorithms: List[str] = None,
                                    **kwargs) -> Dict[str, Dict[str, Optional[PerformanceMetrics]]]:
        """
        运行多场景对比实验
        
        Args:
            scenarios: 场景列表
            algorithms: 算法列表
            **kwargs: 实验参数
            
        Returns:
            多场景结果字典 {scenario: {algorithm: metrics}}
        """
        if algorithms is None:
            algorithms = ['ORCA', 'VR-ORCA']
            
        print(f"\n━━ 多场景对比实验 ━━")
        print(f"场景: {', '.join([s.upper() for s in scenarios])}")
        print(f"算法: {', '.join(algorithms)}")
        print()
        
        multi_scenario_results = {}
        
        for scenario in scenarios:
            scenario_results = self.run_scenario_comparison(
                scenario=scenario,
                algorithms=algorithms,
                **kwargs
            )
            multi_scenario_results[scenario] = scenario_results
        
        return multi_scenario_results
    
    def run_complete_comparison_suite(self, 
                                    output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        运行完整的对比实验套件
        
        Args:
            output_dir: 输出目录，如果为None则自动创建
            
        Returns:
            完整实验结果字典
        """
        self.experiment_metadata['start_time'] = datetime.now()
        
        if output_dir is None:
            output_dir = self.config.create_output_directory()
        
        print("┌" + "─" * 58 + "┐")
        print("│" + " " * 15 + "VR-ORCA Complete Comparison" + " " * 15 + "│")
        print("│" + " " * 18 + "完整对比实验套件" + " " * 18 + "│")
        print("└" + "─" * 58 + "┘")
        print(f"\n输出目录: {output_dir}")
        
        complete_results = {
            'basic_comparison': {},
            'parameter_sweeps': {},
            'metadata': self.experiment_metadata.copy()
        }
        
        # 1. 基础场景对比
        print(f"\n{'='*60}")
        print("第一部分: 基础场景对比")
        print(f"{'='*60}")
        
        basic_scenarios = ['circle', 'random']
        basic_results = self.run_multi_scenario_comparison(basic_scenarios)
        complete_results['basic_comparison'] = basic_results
        
        # 2. 邻域范围参数扫描
        print(f"\n{'='*60}")
        print("第二部分: 邻域范围参数扫描")
        print(f"{'='*60}")
        
        for scenario in basic_scenarios:
            sweep_results = self.run_parameter_sweep(
                parameter_name='neighbor_range',
                parameter_values=self.config.NEIGHBORHOOD_RANGE_VALUES.tolist(),
                scenario=scenario
            )
            complete_results['parameter_sweeps'][f'neighborhood_{scenario}'] = sweep_results
        
        # 3. 安全权重参数扫描
        print(f"\n{'='*60}")
        print("第三部分: 安全权重参数扫描")
        print(f"{'='*60}")
        
        for scenario in basic_scenarios:
            sweep_results = self.run_parameter_sweep(
                parameter_name='safety_weight',
                parameter_values=self.config.SAFETY_WEIGHT_RANGE.tolist(),
                scenario=scenario
            )
            complete_results['parameter_sweeps'][f'safety_{scenario}'] = sweep_results
        
        # 更新元数据
        self.experiment_metadata['end_time'] = datetime.now()
        complete_results['metadata'] = self.experiment_metadata.copy()
        
        # 保存结果
        self._save_results(complete_results, output_dir)
        
        # 打印总结
        self._print_experiment_summary(complete_results, output_dir)
        
        return complete_results
    
    def _save_results(self, results: Dict[str, Any], output_dir: str) -> None:
        """
        保存实验结果到文件
        
        Args:
            results: 实验结果
            output_dir: 输出目录
        """
        # 保存完整结果
        results_file = os.path.join(output_dir, 'comparison_results.json')
        
        # 转换结果为可序列化格式
        serializable_results = self._make_serializable(results)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n结果已保存到: {results_file}")
    
    def _make_serializable(self, obj: Any) -> Any:
        """
        将对象转换为JSON可序列化格式
        
        Args:
            obj: 要转换的对象
            
        Returns:
            可序列化的对象
        """
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):  # ExperimentMetrics等对象
            return self._make_serializable(obj.__dict__)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        else:
            return obj
    
    def _print_experiment_summary(self, results: Dict[str, Any], output_dir: str) -> None:
        """
        打印实验总结
        
        Args:
            results: 实验结果
            output_dir: 输出目录
        """
        metadata = results['metadata']
        start_time = metadata['start_time']
        end_time = metadata['end_time']
        
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        
        duration = end_time - start_time
        
        print(f"\n\n┌" + "─" * 58 + "┐")
        print("│" + " " * 20 + "实验完成总结" + " " * 20 + "│")
        print("└" + "─" * 58 + "┘")
        
        print(f"实验开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"实验结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration.total_seconds():.1f}秒")
        print(f"总实验数: {metadata['total_experiments']}")
        print(f"成功实验: {metadata['successful_experiments']}")
        print(f"失败实验: {metadata['failed_experiments']}")
        print(f"成功率: {metadata['successful_experiments']/metadata['total_experiments']:.1%}")
        print(f"输出目录: {output_dir}")
        
        print("\n✓ VR-ORCA 完整对比实验完成！")
        print(f"✓ 所有结果已保存到: {output_dir}")
    
    def get_summary_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算实验结果的统计摘要
        
        Args:
            results: 实验结果
            
        Returns:
            统计摘要字典
        """
        summary = {
            'scenarios_tested': [],
            'algorithms_compared': [],
            'performance_improvements': {},
            'success_rates': {},
            'parameter_sensitivities': {}
        }
        
        # 基础对比统计
        if 'basic_comparison' in results:
            basic_results = results['basic_comparison']
            
            for scenario, scenario_results in basic_results.items():
                summary['scenarios_tested'].append(scenario)
                
                orca_result = scenario_results.get('orca')
                vrorca_result = scenario_results.get('vrorca')
                
                if orca_result and vrorca_result:
                    # 计算性能改进
                    time_improvement = ((orca_result.time_ratio - vrorca_result.time_ratio) / orca_result.time_ratio) * 100
                    distance_improvement = ((orca_result.distance_ratio - vrorca_result.distance_ratio) / orca_result.distance_ratio) * 100
                    
                    summary['performance_improvements'][scenario] = {
                        'time_improvement_percent': time_improvement,
                        'distance_improvement_percent': distance_improvement,
                        'success_rate_improvement': (vrorca_result.success_rate - orca_result.success_rate) * 100
                    }
                    
                    summary['success_rates'][scenario] = {
                        'orca': orca_result.success_rate,
                        'vrorca': vrorca_result.success_rate
                    }
        
        return summary

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