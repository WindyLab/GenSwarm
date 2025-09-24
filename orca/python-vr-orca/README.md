# Python VR-ORCA

Python bindings for **VR-ORCA** (Variable Responsibility Optimal Reciprocal Collision Avoidance), an advanced multi-agent collision avoidance algorithm that extends the standard ORCA approach.

## Overview

VR-ORCA improves upon the traditional ORCA algorithm by dynamically adjusting the responsibility distribution between agents for collision avoidance. This leads to more natural, efficient, and smoother agent movements in multi-agent scenarios.

### Key Features

- **Variable Responsibility**: Agents dynamically adjust their collision avoidance responsibility
- **Improved Efficiency**: Better performance in dense multi-agent scenarios
- **Smoother Motion**: More natural agent movements compared to standard ORCA
- **Python-Friendly**: Easy-to-use Python interface similar to python-rvo2
- **High Performance**: C++ backend with Python bindings using Cython

## Installation

### Prerequisites

- Python 3.6+
- CMake 3.10+
- C++ compiler with C++11 support
- Cython 0.29+
- NumPy

### Building from Source

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/WestlakeIUSL/GenSwarm.git
   cd GenSwarm/orca/python-vr-orca
   ```

2. **Install Python dependencies**:
   ```bash
   pip install cython numpy
   ```

3. **Build and install**:
   ```bash
   python setup.py build
   python setup.py install
   ```

### Alternative: Development Installation

For development or if you want to modify the code:

```bash
pip install -e .
```

## Quick Start

Here's a simple example to get you started:

```python
import vrorca

# Create VR-ORCA simulator
sim = vrorca.PyVRORCASimulator(
    timeStep=1/60.,          # Simulation time step
    neighborDist=1.5,        # Neighbor detection distance
    maxNeighbors=5,          # Maximum neighbors to consider
    timeHorizon=1.5,         # Time horizon for agent avoidance
    timeHorizonObst=2.0,     # Time horizon for obstacle avoidance
    radius=0.4,              # Agent radius
    maxSpeed=2.0,            # Maximum agent speed
    prefSpeed=1.0            # Preferred agent speed (VR-ORCA specific)
)

# Add agents
agent1 = sim.addAgent((0, 0))    # Agent at origin
agent2 = sim.addAgent((1, 0))    # Agent at (1, 0)

# Set preferred velocities (desired movement directions)
sim.setAgentPrefVelocity(agent1, (1, 1))   # Move diagonally
sim.setAgentPrefVelocity(agent2, (-1, 1))  # Move diagonally opposite

# Run simulation
for step in range(100):
    sim.doStep()
    
    # Get current positions
    pos1 = sim.getAgentPosition(agent1)
    pos2 = sim.getAgentPosition(agent2)
    
    print(f"Step {step}: Agent1 at {pos1}, Agent2 at {pos2}")
```

## Advanced Usage

### Adding Obstacles

```python
# Add a triangular obstacle
obstacle = sim.addObstacle([
    (0.1, 0.1), 
    (-0.1, 0.1), 
    (-0.1, -0.1)
])

# Process obstacles (must be called after adding all obstacles)
sim.processObstacles()
```

### VR-ORCA Specific Features

```python
# Get VR-ORCA specific information
total_energy = sim.getTotalEnergy()
current_weight = sim.getWeight()

# Adjust responsibility distribution weight
sim.setWeight(0.8)  # Range typically 0.0 to 1.0

# Get preferred speed (VR-ORCA specific parameter)
pref_speed = sim.getAgentPrefSpeed(agent_id)
```

### Detailed Agent Control

```python
# Add agent with custom parameters
agent_id = sim.addAgent(
    pos=(2.0, 3.0),
    neighborDist=2.0,
    maxNeighbors=8,
    timeHorizon=2.5,
    timeHorizonObst=3.0,
    radius=0.5,
    maxSpeed=3.0,
    velocity=(0.5, 0.0)  # Initial velocity
)

# Query agent information
position = sim.getAgentPosition(agent_id)
velocity = sim.getAgentVelocity(agent_id)
neighbors = sim.getAgentNumAgentNeighbors(agent_id)
orca_lines = sim.getAgentNumORCALines(agent_id)

