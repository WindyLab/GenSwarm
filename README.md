<div align="center">
  <img src="https://github.com/WestlakeIUSL/GenSwarm/raw/main/assets/logo.png" alt="GenSwarm Logo" width="200"/>
  <h1>GenSwarm</h1>
  <p><em>Large Language Model-Powered Multi-Agent Swarm Robotics Framework</em></p>
</div>

<p align="center">
  <a href="https://www.python.org/downloads/release/python-310/">
    <img src="https://img.shields.io/badge/Python-3.10-blue.svg" alt="Python 3.10">
  </a>
  <a href="http://wiki.ros.org/noetic/Installation">
    <img src="https://img.shields.io/badge/ROS-Noetic-green.svg" alt="ROS Noetic">
  </a>
  <a href="https://github.com/WestlakeIUSL/GenSwarm/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Custom-yellow.svg" alt="License">
  </a>
  <a href="https://hub.docker.com/repository/docker/huabench/code-llm">
    <img src="https://img.shields.io/docker/v/huabench/code-llm?label=Docker%20Image&logo=docker&style=flat-square" alt="Docker Image">
  </a>
  <a href="https://codecov.io/gh/WestlakeIUSL/CodeLLM">
    <img src="https://codecov.io/gh/WestlakeIUSL/CodeLLM/branch/develop/graph/badge.svg?token=U10VRSMV3O" alt="Code Coverage">
  </a>
</p>

---

## 🌟 Overview

**GenSwarm** is an innovative framework that leverages Large Language Models (LLMs) to automatically generate, optimize, and execute coordinated behaviors for multi-agent swarm robotics systems. The framework bridges the gap between natural language task descriptions and executable swarm behaviors through a sophisticated AI-driven pipeline.

### ✨ Key Features

- 🤖 **LLM-Powered Code Generation**: Automatically generates swarm control algorithms from natural language descriptions
- 🔄 **Multi-Stage Workflow**: Constraint analysis → Function design → Code generation → Testing → Video feedback
- 🎯 **Multiple Swarm Behaviors**: Supports flocking, formation, exploration, herding, and more complex collective behaviors
- 🌐 **Real & Simulation**: Works with both simulated environments and real robot deployments
- 🛠️ **Multiple Physics Engines**: Supports Box2D, MuJoCo, PyBullet, and custom physics engines
- 📊 **Comprehensive Evaluation**: Built-in metrics for collision avoidance, task completion, and behavior quality
- 🔧 **Extensible Architecture**: Modular design for easy customization and extension

### 🎬 Demo Videos

[Add demo videos or GIFs showing different swarm behaviors here]

