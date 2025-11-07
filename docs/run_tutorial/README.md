# Run 运行脚本教程

本教程详细介绍GenSwarm项目中`run`目录下的各类运行脚本，帮助你理解如何运行单次实验、批量实验和大规模实验。

## 📁 目录结构

```
run/
├── run_single.py           # 单次代码生成
├── run_batch.py            # 批量运行实验（标准规模）
├── run_batch_large.py      # 批量运行实验（大规模）
├── run_multiple_times.py   # 多次重复运行
├── run_code.py             # 运行单个批次
├── parser.py               # 参数解析工具
├── result_analyzer.py      # 结果分析工具
├── auto_runner/            # 自动运行器模块
│   ├── __init__.py
│   ├── auto_runner_base.py         # 基类
│   ├── auto_runner_flocking.py     # 集群飞行任务
│   ├── auto_runner_covering.py     # 区域覆盖任务
│   ├── auto_runner_encircling.py   # 包围任务
│   └── ... (其他任务)
└── utils/                  # 工具函数
```

## 🎯 核心脚本说明

### 1. run_single.py - 单次代码生成

**用途**：生成单个任务的控制代码

**使用场景**：
- 开发调试
- 验证新任务
- 测试新的LLM模型或提示词

**命令示例**：
```bash
# 基础用法
python run/run_single.py --task_name flocking

# 指定LLM模型
python run/run_single.py \
  --task_name flocking \
  --llm_name gpt-4o-2024-11-20

# 指定提示词类型
python run/run_single.py \
  --task_name encircling \
  --llm_name gpt-4 \
  --prompt_type structured_default
```

**关键参数**：
- `--task_name`: 任务名称（flocking/covering/encircling等）
- `--llm_name`: LLM模型名称
- `--prompt_type`: 提示词模板类型

**输出**：
- 生成的代码保存在 `workspace/{task_name}/{timestamp}/`
- 日志文件：`log.md`
- 流程图：`flow.md`
- 生成的函数：`local_skill.py`, `global_skill.py`

---

### 2. run_batch.py - 标准批量运行

**用途**：在标准规模下批量运行实验（单个LLM、单个提示词）

**使用场景**：
- 单个模型的批量测试
- 对比分析（与CaP、MetaGPT、LLM2Swarm等）
- 标准实验流程

**命令示例**：
```bash
# 运行flocking任务，批次1
python run/run_batch.py \
  --task_name flocking \
  --exp_batch 1 \
  --test_mode wo_vlm \
  --run_mode analyze

# 对比实验（MetaGPT）
python run/run_batch.py \
  --task_name covering \
  --exp_batch 1 \
  --test_mode meta \
  --run_mode analyze
```

**关键参数**：
- `--exp_batch`: 实验批次号
- `--task_name`: 任务名称
- `--test_mode`: 测试模式
  - `wo_vlm`: 不使用视觉语言模型
  - `vlm`: 使用视觉语言模型
  - `meta`: MetaGPT对比
  - `cap`: CaP对比
  - `llm2swarm`: LLM2Swarm对比
- `--run_mode`: 运行模式
  - `analyze`: 仅分析已有结果
  - `rerun`: 重新运行所有
  - `continue`: 继续未完成的实验

**工作空间路径**：
- 对比实验：`workspace/comparative/{test_mode}/{task_name}/`
- 普通实验：`workspace/{task_name}/`

---

### 3. run_batch_large.py - 大规模批量运行 ⭐

**用途**：在**大规模**下批量运行实验（多个LLM、多个提示词、多个任务）

**使用场景**：
- 多模型对比实验
- 多提示词策略评估
- 大规模性能测试
- 论文实验数据收集

**核心特点**：
```python
# 支持多个LLM模型
llm_model_list = [
    "o1-mini", 
    "gpt-4o-2024-11-20", 
    "DMXAPI-HuoShan-DeepSeek-V3"
]

# 支持多种提示词类型
prompt_type_list = [
    "structured_default",
    "simple",
    "narrative",
    # ...
]

# 支持多个任务
task_keys = [
    "encircling",
    "covering",
    "flocking",
    # ...
]
```

**并发控制**：
```python
MAX_THREADS = 1  # 最大并发线程数
```

**运行流程**：
1. 遍历所有LLM模型
2. 遍历所有提示词类型
3. 遍历所有任务
4. 使用线程池并发执行
5. 实时显示进度条

**命令示例**：
```bash
# 直接运行（使用脚本内预设配置）
python run/run_batch_large.py

# 需要修改配置时，编辑脚本中的列表
```

**工作空间路径**：
```
workspace/{llm_model}/{prompt_type}/{task_name}/
```

例如：
```
workspace/gpt-4o-2024-11-20/structured_default/encircling/
workspace/DMXAPI-HuoShan-DeepSeek-V3/simple/covering/
```

**与run_batch.py的区别**：