# Modify agent parameters during simulation
sim.setAgentMaxSpeed(agent_id, 2.5)
sim.setAgentRadius(agent_id, 0.6)
```

## API Reference

### Simulator Creation

```python
sim = vrorca.PyVRORCASimulator(timeStep, neighborDist, maxNeighbors, 
                               timeHorizon, timeHorizonObst, radius, 
                               maxSpeed, prefSpeed, velocity=(0,0))
```

### Agent Management

- `addAgent(pos, ...)` - Add agent to simulation
- `setAgentPrefVelocity(agent_id, velocity)` - Set desired velocity
- `getAgentPosition(agent_id)` - Get current position
- `getAgentVelocity(agent_id)` - Get current velocity
- `setAgentPosition(agent_id, pos)` - Set agent position
- `setAgentMaxSpeed(agent_id, speed)` - Set maximum speed

### Obstacle Management

- `addObstacle(vertices)` - Add polygonal obstacle
- `processObstacles()` - Finalize obstacle setup
- `queryVisibility(point1, point2, radius)` - Check line of sight

### Simulation Control

- `doStep()` - Advance simulation by one time step
- `getGlobalTime()` - Get current simulation time
- `setTimeStep(dt)` - Change simulation time step

### VR-ORCA Specific

- `getTotalEnergy()` - Get system energy
- `getWeight()` - Get responsibility weight
- `setWeight(weight)` - Set responsibility weight
- `getAgentPrefSpeed(agent_id)` - Get preferred speed

## Examples

The `example.py` file contains comprehensive examples including:

- **Basic Usage**: Simple multi-agent scenario
- **Comparison Demo**: VR-ORCA vs standard scenarios  
- **Performance Test**: Scaling with different agent counts
- **Advanced Features**: VR-ORCA specific capabilities

Run the examples:

```bash
python example.py
```

## Performance

VR-ORCA provides improved performance in several scenarios:

- **Dense Crowds**: Better handling of high-density agent scenarios
- **Deadlock Resolution**: More effective resolution of deadlock situations
- **Natural Motion**: Smoother, more human-like movement patterns
- **Computational Efficiency**: Optimized responsibility distribution reduces unnecessary computations

## Comparison with Standard ORCA

| Feature | Standard ORCA | VR-ORCA |
|---------|---------------|---------|
| Responsibility Distribution | Fixed (50-50) | Variable/Dynamic |
| Deadlock Handling | Basic | Enhanced |
| Motion Smoothness | Good | Better |
| Dense Scenario Performance | Good | Superior |
| Computational Overhead | Low | Slightly Higher |

## Integration with GenSwarm

This VR-ORCA Python interface is designed to integrate seamlessly with the GenSwarm framework:

```python
# Use in GenSwarm physics engine
from modules.deployment.engine.vrorca_engine import VRORCAEngine

engine = VRORCAEngine()
# VR-ORCA will be used for collision avoidance
```

## Troubleshooting

### Build Issues

1. **CMake not found**: Install CMake 3.10+
2. **Compiler errors**: Ensure C++11 compatible compiler
3. **Cython issues**: Update Cython to latest version

### Runtime Issues

1. **Import errors**: Check installation and Python path
2. **Segmentation faults**: Verify agent/obstacle parameters are valid
3. **Performance issues**: Reduce `maxNeighbors` or `neighborDist`

### Common Solutions

```bash
# Clean build
rm -rf build/
python setup.py clean --all

# Reinstall dependencies
pip install --upgrade cython numpy

# Debug build
CYTHON_DEBUG=1 python setup.py build_ext --inplace
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## References

- **VR-ORCA Paper**: Guo K, Wang D, Fan T, et al. "VR-ORCA: Variable responsibility optimal reciprocal collision avoidance." IEEE Robotics and Automation Letters, 2021.
- **Original ORCA**: Van Den Berg J, et al. "Reciprocal velocity obstacles for real-time multi-agent navigation." ICRA 2008.
- **RVO2 Library**: http://gamma.cs.unc.edu/RVO2/

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@article{guo2021vrorca,
  title={VR-ORCA: Variable responsibility optimal reciprocal collision avoidance},
  author={Guo, Kun and Wang, Dinesh and Fan, Tingxiang and others},
  journal={IEEE Robotics and Automation Letters},
  volume={6},
  number={3},
  pages={4520--4527},
  year={2021},
  publisher={IEEE}
}
```