"""
Python VR-ORCA (Variable Responsibility Optimal Reciprocal Collision Avoidance)

This package provides Python bindings for the VR-ORCA algorithm, an advanced
multi-agent collision avoidance system that improves upon the standard ORCA
approach by dynamically adjusting responsibility distribution between agents.

Basic usage:
    import vrorca
    
    sim = vrorca.PyVRORCASimulator(1/60., 1.5, 5, 1.5, 2, 0.4, 2, 1.0)
    agent = sim.addAgent((0, 0))
    sim.setAgentPrefVelocity(agent, (1, 0))
    sim.doStep()
    position = sim.getAgentPosition(agent)

For more detailed examples, see example.py
"""

from .vrorca import PyVRORCASimulator, PyRVOSimulator

__version__ = "1.0.0"
__author__ = "GenSwarm Team"
__email__ = "contact@genswarm.org"

__all__ = ['PyVRORCASimulator', 'PyRVOSimulator']