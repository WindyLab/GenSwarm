# Prompt 提示词模块

## 概述

`prompt` 模块是系统与LLM交互的关键，包含了针对不同阶段和任务定制的提示词模板。好的提示词设计直接决定了代码生成的质量。

## 模块结构

```
prompt/
├── __init__.py                      # 模块导出和Prompt类
├── base_prompt.py                   # 提示词管理类
├── analyze_stage_prompt.py          # 分析阶段提示词
├── design_stage_prompt.py           # 设计阶段提示词
├── coding_stage_prompt.py           # 编码阶段提示词
├── code_review_stage_prompt.py      # 代码审查提示词
├── run_code_prompt.py              # 运行代码提示词
├── video_critic_prompt.py          # 视频评估提示词
├── env_description_prompt.py       # 环境描述
├── task_description.py             # 任务描述
├── robot_api_prompt.py             # 机器人API说明
└── user_requirements.py            # 用户需求模板
```

## 提示词管理类

### Prompt - 提示词管理器

统一管理所有提示词模板：

```python
class Prompt:
    def __init__(self):
        self.action_map: dict = {
            "AnalyzeConstraints": ANALYZE_CONSTRAINT_PROMPT_TEMPLATE,
            "AnalyzeSkills": ANALYZE_SKILL_PROMPT_TEMPLATE,
            "DesignFunction": {
                "global": DESIGN_GLOBAL_FUNCTION_PROMPT_TEMPLATE,
                "local": DESIGN_LOCAL_FUNCTION_PROMPT_TEMPLATE,
            },
            "WriteFunction": {
                "global": WRITE_GLOBAL_FUNCTION_PROMPT_TEMPLATE,
                "local": WRITE_LOCAL_FUNCTION_PROMPT_TEMPLATE,
            },
            "CodeReview": {
                "global": GLOBAL_CODE_REVIEW_PROMPT_TEMPLATE,
                "local": LOCAL_CODE_REVIEW_PROMPT_TEMPLATE,
            },
            "WriteRun": {
                "global": WRITE_GLOBAL_RUN_PROMPT_TEMPLATE,
                "local": WRITE_LOCAL_RUN_PROMPT_TEMPLATE,
            },
        }
    
    def get_prompt(self, action: str, scope: str) -> str:
        """获取指定动作和作用域的提示词模板"""
        if action not in self.action_map:
            return ""
        if action in ["AnalyzeSkills", "AnalyzeConstraints"]:
            return self.action_map[action]
        return self.action_map[action][scope]
```

**设计思路**：
- **按阶段分类**：不同阶段使用不同的提示词
- **区分作用域**：global（全局协调）和local（单机器人）
- **模板化设计**：使用占位符，运行时填充

## 分析阶段提示词

### ANALYZE_CONSTRAINT_PROMPT_TEMPLATE - 约束分析

**目标**：让LLM理解任务的约束条件

```python
ANALYZE_CONSTRAINT_PROMPT_TEMPLATE = """
{task_des}

# User Instruction
{instruction}

# Available APIs
## Global APIs
{global_api}

## Local APIs
{local_api}

# Environment Description
{env_des}

# Your Task
Analyze the constraints and requirements from the user instruction.
Output in the following JSON format:
{output_template}

# Existing Constraints (for reference)
{user_constraints}
"""
```

**占位符说明**：
- `{task_des}`: 任务类型描述（如flocking、covering等）
- `{instruction}`: 用户具体指令
- `{global_api}`: 可用的全局API列表
- `{local_api}`: 可用的局部API列表
- `{env_des}`: 环境描述
- `{output_template}`: 期望的输出格式（JSON模板）
- `{user_constraints}`: 已有的约束列表

**输出格式（CONSTRAIN_TEMPLATE）**：
```json
{
    "constraints": [
        {
            "id": "C1",
            "description": "机器人之间必须保持最小距离0.3米",
            "type": "safety",
            "priority": "high"
        }
    ]
}
```

### ANALYZE_SKILL_PROMPT_TEMPLATE - 技能分析

**目标**：将任务分解为函数列表

```python
ANALYZE_SKILL_PROMPT_TEMPLATE = """
{task_des}

# User Instruction
{instruction}

# Constraints
{constraints}

# Available APIs
## Global APIs
{global_api}

## Local APIs
{local_api}

# Environment Description
{env_des}

# Your Task
Decompose the task into functions (both global and local scope).
Output in the following JSON format:
{output_template}
"""
```

**输出格式（FUNCTION_TEMPLATE）**：
```json
{
    "functions": [
        {
            "name": "calculate_formation_position",
            "scope": "global",
            "description": "计算每个机器人在编队中的目标位置",
            "inputs": ["robot_positions", "formation_type"],
            "outputs": ["target_positions"],
            "dependencies": []
        },
        {
            "name": "move_to_target",
            "scope": "local",
            "description": "控制单个机器人移动到目标位置",
            "inputs": ["target_position"],
            "outputs": ["velocity"],
            "dependencies": []
        }
    ]
}
```

## 设计阶段提示词