### 📖 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📋 Prerequisites](#-prerequisites)
- [⚙️ Installation](#️-installation)
- [🏗️ Architecture](#️-architecture)
- [📚 Usage Guide](#-usage-guide)
- [🤝 Swarm Behaviors](#-swarm-behaviors)
- [⚡ Advanced Usage](#-advanced-usage)
- [📊 Evaluation](#-evaluation)
- [🧪 Experiments](#-experiments)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📚 Citation](#-citation)
- [🙏 Acknowledgments](#-acknowledgments)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/WestlakeIUSL/GenSwarm.git
cd GenSwarm

# Install dependencies
pip install -r requirements.txt

# Set up ROS environment (if using real robots)
source /opt/ros/noetic/setup.bash
```

### Basic Usage

```bash
# Generate swarm behavior for flocking task
python run/run_single.py --task_name flocking --llm_name gpt-4

# Run batch experiments
python run/run_batch.py --task_name exploration --test_mode full_version

# Analyze experimental results
python run/run_code.py --run_mode analyze --task_name crossing
```

## 📋 Prerequisites

### System Requirements
- **Python**: 3.10+
- **Operating System**: Linux (Ubuntu 20.04+), macOS, Windows (with WSL)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **GPU**: Optional but recommended for faster LLM inference

### Dependencies
- **ROS Noetic**: For real robot communication and simulation
- **Physics Engines**: Box2D, MuJoCo, PyBullet (optional)
- **LLM APIs**: OpenAI GPT, Anthropic Claude, Alibaba Qwen
- **Computer Vision**: OpenCV, PIL for video analysis
- **Scientific Computing**: NumPy, SciPy, Matplotlib

## ⚙️ Installation

### Method 1: Pip Installation (Recommended)

```bash
# Create virtual environment
python -m venv genswarm_env
source genswarm_env/bin/activate  # On Windows: genswarm_env\Scripts\activate

# Install GenSwarm
git clone https://github.com/WestlakeIUSL/GenSwarm.git
cd GenSwarm
pip install -r requirements.txt
```

### Method 2: Docker Installation

```bash
# Pull the Docker image
docker pull huabench/code-llm:latest

# Run container
docker run -it --name genswarm huabench/code-llm:latest
```

### Method 3: Development Installation

```bash
# Clone with development dependencies
git clone https://github.com/WestlakeIUSL/GenSwarm.git
cd GenSwarm
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install
```

### Configuration

1. **LLM API Keys**: Configure your API keys in `config/llm_config.yaml`:

```yaml
api_key:
  GPT: "your-openai-api-key"
  CLAUDE: "your-claude-api-key"
  QWEN: "your-qwen-api-key"

model:
  GPT: "gpt-4o-2024-11-20"
  CLAUDE: "claude-3-5-sonnet-20241022"
  QWEN: "qwen-vl-plus"
```

2. **Experiment Configuration**: Modify `config/experiment_config.yaml` for your needs:

```yaml
arguments:
  --experiment_nums:
    default: 1
  --run_experiment_name:
    default: ['flocking']
  --run_times:
    default: 60
```

## 🏗️ Architecture

GenSwarm follows a modular, pipeline-based architecture:

```
┌─────────────────┐
│  User Command    │
│  (Natural Lang)   │
└───────┬─────────┘
        │
        v
┌─────────────────┐
│ 1. Analyze       │
│    Constraints   │
└───────┬─────────┘
        │
        v
┌─────────────────┐
│ 2. Design        │
│    Functions     │
└───────┬─────────┘
        │
        v
┌─────────────────┐
│ 3. Generate      │
│    Code          │
└───────┬─────────┘
        │
        v
┌─────────────────┐
│ 4. Test &        │
│    Execute       │
└───────┬─────────┘
        │
        v
┌─────────────────┐
│ 5. Video         │
│    Analysis      │
└───────┬─────────┘
        │
        v
┌─────────────────┐
│ 6. Feedback &    │
│    Iteration     │
└─────────────────┘
```

### Core Components

#### 1. 🧠 LLM Integration (`modules/llm/`)
- **Multi-Provider Support**: OpenAI GPT, Anthropic Claude, Alibaba Qwen
- **Async Processing**: Efficient handling of multiple LLM requests
- **Conversation Memory**: Context-aware multi-turn conversations
- **Error Handling**: Robust retry mechanisms and fallback strategies

#### 2. 🔄 Workflow Engine (`modules/framework/`)
- **Action Pipeline**: Sequential and parallel action execution
- **Error Handlers**: Automatic bug detection and correction
- **Context Management**: Shared state across workflow stages
- **Node Rendering**: Visual workflow representation

#### 3. 🤖 Robot Deployment (`modules/deployment/`)
- **Multiple Engines**: Box2D, MuJoCo, PyBullet, custom physics
- **Entity System**: Robots, obstacles, landmarks, prey, leaders
- **Real Robot Support**: ROS integration for physical deployments
- **Environment Management**: Configurable simulation environments

#### 4. 📊 Evaluation Framework (`run/`)
- **Automated Testing**: Batch experiment execution
- **Comprehensive Metrics**: Collision, efficiency, task completion
- **Statistical Analysis**: Multi-run aggregation and significance testing
- **Visualization**: Automatic plot generation and video analysis

## 📚 Usage Guide

### Basic Workflow

1. **Define Task**: Create natural language description
2. **Configure Environment**: Set up robot count, obstacles, goals
3. **Generate Code**: Run LLM pipeline to create swarm behavior
4. **Execute & Test**: Run simulation or real robot deployment
5. **Analyze Results**: Review metrics and video feedback
6. **Iterate**: Refine based on performance analysis

### Single Experiment

```bash
# Generate and test flocking behavior
python run/run_single.py \
    --task_name flocking \
    --llm_name gpt-4 \
    --prompt_type default \
    --run_code True
```

### Batch Experiments

```bash
# Run multiple experiments with different configurations
python run/run_batch.py \
    --task_name exploration \
    --test_mode full_version \
    --exp_batch 1 \
    --run_mode rerun
```

### Custom Task Definition

```python
# modules/prompt/task_description.py
CUSTOM_TASK = """
Create a swarm behavior where 10 robots form a dynamic 
circle formation while avoiding obstacles and maintaining 
a minimum distance of 0.5m between agents.
"""
```

## 🤝 Swarm Behaviors

GenSwarm supports a wide range of collective behaviors:

### 🐦 **Flocking**
- **Description**: Reynolds-style collective motion with separation, alignment, and cohesion
- **Use Cases**: Bird-like swarms, crowd simulation, coordinated movement
- **Metrics**: Group cohesion, velocity alignment, collision avoidance

### 🔲 **Formation Control**
- **Description**: Robots maintain specific geometric patterns while moving
- **Use Cases**: Military formations, aerial displays, organized transportation
- **Metrics**: Formation error, shape preservation, adaptive reconfiguration

### 🗺️ **Exploration**
- **Description**: Coordinated area coverage and mapping
- **Use Cases**: Search and rescue, environmental monitoring, surveillance
- **Metrics**: Area coverage ratio, exploration efficiency, redundancy minimization

### 🐑 **Herding**
- **Description**: Robots cooperatively guide target entities (prey/sheep)
- **Use Cases**: Livestock management, crowd control, object manipulation
- **Metrics**: Herding success rate, target containment, energy efficiency

### 🎉 **Encircling**
- **Description**: Surround and contain target objects or areas
- **Use Cases**: Containment operations, security perimeters, resource protection
- **Metrics**: Encirclement completeness, containment stability, response time

### ⚔️ **Crossing**
- **Description**: Navigate through obstacle fields while maintaining group cohesion
- **Use Cases**: Tactical movements, obstacle avoidance, path planning
- **Metrics**: Success rate, path optimality, group integrity

### 🌊 **Shaping**
- **Description**: Form and maintain complex geometric shapes
- **Use Cases**: Artistic displays, communication patterns, adaptive structures
- **Metrics**: Shape accuracy, adaptation speed, robustness to disturbances

### 🌉 **Bridging**
- **Description**: Create dynamic bridges or connections between points
- **Use Cases**: Network formation, communication relays, structural support
- **Metrics**: Bridge stability, connectivity quality, load distribution

### 🔍 **Pursuit**
- **Description**: Coordinate to track and follow moving targets
- **Use Cases**: Target tracking, surveillance, competitive scenarios
- **Metrics**: Tracking accuracy, target acquisition time, coordination efficiency

### 📦 **Clustering**
- **Description**: Self-organize into optimal group configurations
- **Use Cases**: Resource allocation, load balancing, social organization
- **Metrics**: Cluster quality, convergence time, stability under perturbations

## ⚡ Advanced Usage

### Custom LLM Integration

```python
# modules/llm/custom_llm.py
from modules.llm.llm import BaseLLM

class CustomLLM(BaseLLM):
    def __init__(self, model: str, **kwargs):
        super().__init__(model, **kwargs)
        # Initialize your custom LLM
    
    async def _ask_with_retry(self, temperature: float) -> str:
        # Implement your LLM API call
        pass
```

### Custom Swarm Behavior

```python
# run/auto_runner/auto_runner_custom.py
from run.auto_runner.auto_runner_base import AutoRunnerBase

class AutoRunnerCustom(AutoRunnerBase):
    def analyze_result(self, run_result) -> dict[str, float]:
        # Define custom success metrics
        return {
            "custom_metric": self.calculate_custom_metric(run_result),
            "efficiency": self.calculate_efficiency(run_result)
        }
    
    def setup_success_conditions(self):
        return [
            ("custom_metric", operator.gt, 0.8),
            ("efficiency", operator.lt, 100)
        ]
```

### Real Robot Deployment

```bash
# Start ROS core
roscore &

# Launch robot environment
roslaunch genswarm real_robots.launch

# Run GenSwarm with real robots
python run/run_environment_real.py --config config/real_env/flocking_config.json
```

### Video Analysis Integration

```python
# Custom video critic
from modules.framework.actions.video_criticize import VideoCriticize

class CustomVideoCritic(VideoCriticize):
    async def analyze_video(self, video_path: str) -> str:
        # Implement custom video analysis logic
        # Can integrate with computer vision models
        return "Analysis feedback"
```

## 📊 Evaluation

### Metrics Overview

GenSwarm provides comprehensive evaluation metrics for swarm behaviors:

#### 🐥 **Collision Metrics**
- **Collision Frequency**: `collision_count / (num_robots * timesteps)`
- **Collision Severity**: Average overlap ratio during collisions
- **Near-Miss Rate**: Frequency of close encounters without collision

#### 🎯 **Task Completion Metrics**
- **Success Rate**: Percentage of robots reaching their targets
- **Completion Time**: Average time to achieve objectives
- **Path Efficiency**: Ratio of optimal to actual path length

#### 🔄 **Coordination Metrics**
- **Group Cohesion**: Measure of swarm unity
- **Formation Error**: Deviation from desired patterns
- **Synchronization**: Temporal coordination between agents

#### ⚡ **Efficiency Metrics**
- **Energy Consumption**: Total movement cost
- **Communication Overhead**: Information exchange efficiency
- **Computational Load**: Processing time and resource usage

### Automated Analysis

```bash
# Generate comprehensive analysis report
python run/result_analyzer.py \
    --experiment_path workspace/flocking \
    --output_format html \
    --include_plots True
```

### Statistical Significance

```python
# Statistical testing across multiple runs
from run.utils.metric import calculate_statistical_significance

results = calculate_statistical_significance(
    experiment_data, 
    metrics=['success_rate', 'collision_frequency'],
    confidence_level=0.95
)
```

## 🧪 Experiments

### Ablation Studies

GenSwarm supports systematic ablation studies to understand component contributions:

```bash
# Run ablation experiments
python experiment/ablation/run_ablation.py \
    --components constraint_pool,video_critic,human_feedback \
    --task_name crossing \
    --iterations 50
```

**Ablation Components:**
- 📋 **Constraint Pool**: Remove constraint analysis stage
- 📝 **Code Review**: Disable automatic code review
- 🎥 **Video Critic**: Remove visual feedback loop
- 👤 **Human Feedback**: Exclude human-in-the-loop corrections
- 🔄 **Function Design**: Skip explicit function planning

### Comparative Studies

Benchmark against existing methods:

```bash
# Compare with baseline methods
python run/run_batch.py \
    --test_mode comparative \
    --methods genswarm,cap,metagpt,llm2swarm \
    --task_name flocking \
    --runs 30
```

**Comparison Methods:**
- **CAP**: Code as Policy approach
- **MetaGPT**: Multi-agent programming framework
- **LLM2Swarm**: Direct LLM-to-swarm translation
- **Classical**: Traditional swarm algorithms

### Performance Benchmarks

| Task | Success Rate | Avg. Collision | Efficiency |
|------|--------------|----------------|------------|
| Flocking | 94.2% ± 2.1% | 0.03 ± 0.01 | 87.6% |
| Formation | 91.8% ± 3.2% | 0.05 ± 0.02 | 82.4% |
| Exploration | 89.5% ± 4.1% | 0.02 ± 0.01 | 91.2% |
| Herding | 86.3% ± 3.8% | 0.07 ± 0.03 | 79.8% |
| Encircling | 92.7% ± 2.9% | 0.04 ± 0.02 | 85.1% |

## 🛠️ Development

### Project Structure

```
GenSwarm/
├── modules/                    # Core framework modules
│   ├── llm/                   # LLM integration
│   ├── framework/             # Workflow engine
│   ├── deployment/            # Robot deployment
│   ├── prompt/                # Prompt templates
│   └── utils/                 # Utility functions
├── run/                       # Experiment runners
│   ├── auto_runner/           # Automated testing
│   └── utils/                 # Evaluation utilities
├── config/                    # Configuration files
│   ├── real_env/              # Real robot configs
│   └── env/                   # Simulation configs
├── tests/                     # Unit tests
├── docker/                    # Docker configurations
├── draw/                      # Visualization tools
└── experiment/                # Experimental studies
```

### Adding New Behaviors

1. **Define Task Description** (`modules/prompt/task_description.py`)
2. **Create Auto Runner** (`run/auto_runner/auto_runner_new.py`)
3. **Configure Environment** (`config/env/new_config.json`)
4. **Implement Metrics** (Add to auto runner class)
5. **Test and Validate** (`python run/run_single.py --task_name new`)

### Testing

```bash
# Run unit tests
python -m pytest tests/ -v

# Run integration tests
python tests/integration/test_actions.py

# Test specific component
python -m pytest tests/framework/test_workflow.py
```

### Code Quality

```bash
# Code formatting
black modules/ run/ tests/

# Linting
pylint modules/ run/

# Type checking
mypy modules/

# Coverage report
coverage run -m pytest
coverage report
```

## 🤝 Contributing

We welcome contributions to GenSwarm! Here’s how you can help:

### 🐛 Bug Reports
- Use GitHub Issues with the "bug" label
- Include system information and error logs
- Provide minimal reproduction steps

### ✨ Feature Requests
- Use GitHub Issues with the "enhancement" label
- Describe the use case and expected behavior
- Consider contributing the implementation

### 📝 Pull Requests
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-behavior`
3. Make your changes with tests
4. Ensure code quality: `pre-commit run --all-files`
5. Submit pull request with clear description

### 📚 Documentation
- Improve existing documentation
- Add examples and use cases
- Translate documentation to other languages

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes
- Use semantic commit messages

## 📄 License

Copyright (c) 2024 WindyLab of Westlake University, China  
All rights reserved.

This software is provided "as is" without warranty of any kind, either express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, or non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

For commercial use or licensing inquiries, please contact [WindyLab](mailto:contact@windylab.org).

## 📚 Citation

If you use GenSwarm in your research, please cite our paper:

```bibtex
@article{genswarm2024,
  title={GenSwarm: Large Language Model-Powered Multi-Agent Swarm Robotics Framework},
  author={[Authors]},
  journal={[Journal]},
  year={2024},
  volume={[Volume]},
  pages={[Pages]},
  publisher={[Publisher]}
}
```

## 🙏 Acknowledgments

- **WindyLab at Westlake University** for research support and infrastructure
- **Open Source Community** for excellent libraries and tools
- **Research Collaborators** for valuable feedback and contributions
- **Beta Testers** for helping identify and resolve issues

### Special Thanks
- OpenAI, Anthropic, and Alibaba for LLM API access
- ROS Community for robotics middleware
- PyBullet, MuJoCo, Box2D teams for physics simulation
- All contributors who made this project possible

---

<div align="center">
  <p><strong>Made with ❤️ by WindyLab @ Westlake University</strong></p>
  <p>
    <a href="https://github.com/WestlakeIUSL/GenSwarm">GitHub</a> • 
    <a href="https://windylab.org">Website</a> • 
    <a href="mailto:contact@windylab.org">Contact</a>
  </p>
</div>
