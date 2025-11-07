# File & Utils 工具模块

## 概述

`file` 和 `utils` 模块提供了系统的基础设施支持，包括文件管理、日志记录、代码分析、可视化等通用功能。这些工具被整个系统广泛使用。

## File 模块

### 模块结构

```
file/
├── __init__.py          # 模块导出
├── base_file.py        # 文件基类
├── file.py             # 文件管理类
└── log_file.py         # 日志文件类
```

### File - 文件管理类

统一的文件读写接口，带版本管理和状态跟踪：

```python
class FileStatus(Enum):
    NOT_WRITTEN = 0    # 未写入
    NOT_TESTED = 1     # 已写入但未测试
    TESTED_FAIL = 2    # 测试失败
    TESTED_PASS = 3    # 测试通过

class File(BaseFile):
    def __init__(self, name: str = "", message: str = "", root: str = ""):
        self.version = 0                # 版本号
        self._name = name               # 文件名
        self._root = root or workspace_root  # 根目录
        self._status = FileStatus.NOT_WRITTEN
        self._message = message         # 文件内容
```

**核心功能**：

#### 1. 读取文件

```python
file = File(name="example.py")
content = file.read()  # 自动从 root/name 读取
```

#### 2. 写入文件

```python
file = File(name="generated_code.py")
file.message = code_content  # 设置内容时自动写入
```

**自动行为**：
- 写入时自动创建目录
- 自动记录日志
- 更新文件状态

#### 3. 复制文件

```python
new_file = file.copy(root="/new/path", name="new_name.py")
```

#### 4. 懒加载

```python
file = File(name="large_file.txt")
# 此时还未读取文件

content = file.message  # 访问时才真正读取
```

**优点**：节省内存，避免不必要的IO

#### 5. 根目录切换

```python
file.root = "/new/workspace"
# 自动复制文件到新位置
```

**用途**：
- 切换工作空间
- 迁移文件
- 测试环境隔离

### LogFile - 日志文件

特殊的文件类，用于记录系统日志：

```python
class LogFile:
    def __init__(self):
        self._file = None
        self._level_colors = {
            "debug": "blue",
            "info": "green",
            "warning": "yellow",
            "error": "red",
            "success": "bright_green"
        }
    
    def set_file(self, file: File):
        """设置日志文件"""
        self._file = file
    
    def log(self, message: str, level: str = "info", 
            print_to_terminal: bool = True):
        """记录日志"""
        # 1. 格式化消息
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level.upper()}] {message}"
        
        # 2. 写入文件
        if self._file:
            self._file.write(formatted + "\n", mode="a")
        
        # 3. 打印到终端（带颜色）
        if print_to_terminal:
            color = self._level_colors.get(level, "white")
            rich_print(formatted, style=color)

# 全局日志实例
logger = LogFile()
```

**使用示例**：

```python
from modules.file import logger, File

# 设置日志文件
logger.set_file(File("log.md"))

# 记录不同级别的日志
logger.log("Starting workflow", "info")
logger.log("Potential issue detected", "warning")
logger.log("Code generation failed", "error")
logger.log("All tests passed!", "success")
logger.log("Detailed debug info", "debug", print_to_terminal=False)
```

**日志级别**：
- **debug**: 详细调试信息（默认不打印到终端）
- **info**: 一般信息
- **warning**: 警告信息
- **error**: 错误信息
- **success**: 成功信息

## Utils 模块

### 模块结构

```
utils/
├── __init__.py          # 模块导出
├── logger.py           # 标准日志工具
├── root.py             # 根目录管理
├── code_analyzer.py    # 代码分析工具
├── media.py            # 媒体处理（视频、图像）
├── rich_print.py       # 美化终端输出
├── run_scripts.py      # 脚本执行工具
└── save_json.py        # JSON序列化工具
```

### Logger - 标准日志

基于Python logging模块，提供彩色终端输出：

```python
class LoggerLevel(Enum):
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING

def setup_logger(name, level=LoggerLevel.INFO):
    """
    创建日志记录器
    
    Args:
        name: 日志记录器名称（通常用类名）
        level: 日志级别
    
    Returns:
        配置好的logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.value)
    
    # 彩色格式化器
    ch = logging.StreamHandler()
    formatter = ColoredFormatter("%(created)s%(name)s%(levelname)s %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger
```

**使用示例**：

```python
from modules.utils import setup_logger, LoggerLevel

# 在类中使用
class MyAction:
    def __init__(self):
        self._logger = setup_logger(self.__class__.__name__, LoggerLevel.DEBUG)
    
    def run(self):
        self._logger.info("Starting action")
        self._logger.debug("Detailed info")
        self._logger.warning("Be careful")
        self._logger.error("Something went wrong")
```

