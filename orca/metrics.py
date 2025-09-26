#!/usr/bin/env python
"""
VR-ORCA论文性能指标计算模块

实现Time Ratio, Distance Ratio, Penetration Ratio等核心指标
"""

import numpy as np
import time
from typing import List, Dict, Any
from dataclasses import dataclass, field
from scenarios import AgentState
from config import ExperimentConfig, MetricsConfig


@dataclass
class SimulationStep:
    """单个仿真步骤的数据"""
    time: float
    positions: np.ndarray  # shape: (num_agents, 2)
    velocities: np.ndarray  # shape: (num_agents, 2)
    decision_times: List[float]  # 每个智能体的决策时间 (ms)
    max_penetration: float  # 当前步的最大穿透深度


@dataclass 
class SimulationRecord:
    """完整仿真记录"""
    algorithm: str
    scenario: str
    steps: List[SimulationStep] = field(default_factory=list)
    agents_initial: List[AgentState] = field(default_factory=list)
    total_time: float = 0.0
    completed: bool = False
    
    def add_step(self, step: SimulationStep):
        """添加仿真步骤"""
        self.steps.append(step)
        self.total_time = step.time


@dataclass
class PerformanceMetrics:
    """性能指标结果"""
    time_ratio: float
    distance_ratio: float
    penetration_ratio: float
    success_rate: float
    total_simulation_time: float
    average_decision_time: float
    max_decision_time: float
    computation_time: float


class MetricsCalculator:
    """性能指标计算器"""
    
    def __init__(self, config: ExperimentConfig = None):
        self.config = config or ExperimentConfig()
    
    def calculate_penetration(self, positions: np.ndarray, 
                            agent_radius: float) -> float:
        """
        计算当前时刻的最大穿透深度
        
        Args:
            positions: 智能体位置数组 shape=(N, 2)
            agent_radius: 智能体半径
            
        Returns:
            最大穿透深度
        """
        num_agents = len(positions)
        max_penetration = 0.0
        
        for i in range(num_agents):
            for j in range(i + 1, num_agents):
                # 计算两个智能体之间的距离
                distance = np.linalg.norm(positions[i] - positions[j])
                
                # 计算穿透深度
                min_distance = 2 * agent_radius
                if distance < min_distance:
                    penetration = min_distance - distance
                    max_penetration = max(max_penetration, penetration)
        
        return max_penetration
    
    def calculate_metrics(self, record: SimulationRecord) -> PerformanceMetrics:
        """
        从仿真记录计算所有性能指标
        
        Args:
            record: 完整的仿真记录
            
        Returns:
            性能指标结果
        """
        if not record.steps or not record.agents_initial:
            raise ValueError("仿真记录为空")
        
        # 1. 计算Time Ratio
        time_ratio = self._calculate_time_ratio(record)
        
        # 2. 计算Distance Ratio
        distance_ratio = self._calculate_distance_ratio(record)
        
        # 3. 计算Penetration Ratio
        penetration_ratio = self._calculate_penetration_ratio(record)
        
        # 4. 计算Success Rate
        success_rate = self._calculate_success_rate(record)
        
        # 5. 计算决策时间统计
        decision_stats = self._calculate_decision_time_stats(record)
        
        return PerformanceMetrics(
            time_ratio=time_ratio,
            distance_ratio=distance_ratio,
            penetration_ratio=penetration_ratio,
            success_rate=success_rate,
            total_simulation_time=record.total_time,
            average_decision_time=decision_stats['average'],
            max_decision_time=decision_stats['max'],
            computation_time=decision_stats['total']
        )
    
    def _calculate_time_ratio(self, record: SimulationRecord) -> float:
        """计算时间比率"""
        actual_time = record.total_time
        
        # 计算理想时间 (最长的智能体直线到达时间)
        ideal_times = []
        for agent in record.agents_initial:
            distance = np.linalg.norm(agent.goal - agent.position)
            ideal_time = distance / agent.preferred_speed if agent.preferred_speed > 0 else float('inf')
            ideal_times.append(ideal_time)
        
        max_ideal_time = max(ideal_times) if ideal_times else 1.0
        
        return MetricsConfig.calculate_time_ratio(actual_time, max_ideal_time)
    
    def _calculate_distance_ratio(self, record: SimulationRecord) -> float:
        """计算距离比率"""
        # 计算实际总距离
        actual_total_distance = 0.0
        
        if len(record.steps) >= 2:
            for i in range(1, len(record.steps)):
                prev_positions = record.steps[i-1].positions
                curr_positions = record.steps[i].positions
                
                # 计算每个智能体在这一步的移动距离
                distances = np.linalg.norm(curr_positions - prev_positions, axis=1)
                actual_total_distance += distances.sum()
        
        # 计算理想总距离 (所有智能体的直线距离)
        ideal_total_distance = 0.0
        for agent in record.agents_initial:
            ideal_distance = np.linalg.norm(agent.goal - agent.position)
            ideal_total_distance += ideal_distance
        
        return MetricsConfig.calculate_distance_ratio(actual_total_distance, ideal_total_distance)
    
    def _calculate_penetration_ratio(self, record: SimulationRecord) -> float:
        """计算穿透比率"""
        max_penetration = 0.0
        
        for step in record.steps:
            max_penetration = max(max_penetration, step.max_penetration)
        
        return MetricsConfig.calculate_penetration_ratio(max_penetration, self.config.AGENT_RADIUS)
    
    def _calculate_success_rate(self, record: SimulationRecord) -> float:
        """计算成功率"""
        if not record.steps:
            return 0.0
        
        # 获取最后一步的位置
        final_positions = record.steps[-1].positions
        num_agents = len(record.agents_initial)
        successful_agents = 0
        
        for i, agent in enumerate(record.agents_initial):
            final_pos = final_positions[i]
            distance_to_goal = np.linalg.norm(agent.goal - final_pos)
            
            if distance_to_goal < self.config.GOAL_THRESHOLD:
                successful_agents += 1
        
        return successful_agents / num_agents if num_agents > 0 else 0.0
    
    def _calculate_decision_time_stats(self, record: SimulationRecord) -> Dict[str, float]:
        """计算决策时间统计"""
        all_decision_times = []
        
        for step in record.steps:
            all_decision_times.extend(step.decision_times)
        
        if not all_decision_times:
            return {'average': 0.0, 'max': 0.0, 'total': 0.0}
        
        return {
            'average': np.mean(all_decision_times),
            'max': np.max(all_decision_times),
            'total': np.sum(all_decision_times)
        }


