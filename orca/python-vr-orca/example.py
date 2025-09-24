#!/usr/bin/env python
"""
VR-ORCA Python Interface Example

This example demonstrates how to use the Python interface for VR-ORCA
(Variable Responsibility Optimal Reciprocal Collision Avoidance).

VR-ORCA extends the standard ORCA algorithm by dynamically adjusting
the responsibility distribution between agents, leading to more natural
and efficient collision avoidance behavior.
"""

import vrorca
import numpy as np
import matplotlib.pyplot as plt
import time


def run_basic_example():
    """Basic usage example similar to python-rvo2."""
    print("=== Basic VR-ORCA Example ===")
    
    # Create VR-ORCA simulator
    # Parameters: timeStep, neighborDist, maxNeighbors, timeHorizon, 
    #            timeHorizonObst, radius, maxSpeed, prefSpeed
    sim = vrorca.PyVRORCASimulator(1/60., 1.5, 5, 1.5, 2, 0.4, 2, 1.0)

    # Add agents with default parameters
    a0 = sim.addAgent((0, 0))
    a1 = sim.addAgent((1, 0))
    a2 = sim.addAgent((1, 1))
    a3 = sim.addAgent((0, 1))

    # Add an obstacle (triangle)
    obstacle = sim.addObstacle([(0.1, 0.1), (-0.1, 0.1), (-0.1, -0.1)])
    sim.processObstacles()

    # Set preferred velocities (where agents want to go)
    sim.setAgentPrefVelocity(a0, (1, 1))
    sim.setAgentPrefVelocity(a1, (-1, 1))
    sim.setAgentPrefVelocity(a2, (-1, -1))
    sim.setAgentPrefVelocity(a3, (1, -1))

    print(f'Simulation has {sim.getNumAgents()} agents and {sim.getNumObstacleVertices()} obstacle vertices.')
    print('Running simulation...')

    # Run simulation for 20 steps
    for step in range(20):
        sim.doStep()

        positions = [sim.getAgentPosition(agent_no) for agent_no in (a0, a1, a2, a3)]
        position_str = '  '.join(['(%5.3f, %5.3f)' % pos for pos in positions])
        print(f'step={step:2d}  t={sim.getGlobalTime():.3f}  {position_str}')

    print("Basic example completed!\n")


def run_comparison_example():
    """Compare VR-ORCA with different scenarios."""
    print("=== VR-ORCA vs Standard Scenarios ===")
    
    def create_circle_scenario(n_agents=8, radius=2.0):
        """Create agents in a circle formation."""
        angles = np.linspace(0, 2*np.pi, n_agents, endpoint=False)
        positions = [(radius * np.cos(angle), radius * np.sin(angle)) for angle in angles]
        goals = [(-pos[0], -pos[1]) for pos in positions]  # Opposite positions
        return positions, goals

    def run_scenario(positions, goals, title="Scenario"):
        """Run a scenario and return trajectory data."""
        sim = vrorca.PyVRORCASimulator(
            timeStep=1/30.,
            neighborDist=3.0,
            maxNeighbors=10,
            timeHorizon=2.0,
            timeHorizonObst=2.0,
            radius=0.3,
            maxSpeed=1.5,
            prefSpeed=1.0
        )
        
        # Add agents
        agent_ids = []
        for pos in positions:
            agent_ids.append(sim.addAgent(pos))
        
        # Store trajectory
        trajectory = []
        max_steps = 100
        
        for step in range(max_steps):
            # Set preferred velocities toward goals
            for i, agent_id in enumerate(agent_ids):
                current_pos = np.array(sim.getAgentPosition(agent_id))
                goal_pos = np.array(goals[i])
                direction = goal_pos - current_pos
                distance = np.linalg.norm(direction)
                
                if distance > 0.1:  # Still moving toward goal
                    pref_velocity = (direction / distance) * sim.getAgentMaxSpeed(agent_id)
                    sim.setAgentPrefVelocity(agent_id, tuple(pref_velocity))
                else:
                    sim.setAgentPrefVelocity(agent_id, (0, 0))
            
            # Simulation step
            sim.doStep()
            
            # Record positions
            step_positions = [sim.getAgentPosition(agent_id) for agent_id in agent_ids]
            trajectory.append(step_positions)
            
            # Check if all agents reached goals
            all_reached = True
            for i, agent_id in enumerate(agent_ids):
                pos = np.array(sim.getAgentPosition(agent_id))
                goal = np.array(goals[i])
                if np.linalg.norm(pos - goal) > 0.2:
                    all_reached = False
                    break
            
            if all_reached:
                print(f"{title}: All agents reached goals in {step} steps")
                break
        
        return trajectory

    # Test scenario: Circle of agents moving to opposite positions
    positions, goals = create_circle_scenario(8, 2.5)
    trajectory = run_scenario(positions, goals, "Circle Exchange")
    
    print("Comparison example completed!\n")