### DESIGN_GLOBAL_FUNCTION_PROMPT_TEMPLATE - 全局函数设计

**目标**：为全局协调函数设计伪代码

```python
DESIGN_GLOBAL_FUNCTION_PROMPT_TEMPLATE = """
# Function to Design
{function_info}

# All Functions Context
{all_functions}

# Constraints
{constraints}

# Available Global APIs
{global_api}

# Your Task
Design the pseudocode for this global coordination function.
Consider:
1. How to collect information from all robots
2. How to compute global strategy
3. How to allocate tasks to individual robots

Output the pseudocode with clear logic and comments.
"""
```

**设计要点**：
- 明确输入输出
- 考虑全局视角
- 任务分配策略
- 与其他函数的协作

### DESIGN_LOCAL_FUNCTION_PROMPT_TEMPLATE - 局部函数设计

**目标**：为单机器人函数设计伪代码

```python
DESIGN_LOCAL_FUNCTION_PROMPT_TEMPLATE = """
# Function to Design
{function_info}

# All Functions Context
{all_functions}

# Constraints
{constraints}

# Available Local APIs
{local_api}

# Your Task
Design the pseudocode for this local robot function.
Consider:
1. What information the robot needs
2. How to make decisions based on local observations
3. How to interact with neighbors

Output the pseudocode with clear logic and comments.
"""
```

**设计要点**：
- 基于局部信息
- 邻居交互
- 实时响应

## 编码阶段提示词

### WRITE_GLOBAL_FUNCTION_PROMPT_TEMPLATE - 全局函数编写

**目标**：将伪代码转换为Python代码

```python
WRITE_GLOBAL_FUNCTION_PROMPT_TEMPLATE = """
# Function Specification
{function_info}

# Pseudocode
{pseudocode}

# Available APIs
{global_api}

# Existing Functions (can be called)
{existing_functions}

# Your Task
Implement the function in Python based on the pseudocode.
Requirements:
1. Use only the provided APIs
2. Follow Python best practices
3. Add type hints
4. Include docstrings
5. Handle edge cases

Output format:
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    \"\"\"
    Function description.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Description
    \"\"\"
    # Implementation
    pass
```
"""
```

**代码质量要求**：
- 类型注解完整
- 文档字符串清晰
- 错误处理完善
- 代码风格一致

### WRITE_LOCAL_FUNCTION_PROMPT_TEMPLATE - 局部函数编写

类似全局函数，但强调：
- 使用local APIs
- 基于ROS通信
- 实时性考虑

## 代码审查提示词

### GLOBAL_CODE_REVIEW_PROMPT_TEMPLATE - 全局代码审查

**目标**：检查代码质量和逻辑正确性

```python
GLOBAL_CODE_REVIEW_PROMPT_TEMPLATE = """
# Function to Review
{function_code}

# Function Specification
{function_info}

# Review Checklist
1. Logic Correctness
   - Does it match the specification?
   - Are all edge cases handled?
   
2. API Usage
   - Are APIs used correctly?
   - Are there any undefined functions called?
   
3. Code Quality
   - Is the code readable?
   - Are there type hints?
   - Is there proper documentation?
   
4. Performance
   - Is the algorithm efficient?
   - Are there unnecessary computations?

# Your Task
Review the code and provide:
1. Overall assessment (PASS/FAIL)
2. Specific issues found
3. Suggestions for improvement

Output in JSON format:
{output_template}
"""
```

**输出格式**：
```json
{
    "status": "PASS",
    "issues": [
        {
            "type": "warning",
            "line": 15,
            "message": "Consider caching this computation"
        }
    ],
    "suggestions": [
        "Add input validation for edge cases"
    ]
}
```

## 运行脚本提示词

### WRITE_GLOBAL_RUN_PROMPT_TEMPLATE - 全局运行脚本

**目标**：生成多机器人协调的主运行脚本

```python
WRITE_GLOBAL_RUN_PROMPT_TEMPLATE = """
# All Global Functions
{all_global_functions}

# All Local Functions  
{all_local_functions}

# Task Allocator Template
{allocator_template}

# Your Task
Write the main coordination script that:
1. Calls global functions to compute strategies
2. Allocates tasks to individual robots
3. Coordinates execution

Template structure:
```python
def allocate_tasks():
    # Get robot states
    robot_states = get_all_robot_states()
    
    # Compute global strategy
    strategy = global_function1(robot_states)
    
    # Allocate to each robot
    for robot_id in range(num_robots):
        task = allocate_task(robot_id, strategy)
        assign_task(robot_id, task)
    
    return allocation_result
```
"""
```

**关键点**：
- 调用全局函数计算策略
- 任务分配给各机器人
- 返回分配结果

### WRITE_LOCAL_RUN_PROMPT_TEMPLATE - 局部运行脚本

**目标**：生成单机器人的执行脚本

```python
WRITE_LOCAL_RUN_PROMPT_TEMPLATE = """
# All Local Functions
{all_local_functions}

# Your Task
Write the local execution script for individual robots:
1. Initialize ROS node
2. Get assigned task
3. Execute local functions in control loop
4. Publish velocity commands

