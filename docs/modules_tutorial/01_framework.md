# Framework 框架模块

## 概述

`framework` 模块是整个系统的控制中枢，负责定义和执行工作流。它采用节点和链表的方式组织任务流程，实现了灵活的任务编排和错误处理机制。

## 模块结构

```
framework/
├── action.py              # 基础动作节点定义
├── actions/              # 具体动作实现
│   ├── analyze_constraints.py    # 约束分析
│   ├── analyze_skills.py         # 技能分析
│   ├── design_function.py        # 函数设计
│   ├── write_function.py         # 函数编写
│   ├── code_review.py            # 代码审查
│   ├── grammar_check.py          # 语法检查
│   ├── debug_error.py            # 错误调试
│   ├── improve_code.py           # 代码改进
│   ├── generate_functions.py    # 函数生成协调
│   ├── run_code.py               # 代码运行
│   ├── video_criticize.py        # 视频评估
│   └── write_run.py              # 运行脚本编写
├── code/                 # 代码结构管理
├── constraint/           # 约束池管理
├── context/             # 上下文管理
│   └── workflow_context.py  # 工作流上下文（单例）
├── parser/              # 响应解析器
├── handler.py           # 错误处理链
├── node_renderer.py     # 节点渲染（生成Mermaid图）
├── workflow.py          # 工作流主类
└── error.py            # 错误定义
```

## 核心类详解

### 1. BaseNode - 基础节点

所有节点的抽象基类，定义了节点的基本行为：

```python
class BaseNode(ABC):
    def __init__(self):
        self.__next = None      # 下一个节点
        self._renderer = None   # 渲染器（用于生成流程图）
    
    @abstractmethod
    async def run(self, auto_next: bool = True) -> str:
        pass
```

**核心功能**：
- 维护节点链表关系
- 支持流程图渲染(流程图用的不多)
- 定义统一的运行接口

### 2. ActionNode - 动作节点

执行具体任务的节点，每个动作节点负责与LLM交互完成特定任务：

```python
class ActionNode(BaseNode):
    def __init__(self, next_text: str = "", node_name: str = "", llm: GPT = None):
        self.prompt = None              # 提示词
        self._next_text = next_text     # 流程图连接文本
        self._node_name = node_name     # 节点名称
        self.error_handler = None       # 错误处理链
        self.context = WorkflowContext()  # 全局上下文
```

**执行流程**：
1. `_build_prompt()` - 构建提示词
2. `_run()` - 调用LLM获取响应（带重试机制）
3. `_process_response()` - 处理LLM响应
4. 若有错误，交给 `error_handler` 处理
5. 自动执行下一个节点

**重试机制**：
使用 `tenacity` 库实现指数退避重试，最多5次：
```python
@retry(stop=stop_after_attempt(5), 
       wait=wait_random_exponential(multiplier=1, max=10))
async def _run(self):
    # LLM调用
```

### 3. AsyncNode - 异步节点

用于并行或分层处理多个函数的节点：

```python
class AsyncNode(ActionNode):
    def __init__(self, skill_tree: FunctionTree, run_mode="layer", 
                 start_state=None, end_state=None):
        self._run_mode = run_mode  # layer/sequential/parallel
        self.skill_tree = skill_tree
```

**运行模式**：
- **layer（分层）**：按函数依赖层级逐层处理
- **sequential（顺序）**：按顺序处理每个函数
- **parallel（并行）**：同时处理所有函数

### 4. ActionLinkedList - 动作链表

将多个动作节点组织成链表：

```python
class ActionLinkedList(BaseNode):
    def __init__(self, name: str, head: BaseNode):
        self.head = head
        self._name = name
        
    def add(self, action: BaseNode):
        # 添加到链表尾部
```

**特点**：
- 自动维护链表结构
- 支持内部动作的独立运行
- 可作为整体嵌套使用

### 5. Workflow - 工作流

系统的顶层控制类，负责初始化和启动整个流程：

```python
class Workflow:
    def __init__(self, user_command: str, args=None):
        self._context = WorkflowContext(args=args)
        self._context.command = user_command
        self.init_workspace()    # 初始化工作空间
        self.build_up()          # 构建工作流
```

**构建流程**：
```python
def build_up(self):
    # Stage 1: 分析阶段
    analysis_stage = ActionLinkedList("Analysis", analyze_constraints)
    analysis_stage.add(analyze_functions)
    
    # Stage 2: 编码阶段
    coding_stage = ActionLinkedList("Coding", generate_functions)
    
    # Stage 3: 测试阶段
    test_stage = ActionLinkedList("Testing", run_code)
    test_stage.add(video_critic)
    
    # 组合所有阶段
    code_llm = ActionLinkedList("Code-LLM", analysis_stage)
    code_llm.add(coding_stage)
    if self._run_code:
        code_llm.add(test_stage)
```

