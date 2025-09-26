#!/usr/bin/env python
"""
VR-ORCA轨迹可视化和动画生成器

生成智能体轨迹动画并保存为视频文件
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle as PlotCircle
import math

# Add paths for modules
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


class TrajectoryAnimator:
    """轨迹动画生成器"""
    
    def __init__(self):
        self.agent_radius = 0.15
        self.max_speed = 2.0
        self.time_step = 1/60.0
        
    def create_circle_scenario(self, n_agents=50, radius=40.0):
        """创建Circle场景数据"""
        agents_data = []
        for i in range(n_agents):
            angle = i * 2.0 * np.pi / n_agents
            start_x = radius * np.cos(angle)
            start_y = radius * np.sin(angle)
            goal_x = -start_x
            goal_y = -start_y
            agents_data.append({'start': (start_x, start_y), 'goal': (goal_x, goal_y)})
        return agents_data
    
    def run_with_trajectory_recording(self, algorithm, agents_data, neighbor_dist=10.0, 
                                    safety_weight=100.0, max_steps=800):
        """运行算法并记录轨迹"""
        trajectories = {i: [] for i in range(len(agents_data))}
        
        if algorithm == 'ORCA' and ORCA_AVAILABLE:
            sim = rvo2.PyRVOSimulator(
                timeStep=self.time_step, neighborDist=neighbor_dist, maxNeighbors=10,
                timeHorizon=5.0, timeHorizonObst=5.0, radius=self.agent_radius, maxSpeed=self.max_speed
            )
        elif algorithm == 'VR-ORCA' and VRORCA_AVAILABLE:
            sim = vrorca.PyVRORCASimulator(
                timeStep=self.time_step, neighborDist=neighbor_dist, maxNeighbors=10,
                timeHorizon=5.0, timeHorizonObst=5.0, radius=self.agent_radius,
                maxSpeed=self.max_speed, prefSpeed=self.max_speed, safetyWeight=safety_weight
            )
        else:
            print(f"Algorithm {algorithm} not available")
            return None
        
        # 添加智能体
        agent_ids = [sim.addAgent(agent_data['start']) for agent_data in agents_data]
        
        # 运行仿真并记录轨迹
        for step in range(max_steps):
            # 记录当前位置
            for i, agent_id in enumerate(agent_ids):
                pos = sim.getAgentPosition(agent_id)
                trajectories[i].append(pos)
            
            # 设置偏好速度
            for i, agent_id in enumerate(agent_ids):
                current_pos = sim.getAgentPosition(agent_id)
                goal_pos = agents_data[i]['goal']
                
                direction = (goal_pos[0] - current_pos[0], goal_pos[1] - current_pos[1])
                distance = math.sqrt(direction[0]**2 + direction[1]**2)
                
                if distance > 1.0:
                    pref_vel = (direction[0]/distance * self.max_speed, direction[1]/distance * self.max_speed)
                else:
                    pref_vel = (0, 0)
                
                sim.setAgentPrefVelocity(agent_id, pref_vel)
            
            sim.doStep()
            
            # 检查完成情况
            completed = sum(1 for i, agent_id in enumerate(agent_ids) 
                          if math.sqrt((sim.getAgentPosition(agent_id)[0] - agents_data[i]['goal'][0])**2 + 
                                     (sim.getAgentPosition(agent_id)[1] - agents_data[i]['goal'][1])**2) < 2.0)
            
            if completed >= len(agent_ids) * 0.8:
                break
        
        return trajectories
    
    def create_animation(self, algorithm, agents_data, trajectories, save_video=True):
        """创建动画"""
        print(f"Creating animation for {algorithm}...")
        
        if not trajectories:
            print("No trajectory data available")
            return None
        
        # 设置图形
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 计算边界
        all_positions = []
        for traj in trajectories.values():
            all_positions.extend(traj)
        
        if not all_positions:
            return None
        
        x_coords = [pos[0] for pos in all_positions]
        y_coords = [pos[1] for pos in all_positions]
        margin = 10
        ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
        ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)
        
        # 初始化绘图元素
        colors = plt.cm.tab10(np.linspace(0, 1, len(trajectories)))
        agent_dots = []
        trail_lines = []
        
        for i, (agent_id, trajectory) in enumerate(trajectories.items()):\n            if len(trajectory) == 0:
                continue
            color = colors[i % len(colors)]
            
            # 智能体点
            dot, = ax.plot([], [], 'o', color=color, markersize=6)
            agent_dots.append((agent_id, dot, trajectory))
            
            # 轨迹线
            trail, = ax.plot([], [], '-', color=color, alpha=0.3, linewidth=1)
            trail_lines.append((agent_id, trail))
            
            # 目标点
            goal = agents_data[agent_id]['goal']
            ax.plot(goal[0], goal[1], 's', color=color, markersize=4, alpha=0.7)
        
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_title(f'{algorithm} - Circle Scenario Animation')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        def animate(frame):
            """动画函数"""
            for i, (agent_id, dot, trajectory) in enumerate(agent_dots):
                if frame < len(trajectory):
                    pos = trajectory[frame]
                    dot.set_data([pos[0]], [pos[1]])
                    
                    # 更新轨迹
                    if frame > 0:
                        trail_agent_id, trail = trail_lines[i]
                        trail_x = [trajectory[j][0] for j in range(frame + 1)]
                        trail_y = [trajectory[j][1] for j in range(frame + 1)]
                        trail.set_data(trail_x, trail_y)
            
            ax.set_title(f'{algorithm} - Circle Scenario (Step {frame})')
            return [dot for _, dot, _ in agent_dots] + [trail for _, trail in trail_lines]
        
        max_frames = max(len(traj) for traj in trajectories.values() if len(traj) > 0)
        anim = animation.FuncAnimation(fig, animate, frames=min(max_frames, 500), 
                                     interval=50, blit=False, repeat=True)
        
        if save_video:
            filename = f'/Users/wenkang/GenSwarm/orca/{algorithm}_circle_animation.gif'
            try:
                anim.save(filename, writer='pillow', fps=20)
                print(f"Animation saved: {filename}")
            except Exception as e:
                print(f"Failed to save animation: {e}")
        
        plt.show()
        return anim
    
    def generate_comparison_animation(self):
        """生成对比动画"""
        print("Generating trajectory comparison animations...")
        
        # 创建场景
        agents_data = self.create_circle_scenario(n_agents=50, radius=40.0)
        
        # 运行ORCA实验
        if ORCA_AVAILABLE:
            print("Recording ORCA trajectories...")
            orca_trajectories = self.run_with_trajectory_recording('ORCA', agents_data)
            if orca_trajectories:
                self.create_animation('ORCA', agents_data, orca_trajectories)
        
        # 运行VR-ORCA实验
        if VRORCA_AVAILABLE:
            print("Recording VR-ORCA trajectories...")
            vrorca_trajectories = self.run_with_trajectory_recording('VR-ORCA', agents_data)
            if vrorca_trajectories:
                self.create_animation('VR-ORCA', agents_data, vrorca_trajectories)
        
        print("Animation generation completed!")


def main():
    """主函数"""
    print("VR-ORCA Trajectory Animation Generator")
    print("=" * 40)
    
    if not (ORCA_AVAILABLE and VRORCA_AVAILABLE):
        print("Warning: Some algorithms may not be available")
        print(f"ORCA available: {ORCA_AVAILABLE}")
        print(f"VR-ORCA available: {VRORCA_AVAILABLE}")
    
    animator = TrajectoryAnimator()
    animator.generate_comparison_animation()


if __name__ == "__main__":
    main()