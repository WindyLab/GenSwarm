# Modules 模块概览

## 简介

本教程系列将详细介绍 `modules` 文件夹下各个模块的功能和整体工作流程。`modules` 是 GenSwarm 项目的核心代码模块，实现了从任务分析到代码生成、测试运行的完整自动化流程。

## 模块结构

```
modules/
├── deployment/         # 部署与执行模块
│   ├── engine/        # 物理引擎实现
│   ├── entity/        # 实体对象定义
│   ├── execution_scripts/  # 执行脚本
│   ├── gymnasium_env/  # Gymnasium环境实现
│   ├── real_env/      # 真实环境接口
│   └── utils/         # 部署工具
├── file/              # 文件管理模块
├── framework/         # 核心框架模块
│   ├── actions/       # 工作流动作实现
│   ├── code/          # 代码结构与管理
│   ├── constraint/    # 约束管理
│   ├── context/       # 上下文管理
│   └── parser/        # 解析器
├── llm/               # 大语言模型接口
├── prompt/            # 提示词模板
├── utils/             # 通用工具
└── run_ansible.py     # Ansible运行脚本
```

## 核心功能

GenSwarm 系统的核心功能是**自动生成集群机器人控制代码**。整个流程分为以下几个阶段：

1. **分析阶段（Analysis）**：分析任务约束和所需技能
2. **编码阶段（Coding）**：生成控制函数和运行脚本
3. **测试阶段（Testing）**：在仿真环境中执行并验证代码

## 模块间的关系

- **framework** 是系统的控制中枢，定义了工作流和动作节点
- **llm** 提供与大语言模型的交互能力
- **prompt** 为每个阶段提供专门的提示词模板
- **deployment** 负责在仿真或真实环境中执行生成的代码
- **file** 和 **utils** 提供基础设施支持

## 教程导航

本教程系列包含以下部分：

- [01_framework 框架模块](./01_framework.md) - 核心工作流和动作系统
- [02_llm 语言模型模块](./02_llm.md) - 大语言模型接口
- [03_prompt 提示词模块](./03_prompt.md) - 提示词模板系统
- [04_deployment 部署模块](./04_deployment.md) - 执行环境和物理引擎
- [05_file_utils 工具模块](./05_file_utils.md) - 文件管理和通用工具
- [06_workflow 工作流程](./06_workflow.md) - 完整的执行流程

## 设计原则

系统采用以下设计模式和原则：

1. **责任链模式（Chain of Responsibility）**：错误处理采用责任链
2. **策略模式（Strategy）**：不同的LLM实现可互换
3. **单例模式（Singleton）**：WorkflowContext 保证全局唯一
4. **异步编程**：使用 async/await 处理LLM调用和并行任务
5. **模板方法**：ActionNode 定义了统一的执行模板

## 下一步

建议按照顺序阅读教程，从 [framework 模块](./01_framework.md) 开始了解系统的核心架构。