## Actions 子模块详解

### 分析类动作

#### AnalyzeConstraints - 约束分析
**功能**：分析任务的约束条件
- 输入：任务描述、API列表
- 输出：约束池（ConstraintPool）
- 保存位置：`context.constraint_pool`

#### AnalyzeSkills - 技能分析
**功能**：分解任务为函数列表
- 输入：约束池、任务描述
- 输出：全局和局部函数树（FunctionTree）
- 保存位置：`context.global_skill_tree` 和 `context.local_skill_tree`

### 编码类动作

#### GenerateFunctions - 函数生成协调器
**功能**：协调整个代码生成过程
- 包含子流程：设计 → 编写 → 审查 → 语法检查
- 支持分层、顺序、并行三种模式
- 自动切换 global/local 作用域

#### DesignFunctionAsync - 函数设计
**功能**：为每个函数设计伪代码
- 运行模式：AsyncNode（支持并行）
- 状态转换：NOT_STARTED → DESIGNED

#### WriteFunctionsAsync - 函数编写
**功能**：将伪代码转换为实际代码
- 状态转换：DESIGNED → WRITTEN

#### CodeReviewAsync - 代码审查
**功能**：审查代码质量和正确性
- 状态转换：WRITTEN → REVIEWED

#### GrammarCheckAsync - 语法检查
**功能**：检查代码语法错误
- 使用Python AST验证语法
- 状态转换：REVIEWED → CHECKED
- 若有错误，触发错误处理链

#### WriteRun - 编写运行脚本
**功能**：生成多机器人协调的主运行脚本
- 输入：所有已生成的函数
- 输出：`run.py` 或 `allocate_run.py`

### 测试类动作

#### RunCodeAsync - 代码运行
**功能**：在仿真环境中执行生成的代码
- 启动Gymnasium环境
- 记录机器人状态
- 生成视频文件
- 若运行出错，触发错误处理

#### VideoCriticize - 视频评估
**功能**：使用视觉语言模型评估运行结果
- 输入：运行视频
- 输出：性能反馈或改进建议

### 改进类动作

#### DebugError - 错误调试
**功能**：修复代码中的错误
- 输入：错误信息和错误代码
- 输出：修复后的代码
- 自动重新运行语法检查

#### CodeImprove - 代码改进
**功能**：根据人类反馈或视频评估改进代码
- 输入：反馈信息
- 输出：改进后的代码

## 错误处理机制

系统采用**责任链模式**处理不同类型的错误：

```python
class Handler(ABC):
    def __init__(self):
        self._successor = None      # 下一个处理器
        self._next_action = None    # 处理动作
    
    @abstractmethod
    def handle(self, request: CodeError) -> BaseNode:
        pass
```

### 处理器链

```
BugLevelHandler → FeedbackHandler
       ↓                 ↓
   DebugError       CodeImprove
```

**错误类型**：
1. **Bug/Bugs**：代码语法或运行错误 → `DebugError`
2. **Feedback**：人类反馈或性能不佳 → `CodeImprove`
3. **CriticNotSatisfied**：视频评估不满意 → （预留）

## Context 上下文管理

### WorkflowContext（单例模式）

存储整个工作流的共享状态：

```python
class WorkflowContext(Context):
    def __init__(self, args=None):
        self.user_command = File(name="command.md")
        self.constraint_pool = ConstraintPool()
        self.global_skill_tree = FunctionTree(name="global_skill")
        self.local_skill_tree = FunctionTree(name="local_skill")
        self.scoop = "global"  # 当前作用域
        self.args = args       # 命令行参数
```

**关键功能**：
- `save_to_file()` - 序列化保存状态
- `load_from_file()` - 从文件恢复状态
- `set_root_for_files()` - 批量设置文件根目录

## 流程图生成

系统自动生成Mermaid格式的流程图：

```python
async def run(self):
    text = display_all(self._pipeline, self._chain_of_handler)
    flow = File(name="flow.md")
    flow.message = text  # 保存流程图
    await self._pipeline.run()
```

生成的流程图包含：
- 所有动作节点
- 节点间的连接关系
- 错误处理分支

## 实际使用示例

```python
# 创建工作流
workflow = Workflow(
    user_command="让机器人形成圆形编队", 
    args=args
)

# 启动工作流（异步）
await workflow.run()
```

工作流会自动执行：
1. 分析约束和技能
2. 生成全局和局部函数
3. 运行代码并评估

## 状态管理

函数的状态流转：

```
NOT_STARTED → DESIGNED → WRITTEN → REVIEWED → CHECKED
                                               ↓
                                          (运行就绪)
```

## 下一步

阅读 [LLM 模块](./02_llm.md) 了解如何与大语言模型交互。
