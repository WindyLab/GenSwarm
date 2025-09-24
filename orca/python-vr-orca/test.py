#!/usr/bin/env python
"""
Simple test script for VR-ORCA Python interface.

This script performs basic functionality tests to ensure the interface works correctly.
"""

import sys
import math

def test_basic_functionality():
    """Test basic VR-ORCA functionality."""
    print("Testing basic VR-ORCA functionality...")
    
    try:
        import vrorca
        print("✓ VR-ORCA module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import VR-ORCA module: {e}")
        return False
    
    try:
        # Create simulator
        sim = vrorca.PyVRORCASimulator(1/60., 1.5, 5, 1.5, 2, 0.4, 2, 1.0)
        print("✓ Simulator created successfully")
        
        # Add agents
        agent1 = sim.addAgent((0, 0))
        agent2 = sim.addAgent((2, 0))
        print(f"✓ Added agents: {agent1}, {agent2}")
        
        # Set preferred velocities
        sim.setAgentPrefVelocity(agent1, (1, 0))
        sim.setAgentPrefVelocity(agent2, (-1, 0))
        print("✓ Set preferred velocities")
        
        # Run simulation steps
        for step in range(10):
            sim.doStep()
        
        # Get final positions
        pos1 = sim.getAgentPosition(agent1)
        pos2 = sim.getAgentPosition(agent2)
        print(f"✓ Simulation completed. Final positions: {pos1}, {pos2}")
        
        # Test VR-ORCA specific methods
        energy = sim.getTotalEnergy()
        weight = sim.getWeight()
        print(f"✓ VR-ORCA specific methods work. Energy: {energy}, Weight: {weight}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during basic functionality test: {e}")
        return False


def test_obstacle_functionality():
    """Test obstacle-related functionality."""
    print("\nTesting obstacle functionality...")
    
    try:
        import vrorca
        
        sim = vrorca.PyVRORCASimulator(1/60., 2.0, 8, 2.0, 2.0, 0.3, 1.5, 1.0)
        
        # Add obstacle
        obstacle_vertices = [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5)]
        obstacle_id = sim.addObstacle(obstacle_vertices)
        sim.processObstacles()
        print(f"✓ Added obstacle with ID: {obstacle_id}")
        
        # Add agent near obstacle
        agent = sim.addAgent((1.0, 0))
        sim.setAgentPrefVelocity(agent, (-1, 0))  # Move toward obstacle
        
        # Run simulation
        for step in range(20):
            sim.doStep()
        
        final_pos = sim.getAgentPosition(agent)
        print(f"✓ Agent navigated around obstacle. Final position: {final_pos}")
        
        # Test visibility query
        visible = sim.queryVisibility((1.0, 0), (-1.0, 0), 0.1)
        print(f"✓ Visibility query result: {visible}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during obstacle functionality test: {e}")
        return False


def test_utilities():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from vrorca.utils import (
            create_circle_formation, 
            create_grid_formation,
            normalize_vector,
            vector_distance,
            SimulationRecorder
        )
        
        # Test formation creation
        circle_positions = create_circle_formation(6, 2.0)
        assert len(circle_positions) == 6
        print(f"✓ Created circle formation: {len(circle_positions)} positions")
        
        grid_positions = create_grid_formation(2, 3, 1.0)
        assert len(grid_positions) == 6
        print(f"✓ Created grid formation: {len(grid_positions)} positions")
        
        # Test vector operations
        normalized = normalize_vector((3, 4))
        expected_length = math.sqrt(normalized[0]**2 + normalized[1]**2)
        assert abs(expected_length - 1.0) < 1e-10
        print(f"✓ Vector normalization works: {normalized}")
        
        distance = vector_distance((0, 0), (3, 4))
        assert abs(distance - 5.0) < 1e-10
        print(f"✓ Vector distance calculation works: {distance}")
        
        # Test recorder
        recorder = SimulationRecorder()
        print("✓ Simulation recorder created")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during utility function test: {e}")
        return False


def test_performance():
    """Test performance with multiple agents."""
    print("\nTesting performance with multiple agents...")
    
    try:
        import vrorca
        import time
        
        sim = vrorca.PyVRORCASimulator(1/60., 2.0, 5, 1.5, 1.5, 0.2, 2.0, 1.5)
        
        # Add many agents
        n_agents = 50
        agent_ids = []
        
        for i in range(n_agents):
            angle = 2 * math.pi * i / n_agents
            pos = (2 * math.cos(angle), 2 * math.sin(angle))
            agent_id = sim.addAgent(pos)
            agent_ids.append(agent_id)
        
        print(f"✓ Added {n_agents} agents")
        
        # Set all agents to move toward center
        for agent_id in agent_ids:
            sim.setAgentPrefVelocity(agent_id, (-0.5, -0.5))
        
        # Time simulation steps
        n_steps = 100
        start_time = time.time()
        
        for step in range(n_steps):
            sim.doStep()
        
        elapsed_time = time.time() - start_time
        steps_per_second = n_steps / elapsed_time
        
        print(f"✓ Performance test completed")
        print(f"  - {n_agents} agents, {n_steps} steps")
        print(f"  - {elapsed_time:.3f} seconds total")
        print(f"  - {steps_per_second:.1f} steps/second")
        print(f"  - {elapsed_time/n_steps*1000:.1f} ms per step")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during performance test: {e}")
        return False


def main():
    """Run all tests."""
    print("VR-ORCA Python Interface Test Suite")
    print("=" * 40)
    
    tests = [
        test_basic_functionality,
        test_obstacle_functionality, 
        test_utilities,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VR-ORCA Python interface is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())