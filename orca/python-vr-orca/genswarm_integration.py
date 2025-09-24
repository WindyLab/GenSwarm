#!/usr/bin/env python
"""
GenSwarm Integration Example for VR-ORCA

This example shows how to integrate the VR-ORCA Python interface with GenSwarm
for enhanced swarm robotics simulations with variable responsibility collision avoidance.
"""

import numpy as np
import vrorca
from typing import List, Tuple, Dict, Any
import time


class VRORCASwarmEngine:
    """
    A swarm simulation engine using VR-ORCA for collision avoidance.
    
    This class provides a high-level interface for swarm robotics simulations
    using the VR-ORCA algorithm, designed to integrate with GenSwarm.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the VR-ORCA swarm engine.
        
        Args:
            config: Configuration dictionary with simulation parameters
        """
        # Simulation parameters
        self.time_step = config.get('time_step', 1/60.0)
        self.neighbor_dist = config.get('neighbor_dist', 2.0)
        self.max_neighbors = config.get('max_neighbors', 8)
        self.time_horizon = config.get('time_horizon', 2.0)
        self.time_horizon_obst = config.get('time_horizon_obst', 2.0)
        self.agent_radius = config.get('agent_radius', 0.3)
        self.max_speed = config.get('max_speed', 2.0)
        self.pref_speed = config.get('pref_speed', 1.5)
        
        # VR-ORCA specific parameters
        self.vr_weight = config.get('vr_weight', 0.5)
        
        # Initialize VR-ORCA simulator
        self.sim = vrorca.PyVRORCASimulator(
            self.time_step,
            self.neighbor_dist,
            self.max_neighbors,
            self.time_horizon,
            self.time_horizon_obst,
            self.agent_radius,
            self.max_speed,
            self.pref_speed
        )
        
        # Set VR-ORCA weight
        self.sim.setWeight(self.vr_weight)
        
        # Agent management
        self.agents = {}  # agent_id -> agent_info
        self.obstacles = []
        self.simulation_time = 0.0
        
        print(f"VR-ORCA Swarm Engine initialized with {self.max_neighbors} max neighbors, "
              f"VR-weight: {self.vr_weight}")
    
    def add_agent(self, agent_id: int, position: Tuple[float, float], 
                  goal: Tuple[float, float] = None, **kwargs) -> int:
        """
        Add an agent to the swarm simulation.
        
        Args:
            agent_id: Unique identifier for the agent
            position: Initial position (x, y)
            goal: Goal position (x, y), optional
            **kwargs: Additional agent parameters
            
        Returns:
            VR-ORCA internal agent ID
        """
        # Agent-specific parameters (use defaults if not provided)
        radius = kwargs.get('radius', self.agent_radius)
        max_speed = kwargs.get('max_speed', self.max_speed)
        neighbor_dist = kwargs.get('neighbor_dist', self.neighbor_dist)
        
        # Add agent to VR-ORCA simulator
        if 'custom_params' in kwargs:
            # Add with custom parameters
            vrorca_id = self.sim.addAgent(
                position,
                neighbor_dist,
                self.max_neighbors,
                self.time_horizon,
                self.time_horizon_obst,
                radius,
                max_speed,
                kwargs.get('initial_velocity', (0, 0))
            )
        else:
            # Add with default parameters
            vrorca_id = self.sim.addAgent(position)
        
        # Store agent information
        self.agents[agent_id] = {
            'vrorca_id': vrorca_id,
            'goal': goal,
            'position': position,
            'velocity': (0, 0),
            'radius': radius,
            'max_speed': max_speed,
            'active': True
        }
        
        return vrorca_id
    
    def add_obstacle(self, vertices: List[Tuple[float, float]]) -> int:
        """
        Add a polygonal obstacle to the simulation.
        
        Args:
            vertices: List of vertices in counterclockwise order
            
        Returns:
            Obstacle ID
        """
        obstacle_id = self.sim.addObstacle(vertices)
        self.obstacles.append({
            'vrorca_id': obstacle_id,
            'vertices': vertices
        })
        return obstacle_id
    
    def finalize_obstacles(self):
        """Finalize obstacle setup. Must be called after adding all obstacles."""
        self.sim.processObstacles()
        print(f"Processed {len(self.obstacles)} obstacles")
    
    def set_agent_goal(self, agent_id: int, goal: Tuple[float, float]):
        """Set or update an agent's goal position."""
        if agent_id in self.agents:
            self.agents[agent_id]['goal'] = goal
    
    def get_agent_position(self, agent_id: int) -> Tuple[float, float]:
        """Get current position of an agent."""
        if agent_id in self.agents:
            vrorca_id = self.agents[agent_id]['vrorca_id']
            return self.sim.getAgentPosition(vrorca_id)
        return None
    
    def get_agent_velocity(self, agent_id: int) -> Tuple[float, float]:
        """Get current velocity of an agent."""
        if agent_id in self.agents:
            vrorca_id = self.agents[agent_id]['vrorca_id']
            return self.sim.getAgentVelocity(vrorca_id)
        return None
    
    def set_agent_preferred_velocity(self, agent_id: int, velocity: Tuple[float, float]):
        """Set preferred velocity for an agent."""
        if agent_id in self.agents:
            vrorca_id = self.agents[agent_id]['vrorca_id']
            self.sim.setAgentPrefVelocity(vrorca_id, velocity)
    
    def update_preferred_velocities(self):
        """Update preferred velocities for all agents based on their goals."""
        for agent_id, agent_info in self.agents.items():
            if not agent_info['active'] or agent_info['goal'] is None:
                continue
            
            vrorca_id = agent_info['vrorca_id']
            current_pos = np.array(self.sim.getAgentPosition(vrorca_id))
            goal_pos = np.array(agent_info['goal'])
            
            # Calculate direction to goal
            direction = goal_pos - current_pos
            distance = np.linalg.norm(direction)
            
            if distance > 0.1:  # Still moving toward goal
                # Normalize and scale by preferred speed
                pref_velocity = (direction / distance) * self.pref_speed
                self.sim.setAgentPrefVelocity(vrorca_id, tuple(pref_velocity))
            else:
                # Close to goal, stop
                self.sim.setAgentPrefVelocity(vrorca_id, (0, 0))
    
    def step(self):
        """Perform one simulation step."""
        # Update preferred velocities based on goals
        self.update_preferred_velocities()
        
        # Perform VR-ORCA simulation step
        self.sim.doStep()
        
        # Update agent information
        for agent_id, agent_info in self.agents.items():
            vrorca_id = agent_info['vrorca_id']
            agent_info['position'] = self.sim.getAgentPosition(vrorca_id)
            agent_info['velocity'] = self.sim.getAgentVelocity(vrorca_id)
        
        self.simulation_time += self.time_step
    
    def get_swarm_state(self) -> Dict[str, Any]:
        """Get current state of the entire swarm."""
        state = {
            'time': self.simulation_time,
            'agents': {},
            'total_energy': self.sim.getTotalEnergy(),
            'vr_weight': self.sim.getWeight()
        }
        
        for agent_id, agent_info in self.agents.items():
            vrorca_id = agent_info['vrorca_id']
            state['agents'][agent_id] = {
                'position': agent_info['position'],
                'velocity': agent_info['velocity'],
                'goal': agent_info['goal'],
                'neighbors': self.sim.getAgentNumAgentNeighbors(vrorca_id),
                'orca_lines': self.sim.getAgentNumORCALines(vrorca_id)
            }
        
        return state
    
    def run_scenario(self, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a complete swarm scenario.
        
        Args:
            scenario_config: Configuration for the scenario
            
        Returns:
            Results dictionary with performance metrics
        """
        max_steps = scenario_config.get('max_steps', 1000)
        goal_tolerance = scenario_config.get('goal_tolerance', 0.2)
        record_trajectory = scenario_config.get('record_trajectory', False)
        
        # Initialize trajectory recording
        trajectory = [] if record_trajectory else None
        
        start_time = time.time()
        
        for step in range(max_steps):
            self.step()
            
            # Record trajectory if requested
            if record_trajectory:
                trajectory.append(self.get_swarm_state())
            
            # Check if all agents reached goals
            all_reached = True
            for agent_id, agent_info in self.agents.items():
                if agent_info['goal'] is None:
                    continue
                
                current_pos = np.array(agent_info['position'])
                goal_pos = np.array(agent_info['goal'])
                distance = np.linalg.norm(current_pos - goal_pos)
                
                if distance > goal_tolerance:
                    all_reached = False
                    break
            
            if all_reached:
                print(f"All agents reached goals in {step} steps ({self.simulation_time:.2f}s)")
                break
        
        wall_time = time.time() - start_time
        
        # Calculate results
        results = {
            'success': all_reached,
            'steps': step + 1,
            'simulation_time': self.simulation_time,
            'wall_time': wall_time,
            'final_state': self.get_swarm_state(),
            'trajectory': trajectory
        }
        
        return results


def run_flocking_example():
    """Example: Flocking behavior using VR-ORCA."""
    print("=== VR-ORCA Flocking Example ===")
    
    # Configuration
    config = {
        'time_step': 1/30.0,
        'neighbor_dist': 2.5,
        'max_neighbors': 6,
        'time_horizon': 2.0,
        'agent_radius': 0.25,
        'max_speed': 2.0,
        'pref_speed': 1.5,
        'vr_weight': 0.6  # VR-ORCA responsibility weight
    }
    
    # Create engine
    engine = VRORCASwarmEngine(config)
    
    # Add agents in random positions
    np.random.seed(42)
    n_agents = 8
    
    for i in range(n_agents):
        pos = (np.random.uniform(-3, 3), np.random.uniform(-3, 3))
        goal = (np.random.uniform(-1, 1), np.random.uniform(-1, 1))  # Center region
        engine.add_agent(i, pos, goal)
    
    # Run scenario
    scenario_config = {
        'max_steps': 200,
        'goal_tolerance': 0.5,
        'record_trajectory': True
    }
    
    results = engine.run_scenario(scenario_config)
    
    print(f"Flocking simulation completed:")
    print(f"  Success: {results['success']}")
    print(f"  Steps: {results['steps']}")
    print(f"  Simulation time: {results['simulation_time']:.2f}s")
    print(f"  Wall time: {results['wall_time']:.3f}s")
    print(f"  Final energy: {results['final_state']['total_energy']:.3f}")


def run_obstacle_avoidance_example():
    """Example: Obstacle avoidance using VR-ORCA."""
    print("\n=== VR-ORCA Obstacle Avoidance Example ===")
    
    config = {
        'time_step': 1/60.0,
        'neighbor_dist': 3.0,
        'max_neighbors': 8,
        'time_horizon': 2.5,
        'time_horizon_obst': 3.0,
        'agent_radius': 0.2,
        'max_speed': 1.5,
        'pref_speed': 1.2,
        'vr_weight': 0.7
    }
    
    engine = VRORCASwarmEngine(config)
    
    # Add obstacles
    obstacles = [
        [(-1, -1), (1, -1), (1, 1), (-1, 1)],  # Square obstacle
        [(2, 0), (2.5, 0.5), (2, 1), (1.5, 0.5)]  # Diamond obstacle
    ]
    
    for obstacle in obstacles:
        engine.add_obstacle(obstacle)
    
    engine.finalize_obstacles()
    
    # Add agents
    start_positions = [(-3, -2), (-3, 0), (-3, 2)]
    goal_positions = [(3, -2), (3, 0), (3, 2)]
    
    for i, (start, goal) in enumerate(zip(start_positions, goal_positions)):
        engine.add_agent(i, start, goal)
    
    # Run scenario
    scenario_config = {
        'max_steps': 300,
        'goal_tolerance': 0.3,
        'record_trajectory': False
    }
    
    results = engine.run_scenario(scenario_config)
    
    print(f"Obstacle avoidance simulation completed:")
    print(f"  Success: {results['success']}")
    print(f"  Steps: {results['steps']}")
    print(f"  Wall time: {results['wall_time']:.3f}s")


def main():
    """Run GenSwarm integration examples."""
    print("GenSwarm VR-ORCA Integration Examples")
    print("=" * 40)
    
    try:
        run_flocking_example()
        run_obstacle_avoidance_example()
        
        print("\n🎉 All integration examples completed successfully!")
        print("VR-ORCA is ready for use with GenSwarm.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure VR-ORCA Python interface is properly installed.")
        print("Run: python setup.py install")
        
    except Exception as e:
        print(f"❌ Error during examples: {e}")
        print("Please check the VR-ORCA installation and configuration.")


if __name__ == "__main__":
    main()