# Deployment 部署模块

## 概述

`deployment` 模块负责在仿真或真实环境中执行生成的控制代码。它提供了多种物理引擎、实体对象、环境封装和执行脚本，支持从代码到实际运行的完整流程。

## 模块结构

```
deployment/
├── engine/              # 硬件平台抽象
│   ├── base_engine.py          # 引擎基类
│   ├── quadtree_engine.py      # 四叉树仿真引擎（推荐使用）
│   ├── box2d_engine.py         # Box2D引擎（不推荐，存在问题）
│   ├── pybullet_engine.py      # PyBullet引擎（不推荐，存在问题）
│   ├── mujoco_engine.py        # MuJoCo引擎（不推荐，存在问题）
│   └── omni_engine.py          # 真实硬件平台引擎示例
├── entity/             # 实体对象定义
│   ├── robot.py               # 机器人实体
│   ├── obstacle.py            # 障碍物
│   ├── landmark.py            # 地标点
│   └── prey.py                # 猎物（用于追捕任务）
├── gymnasium_env/      # Gymnasium环境实现
│   ├── gymnasium_base_env.py        # 环境基类
│   ├── gymnasium_flocking_env.py    # 集群飞行环境
│   ├── gymnasium_covering_env.py    # 区域覆盖环境
│   ├── gymnasium_aggregation_env.py # 聚合环境
│   ├── gymnasium_encircling_env.py  # 包围环境
│   └── ... (其他任务环境)
├── execution_scripts/  # 执行脚本
│   ├── apis.py               # 局部API实现
│   ├── global_apis.py        # 全局API实现
│   ├── run.py                # 局部运行脚本模板
│   └── allocate_run.py       # 全局分配脚本模板
├── real_env/          # 真实环境接口
│   └── ros_interface.py      # ROS通信接口
└── utils/             # 部署工具
    ├── coordinate_transform.py  # 坐标转换
    ├── collision_detection.py   # 碰撞检测
    └── visualization.py         # 可视化工具
```

## Engine 硬件平台抽象

### 重要说明

**Engine不是物理引擎，而是硬件平台的抽象接口**。系统预置的engine（如QuadTreeEngine、Box2DEngine等）是针对仿真环境的实现。

**如果您有自己的硬件平台**（如真实机器人、无人机、定制化硬件），需要实现自己的Engine类，提供基础的控制技能接口。

### BaseEngine - 硬件平台基类

定义了所有硬件平台必须实现的通用接口：

```python
class BaseEngine(ABC):
    def __init__(self):
        self.entities = []  # 所有实体对象
    
    @abstractmethod
    def step(self, dt: float):
        """执行一个控制周期"""
        pass
    
    @abstractmethod
    def add_entity(self, entity):
        """添加实体到平台（注册机器人）"""
        pass
    
    @abstractmethod
    def remove_entity(self, entity):
        """从平台移除实体（注销机器人）"""
        pass
    
    @abstractmethod
    def check_collision(self, entity1, entity2) -> bool:
        """检测两个实体是否发生碰撞（可选实现）"""
        pass
```

### 预置Engine示例

系统提供了几个Engine实现供参考。**强烈推荐使用QuadTreeEngine进行仿真验证**。

> ⚠️ **重要提示**：
> - **推荐使用**：QuadTreeEngine（稳定、高效）
> - **不推荐使用**：Box2DEngine、PyBulletEngine、MuJoCoEngine（存在已知问题）
> - **真实硬件**：OmniEngine是真实硬件平台的示例，用户应根据自己的硬件实现自定义Engine

#### QuadTreeEngine - 2D仿真平台 ⭐ 推荐

**特点**：
- 轻量级2D仿真
- 高效的碰撞检测（基于四叉树）
- 适合大规模机器人集群仿真

**实现参考**：
```python
class QuadTreeEngine(BaseEngine):
    def __init__(self, world_size, alpha=0.5, damping=0.75):
        self.world_size = world_size    # 仿真世界大小
        self.alpha = alpha              # 碰撞响应系数
        self.damping = damping          # 阻尼系数
        self.quadtree = QuadTree(...)   # 空间划分数据结构
    
    def step(self, dt: float):
        # 1. 更新空间索引
        self.quadtree.clear()
        for entity in self.entities:
            self.quadtree.insert(entity)
        
        # 2. 碰撞检测和响应
        for entity in self.entities:
            nearby = self.quadtree.query(entity.position, entity.radius * 2)
            for other in nearby:
                if self.check_collision(entity, other):
                    self.resolve_collision(entity, other)
        
        # 3. 更新实体状态
        for entity in self.entities:
            entity.update(dt)
```

