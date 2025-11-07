# LLM 语言模型模块

## 概述

`llm` 模块提供了与大语言模型（LLM）交互的统一接口，支持多种LLM提供商，包括OpenAI GPT（实际上所有主流的api厂商都支持openai 的api 格式）、Anthropic Claude和阿里通义千问。该模块采用策略模式设计，便于扩展新的LLM实现。

## 模块结构

```
llm/
├── __init__.py           # 模块导出
├── llm.py               # 基类定义
├── gpt.py               # OpenAI GPT实现
├── claude.py            # Anthropic Claude实现
├── qwen.py              # 阿里通义千问实现
└── model_manager.py     # 模型管理器
```

## 核心类详解

### 1. BaseLLM - 基础抽象类

所有LLM实现的基类，定义了统一的接口：

```python
class BaseLLM(ABC):
    def __init__(self, model: str, memorize: bool = False, 
                 stream_output: bool = False):
        self._model = model              # 模型名称
        self._memorize = memorize        # 是否记忆对话历史
        self._stream_output = stream_output  # 是否流式输出
        self._memories = []              # 对话历史
        self.system_prompt = "You are a helpful assistant."
```

**核心方法**：

#### `reset(system_prompt: str)` - 重置对话
清空对话历史，设置新的系统提示词。

#### `ask(prompt: str | list, temperature=1)` - 异步提问
```python
async def ask(self, prompt: str | list, temperature=1) -> str:
    # 1. 添加用户消息到历史
    self._memories.append({"role": "user", "content": prompt})
    
    # 2. 调用LLM（带重试）
    response = await self._ask_with_retry(temperature)
    
    # 3. 如果开启记忆，保存回复
    if self._memorize:
        self._memories.append({"role": "assistant", "content": response})
    
    return response
```

#### `_ask_with_retry(temperature: float)` - 抽象方法
需要子类实现具体的LLM调用逻辑，包含重试机制。

### 2. GPT - OpenAI实现

最常用的LLM实现，支持任何能用openai的api调用的模型：

```python
class GPT(BaseLLM):
    def __init__(self, model="gpt-4o-mini", memorize=False, 
                 stream_output=False, modeL_name=None):
        # 支持从配置文件读取模型名称
        if modeL_name:
            model = modeL_name
        
        super().__init__(model, memorize, stream_output)
        
        # 从配置读取API密钥
        config = load_yaml_config()
        self._api_key = config["llm"]["api_key"]
        self.base_url = config["llm"].get("base_url", 
                                          "https://api.openai.com/v1")
        
        # 创建OpenAI客户端
        self.client = AsyncOpenAI(api_key=self._api_key, 
                                   base_url=self.base_url)
```

**关键特性**：
- 支持异步调用
- 自动重试（最多10次，指数退避）
- 支持流式输出
- 灵活的API配置（支持代理和自定义base_url）

**调用实现**：
```python
@retry(stop=stop_after_attempt(10), 
       wait=wait_random_exponential(multiplier=1, max=60))
async def _ask_with_retry(self, temperature: float) -> str:
    messages = [{"role": "system", "content": self.system_prompt}]
    messages.extend(self._memories)
    
    response = await self.client.chat.completions.create(
        model=self._model,
        messages=messages,
        temperature=temperature,
    )
    
    return response.choices[0].message.content
```

### 3. Claude - Anthropic实现

支持Claude系列模型：

```python
class Claude(BaseLLM):
    def __init__(self, model="claude-3-5-sonnet-20241022", 
                 memorize=False):
        super().__init__(model, memorize)
        
        # 从配置读取API密钥
        config = load_yaml_config()
        self._api_key = config["claude"]["api_key"]
        
        # 创建Anthropic客户端
        self.client = AsyncAnthropic(api_key=self._api_key)
```

**与GPT的区别**：
- Claude的system prompt作为独立参数传递
- 消息格式略有不同
- 不支持流式输出（当前实现）

**调用实现**：
```python
@retry(stop=stop_after_attempt(10), 
       wait=wait_random_exponential(multiplier=1, max=60))
async def _ask_with_retry(self, temperature: float) -> str:
    response = await self.client.messages.create(
        model=self._model,
        max_tokens=4096,
        system=self.system_prompt,
        messages=self._memories,
        temperature=temperature,
    )
    
    return response.content[0].text
```

### 4. Qwen - 通义千问实现

支持阿里巴巴的通义千问系列模型：

```python
class Qwen(BaseLLM):
    def __init__(self, model="qwen-max", memorize=False):
        super().__init__(model, memorize)
        
        # 从配置读取API密钥
        config = load_yaml_config()
        self._api_key = config["qwen"]["api_key"]
        
        # 初始化DashScope
        dashscope.api_key = self._api_key
```

**特点**：
- 使用DashScope SDK
- 支持增量输出
- 采用不同的重试策略

**调用实现**：
```python
@retry(stop=stop_after_attempt(10), 
       wait=wait_random_exponential(multiplier=1, max=60))
async def _ask_with_retry(self, temperature: float) -> str:
    messages = [{"role": "system", "content": self.system_prompt}]
    messages.extend(self._memories)
    
    responses = Generation.call(
        model=self._model,
        messages=messages,
        result_format='message',
        stream=True,
        incremental_output=True,
        temperature=temperature,
    )
    
    # 处理流式响应
    full_content = ""
    for response in responses:
        content = response.output.choices[0]['message']['content']
        full_content = content
    
    return full_content
```