Template structure:
```python
def run():
    # Initialize
    initialize_ros_node()
    
    # Get task assignment
    task = get_assigned_task()
    
    # Control loop
    rate = rospy.Rate(10)  # 10Hz
    while not rospy.is_shutdown():
        # Execute local functions
        velocity = local_function(task, get_robot_state())
        
        # Publish command
        publish_velocity(velocity)
        
        rate.sleep()
```
"""
```

## 视频评估提示词

### VIDEO_CRITIC_PROMPT_TEMPLATE - 视频评估

**目标**：使用视觉语言模型评估执行结果

```python
VIDEO_CRITIC_PROMPT_TEMPLATE = """
# Task Description
{task_description}

# Success Criteria
{success_criteria}

# Video Frames
[Attached: {num_frames} frames from the execution]

# Your Task
Analyze the video frames and evaluate:
1. Task Completion: Did robots achieve the goal?
2. Constraints Satisfaction: Were all constraints met?
3. Performance Metrics: Speed, smoothness, coordination
4. Issues Observed: Collisions, oscillations, failures

Provide:
- Overall score (0-100)
- Detailed feedback
- Suggestions for improvement

Output format:
{output_template}
"""
```

**适用场景**：
- 需要视觉验证的任务（编队、覆盖等）
- 性能评估

## Robot API 提示词

### robot_api_prompt.py - API文档生成

提供不同任务和作用域的API说明：

```python
def get_api_prompt(task_name: str, scope: str, 
                   only_names: bool = False) -> str:
    """
    获取指定任务和作用域的API提示词
    
    Args:
        task_name: 任务名称（如"flocking", "covering"）
        scope: "global" 或 "local"
        only_names: 是否只返回API名称列表
    
    Returns:
        API说明文档或名称列表
    """
```

**示例输出（global scope）**：
```python
"""
# Global APIs for Flocking Task

1. get_all_robot_states() -> List[RobotState]
   Get current states of all robots
   
2. calculate_centroid(positions: List[Position]) -> Position
   Calculate the geometric center of robot positions
   
3. assign_task(robot_id: int, task: Task) -> None
   Assign a task to specific robot
"""
```

**示例输出（local scope）**：
```python
"""
# Local APIs for Flocking Task

1. get_robot_state() -> RobotState
   Get current robot state (position, velocity)
   
2. get_neighbors(radius: float) -> List[Neighbor]
   Get neighboring robots within radius
   
3. publish_velocity(vx: float, vy: float) -> None
   Publish velocity command
   
4. initialize_ros_node() -> None
   Initialize ROS communication
"""
```

## 用户需求模板

### user_requirements.py - 任务描述

预定义各类集群机器人任务的描述：

```python
def get_user_commands(task_name: str, format_type: str = "default") -> List[str]:
    """
    获取任务的用户指令
    
    Args:
        task_name: 任务名称
        format_type: 提示词格式类型
    
    Returns:
        用户指令列表
    """
```

**任务类型**：
- **flocking**: 集群飞行/蜂群行为
- **covering**: 区域覆盖
- **aggregation**: 聚合
- **encircling**: 包围
- **crossing**: 交叉通过
- **shaping**: 形状形成
- 等等

**示例（flocking任务）**：
```
"Control a swarm of robots to exhibit flocking behavior. 
The robots should:
1. Move cohesively as a group
2. Maintain safe distances from neighbors
3. Align velocities with nearby robots
4. Avoid obstacles in the environment"
```

## 提示词调试技巧

### 1. 记录完整提示词

```python
logger.log(f"Full Prompt:\n{prompt}", "debug")
logger.log(f"Response:\n{response}", "debug")
```

### 2. A/B测试

```python
prompt_v1 = template_v1.format(...)
prompt_v2 = template_v2.format(...)

response_v1 = await llm.ask(prompt_v1)
response_v2 = await llm.ask(prompt_v2)

# 比较质量
```

### 3. 渐进式优化

```python
# 从简单开始
basic_prompt = "Generate a flocking function"

# 添加约束
+ "using only these APIs: ..."

# 添加格式要求
+ "Output in Python with type hints"

# 添加质量要求
+ "Include error handling and documentation"
```

## 与其他模块的协作

### 与LLM模块

```python
from modules.prompt import Prompt
from modules.llm import GPT

# 获取模板
prompt_mgr = Prompt()
template = prompt_mgr.get_prompt("WriteFunction", "global")

# 填充模板
filled = template.format(function_info=..., global_api=...)

# 调用LLM
llm = GPT()
response = await llm.ask(filled)
```

### 与Framework模块

```python
class AnalyzeSkills(ActionNode):
    def _build_prompt(self):
        # 获取模板
        self.prompt = Prompt().get_prompt("AnalyzeSkills", "global")
        
        # 填充上下文
        self.prompt = self.prompt.format(
            task_des=TASK_DES,
            instruction=self.context.command,
            constraints=str(self.context.constraint_pool),
            global_api=self.context.global_robot_api,
            ...
        )
```

## 下一步

阅读 [Deployment 模块](./04_deployment.md) 了解如何在仿真环境中执行生成的代码。