**适用场景**：
- ✅ 2D平面集群任务的仿真验证
- ✅ 大规模机器人（100+）快速测试
- ✅ 代码生成的验证和调试
- ✅ 论文实验和算法验证

**推荐理由**：
- 轻量、稳定、经过充分测试
- 性能优秀，支持大规模仿真
- 碰撞检测准确
- 易于调试和扩展

---

#### ⚠️ 不推荐的Engine实现

以下Engine实现存在已知问题，**不建议使用**：

##### Box2DEngine - 存在问题 ❌

**问题说明**：
- 实现存在稳定性问题
- 可能导致仿真异常
- 不推荐用于生产环境

**代码仅供参考**，不建议直接使用。

##### PyBulletEngine - 存在问题 ❌

**问题说明**：
- 集成存在兼容性问题
- 性能不稳定
- 不推荐用于生产环境

##### MuJoCoEngine - 存在问题 ❌

**问题说明**：
- 实现不完善
- 存在已知bug
- 不推荐用于生产环境

> 💡 **建议**：如需3D仿真或复杂物理效果，建议自行实现自定义Engine或等待后续版本修复。

---

#### OmniEngine - 真实硬件平台示例

**重要说明**：
- OmniEngine **不是仿真引擎**，而是连接真实硬件平台的示例实现
- 代表实际的物理机器人系统或定制硬件平台
- 用户应参考此实现，根据自己的硬件平台编写自定义Engine

**用途**：
- 作为真实硬件平台Engine的实现参考
- 展示如何将生成的代码部署到实际硬件
- 提供硬件接口的设计模式

**如果您有自己的硬件平台**（如地面机器人、无人机、水下机器人等），应该：
1. 参考OmniEngine的实现结构
2. 根据硬件的通信协议实现相应接口
3. 提供硬件平台特定的基础技能（状态读取、指令发送等）

### 如何实现自定义硬件平台Engine

如果您有自己的硬件平台（如真实机器人系统），需要实现自定义Engine：

#### 步骤1：继承BaseEngine

```python
class MyRobotPlatformEngine(BaseEngine):
    """自定义机器人平台Engine"""
    
    def __init__(self, platform_config):
        super().__init__()
        # 初始化与硬件平台的连接
        self.connection = self._connect_to_platform(platform_config)
        self.robot_clients = {}  # 机器人客户端映射
```

#### 步骤2：实现必需接口

```python
    def add_entity(self, entity):
        """注册机器人到硬件平台"""
        # 与硬件平台建立连接
        robot_id = entity.id
        client = self._create_robot_client(robot_id)
        self.robot_clients[robot_id] = client
        
        # 初始化机器人
        client.initialize()
        self.entities.append(entity)
    
    def step(self, dt: float):
        """执行一个控制周期"""
        # 1. 从硬件读取当前状态
        for entity in self.entities:
            robot_id = entity.id
            client = self.robot_clients[robot_id]
            
            # 读取传感器数据
            sensor_data = client.read_sensors()
            entity.position = sensor_data['position']
            entity.velocity = sensor_data['velocity']
        
        
        # 3. 将速度指令发送到硬件
        for entity in self.entities:
            robot_id = entity.id
            client = self.robot_clients[robot_id]
            client.send_velocity_command(entity.velocity)
    
    def remove_entity(self, entity):
        """注销机器人"""
        robot_id = entity.id
        if robot_id in self.robot_clients:
            self.robot_clients[robot_id].shutdown()
            del self.robot_clients[robot_id]
        self.entities.remove(entity)
    
    def check_collision(self, entity1, entity2) -> bool:
        """碰撞检测（可选，根据硬件能力）"""
        # 如果硬件平台有碰撞传感器，可以实现
        # 否则可以基于位置简单估计
        dist = np.linalg.norm(entity1.position - entity2.position)
        return dist < (entity1.radius + entity2.radius)
```

#### 步骤3：提供平台特定的基础技能

根据您的硬件平台能力，可能需要提供额外的接口：

```python
    def get_robot_state(self, robot_id: int) -> Dict:
        """获取机器人状态（供生成代码调用）"""
        client = self.robot_clients[robot_id]
        return client.get_full_state()
    
    def set_robot_velocity(self, robot_id: int, vx: float, vy: float):
        """设置机器人速度（供生成代码调用）"""
        client = self.robot_clients[robot_id]
        client.set_velocity(vx, vy)
    
    def emergency_stop(self):
        """紧急停止所有机器人"""
        for client in self.robot_clients.values():
            client.stop()
```

### Engine实现要点

1. **状态同步**：确保从硬件读取的状态及时更新到entity对象
2. **指令发送**：将控制指令可靠地发送到硬件平台
3. **错误处理**：处理硬件通信失败、超时等异常情况
4. **安全机制**：实现紧急停止、越界保护等安全功能
5. **时间同步**：保证控制周期的时间准确性