**颜色方案**：
- DEBUG: 蓝色
- INFO: 绿色
- WARNING: 黄色
- ERROR: 红色
- CRITICAL: 洋红色

### RootManager - 根目录管理

管理工作空间和项目根目录：

```python
class RootManager:
    def __init__(self):
        self._project_root = None
        self._workspace_root = None
    
    @property
    def project_root(self) -> Path:
        """项目根目录（代码仓库根）"""
        if not self._project_root:
            # 自动检测（找到包含.git的目录）
            self._project_root = self._find_project_root()
        return self._project_root
    
    @property
    def workspace_root(self) -> Path:
        """工作空间目录（生成代码存放处）"""
        return self._workspace_root
    
    def update_root(self, args=None, path=None) -> str:
        """
        更新工作空间根目录
        
        根据参数创建新的工作空间目录，格式：
        workspace/{task_name}/{timestamp}
        
        Returns:
            创建的目录名（timestamp部分）
        """
        if path:
            self._workspace_root = Path(path)
            return path
        
        # 生成时间戳目录名
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        task_name = args.run_experiment_name[0]
        
        workspace_path = self.project_root / "workspace" / task_name / timestamp
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        self._workspace_root = workspace_path
        
        logger.log(f"Workspace created: {workspace_path}", "info")
        
        return timestamp

# 全局单例
root_manager = RootManager()
```

**使用示例**：

```python
from modules.utils import root_manager

# 获取项目根目录
project_root = root_manager.project_root
config_path = project_root / "config" / "llm_config.yaml"

# 创建新工作空间
timestamp = root_manager.update_root(args=args)

# 获取工作空间
workspace = root_manager.workspace_root
output_file = workspace / "generated_code.py"
```

**目录结构示例**：

```
GenSwarm/                          # project_root
├── modules/
├── config/
└── workspace/                     
    ├── flocking/
    │   ├── 2024-01-15_10-30-00/  # workspace_root
    │   │   ├── generated_code.py
    │   │   ├── run.py
    │   │   └── log.md
    │   └── 2024-01-15_14-20-00/
    └── covering/
        └── ...
```

### Media - 媒体处理

处理视频和图像：

```python
class MediaProcessor:
    @staticmethod
    def create_video_from_frames(frame_dir: Path, output_path: Path, 
                                 fps: int = 30):
        """
        从帧图像创建视频
        
        Args:
            frame_dir: 帧图像目录
            output_path: 输出视频路径
            fps: 帧率
        """
        import cv2
        
        # 获取所有帧
        frames = sorted(frame_dir.glob("frame_*.png"))
        
        if not frames:
            logger.log("No frames found", "error")
            return
        
        # 读取第一帧获取尺寸
        first_frame = cv2.imread(str(frames[0]))
        height, width, _ = first_frame.shape
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # 写入所有帧
        for frame_path in frames:
            frame = cv2.imread(str(frame_path))
            video.write(frame)
        
        video.release()
        logger.log(f"Video created: {output_path}", "success")
    
    @staticmethod
    def extract_keyframes(video_path: Path, num_frames: int = 10) -> List[np.ndarray]:
        """
        从视频提取关键帧
        
        Args:
            video_path: 视频路径
            num_frames: 提取帧数
        
        Returns:
            帧图像列表
        """
        import cv2
        
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 均匀采样
        indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        frames = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        
        cap.release()
        return frames
```

**使用示例**：

```python
from modules.utils.media import MediaProcessor

# 从仿真帧创建视频
MediaProcessor.create_video_from_frames(
    frame_dir=workspace / "frames",
    output_path=workspace / "simulation.mp4",
    fps=30
)

# 提取关键帧用于视觉评估
keyframes = MediaProcessor.extract_keyframes(
    video_path=workspace / "simulation.mp4",
    num_frames=10
)
```

### RichPrint - 美化输出

使用rich库美化终端输出：

```python
def rich_print(content: str, title: str = "", style: str = ""):
    """
    美化打印
    
    Args:
        content: 内容
        title: 标题
        style: 样式（颜色）
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    console = Console()
    
    if title:
        panel = Panel(content, title=title, style=style)
        console.print(panel)
    else:
        console.print(content, style=style)

def rich_input(prompt: str) -> str:
    """美化输入提示"""
    from rich.prompt import Prompt
    return Prompt.ask(prompt)

def print_table(data: List[Dict], title: str = ""):
    """
    打印表格
    
    Args:
        data: 字典列表，每个字典是一行
        title: 表格标题
    """
    from rich.table import Table
    from rich.console import Console
    
    if not data:
        return
    
    table = Table(title=title)
    
    # 添加列
    for key in data[0].keys():
        table.add_column(key, style="cyan")
    
    # 添加行
    for row in data:
        table.add_row(*[str(v) for v in row.values()])
    
    console = Console()
    console.print(table)
```

