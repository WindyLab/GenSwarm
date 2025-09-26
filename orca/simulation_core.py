#!/usr/bin/env python
"""
VR-ORCA仿真核心模块

集成算法调用，实现主仿真循环
"""

import sys
import numpy as np
from typing import List, Dict, Any
from scenarios import AgentState, ScenarioGenerator, select_neighbors
from metrics import SimulationRecorder, DecisionTimer, PerformanceMetrics
from config import ExperimentConfig

# 算法模块路径
sys.path.append('/Users/wenkang/GenSwarm/orca/Python-RVO2')
sys.path.append('/Users/wenkang/GenSwarm/orca/python-vr-orca')

try:
    import rvo2
    ORCA_AVAILABLE = True
except ImportError:
    ORCA_AVAILABLE = False

try:
    import vrorca  
    VRORCA_AVAILABLE = True
except ImportError:
    VRORCA_AVAILABLE = False


class SimulationCore:
    """仿真核心类"""
    
    def __init__(self, config: ExperimentConfig = None):
        self.config = config or ExperimentConfig()
        self.scenario_generator = ScenarioGenerator(self.config)
    
    def run_orca_simulation(self, agents: List[AgentState], 
                          neighbor_range: float = None,
                          max_time: float = None) -> PerformanceMetrics:
        """运行ORCA算法仿真"""
        if not ORCA_AVAILABLE:
            raise RuntimeError("ORCA (RVO2) module not available")
        
        neighbor_range = neighbor_range or self.config.NEIGHBORHOOD_RANGE
        max_time = max_time or self.config.MAX_SIMULATION_TIME
        
        # 创建RVO2模拟器
        sim = rvo2.PyRVOSimulator(
            self.config.TIME_STEP,
            neighbor_range, 
            10,  # maxNeighbors
            self.config.TIME_HORIZON,
            self.config.TIME_HORIZON, 
            self.config.AGENT_RADIUS,
            self.config.MAX_SPEED
        )
        
        # 添加智能体到模拟器
        agent_ids = []
        for agent in agents:
            agent_id = sim.addAgent(tuple(agent.position))
            agent_ids.append(agent_id)
        
        # 创建记录器
        recorder = SimulationRecorder("ORCA", "simulation")
        recorder.initialize(agents)
        
        # 主仿真循环
        current_time = 0.0
        timer = DecisionTimer()
        
        while current_time < max_time:
            decision_times = []
            
            # 为每个智能体设置偏好速度
            for i, agent in enumerate(agents):
                timer.start()
                
                # 计算偏好速度 
                pref_velocity = agent.get_preferred_velocity()
                sim.setAgentPrefVelocity(agent_ids[i], tuple(pref_velocity))
                
                decision_time = timer.stop()
                decision_times.append(decision_time)
            
            # 执行一步仿真
            sim.doStep()
            
            # 更新智能体状态
            for i, agent in enumerate(agents):
                new_pos = np.array(sim.getAgentPosition(agent_ids[i]))
                new_vel = np.array(sim.getAgentVelocity(agent_ids[i]))
                
                agent.position = new_pos
                agent.velocity = new_vel
            
            current_time += self.config.TIME_STEP
            
            # 记录这一步
            recorder.record_step(current_time, agents, decision_times)
            
            # 检查是否完成
            if self._check_completion(agents):
                break
        
        # 完成记录
        recorder.finalize(completed=True)
        return recorder.get_metrics()
    
    def run_vrorca_simulation(self, agents: List[AgentState],
                            neighbor_range: float = None,
                            safety_weight: float = None,
                            max_time: float = None) -> PerformanceMetrics:
        """运行VR-ORCA算法仿真"""
        if not VRORCA_AVAILABLE:
            raise RuntimeError("VR-ORCA module not available")
        
        neighbor_range = neighbor_range or self.config.NEIGHBORHOOD_RANGE
        safety_weight = safety_weight or self.config.SAFETY_WEIGHT
        max_time = max_time or self.config.MAX_SIMULATION_TIME
        
        # 创建VR-ORCA模拟器 
        sim = vrorca.PyVRORCASimulator(
            self.config.TIME_STEP,
            neighbor_range,
            10,  # maxNeighbors
            self.config.TIME_HORIZON,
            self.config.TIME_HORIZON,
            self.config.AGENT_RADIUS,
            self.config.MAX_SPEED
        )
        
        # 添加智能体到模拟器
        agent_ids = []
        for agent in agents:
            agent_id = sim.addAgent(tuple(agent.position))
            agent_ids.append(agent_id)
        
        # 创建记录器
        recorder = SimulationRecorder("VR-ORCA", "simulation")
        recorder.initialize(agents)
        
        # 主仿真循环
        current_time = 0.0
        timer = DecisionTimer()
        
        while current_time < max_time:
            decision_times = []
            
            # 为每个智能体设置偏好速度
            for i, agent in enumerate(agents):
                timer.start()
                
                # 计算偏好速度
                pref_velocity = agent.get_preferred_velocity()
                sim.setAgentPrefVelocity(agent_ids[i], tuple(pref_velocity))
                
                decision_time = timer.stop()
                decision_times.append(decision_time)
            
            # 执行一步仿真
            sim.doStep()
            
            # 更新智能体状态
            for i, agent in enumerate(agents):
                new_pos = np.array(sim.getAgentPosition(agent_ids[i]))
                new_vel = np.array(sim.getAgentVelocity(agent_ids[i]))
                
                agent.position = new_pos
                agent.velocity = new_vel
            
            current_time += self.config.TIME_STEP
            
            # 记录这一步
            recorder.record_step(current_time, agents, decision_times)
            
            # 检查是否完成
            if self._check_completion(agents):
                break
        
        # 完成记录
        recorder.finalize(completed=True)
        return recorder.get_metrics()
    
    def _check_completion(self, agents: List[AgentState]) -> bool:
        """检查仿真是否完成"""
        completed_agents = 0
        for agent in agents:
            if agent.has_reached_goal(self.config.GOAL_THRESHOLD):
                completed_agents += 1
        
        # 如果80%的智能体到达目标，认为完成
        completion_rate = completed_agents / len(agents)
        return completion_rate >= 0.8