### 真实硬件平台示例

如果您使用ROS机器人平台：

```python
class ROSPlatformEngine(BaseEngine):
    def __init__(self):
        import rospy
        rospy.init_node('genswarm_engine')
        self.velocity_publishers = {}
        self.state_subscribers = {}
    
    def add_entity(self, entity):
        robot_id = entity.id
        
        # 创建速度发布器
        topic = f'/robot_{robot_id}/cmd_vel'
        self.velocity_publishers[robot_id] = rospy.Publisher(
            topic, Twist, queue_size=10
        )
        
        # 订阅状态
        topic = f'/robot_{robot_id}/odom'
        self.state_subscribers[robot_id] = rospy.Subscriber(
            topic, Odometry, 
            lambda msg: self._update_state(entity, msg)
        )
        
        self.entities.append(entity)
    
    def step(self, dt: float):
        # ROS通过回调自动更新状态
        # 这里只需要等待一个周期
        rospy.sleep(dt)
```

### 总结

- **Engine是硬件平台抽象**，不仅仅是物理仿真
- **预置Engine**用于仿真环境，供参考和快速验证
- **自定义Engine**需要实现BaseEngine接口，连接您的硬件平台
- **关键是提供基础技能**：状态读取、指令发送、实体管理

## Entity 实体对象

### Robot - 机器人实体

```python
class Robot:
    def __init__(self, robot_id: int, position: np.ndarray, 
                 radius: float = 0.15):
        self.id = robot_id
        self.position = position        # [x, y]
        self.velocity = np.zeros(2)     # [vx, vy]
        self.radius = radius
        self.color = (0, 0, 255)       # 蓝色
        
        # 状态
        self.target_position = None
        self.task = None
        
        # 物理属性
        self.max_speed = 1.0
        self.max_acceleration = 2.0
    
    def update(self, dt: float):
        """更新位置"""
        # 限制速度
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = self.velocity / speed * self.max_speed
        
        # 更新位置
        self.position += self.velocity * dt
    
    def set_velocity(self, vx: float, vy: float):
        """设置速度（由控制代码调用）"""
        self.velocity = np.array([vx, vy])
```

**关键属性**：
- `id`: 唯一标识
- `position`: 当前位置
- `velocity`: 当前速度
- `task`: 分配的任务
- `neighbors`: 邻居列表

### Obstacle - 障碍物

```python
class Obstacle:
    def __init__(self, position: np.ndarray, radius: float):
        self.position = position
        self.radius = radius
        self.color = (128, 128, 128)  # 灰色
        self.is_static = True         # 静态对象
```

### Landmark - 地标点

```python
class Landmark:
    def __init__(self, landmark_id: int, position: np.ndarray):
        self.id = landmark_id
        self.position = position
        self.color = (0, 255, 0)      # 绿色
        self.radius = 0.1
```

**用途**：
- 目标点（aggregation任务）
- 编队参考点
- 路径点

### Prey - 猎物

```python
class Prey:
    def __init__(self, prey_id: int, position: np.ndarray):
        self.id = prey_id
        self.position = position
        self.velocity = np.random.randn(2) * 0.5
        self.color = (255, 0, 0)      # 红色
        self.max_speed = 0.8
    
    def update(self, dt: float, robots: List[Robot]):
        """逃离机器人"""
        escape_force = np.zeros(2)
        for robot in robots:
            diff = self.position - robot.position
            dist = np.linalg.norm(diff)
            if dist < 2.0:  # 感知范围
                escape_force += diff / (dist ** 2)
        
        self.velocity += escape_force * dt
        # 限速并更新位置...
```

**用途**：
- 追捕任务
- 动态目标

## Gymnasium Environment 环境封装

### GymnasiumEnvironmentBase - 环境基类

遵循Gymnasium标准接口：