**使用示例**：

```python
from modules.utils.rich_print import rich_print, print_table

# 打印面板
rich_print(
    "Code generation completed successfully!",
    title="Success",
    style="green"
)

# 打印表格
results = [
    {"Task": "flocking", "Success": "✓", "Time": "45.2s"},
    {"Task": "covering", "Success": "✓", "Time": "52.1s"},
    {"Task": "encircling", "Success": "✗", "Time": "N/A"},
]
print_table(results, title="Experiment Results")
```

### SaveJson - JSON工具

安全的JSON序列化：

```python
def save_json(data: dict, file_path: Path, indent: int = 4):
    """
    保存JSON文件
    
    处理numpy类型、日期等特殊对象
    """
    import json
    import numpy as np
    from datetime import datetime
    
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent, cls=NumpyEncoder)

def load_json(file_path: Path) -> dict:
    """加载JSON文件"""
    import json
    with open(file_path, 'r') as f:
        return json.load(f)
```

**使用示例**：

```python
from modules.utils import save_json, load_json

# 保存结果（包含numpy数组）
results = {
    "task": "flocking",
    "robot_positions": np.random.rand(20, 2),  # numpy数组
    "timestamp": datetime.now(),
    "success": True
}

save_json(results, workspace / "results.json")

# 加载
loaded = load_json(workspace / "results.json")
```

## 常用工具函数

### 坐标转换

```python
def world_to_screen(world_pos: np.ndarray, world_size: Tuple[float, float],
                   screen_size: Tuple[int, int]) -> Tuple[int, int]:
    """世界坐标转屏幕坐标"""
    x = int((world_pos[0] + world_size[0]/2) / world_size[0] * screen_size[0])
    y = int((world_size[1]/2 - world_pos[1]) / world_size[1] * screen_size[1])
    return (x, y)

def screen_to_world(screen_pos: Tuple[int, int], world_size: Tuple[float, float],
                   screen_size: Tuple[int, int]) -> np.ndarray:
    """屏幕坐标转世界坐标"""
    x = (screen_pos[0] / screen_size[0]) * world_size[0] - world_size[0]/2
    y = world_size[1]/2 - (screen_pos[1] / screen_size[1]) * world_size[1]
    return np.array([x, y])
```

### 碰撞检测

```python
def check_circle_collision(pos1: np.ndarray, radius1: float,
                          pos2: np.ndarray, radius2: float) -> bool:
    """检测两个圆形是否碰撞"""
    dist = np.linalg.norm(pos1 - pos2)
    return dist < (radius1 + radius2)

def check_point_in_polygon(point: np.ndarray, polygon: List[np.ndarray]) -> bool:
    """检测点是否在多边形内（射线法）"""
    n = len(polygon)
    inside = False
    
    p1 = polygon[0]
    for i in range(1, n + 1):
        p2 = polygon[i % n]
        if point[1] > min(p1[1], p2[1]):
            if point[1] <= max(p1[1], p2[1]):
                if point[0] <= max(p1[0], p2[0]):
                    if p1[1] != p2[1]:
                        xinters = (point[1] - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
                    if p1[0] == p2[0] or point[0] <= xinters:
                        inside = not inside
        p1 = p2
    
    return inside
```

## 最佳实践

### 1. 统一使用File类

```python
# 推荐
file = File(name="code.py")
file.message = code
content = file.read()

# 不推荐
with open("code.py", "w") as f:
    f.write(code)
```

**好处**：
- 自动日志记录
- 统一的错误处理
- 版本管理
- 状态跟踪

### 2. 使用日志而非print

```python
# 推荐
logger.log("Processing started", "info")

# 不推荐
print("Processing started")
```

**好处**：
- 统一格式
- 持久化记录
- 级别控制
- 彩色输出

### 3. 使用root_manager管理路径

```python
# 推荐
file_path = root_manager.workspace_root / "output.json"

# 不推荐
file_path = "/absolute/path/to/workspace/output.json"
```

**好处**：
- 路径可移植
- 自动创建目录
- 工作空间隔离

## 下一步

阅读 [工作流程详解](./06_workflow.md) 了解各模块如何协作完成完整的代码生成流程。