## 配置文件格式

LLM配置存储在 `config/llm_config.yaml`：

```yaml
llm:
  api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
  base_url: "https://api.openai.com/v1"  # 可选，支持代理

claude:
  api_key: "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx"

qwen:
  api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

**安全提示**：
- 配置文件应添加到 `.gitignore`
- 生产环境建议使用环境变量
- 定期轮换API密钥

## 使用示例

### 基础使用

```python
from modules.llm import GPT

# 创建LLM实例
llm = GPT(model="gpt-4o-mini")

# 单次提问
response = await llm.ask("解释什么是集群机器人")
print(response)
```

### 带记忆的对话

```python
# 开启对话记忆
llm = GPT(model="gpt-4o-mini", memorize=True)

# 多轮对话
response1 = await llm.ask("我叫张三")
response2 = await llm.ask("我叫什么名字？")  # 会记住之前的对话
print(response2)  # 输出：您叫张三

# 重置对话
llm.reset("你是一个专业的机器人工程师")
```

### 切换不同模型

```python
# 使用GPT-4
gpt4 = GPT(model="gpt-4")

# 使用Claude
from modules.llm import Claude
claude = Claude(model="claude-3-5-sonnet-20241022")

# 使用通义千问
from modules.llm import Qwen
qwen = Qwen(model="qwen-max")

# 三者接口一致
responses = await asyncio.gather(
    gpt4.ask("分析这个任务"),
    claude.ask("分析这个任务"),
    qwen.ask("分析这个任务"),
)
```

### 在ActionNode中使用

```python
class MyAction(ActionNode):
    def __init__(self):
        super().__init__()
        # 从上下文参数获取模型名称
        model_name = self.context.args.llm_name
        self._llm = GPT(modeL_name=model_name)
    
    async def _run(self):
        # 调用LLM
        response = await self._llm.ask(self.prompt)
        return response
```

## 重试机制详解

所有LLM实现都使用 `tenacity` 库实现重试：

```python
from tenacity import retry, stop_after_attempt, wait_random_exponential

@retry(
    stop=stop_after_attempt(10),           # 最多重试10次
    wait=wait_random_exponential(          # 指数退避
        multiplier=1,                      # 基础乘数
        max=60                             # 最大等待60秒
    )
)
async def _ask_with_retry(self, temperature: float) -> str:
    # LLM调用逻辑
```

**重试策略**：
- 第1次失败：等待 1-2 秒
- 第2次失败：等待 2-4 秒
- 第3次失败：等待 4-8 秒
- ...
- 最多等待60秒

**适用场景**：
- API限流（Rate Limit）
- 网络不稳定
- 服务暂时不可用

## 错误处理

### 常见错误类型

```python
try:
    response = await llm.ask(prompt)
except Exception as e:
    if "rate_limit" in str(e):
        # API限流，重试会自动处理
        pass
    elif "authentication" in str(e):
        # API密钥错误
        logger.error("请检查API密钥配置")
    elif "timeout" in str(e):
        # 超时
        logger.error("请求超时，请检查网络")
```

### 日志记录

系统自动记录LLM交互：

```python
logger.log(f"Prompt:\n {self.prompt}", "debug")
logger.log(f"Response:\n {response}", "info")
```

## 性能优化

### 1. 并发调用

使用 `asyncio.gather` 并发调用多个LLM：

```python
# 同时为多个函数生成代码
tasks = [llm.ask(prompt) for prompt in prompts]
responses = await asyncio.gather(*tasks)
```

### 2. 温度参数调优

```python
# 需要稳定输出（代码生成）
response = await llm.ask(prompt, temperature=0.7)

# 需要创意输出（设计阶段）
response = await llm.ask(prompt, temperature=1.0)
```

### 3. 模型选择策略

- **GPT-4**：复杂任务、高质量要求
- **GPT-3.5**：简单任务、快速响应
- **Claude**：长文本处理、深度分析
- **Qwen**：中文任务、成本敏感场景

## 扩展新的LLM

实现新的LLM只需继承 `BaseLLM` 并实现 `_ask_with_retry`：

```python
class NewLLM(BaseLLM):
    def __init__(self, model="new-model", memorize=False):
        super().__init__(model, memorize)
        # 初始化客户端
        self.client = SomeNewLLMClient()
    
    @retry(stop=stop_after_attempt(10))
    async def _ask_with_retry(self, temperature: float) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self._memories)
        
        # 调用新LLM的API
        response = await self.client.complete(
            messages=messages,
            temperature=temperature,
        )
        
        return response.text
```

## 与Prompt模块的协作

LLM模块通常与Prompt模块配合使用：

```python
from modules.prompt import Prompt
from modules.llm import GPT

# 获取提示词模板
prompt_template = Prompt().get_prompt("AnalyzeSkills", "global")

# 填充模板
filled_prompt = prompt_template.format(
    task_des=task_description,
    constraints=constraints_str
)

# 调用LLM
llm = GPT()
response = await llm.ask(filled_prompt)
```

## 下一步

阅读 [Prompt 模块](./03_prompt.md) 了解如何设计有效的提示词模板。