| 特性 | run_batch.py | run_batch_large.py |
|------|-------------|-------------------|
| 规模 | 标准（单模型/单提示词） | 大规模（多模型/多提示词/多任务） |
| 参数方式 | 命令行参数 | 脚本内配置 |
| 并发 | 单线程 | 多线程（可配置） |
| 适用场景 | 单次实验、调试 | 批量对比实验、论文数据 |
| 工作空间 | 简单路径 | 分层路径（llm/prompt/task） |

---

### 4. run_multiple_times.py - 多次重复运行

**用途**：在相同配置下多次重复运行（用于统计分析）

**使用场景**：
- 收集统计数据
- 验证算法稳定性
- 评估随机性影响

**核心特点**：
```python
# 每种组合重复50次
repeat_each = 50

# 最大并发数
max_concurrent = 100

# 单次超时设置
per_task_timeout = 1800  # 30分钟
```

**命令示例**：
```bash
# 直接运行（使用脚本内预设配置）
python run/run_multiple_times.py
```

**配置说明**：
```python
llm_model_list = ["DMXAPI-HuoShan-DeepSeek-V3"]
prompt_type_list = ["structured_default"]
task_list = ["encircling", "covering"]
repeat_each = 50  # 每个任务重复50次
```

**执行流程**：
1. 生成所有任务组合
2. 使用线程池并发执行
3. 每提交一个任务暂停2秒（避免API限流）
4. 实时显示进度条
5. 记录详细日志

**日志输出**：
```
logs/run_log_[timestamp].txt
```

日志内容包括：
- 每个任务的执行状态（成功/超时/错误）
- 执行摘要统计
- 时间戳

---

### 5. run_code.py - 单批次运行

**用途**：运行单个实验批次（被batch脚本调用）

**关键参数**：
- `--exp_batch`: 批次号
- `--task_name`: 任务名称
- `--test_mode`: 测试模式
- `--run_mode`: 运行模式
- `--task_path`: 工作空间子路径（用于large模式）

**通常不直接调用**，而是被以下脚本调用：
- `run_batch.py`
- `run_batch_large.py`

---

## 🔧 辅助工具

### parser.py - 参数解析

**功能**：
- 从YAML配置文件加载参数
- 支持命令行参数覆盖
- 提供参数表格化显示

**使用示例**：
```python
from run.parser import ParameterService

parameter_service = ParameterService()
parameter_service.add_arguments_from_yaml("config/experiment_config.yaml")
parameter_service.add_argument('--task_name', type=str, default='flocking')

args = parameter_service.parse_arguments(sys.argv[1:])
print(parameter_service.format_arguments_as_table(args))
```

### result_analyzer.py - 结果分析

**功能**：
- 分析实验日志
- 统计成功率
- 计算代码复杂度和可维护性指标
- 生成对比图表

**使用方法**：
```bash
# 修改base_path指向你的workspace
python run/result_analyzer.py
```

**分析指标**：
- 代码生成时间
- 平均圈复杂度
- 可维护性指数（MI Score）
- 运行成功率

---

## 📊 Auto Runner 模块

### auto_runner_base.py - 基类

所有任务运行器的基类，提供：
- 实验管理（创建、加载、保存）
- 环境初始化
- 仿真运行
- 结果记录
- 性能评估

### 任务特定Runner

每个任务都有专门的Runner：
- `auto_runner_flocking.py` - 集群飞行
- `auto_runner_covering.py` - 区域覆盖
- `auto_runner_encircling.py` - 包围任务
- `auto_runner_shaping.py` - 形状形成
- ...

**主要职责**：
- 定义任务特定的评估指标
- 计算任务成功率
- 记录任务特定的数据

---

## 🚀 使用流程

### 流程 A：单次代码生成和测试

```bash
# 1. 生成代码
python run/run_single.py \
  --task_name flocking \
  --llm_name gpt-4o-2024-11-20

# 2. 检查生成的代码
ls workspace/flocking/[timestamp]/

# 3. 查看日志
cat workspace/flocking/[timestamp]/log.md
```

### 流程 B：批量对比实验（标准规模）

```bash
# 运行GenSwarm方法
python run/run_batch.py \
  --task_name covering \
  --exp_batch 1 \
  --test_mode wo_vlm \
  --run_mode analyze

# 运行MetaGPT对比
python run/run_batch.py \
  --task_name covering \
  --exp_batch 1 \
  --test_mode meta \
  --run_mode analyze

# 分析结果
python run/result_analyzer.py
```

### 流程 C：大规模实验（多模型/多提示词）

```bash
# 1. 编辑run_batch_large.py配置
vim run/run_batch_large.py

# 修改以下配置：
# llm_model_list = ["gpt-4o", "o1-mini", "deepseek-v3"]
# prompt_type_list = ["structured_default", "simple"]
# task_keys = ["encircling", "covering"]

# 2. 运行大规模实验
python run/run_batch_large.py

# 3. 查看结果
ls workspace/gpt-4o/structured_default/*/
```

### 流程 D：重复运行收集统计数据