```python
class GymnasiumEnvironmentBase(gymnasium.Env, ABC):
    def __init__(self, data_file: str):
        # 从配置文件加载环境参数
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        # 初始化物理引擎
        engine_type = self.data.get("engine_type", "QuadTreeEngine")
        if engine_type == "QuadTreeEngine":
            self.engine = QuadTreeEngine(...)
        elif engine_type == "Box2DEngine":
            self.engine = Box2DEngine(...)
        
        # 创建实体
        self.robots = []
        self.obstacles = []
        self.landmarks = []
        
        # 定义观察和动作空间
        self.get_spaces()
        
        # 渲染
        self.screen = None
        self.clock = pygame.time.Clock()
    
    def reset(self, seed=None, options=None):
        """重置环境"""
        # 重新初始化实体位置
        self._initialize_entities()
        
        # 获取初始观察
        observation = self._get_obs()
        info = {}
        
        return observation, info
    
    def step(self, action):
        """执行一步"""
        # 1. 应用动作（设置机器人速度）
        self._apply_action(action)
        
        # 2. 物理仿真
        self.engine.step(self.dt)
        
        # 3. 计算奖励
        reward = self._compute_reward()
        
        # 4. 检查终止条件
        terminated = self._is_terminated()
        truncated = self.time_step > self.max_steps
        
        # 5. 获取观察
        observation = self._get_obs()
        info = self._get_info()
        
        self.time_step += 1
        
        return observation, reward, terminated, truncated, info
    
    def render(self):
        """渲染当前帧"""
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode(
                (self.width * self.scale_factor, 
                 self.height * self.scale_factor)
            )
        
        # 绘制背景
        self.screen.fill((255, 255, 255))
        
        # 绘制实体
        for obstacle in self.obstacles:
            self._draw_circle(obstacle.position, obstacle.radius, 
                            obstacle.color)
        for robot in self.robots:
            self._draw_circle(robot.position, robot.radius, 
                            robot.color)
        for landmark in self.landmarks:
            self._draw_circle(landmark.position, landmark.radius, 
                            landmark.color)
        
        pygame.display.flip()
        self.clock.tick(self.FPS)
    
    @abstractmethod
    def _compute_reward(self) -> float:
        """计算奖励（子类实现）"""
        pass
    
    @abstractmethod
    def _is_terminated(self) -> bool:
        """判断是否终止（子类实现）"""
        pass
```

## 环境配置文件

### 配置文件格式（JSON）

**推荐配置示例**（使用QuadTreeEngine）：

```json
{
    "dt": 0.01,
    "engine_type": "QuadTreeEngine",  // 推荐：稳定可靠的仿真引擎
    "display": {
        "width": 10.0,
        "height": 10.0,
        "scale_factor": 50
    },
    "entities": {
        "robot": {
            "count": 20,
            "radius": 0.15,
            "max_speed": 1.0,
            "id_list": [0, 1, 2, ..., 19]
        },
        "obstacle": {
            "count": 5,
            "positions": [[2.0, 3.0], [5.0, 5.0], ...],
            "radii": [0.5, 0.5, ...]
        },
        "landmark": {
            "count": 1,
            "positions": [[5.0, 5.0]]
        }
    },
    "render_mode": "human",
    "output_file": "simulation_data.json"
}
```

**真实硬件平台配置示例**：

```json
{
  "display": {
    "#width and height note": "unit: meter",
    "width": 5,
    "height": 5,
    "#scale_factor_note": "1 meter = 100 pixel",
    "scale_factor": 100
  },
  "task_name": "encircling",
  "#entity note": "position/size/perceptual_range unit: meter",
  "#size note": "the radium of the circle # | the side length of the square robot",
  "#agent number note": "sum of robot + leader",
  "entities": {
    "robot": {
      "count": 5,
      "specified": [],
      "size": 0.15,
      "color": "green",
      "shape": "circle",
      "perceptual_range": 1,
      "id_list": [
        3,
        6,
        5,
        8,
        9
      ]
    },
    "leader": {
      "count": 0,
      "specified": []
    },
    "obstacle": {
      "count": 2,
      "specified": [],
      "size": 0.15,
      "shape": "circle",
      "color": "green",
      "id_list": [
        4,
        9
      ]
    },
    "sheep": {
      "count": 0,
      "specified": []
    },
    "prey": {
      "count": 1,
      "specified": [],
      "id_list": [
        10
      ]
    },
    "landmark": {
      "count": 0,
      "specified": []
    },
    "pushable_object": {
      "count": 0,
      "specified": []
    }
  },
  "engine_type": "OmniEngine",
  "render_mode": "human",
  "output_file": "output.json",
  "dt": 0.1
}
```

> ⚠️ **重要提示**：
> - **仿真验证**：使用 `"engine_type": "QuadTreeEngine"`
> - **真实硬件**：使用您的自定义Engine名称
> - **不要使用**：`"Box2DEngine"`, `"PyBulletEngine"`, `"MuJoCoEngine"`（存在已知问题）
```

## 使用示例

### 创建和运行环境

```python
# 创建环境
env = GymnasiumFlockingEnv(data_file="config/flocking_config.json")

# 重置环境
observation, info = env.reset()

# 运行仿真
for step in range(1000):
    # 生成的代码会设置机器人速度
    # 这里简化为随机动作
    action = env.action_space.sample()
    
    # 执行
    obs, reward, terminated, truncated, info = env.step(action)
    
    # 渲染
    env.render()
    
    if terminated or truncated:
        break

env.close()
```


## 下一步

阅读 [File & Utils 模块](./05_file_utils.md) 了解文件管理和通用工具。