def run_performance_test():
    """Test performance with many agents."""
    print("=== Performance Test ===")
    
    def test_agent_count(n_agents):
        """Test simulation with n_agents."""
        # Create random positions
        np.random.seed(42)  # For reproducible results
        positions = [(np.random.uniform(-5, 5), np.random.uniform(-5, 5)) for _ in range(n_agents)]
        goals = [(np.random.uniform(-5, 5), np.random.uniform(-5, 5)) for _ in range(n_agents)]
        
        sim = vrorca.PyVRORCASimulator(
            timeStep=1/60.,
            neighborDist=2.0,
            maxNeighbors=5,
            timeHorizon=1.5,
            timeHorizonObst=1.5,
            radius=0.2,
            maxSpeed=2.0,
            prefSpeed=1.5
        )
        
        # Add agents
        agent_ids = [sim.addAgent(pos) for pos in positions]
        
        # Time simulation steps
        start_time = time.time()
        n_steps = 50
        
        for step in range(n_steps):
            # Set random preferred velocities
            for i, agent_id in enumerate(agent_ids):
                direction = np.array(goals[i]) - np.array(sim.getAgentPosition(agent_id))
                if np.linalg.norm(direction) > 0.1:
                    pref_vel = direction / np.linalg.norm(direction) * 1.0
                    sim.setAgentPrefVelocity(agent_id, tuple(pref_vel))
            
            sim.doStep()
        
        elapsed_time = time.time() - start_time
        steps_per_second = n_steps / elapsed_time
        
        print(f"Agents: {n_agents:3d}, Steps/sec: {steps_per_second:6.1f}, "
              f"Time per step: {elapsed_time/n_steps*1000:5.1f}ms")
        
        return steps_per_second

    # Test with different agent counts
    agent_counts = [10, 25, 50, 100, 200]
    performance_results = []
    
    for count in agent_counts:
        perf = test_agent_count(count)
        performance_results.append((count, perf))
    
    print("Performance test completed!\n")


def run_advanced_features():
    """Demonstrate VR-ORCA specific features."""
    print("=== VR-ORCA Advanced Features ===")
    
    sim = vrorca.PyVRORCASimulator(1/60., 2.0, 8, 2.0, 2.0, 0.3, 1.5, 1.0)
    
    # Create a more complex scenario
    n_agents = 6
    positions = [(np.cos(i * 2*np.pi/n_agents) * 2, np.sin(i * 2*np.pi/n_agents) * 2) 
                 for i in range(n_agents)]
    
    agent_ids = [sim.addAgent(pos) for pos in positions]
    
    # Add some obstacles
    obstacles = [
        [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5)],  # Square obstacle
        [(2.0, 0.0), (2.5, 0.5), (2.0, 1.0), (1.5, 0.5)]       # Diamond obstacle
    ]
    
    for obstacle_vertices in obstacles:
        sim.addObstacle(obstacle_vertices)
    
    sim.processObstacles()
    
    print(f"Created simulation with {sim.getNumAgents()} agents and {sim.getNumObstacleVertices()} obstacle vertices")
    
    # Demonstrate VR-ORCA specific methods
    print(f"Initial total energy: {sim.getTotalEnergy():.3f}")
    print(f"Current weight parameter: {sim.getWeight():.3f}")
    
    # Adjust weight parameter (VR-ORCA specific)
    sim.setWeight(0.8)
    print(f"Updated weight parameter: {sim.getWeight():.3f}")
    
    # Run simulation with detailed information
    for step in range(10):
        # Set preferred velocities toward center
        for agent_id in agent_ids:
            pos = np.array(sim.getAgentPosition(agent_id))
            toward_center = -pos / np.linalg.norm(pos) * 0.5
            sim.setAgentPrefVelocity(agent_id, tuple(toward_center))
        
        sim.doStep()
        
        # Print detailed agent information
        if step % 5 == 0:
            print(f"\nStep {step}:")
            for i, agent_id in enumerate(agent_ids):
                pos = sim.getAgentPosition(agent_id)
                vel = sim.getAgentVelocity(agent_id)
                n_neighbors = sim.getAgentNumAgentNeighbors(agent_id)
                n_orca_lines = sim.getAgentNumORCALines(agent_id)
                
                print(f"  Agent {i}: pos=({pos[0]:5.2f},{pos[1]:5.2f}), "
                      f"vel=({vel[0]:5.2f},{vel[1]:5.2f}), "
                      f"neighbors={n_neighbors}, orca_lines={n_orca_lines}")
    
    print("Advanced features demo completed!\n")


def main():
    """Run all examples."""
    print("VR-ORCA Python Interface Examples")
    print("=" * 40)
    
    try:
        run_basic_example()
        run_comparison_example()
        run_performance_test()
        run_advanced_features()
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure VR-ORCA is properly compiled and installed.")


if __name__ == "__main__":
    main()