```bash
# 1. 编辑run_multiple_times.py配置
vim run/run_multiple_times.py

# 设置：
# repeat_each = 50
# task_list = ["flocking"]

# 2. 运行
python run/run_multiple_times.py

# 3. 查看日志
cat logs/run_log_[timestamp].txt

# 4. 分析数据
python run/result_analyzer.py
```

---

## ⚙️ 运行模式详解

### test_mode（测试模式）

| 模式 | 说明 | 工作空间路径 |
|------|------|------------|
| `wo_vlm` | 不使用视觉语言模型 | `workspace/{task}/` |
| `vlm` | 使用视觉语言模型评估 | `workspace/{task}/` |
| `cap` | 与CaP方法对比 | `workspace/comparative/cap/{task}/` |
| `meta` | 与MetaGPT方法对比 | `workspace/comparative/meta/{task}/` |
| `llm2swarm` | 与LLM2Swarm方法对比 | `workspace/comparative/llm2swarm/{task}/` |
| `real` | 真实硬件环境 | 根据配置 |

### run_mode（运行模式）

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `analyze` | 仅分析已有结果 | 查看统计数据 |
| `rerun` | 重新运行所有实验 | 完全重新开始 |
| `continue` | 继续未完成的实验 | 中断后恢复 |
| `fail_rerun` | 重新运行失败的实验 | 修复问题后重试 |

---

## 📈 实验数据组织

### 标准实验

```
workspace/
└── flocking/
    ├── 2024-01-15_10-30-00/
    │   ├── local_skill.py
    │   ├── global_skill.py
    │   ├── log.md
    │   ├── flow.md
    │   └── simulation.mp4
    └── 2024-01-15_14-20-00/
        └── ...
```

### 对比实验

```
workspace/
└── comparative/
    ├── cap/
    │   └── flocking/
    │       └── 2024-01-15_10-30-00/
    ├── meta/
    │   └── flocking/
    │       └── 2024-01-15_10-30-01/
    └── llm2swarm/
        └── flocking/
            └── 2024-01-15_10-30-02/
```

### 大规模实验

```
workspace/
├── gpt-4o-2024-11-20/
│   ├── structured_default/
│   │   ├── encircling/
│   │   │   └── 2024-01-15_10-30-00/
│   │   └── covering/
│   │       └── 2024-01-15_10-30-01/
│   └── simple/
│       └── encircling/
└── DMXAPI-HuoShan-DeepSeek-V3/
    └── structured_default/
        └── covering/
```

---

## 🔍 常见问题

### Q1: run_batch.py 和 run_batch_large.py 有什么区别？

**答**：
- **run_batch.py**：标准规模，单个LLM、单个提示词，通过命令行参数控制
- **run_batch_large.py**：大规模，多个LLM、多个提示词、多个任务，适合批量实验

### Q2: 如何选择合适的运行脚本？

**答**：
- **开发调试**：`run_single.py`
- **单次批量实验**：`run_batch.py`
- **多模型对比**：`run_batch_large.py`
- **统计分析**：`run_multiple_times.py`

### Q3: 大规模实验会生成多少数据？

**答**：
假设：
- 3个LLM × 2个提示词 × 3个任务 = 18种组合
- 每种组合50次重复 = 900次运行
- 每次生成约10MB数据
- 总计约9GB数据

建议预留足够磁盘空间。

### Q4: 如何中断和恢复实验？

**答**：
```bash
# 中断后（Ctrl+C），使用continue模式恢复
python run/run_batch.py \
  --task_name flocking \
  --exp_batch 1 \
  --run_mode continue
```

### Q5: 如何查看实验进度？

**答**：
- `run_batch_large.py` 和 `run_multiple_times.py` 都有实时进度条
- 查看日志文件了解详细进度
- 使用 `result_analyzer.py` 分析完成情况

---

## 💡 最佳实践

### 1. 实验命名规范

使用清晰的参数组合：
```bash
python run/run_single.py \
  --task_name flocking \
  --llm_name gpt-4o-2024-11-20 \
  --prompt_type structured_default
```

### 2. 磁盘空间管理

定期清理旧实验：
```bash
# 删除超过30天的实验数据
find workspace/ -type d -mtime +30 -exec rm -rf {} +
```

### 3. 日志管理

保存重要实验的日志：
```bash
cp logs/run_log_*.txt archive/important_experiments/
```

### 4. 并发控制

根据机器性能调整并发数：
```python
# run_batch_large.py
MAX_THREADS = 2  # CPU密集型任务
MAX_THREADS = 10 # IO密集型任务（LLM API调用）
```

### 5. 超时设置

根据任务复杂度设置超时：
```python
# 简单任务
per_task_timeout = 600  # 10分钟

# 复杂任务
per_task_timeout = 1800  # 30分钟
```

---

## 📚 相关文档

- [Modules教程](../modules_tutorial/README.md) - 了解代码生成流程
- [项目README](../../README.md) - 项目整体介绍

---

**提示**：
- 大规模实验前先用`run_single.py`测试
- 注意磁盘空间和API配额
- 合理设置并发数和超时时间
