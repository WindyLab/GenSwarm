#!/usr/bin/env python
"""
VR-ORCA论文场景生成器

实现Circle和Random两个标准测试场景
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from config import ExperimentConfig


@dataclass
class AgentState:
    """智能体状态"""
    id: int
    position: np.ndarray  # [x, y]
    velocity: np.ndarray  # [vx, vy] 
    goal: np.ndarray      # [gx, gy]
    radius: float
    max_speed: float
    preferred_speed: float
    
    def __post_init__(self):
        """确保数组格式正确"""
        self.position = np.array(self.position, dtype=np.float64)
        self.velocity = np.array(self.velocity, dtype=np.float64)
        self.goal = np.array(self.goal, dtype=np.float64)
    
    def distance_to_goal(self) -> float:
        """计算到目标的距离"""
        return np.linalg.norm(self.goal - self.position)
    
    def has_reached_goal(self, threshold: float = 0.5) -> bool:
        """判断是否到达目标"""
        return self.distance_to_goal() < threshold
    
    def get_preferred_velocity(self) -> np.ndarray:
        """计算偏好速度"""
        direction = self.goal - self.position
        distance = np.linalg.norm(direction)
        
        if distance < 1e-6:
            return np.zeros(2)
        
        # 归一化方向向量，乘以偏好速度
        return (direction / distance) * self.preferred_speed
    
    def update_state(self, new_velocity: np.ndarray, dt: float):
        """更新智能体状态"""
        # 限制速度大小
        speed = np.linalg.norm(new_velocity)
        if speed > self.max_speed:
            new_velocity = new_velocity * (self.max_speed / speed)
        
        self.velocity = new_velocity
        self.position += self.velocity * dt


class ScenarioGenerator:
    """场景生成器"""
    
    def __init__(self, config: ExperimentConfig = None):
        self.config = config or ExperimentConfig()
    
    def setup_circle_scenario(self, num_agents: int = None, 
                            circle_radius: float = None,
                            noise: float = None) -> List[AgentState]:
        """
        创建Circle场景
        
        Args:
            num_agents: 智能体数量 (默认100)
            circle_radius: 圆半径 (默认80m)
            noise: 位置噪声范围 (默认1e-5)
        
        Returns:
            智能体列表
        """
        num_agents = num_agents or self.config.NUM_AGENTS
        circle_radius = circle_radius or self.config.CIRCLE_RADIUS
        noise = noise or self.config.POSITION_NOISE
        
        agents = []
        
        for i in range(num_agents):
            # 计算初始位置 (均匀分布在圆周上)
            angle = 2 * np.pi * i / num_agents
            position = np.array([
                circle_radius * np.cos(angle),
                circle_radius * np.sin(angle)
            ])
            
            # 添加微小噪声避免死锁
            position += np.random.uniform(-noise, noise, size=2)
            
            # 目标是对跖点 (圆心对称点)
            goal = -position
            
            # 创建智能体
            agent = AgentState(
                id=i,
                position=position,
                velocity=np.zeros(2),
                goal=goal,
                radius=self.config.AGENT_RADIUS,
                max_speed=self.config.MAX_SPEED,
                preferred_speed=self.config.PREFERRED_SPEED
            )
            
            agents.append(agent)
        
        print(f"Created Circle scenario with {num_agents} agents, radius={circle_radius}m")
        return agents
    
    def setup_random_scenario(self, num_agents: int = None,
                            map_size: float = None,
                            noise: float = None) -> List[AgentState]:
        """
        创建Random场景
        
        Args:
            num_agents: 智能体数量 (默认100)
            map_size: 地图大小 (默认30m x 30m)
            noise: 位置噪声范围 (默认1e-5)
        
        Returns:
            智能体列表
        """
        num_agents = num_agents or self.config.NUM_AGENTS
        map_size = map_size or self.config.RANDOM_MAP_SIZE
        noise = noise or self.config.POSITION_NOISE
        
        agents = []
        
        for i in range(num_agents):
            # 随机初始位置
            position = np.random.uniform(0, map_size, size=2)
            
            # 随机目标位置
            goal = np.random.uniform(0, map_size, size=2)
            
            # 添加微小噪声
            position += np.random.uniform(-noise, noise, size=2)
            goal += np.random.uniform(-noise, noise, size=2)
            
            # 创建智能体
            agent = AgentState(
                id=i,
                position=position,
                velocity=np.zeros(2),
                goal=goal,
                radius=self.config.AGENT_RADIUS,
                max_speed=self.config.MAX_SPEED,
                preferred_speed=self.config.PREFERRED_SPEED
            )
            
            agents.append(agent)
        
        print(f"Created Random scenario with {num_agents} agents, map_size={map_size}m")
        return agents
    
    def get_scenario_info(self, agents: List[AgentState]) -> dict:
        """获取场景统计信息"""
        positions = np.array([agent.position for agent in agents])
        goals = np.array([agent.goal for agent in agents])
        
        # 计算边界
        pos_min, pos_max = positions.min(axis=0), positions.max(axis=0)
        goal_min, goal_max = goals.min(axis=0), goals.max(axis=0)
        
        # 计算总的理想距离
        ideal_distances = [np.linalg.norm(agent.goal - agent.position) for agent in agents]
        total_ideal_distance = sum(ideal_distances)
        
        # 计算理想时间 (最长的那个智能体的时间)
        ideal_times = [dist / agent.preferred_speed for agent, dist in zip(agents, ideal_distances)]
        max_ideal_time = max(ideal_times) if ideal_times else 0
        
        return {
            'num_agents': len(agents),
            'position_bounds': (pos_min, pos_max),
            'goal_bounds': (goal_min, goal_max),
            'total_ideal_distance': total_ideal_distance,
            'max_ideal_time': max_ideal_time,
            'average_ideal_distance': np.mean(ideal_distances),
            'max_ideal_distance': max(ideal_distances)
        }


def select_neighbors(agent: AgentState, all_agents: List[AgentState], 
                    neighbor_range: float) -> List[AgentState]:
    """
    选择邻居智能体
    
    Args:
        agent: 当前智能体
        all_agents: 所有智能体列表
        neighbor_range: 邻域范围
    
    Returns:
        邻居智能体列表
    """
    neighbors = []
    
    for other in all_agents:
        if other.id == agent.id:
            continue
        
        distance = np.linalg.norm(other.position - agent.position)
        if distance <= neighbor_range:
            neighbors.append(other)
    
    return neighbors


if __name__ == "__main__":
    # 测试场景生成器
    print("VR-ORCA场景生成器测试")
    print("=" * 40)
    
    generator = ScenarioGenerator()
    
    # 测试Circle场景
    print("\n1. Circle场景测试:")
    circle_agents = generator.setup_circle_scenario(num_agents=10, circle_radius=20.0)
    circle_info = generator.get_scenario_info(circle_agents)
    
    print(f"智能体数量: {circle_info['num_agents']}")
    print(f"总理想距离: {circle_info['total_ideal_distance']:.2f}m")
    print(f"最大理想时间: {circle_info['max_ideal_time']:.2f}s")
    
    # 测试第一个智能体
    agent0 = circle_agents[0]
    print(f"智能体0 - 位置: {agent0.position}, 目标: {agent0.goal}")
    print(f"智能体0 - 偏好速度: {agent0.get_preferred_velocity()}")
    
    # 测试Random场景  
    print("\n2. Random场景测试:")
    random_agents = generator.setup_random_scenario(num_agents=10, map_size=10.0)
    random_info = generator.get_scenario_info(random_agents)
    
    print(f"智能体数量: {random_info['num_agents']}")
    print(f"总理想距离: {random_info['total_ideal_distance']:.2f}m")
    print(f"最大理想时间: {random_info['max_ideal_time']:.2f}s")
    
    # 测试邻居选择
    print("\n3. 邻居选择测试:")
    neighbors = select_neighbors(circle_agents[0], circle_agents, neighbor_range=10.0)
    print(f"智能体0的邻居数量: {len(neighbors)}")
    
    print("\n场景生成器测试完成!")