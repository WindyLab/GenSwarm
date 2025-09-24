"""
Utility functions for VR-ORCA Python interface.

This module provides helper functions and utilities to make working with
VR-ORCA more convenient in Python applications.
"""

import numpy as np
import math
from typing import List, Tuple, Optional, Union


def create_circle_formation(n_agents: int, radius: float, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    """
    Create agent positions in a circle formation.
    
    Args:
        n_agents: Number of agents to place
        radius: Radius of the circle
        center: Center of the circle (x, y)
        
    Returns:
        List of (x, y) positions
    """
    positions = []
    for i in range(n_agents):
        angle = 2 * math.pi * i / n_agents
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        positions.append((x, y))
    return positions


def create_grid_formation(rows: int, cols: int, spacing: float, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    """
    Create agent positions in a grid formation.
    
    Args:
        rows: Number of rows
        cols: Number of columns
        spacing: Distance between adjacent agents
        center: Center of the grid (x, y)
        
    Returns:
        List of (x, y) positions
    """
    positions = []
    start_x = center[0] - (cols - 1) * spacing / 2
    start_y = center[1] - (rows - 1) * spacing / 2
    
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * spacing
            y = start_y + row * spacing
            positions.append((x, y))
    
    return positions


def create_line_formation(n_agents: int, spacing: float, angle: float = 0, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    """
    Create agent positions in a line formation.
    
    Args:
        n_agents: Number of agents
        spacing: Distance between adjacent agents
        angle: Angle of the line in radians
        center: Center of the line (x, y)
        
    Returns:
        List of (x, y) positions
    """
    positions = []
    start_offset = -(n_agents - 1) * spacing / 2
    
    for i in range(n_agents):
        offset = start_offset + i * spacing
        x = center[0] + offset * math.cos(angle)
        y = center[1] + offset * math.sin(angle)
        positions.append((x, y))
    
    return positions


def calculate_centroid(positions: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate the centroid of a list of positions.
    
    Args:
        positions: List of (x, y) positions
        
    Returns:
        Centroid position (x, y)
    """
    if not positions:
        return (0, 0)
    
    sum_x = sum(pos[0] for pos in positions)
    sum_y = sum(pos[1] for pos in positions)
    n = len(positions)
    
    return (sum_x / n, sum_y / n)


def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """
    Normalize a 2D vector to unit length.
    
    Args:
        vector: Input vector (x, y)
        
    Returns:
        Normalized vector (x, y)
    """
    x, y = vector
    length = math.sqrt(x*x + y*y)
    
    if length < 1e-10:
        return (0, 0)
    
    return (x / length, y / length)


def vector_magnitude(vector: Tuple[float, float]) -> float:
    """
    Calculate the magnitude of a 2D vector.
    
    Args:
        vector: Input vector (x, y)
        
    Returns:
        Magnitude of the vector
    """
    x, y = vector
    return math.sqrt(x*x + y*y)


def vector_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """
    Calculate the Euclidean distance between two positions.
    
    Args:
        pos1: First position (x, y)
        pos2: Second position (x, y)
        
    Returns:
        Distance between positions
    """
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return math.sqrt(dx*dx + dy*dy)


def create_rectangular_obstacle(width: float, height: float, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    """
    Create vertices for a rectangular obstacle.
    
    Args:
        width: Width of the rectangle
        height: Height of the rectangle
        center: Center of the rectangle (x, y)
        
    Returns:
        List of vertices in counterclockwise order
    """
    half_w = width / 2
    half_h = height / 2
    cx, cy = center
    
    return [
        (cx - half_w, cy - half_h),  # Bottom-left
        (cx + half_w, cy - half_h),  # Bottom-right
        (cx + half_w, cy + half_h),  # Top-right
        (cx - half_w, cy + half_h)   # Top-left
    ]


def create_circular_obstacle(radius: float, n_vertices: int = 16, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    """
    Create vertices for a circular obstacle (approximated as polygon).
    
    Args:
        radius: Radius of the circle
        n_vertices: Number of vertices to approximate the circle
        center: Center of the circle (x, y)
        
    Returns:
        List of vertices in counterclockwise order
    """
    vertices = []
    cx, cy = center
    
    for i in range(n_vertices):
        angle = 2 * math.pi * i / n_vertices
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    
    return vertices


class SimulationRecorder:
    """
    Utility class to record simulation data for analysis and visualization.
    """
    
    def __init__(self):
        self.positions_history = []
        self.velocities_history = []
        self.time_steps = []
        
    def record_step(self, sim, agent_ids: List[int], time: float):
        """
        Record the current state of the simulation.
        
        Args:
            sim: VR-ORCA simulator instance
            agent_ids: List of agent IDs to record
            time: Current simulation time
        """
        positions = [sim.getAgentPosition(agent_id) for agent_id in agent_ids]
        velocities = [sim.getAgentVelocity(agent_id) for agent_id in agent_ids]
        
        self.positions_history.append(positions)
        self.velocities_history.append(velocities)
        self.time_steps.append(time)
    
    def get_trajectory(self, agent_index: int) -> List[Tuple[float, float]]:
        """
        Get the trajectory of a specific agent.
        
        Args:
            agent_index: Index of the agent in the recorded list
            
        Returns:
            List of positions over time
        """
        return [step[agent_index] for step in self.positions_history]
    
    def get_velocities(self, agent_index: int) -> List[Tuple[float, float]]:
        """
        Get the velocity history of a specific agent.
        
        Args:
            agent_index: Index of the agent in the recorded list
            
        Returns:
            List of velocities over time
        """
        return [step[agent_index] for step in self.velocities_history]
    
    def calculate_path_length(self, agent_index: int) -> float:
        """
        Calculate the total path length traveled by an agent.
        
        Args:
            agent_index: Index of the agent
            
        Returns:
            Total path length
        """
        trajectory = self.get_trajectory(agent_index)
        if len(trajectory) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(1, len(trajectory)):
            total_length += vector_distance(trajectory[i-1], trajectory[i])
        
        return total_length
    
    def clear(self):
        """Clear all recorded data."""
        self.positions_history.clear()
        self.velocities_history.clear()
        self.time_steps.clear()


def simulate_scenario(sim, agent_ids: List[int], goal_positions: List[Tuple[float, float]], 
                     max_steps: int = 1000, goal_tolerance: float = 0.2, 
                     record: bool = False) -> Tuple[bool, Optional[SimulationRecorder]]:
    """
    Run a complete simulation scenario until agents reach their goals.
    
    Args:
        sim: VR-ORCA simulator instance
        agent_ids: List of agent IDs
        goal_positions: List of goal positions for each agent
        max_steps: Maximum number of simulation steps
        goal_tolerance: Distance tolerance for reaching goals
        record: Whether to record simulation data
        
    Returns:
        Tuple of (success, recorder). Success is True if all agents reached goals.
        Recorder is provided if record=True.
    """
    recorder = SimulationRecorder() if record else None
    
    for step in range(max_steps):
        # Set preferred velocities toward goals
        all_reached = True
        
        for i, agent_id in enumerate(agent_ids):
            current_pos = sim.getAgentPosition(agent_id)
            goal_pos = goal_positions[i]
            
            distance_to_goal = vector_distance(current_pos, goal_pos)
            
            if distance_to_goal > goal_tolerance:
                all_reached = False
                # Calculate preferred velocity toward goal
                direction = (goal_pos[0] - current_pos[0], goal_pos[1] - current_pos[1])
                normalized_dir = normalize_vector(direction)
                max_speed = sim.getAgentMaxSpeed(agent_id)
                pref_velocity = (normalized_dir[0] * max_speed, normalized_dir[1] * max_speed)
                sim.setAgentPrefVelocity(agent_id, pref_velocity)
            else:
                # Agent reached goal, stop moving
                sim.setAgentPrefVelocity(agent_id, (0, 0))
        
        # Simulation step
        sim.doStep()
        
        # Record data if requested
        if recorder:
            recorder.record_step(sim, agent_ids, sim.getGlobalTime())
        
        # Check if all agents reached their goals
        if all_reached:
            return True, recorder
    
    return False, recorder