def run_single_experiment(algorithm: str, scenario: str, **kwargs) -> PerformanceMetrics:
    """运行单个实验"""
    print(f"Running {algorithm} on {scenario} scenario...")
    
    core = SimulationCore()
    
    # 创建场景
    if scenario == "circle":
        agents = core.scenario_generator.setup_circle_scenario()
    elif scenario == "random":
        agents = core.scenario_generator.setup_random_scenario()
    else:
        raise ValueError(f"Unknown scenario: {scenario}")
    
    # 运行仿真
    if algorithm == "ORCA":
        return core.run_orca_simulation(agents, **kwargs)
    elif algorithm == "VR-ORCA":
        return core.run_vrorca_simulation(agents, **kwargs)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


if __name__ == "__main__":
    # 测试仿真核心
    print("VR-ORCA仿真核心测试")
    print("=" * 40)
    
    if not (ORCA_AVAILABLE and VRORCA_AVAILABLE):
        print("Warning: Some algorithms not available")
        print(f"ORCA: {ORCA_AVAILABLE}, VR-ORCA: {VRORCA_AVAILABLE}")
    
    # 小规模测试
    core = SimulationCore()
    agents = core.scenario_generator.setup_circle_scenario(num_agents=5, circle_radius=10.0)
    
    print(f"Created test scenario with {len(agents)} agents")
    
    if ORCA_AVAILABLE:
        try:
            print("Testing ORCA...")
            metrics = core.run_orca_simulation(agents, max_time=10.0)
            print(f"ORCA - Time ratio: {metrics.time_ratio:.3f}, Success: {metrics.success_rate:.1%}")
        except Exception as e:
            print(f"ORCA test failed: {e}")
    
    print("\n仿真核心测试完成!")