class SimulationRecorder:
    """仿真数据记录器"""
    
    def __init__(self, algorithm: str, scenario: str):
        self.record = SimulationRecord(algorithm=algorithm, scenario=scenario)
        self.config = ExperimentConfig()
        self.metrics_calculator = MetricsCalculator()
    
    def initialize(self, agents: List[AgentState]):
        """初始化记录器"""
        # 保存初始状态的深拷贝
        self.record.agents_initial = []
        for agent in agents:
            initial_agent = AgentState(
                id=agent.id,
                position=agent.position.copy(),
                velocity=agent.velocity.copy(),
                goal=agent.goal.copy(),
                radius=agent.radius,
                max_speed=agent.max_speed,
                preferred_speed=agent.preferred_speed
            )
            self.record.agents_initial.append(initial_agent)
    
    def record_step(self, simulation_time: float, agents: List[AgentState], 
                   decision_times: List[float]):
        """记录单个仿真步骤"""
        # 提取位置和速度
        positions = np.array([agent.position for agent in agents])
        velocities = np.array([agent.velocity for agent in agents])
        
        # 计算当前步的最大穿透深度
        max_penetration = self.metrics_calculator.calculate_penetration(
            positions, self.config.AGENT_RADIUS
        )
        
        # 创建步骤记录
        step = SimulationStep(
            time=simulation_time,
            positions=positions,
            velocities=velocities,
            decision_times=decision_times.copy(),
            max_penetration=max_penetration
        )
        
        self.record.add_step(step)
    
    def finalize(self, completed: bool = True):
        """完成记录"""
        self.record.completed = completed
    
    def get_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        return self.metrics_calculator.calculate_metrics(self.record)
    
    def get_record(self) -> SimulationRecord:
        """获取完整记录"""
        return self.record


class DecisionTimer:
    """决策时间计时器"""
    
    def __init__(self):
        self.start_time = None
    
    def start(self):
        """开始计时"""
        self.start_time = time.perf_counter()
    
    def stop(self) -> float:
        """停止计时并返回经过的时间(毫秒)"""
        if self.start_time is None:
            return 0.0
        
        end_time = time.perf_counter()
        elapsed_ms = (end_time - self.start_time) * 1000.0
        self.start_time = None
        return elapsed_ms


if __name__ == "__main__":
    # 测试性能指标计算
    print("VR-ORCA性能指标计算器测试")
    print("=" * 40)
    
    from scenarios import ScenarioGenerator
    
    # 创建测试场景
    generator = ScenarioGenerator()
    agents = generator.setup_circle_scenario(num_agents=5, circle_radius=10.0)
    
    # 创建记录器
    recorder = SimulationRecorder("ORCA", "circle")
    recorder.initialize(agents)
    
    # 模拟几个仿真步骤
    for step in range(3):
        # 模拟智能体移动
        for agent in agents:
            # 简单向目标移动
            direction = agent.goal - agent.position
            distance = np.linalg.norm(direction)
            if distance > 0:
                agent.velocity = (direction / distance) * 0.5
                agent.position += agent.velocity * 0.25
        
        # 模拟决策时间
        decision_times = [np.random.uniform(1.0, 5.0) for _ in agents]
        
        # 记录步骤
        recorder.record_step(step * 0.25, agents, decision_times)
    
    # 完成记录并计算指标
    recorder.finalize()
    metrics = recorder.get_metrics()
    
    print(f"时间比率: {metrics.time_ratio:.3f}")
    print(f"距离比率: {metrics.distance_ratio:.3f}")
    print(f"穿透比率: {metrics.penetration_ratio:.3f}")
    print(f"成功率: {metrics.success_rate:.1%}")
    print(f"平均决策时间: {metrics.average_decision_time:.2f}ms")
    
    print("\n性能指标计算器测试完成!")