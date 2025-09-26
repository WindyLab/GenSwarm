#!/usr/bin/env python
"""
VR-ORCA论文实验配置参数

严格按照论文Table I设置所有参数
"""

import numpy as np
import os
from datetime import datetime

class ExperimentConfig:
    """实验配置类，包含所有论文中的参数设置"""
    
    # 论文Table I中的核心参数
    AGENT_RADIUS = 0.6          # r = 0.6 m
    MAX_SPEED = 0.8             # v_max = 0.8 m/s  
    PREFERRED_SPEED = 0.4       # 偏好速度 = 0.4 m/s
    NEIGHBORHOOD_RANGE = 6.0    # d_max = 6 m
    TIME_STEP = 0.25           # dt = 0.25 s
    TIME_HORIZON = 10.0        # tau = 10 s
    
    # VR-ORCA特有参数
    GRAD_STEPS = 100           # M = 100 (梯度下降步数)
    SAFETY_WEIGHT = 100.0      # gamma (变量测试参数)
    
    # 场景参数
    CIRCLE_RADIUS = 80.0       # Circle场景圆半径 80m
    RANDOM_MAP_SIZE = 30.0     # Random场景地图大小 30m x 30m
    NUM_AGENTS = 100           # 智能体数量 100个
    POSITION_NOISE = 1e-5      # 位置噪声范围 [-1e-5, 1e-5]
    
    # 仿真参数
    MAX_SIMULATION_TIME = 1000.0  # 最大仿真时间 (秒)
    GOAL_THRESHOLD = 0.5          # 到达目标的距离阈值
    
    # 实验变量范围 (用于参数扫描)
    SAFETY_WEIGHT_RANGE = np.arange(0, 201, 10)      # gamma: 0-200, 步长10
    NEIGHBORHOOD_RANGE_VALUES = np.arange(2, 11)     # neighbor range: 2-10m
    
    # 统计参数
    NUM_INDEPENDENT_RUNS = 100   # 独立运行次数 (论文中是1000次，这里为了测试设为100)
    
    @classmethod
    def get_circle_scenario_config(cls):
        """获取Circle场景配置"""
        return {
            'num_agents': cls.NUM_AGENTS,
            'circle_radius': cls.CIRCLE_RADIUS,
            'noise': cls.POSITION_NOISE
        }
    
    @classmethod 
    def get_random_scenario_config(cls):
        """获取Random场景配置"""
        return {
            'num_agents': cls.NUM_AGENTS,
            'map_size': cls.RANDOM_MAP_SIZE,
            'noise': cls.POSITION_NOISE
        }
    
    @classmethod
    def get_orca_config(cls, neighbor_range=None):
        """获取ORCA算法配置"""
        return {
            'time_step': cls.TIME_STEP,
            'neighbor_dist': neighbor_range or cls.NEIGHBORHOOD_RANGE,
            'max_neighbors': 10,
            'time_horizon': cls.TIME_HORIZON,
            'time_horizon_obst': cls.TIME_HORIZON,
            'radius': cls.AGENT_RADIUS,
            'max_speed': cls.MAX_SPEED
        }
    
    @classmethod
    def create_output_directory(cls):
        """创建新的输出目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 检查是否在GenSwarm Docker环境中
        if os.path.exists('/catkin_ws/src/code_llm'):
            # GenSwarm Docker环境
            base_dir = "/catkin_ws/src/code_llm/orca"
        elif os.path.exists('/.dockerenv'):
            # 其他Docker环境
            base_dir = "/app/results"
        else:
            # 本地环境
            base_dir = "/Users/wenkang/GenSwarm/orca"
        
        output_dir = f"{base_dir}/results_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        return output_dir


# 性能指标配置
class MetricsConfig:
    """性能指标计算配置"""
    
    # 三个核心指标
    METRICS = ['time_ratio', 'distance_ratio', 'penetration_ratio']
    
    # 额外统计指标
    ADDITIONAL_METRICS = [
        'success_rate',           # 成功率
        'computation_time',       # 计算时间  
        'average_decision_time',  # 平均决策时间
        'max_decision_time'       # 最大决策时间
    ]
    
    @staticmethod
    def calculate_time_ratio(actual_time, ideal_time):
        """计算时间比率"""
        return actual_time / ideal_time if ideal_time > 0 else float('inf')
    
    @staticmethod
    def calculate_distance_ratio(actual_distance, ideal_distance):
        """计算距离比率"""
        return actual_distance / ideal_distance if ideal_distance > 0 else float('inf')
    
    @staticmethod
    def calculate_penetration_ratio(max_penetration, agent_radius):
        """计算穿透比率"""
        return max_penetration / agent_radius if agent_radius > 0 else 0


# 可视化配置
class VisualizationConfig:
    """可视化配置"""
    
    # Pygame窗口设置
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 900
    FPS = 60
    
    # 绘图颜色
    BACKGROUND_COLOR = (255, 255, 255)  # 白色背景
    AGENT_COLOR = (0, 100, 200)        # 蓝色智能体
    GOAL_COLOR = (200, 0, 0)           # 红色目标
    TRAJECTORY_COLOR = (100, 100, 100) # 灰色轨迹
    
    # 缩放参数
    SCALE_FACTOR = 5.0  # 米到像素的缩放比例
    
    # matplotlib图表设置
    FIGURE_SIZE = (12, 8)
    DPI = 300
    FONT_SIZE = 12
    
    @staticmethod
    def world_to_screen(pos, offset=(600, 450)):
        """世界坐标转屏幕坐标"""
        return (
            int(pos[0] * VisualizationConfig.SCALE_FACTOR + offset[0]),
            int(-pos[1] * VisualizationConfig.SCALE_FACTOR + offset[1])  # Y轴翻转
        )


if __name__ == "__main__":
    # 测试配置
    print("VR-ORCA实验配置测试")
    print("=" * 40)
    
    config = ExperimentConfig()
    print(f"智能体半径: {config.AGENT_RADIUS}m")
    print(f"最大速度: {config.MAX_SPEED}m/s") 
    print(f"时间步长: {config.TIME_STEP}s")
    print(f"邻域范围: {config.NEIGHBORHOOD_RANGE}m")
    
    print("\nCircle场景配置:")
    circle_config = config.get_circle_scenario_config()
    for key, value in circle_config.items():
        print(f"  {key}: {value}")
    
    print("\nORCA算法配置:")
    orca_config = config.get_orca_config()
    for key, value in orca_config.items():
        print(f"  {key}: {value}")
    
    print("\n配置验证完成!")